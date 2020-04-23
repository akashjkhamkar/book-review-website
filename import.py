import csv , os
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# engine = create_engine("postgresql://akash:skylinesky5@localhost:5432/test1") 
print(os.getenv("KEY"))
engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))


f = open("books.csv")
reader = csv.reader(f)

for isbn , title , author , year in reader:
    db.execute("INSERT INTO books (isbn , title , author , year) VALUES (:isbn , :title , :author , :year)" , {"isbn":isbn , "title":title , "author":author , "year":year})
    print(f"ADDED :- {title} {isbn} {author} {year}")
db.commit()