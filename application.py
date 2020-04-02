import os
from flask import Flask, render_template, request, session,redirect
from flask_session import Session
from functools import wraps
from models import *

app = Flask(__name__)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Tell Flask what SQLAlchemy databas to use.
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

def get_app():
    return app

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
# @login_required
def index():
    if request.method == "POST":
        pass
    return render_template("index.html",)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        pass
    return render_template("login.html",)
