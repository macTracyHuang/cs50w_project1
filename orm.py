import os
from flask import Flask
from application import get_app
from models import *

app = get_app()

# Tell Flask what SQLAlchemy databas to use.
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:a1234567@localhost"
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Link the Flask app with the database (no Flask app is actually being run yet).

db.init_app(app)

def main():
      # Create tables based on each table definition in `models`
      db.drop_all()
      db.create_all()

if __name__ == "__main__":
  # Allows for command line interaction with Flask application
  with app.app_context():
      main()
