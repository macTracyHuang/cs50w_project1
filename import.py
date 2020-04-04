import csv
from models import *
from application import get_app
from flask_session import Session

app = get_app()
session = Session(app)

# Link the Flask app with the database (no Flask app is actually being run yet).

db.init_app(app)

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader: # loop gives each column a name
        book=Book(isbn=isbn,title=title,author=author,year=int(year))
        db.session.add(book)
    db.session.commit()


if __name__ == "__main__":
    # Allows for command line interaction with Flask application
    with app.app_context():
        main()
