import os
import requests
from flask import Flask, render_template, request,session,redirect,url_for,flash,jsonify
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
        books=db.session.execute("SELECT * FROM books WHERE LOWER(author) like :val OR LOWER(isbn) like :val OR LOWER(title) like :val", {"val": "%"+val+"%"}).fetchall()
        # books = db.session.query(Book).filter(or_(Book.author.ilike("%"+val+"%"),Book.isbn.ilike("%"+val+"%"),Book.title.ilike("%"+val+"%"))).all()
    return books

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/books/<int:book_id>",methods=["GET", "POST"])
def book(book_id):
    """List details about a single book."""
    # Make sure book exists.
    book=db.session.execute("SELECT * FROM books WHERE id=:book_id", {"book_id": book_id}).fetchone()
    # book = Book.query.get(book_id)
    if book is None:
        return render_template("index.html", status="No such book.")
    #Get Reviews from Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Fpqzn63x50WxFTwDduvJLA", "isbns": book.isbn})
    if res.status_code != 200:
      goodrating=0
      goodcount=0
    else:
        data=res.json()
        goodrating=data["books"][0]["average_rating"]
        goodcount=data["books"][0]["work_ratings_count"]
    # Get all reviews.
    reviews=db.session.execute("SELECT * FROM reviews JOIN users ON reviews.user_id=users.id WHERE book_id=:book_id", {"book_id": book_id}).fetchall()
    # reviews = db.session.query(Review,User).filter(Review.user_id==User.id).filter_by(book_id=book_id).all()
    return render_template("books.html", book=book, reviews=reviews,goodrating=goodrating,goodcount=goodcount)

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
        db_user=db.session.execute("SELECT * FROM users WHERE username=:username", {"username": username}).fetchone()
        # db_user = db.session.query(User).filter_by(username=username).first()
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

@app.route("/reviews",methods=["GET", "POST"])
@login_required
def review():
    if request.method == "GET":
        pass
    elif request.method == "POST":
        #Get information
        user_id=session.get("user_id")
        content=request.form.get("message").strip()
        rating=request.form.get("rating")
        book_id=request.form.get("book_id")
        #Validation
        if rating.strip() == "0":
            flash("Please Rating!!")
            return redirect(url_for("book",book_id=book_id))
        else:
            try:
                float(rating)
            except ValueError:
                raise
        if content == "":
            content="No Message"
        #only one review
        pastreview=db.session.execute("SELECT * FROM reviews WHERE book_id=:book_id AND user_id=:user_id", {"book_id": book_id,"user_id":user_id}).fetchone()
        # pastreview=Review.query.filter_by(user_id=user_id,book_id=book_id).first()
        if pastreview is not None:
            flash("Already Rated!!")
            return redirect(url_for("book",book_id=book_id))
        #Save into db
        review=Review(user_id=user_id,content=content,rating=rating,book_id=book_id)
        db.session.add(review)
        db.session.commit()
        flash("Thank you for rating")
        return redirect(url_for("book",book_id=book_id))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        #Get form information
        username=request.form.get("username")
        password=request.form.get("password")
        #chcek input format
        if username is None:
            return render_template("signup.html",status="Enter username")
        elif password is None:
            return render_template("signup.html",status="Enter password")
        #check duplicate
        db_user=db.session.execute("SELECT * FROM users WHERE username=:username", {"username": username}).fetchone()
        # db_user=db.session.query(User).filter_by(username=username).first()
        if db_user is not None:
            return render_template("signup.html",status=db_user.username + " is already taken")
        #save in db
        user=User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        return render_template("index.html",status="signup successed, plz login")
    elif request.method == "GET":
        return render_template("signup.html")


# API
@app.route("/api/<string:isbn>")
def book_api(isbn):
  """Return details about a single book."""

  # Make sure book exists.
  book=db.session.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
  if book is None:
      return jsonify({"error":isbn}), 404
  # Get review information.
  review=db.session.execute("SELECT COUNT(*) AS review_count,AVG(rating) AS average_score FROM reviews WHERE book_id=:book_id", {"book_id": book.id}).fetchone()

  return jsonify({
  "title": book.title,
  "author": book.author,
  "year": book.year,
  "isbn": book.isbn,
  "review_count": review.review_count,
  "average_score": review.average_score
  })
