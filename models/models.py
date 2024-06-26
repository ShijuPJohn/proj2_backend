from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func

db = SQLAlchemy()

author_book = db.Table("author_book",
                       db.Column("author_id", db.Integer, db.ForeignKey("authors.id")),
                       db.Column("book_id", db.Integer, db.ForeignKey("books.id"))
                       )

section_book = db.Table("section_book",
                        db.Column("section_id", db.Integer, db.ForeignKey("sections.id")),
                        db.Column("book_id", db.Integer, db.ForeignKey("books.id"))
                        )


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)
    imageUrl = db.Column(db.String, nullable=True, default="static/uploads/user_thumbs/pro_img1.png")
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())
    requests = db.relationship('Request', backref='user')
    issues = db.relationship('Issue', backref='user')
    reviews = db.relationship('Review', backref='user')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return "User object | email: " + self.email


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())
    description = db.Column(db.String, nullable=True)
    books = db.relationship("books", secondary=section_book, backref="sections")

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return "Section object | name: " + self.name


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    books = db.relationship("books", secondary=author_book, backref="authors")

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Author object | name: " + self.name


class Ebook(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    content = db.Column(db.String)
    publication_year = db.Column(db.Integer)
    requests = db.relationship('Request', backref='book')
    issues = db.relationship('Issue', backref='book')
    reviews = db.relationship('Review', backref='book')

    def __init__(self, name, content, publication_year):
        self.name = name
        self.content = content
        self.publication_year = publication_year

    def __str__(self):
        return "Ebook object | name: " + self.name


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return "Request object | name: " + self.book_id + " book is requested by user " + self.user_id


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating_score = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String, nullable=True)
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())
    date_time_edited = db.Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return "Review object"


class Issue(db.Model):
    __tablename__ = 'issues'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    returned = db.Column(db.Boolean, default=False)
    date_time_issued = db.Column(DateTime(timezone=True), server_default=func.now())
    date_time_returned = db.Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return "Issue object"
