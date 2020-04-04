import os
from flask import Flask, render_template, request, session,redirect
from functools import wraps
from models import *
from werkzeug.security import check_password_hash,generate_password_hash
from flask_session import Session

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Tell Flask what SQLAlchemy databas to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Session configuration
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "sqlalchemy"
Session(app)

def get_app():
    return app

def search_book(val):
    #check val
    if val == "":
        return None
    else:
        books = db.session.query(Book).filter(or_(Book.author.like("%"+val+"%"),Book.isbn.like("%"+val+"%"),Book.title.like("%"+val+"%"))).all()
    return books

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/books")
def books():
    pass

@app.route("/books/<int:book_id>")
def book(book_id):
    """List details about a single book."""

    # Make sure book exists.
    book = Book.query.get(book_id)
    if book is None:
        return render_template("index.html", status="No such book.")
    # Get all reviews.
    reviews = Review.query.filter_by(book_id=book_id).all()
    return render_template("books.html", book=book, reviews=reviews)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        #Get form information
        book_val=request.form.get("book_val")
        #search
        books=search_book(book_val.strip())
        if books == []:
            return render_template("index.html",status="No such book")
        elif books is None:
            return render_template("index.html",status="Empty input")
        else:
            return render_template("books.html",books=books)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id") is None:
            return render_template("login.html")
        else:
            return render_template("index.html",status="Already logged in")

    elif request.method == "POST":
        #Get form information
        username=request.form.get("username")
        password=request.form.get("password")
        #check input is valid
        if username is None:
            return render_template("login.html",status="Please enter username")
        elif password is None:
            return render_template("login.html",status="Please enter password")
        #compare data with db
        db_user = db.session.query(User).filter_by(username=username).first()
        if db_user is None:
            return render_template("login.html",status="No such user")
        else:
            db_username=db_user.username
            db_userpass=db_user.password
            if password != db_userpass:
                return render_template("login.html",status="Incorrect password")
            else:
                session["user_id"]=db_user.id
                session["user_name"]=db_username
        if session.get("user_id") == 9:
            db_username="小寶, Let's 慶餘年"
        return render_template("index.html",status="Welcome Back, Dear " + db_username)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("login.html",status="See you soon")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        #Get form information
        username=request.form.get("username")
        password=request.form.get("password")
        #chcek input format
        if username is None:
            return render_template("signin.html",status="Enter username")
        elif password is None:
            return render_template("signin.html",status="Enter password")
        #check duplicate
        db_user=db.session.query(User).filter_by(username=username).first()
        if db_user is not None:
            return render_template("signin.html",status=db_user.username + " is already taken")
        #save in db
        user=User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        return render_template("index.html",status="signin successed, plz login")
    elif request.method == "GET":
        return render_template("signin.html")
