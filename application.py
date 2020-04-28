import requests
import csv , os , json

from passlib.hash import sha256_crypt

from os.path import join, dirname
from dotenv import load_dotenv
#import env variables from ".env" file 
load_dotenv(join(dirname(__file__), '.env'))

from flask import Flask, url_for , render_template , session , request , redirect , jsonify , abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config['JSON_SORT_KEYS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)    

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/login" , methods=['POST' , 'GET'])
def login():
    
    session.clear()  #clear the previous sessions or logout the user
    if  request.method=="GET":
        return render_template("login.html")
    else: #if post request is made ..
        username = request.form.get("username")
        password = request.form.get("password")


        #return error if username or password are empty or incorrect

        if not username or not password:
            error = "Enter username and password !"
            return render_template("login.html" , error=error)

        usercheck = db.execute("SELECT * FROM users WHERE username = :username" , {"username":username}).fetchone()
        if usercheck == None or not sha256_crypt.verify(password , usercheck[2]):
            error = "Wrong password or username"    
            return render_template("login.html" , error=error)

        #create session for logged in user
        session["user_id"] = usercheck[0]
        session["username"] = usercheck[1]

        #take user to home page
        return redirect("/")   

#--------------------------------------------------------------------------------------------------------------------------------

@app.route("/sign" , methods=['POST' , 'GET'])
def sign():
    session.clear()
    if request.method == "GET":
        return render_template("sign.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        #return error if username or password is empty or passwords dont match up.. 

        if not username:
            error = "PROVIDE USER NAME"
            return render_template("sign.html" , error=error)

        if not password:
            error = "PROVIDE password"
            return render_template("sign.html" , error=error)

        if password!=password2:
            error = "passwords dont match !"
            return render_template("sign.html" , error=error)


        #check for user with same username , if not , add in db  , else return error ..
        data = db.execute("SELECT * FROM users WHERE username = :name " , {"name":username}).fetchone()
        
        if data is None:
            #password is encrypted
            password = sha256_crypt.encrypt(password)
            db.execute("INSERT INTO users (username , password) VALUES(:username , :password)" , {"username":username , "password":password})
            db.commit()
            return redirect("/login")
        else:
            error = "name already exists"
            return render_template("sign.html" , error=error)


#-----------------------------------------------------------------------------------------------------------------------------------

@app.route("/" , methods=["POST" , "GET"])
@login_required #here sessions are checked , if found , user can access home page , else user must login ..
def index():    
    if request.method == "GET":
        return render_template("index.html" , data=session.get("username"))

    search = request.form.get("search")
    if not search:
        #here is empty search string is sent , error is displayed . all the jinjs code for that is stored in index.html file itself 
        return render_template("index.html" , data=" ") 

    #grab all the data matching to given string  
    rows = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:s) OR LOWER(author) LIKE LOWER(:s) OR LOWER(isbn) LIKE LOWER(:s) LIMIT 15" , {"s":"%"+search+"%"}).fetchall()
    if len(rows) == 0:
        #send error saying no book found
        return render_template("index.html" , data="*")

    #if books found , send them to index.html
    return render_template("index.html" , books=rows)


#--------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/book/<string:isbn>" , methods=["POST","GET"])
@login_required
def book(isbn):
    error = ""
    if request.method=="POST":

        comment = request.form.get("comment")
        stars = request.form.get("stars")
        
        #check for empty comment 
        if comment == None or comment=="":
            error = "Enter a valid review"
        else:
            existing_comment = db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id" , {"isbn":isbn , "user_id":session["user_id"]}).fetchone()

            if not existing_comment:
                db.execute("INSERT INTO reviews (isbn , comment , user_id , stars) VALUES (:isbn , :comment , :user_id , :stars)" , {"isbn":isbn , "comment":comment , "user_id":session["user_id"] , "stars":stars})
                db.commit()
            else:
                error = "You have already submitted a review !"
 #----------------------------get req---------------------------------------------------------   
    #use /api for for fetching all details
    res = api(isbn)
    #if book not found , return error page
    if type(res) is tuple:
        return render_template("error.html")

    #else extract json from response
    res = json.loads(res.get_data().decode("utf-8"))
    
    #fetch all the reviews for the book and make a list out of it
    comments = db.execute("SELECT users.username, comment, stars FROM users INNER JOIN reviews ON users.id = reviews.user_id WHERE isbn = :isbn ORDER BY id", {"isbn": isbn}).fetchall()
    if len(comments) > 0:
        comments = list(comments)

    return render_template("book.html" , error = error , details=res , comments=comments)


#--------------------------------------------------------------------------------------------------------------------------------
@app.route("/favourites" , methods=["GET" , "POST"])
@login_required
def fav():
    if request.method == "POST":
        
        new_fav = request.form.get("new_fav")
        
        if new_fav == None:
            return render_template("error.html")

        book_exist = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":new_fav}).fetchone()

        if not book_exist:
            return render_template("error.html")

        favs = db.execute("SELECT favourites FROM users WHERE id = :id" , {"id":session["user_id"]}).fetchone()
       
        if favs[0]!=None:
            favs = list(favs[0])
            if new_fav in favs:
                return render_template("favourites.html" , error="#")
        db.execute("UPDATE users SET favourites = array_append(favourites, :isbn)" , {"isbn":new_fav})
        db.commit()               
    
    books=[]
    fav = db.execute("SELECT favourites FROM users WHERE username=:username" , {"username":session["username"]}).fetchone()
    error = "*"
    if fav[0]!=None :
        if len(fav[0])!=0:
            fav = list(fav[0])
            for i in fav:
                books.append(db.execute("SELECT * FROM books WHERE isbn=:isbn" , {"isbn":str(i)}).fetchone())
            error = " "
    return render_template("favourites.html" , books = books , error=error)
#--------------------------------------------------------------------------------------------------------------------------------
@app.route("/favourites_remove" , methods=["POST"])
@login_required
def fav_remove():
    if request.method == "POST":
        
        new_fav = request.form.get("new_fav")
        
        if new_fav == None:
            return render_template("error.html")
        favs = db.execute("SELECT favourites FROM users WHERE id = :id" , {"id":session["user_id"]}).fetchone()
        
        if favs[0]==None:
            return render_template("favourites.html" , books = [], error="*")

        favs = list(favs[0])
        if new_fav in favs:
            db.execute("UPDATE users SET favourites = array_remove(favourites, :isbn)" , {"isbn":new_fav})
            db.commit()               
        else:
            return render_template("error.html")

        return redirect("/favourites")
#--------------------------------------------------------------------------------------------------------------------------------
#here the api is used for external use and also used in /book/ route to get book details

@app.route("/api/<string:isbn>" , methods=["GET"])
@login_required
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn" , {"isbn":isbn})

    #find the book with given isbn number . if not found , return error message
    if book.rowcount!=1:
        return jsonify({"Error": "Invalid book ISBN"}), 404
    book= list(book.fetchall()[0])
    
    
    #fetch goodread details about book

    details = requests.get("https://www.goodreads.com/book/review_counts.json" , params={"key":"uNhLANABkNFFb4mRUx9yjA" , "isbns": book[1]}).json()["books"][0]
    
    book.append(details)

    #put all the data in array "book" , use it to create dictionary "data"
    
    data = {"title":book[2],"author":book[3],"year":book[4],"isbn":book[1],"review_count":book[5]["reviews_count"],"average_score":book[5]["average_rating"]}

    #return data in json format
    return jsonify(data)