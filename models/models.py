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
    username = db.Column(db.String, unique=False)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    about = db.Column(db.String)
    imageUrl = db.Column(db.String, nullable=True, default="static/uploads/user_thumbs/pro_img1.png")
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())
    requests = db.relationship('Request', backref='user')
    issues = db.relationship('Issue', backref='user')
    reviews = db.relationship('Review', backref='user')
    role = db.Column(db.String, nullable=False)
    created_sections = db.relationship('Section', backref='created_by')
    created_authors = db.relationship('Author', backref='created_by')
    created_ebooks = db.relationship('EBook', backref='created_by')

    def __init__(self, username, email, password, role):
        self.username = username
        self.email = email
        self.password = password
        self.role = role

    def __str__(self):
        return "User object | email: " + self.email


class EBook(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    cover_image = db.Column(db.String, default="static/uploads/user_thumbs/pro_img1.png")
    filename = db.Column(db.String)
    content = db.Column(db.String)
    publication_year = db.Column(db.Integer)
    requests = db.relationship('Request', backref='book')
    issues = db.relationship('Issue', backref='book')
    reviews = db.relationship('Review', backref='book')
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __str__(self):
        return "EBook object | name: " + self.title


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())
    description = db.Column(db.String, nullable=True)
    books = db.relationship("EBook", secondary=section_book, backref="sections")
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, name, description, created_by_id):
        self.name = name
        self.description = description
        self.created_by_id = created_by_id

    def __str__(self):
        return "Section object | name: " + self.name


class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    books = db.relationship("EBook", secondary=author_book, backref="authors")
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, name, created_by_id):
        self.name = name
        self.created_by_id = created_by_id

    def __str__(self):
        return "Author object | name: " + self.name


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    date_time_created = db.Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return "Request object | book_id: " + str(self.book_id) + " requested by user_id: " + str(self.user_id)


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
