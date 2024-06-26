from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)
    imageUrl = db.Column(db.String, nullable=True, default="static/uploads/user_thumbs/pro_img1.png")
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return "User object | email: " + self.email


class Section(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())
    description = db.Column(db.String, nullable=True)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return "Section object | name: " + self.name


class Author(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    # books  TODO


class Ebook(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    content = db.Column(db.String)
    publication_year = db.Column(db.Integer)

    def __init__(self, name, content, publication_year):
        self.name = name
        self.description = content
        self.publication_year = publication_year

    def __str__(self):
        return "Ebook object | name: " + self.name


class Request(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # user TODO
    # book TODO
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())


class Review(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # user TODO
    # book TODO
    rating_score = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String, nullable=True)
