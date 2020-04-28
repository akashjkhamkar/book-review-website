
# Project 1
Web Programming with Python and JavaScript

  

Hi , this is my second submission to cs50 web ,  project 1 , i created a book review website using flask and postgresql  

**Main server file :- application.py**

**hosted on heroku** :- [https://bookd-project1.herokuapp.com/](https://bookd-project1.herokuapp.com/)

# Clone repository

# 1 . Install all dependencies
$ pip install -r requirements.txt

# 2 . Create Database 

###  psql
	tables 
	
	books :- contains all 5000 books from books.csv (id , isbn , title , author , year)

	users :- ( username , password , favourites )

	reviews :- (isbn , comment , user_id , stars)

# 3. ENV Variables
### change the following values with your values in " .env " file
FLASK_APP = application.py 
DATABASE_URL = Postgres  URI  ***OR***  local Postgres db uri
					
			for local eg.  postgresql://user:password@localhost:5432/databasename
				 	 
GOODREADS_KEY = Goodreads API Key.

or you can export variables using  command **export**

# launch
after env variables are set , website can be fired up using command 

	flask run 
# Routes 

**1 .  /**
route  takes to home page if user is authenticated 

**2 .  /login**  
 takes to login page if user is "not" authenticated

**3. /sign**
takes to sign up page if user wants to sign up

**4. /book/< string:isbn >**
takes to book page after clicking on valid book on index page using isbn (search page)

**5. /favourites**
shows all the books that user has marked as favourite

**6. /favourites_remove**
used to remove favourites books


# /api/< string:isbn >

returns json response , containing details for book of given isbn number

		eg.  ...url/api/1423121309
		
**response :-**		

	{
	  "title": "Hex Hall", 
	  "author": "Rachel Hawkins", 
	  "year": 2010, 
	  "isbn": "1423121309", 
	  "review_count": 277859, 
	  "average_score": "3.95"
	}
  **if isbn is incorrect**

	{
	  "Error": "Invalid book ISBN"
	}

	

# Security 
**1. passwords are encrypted using  "sha256_crypt "**

**2. login decorators are used over all routes except login and sign , so that only authenticated users can access the website**

**3. sessions are cleared after requst to /login and /sign**