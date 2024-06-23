from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, unique=True)
    imageUrl = db.Column(db.String, nullable=True, default="static/uploads/user_thumbs/pro_img1.png")
    time_created = db.Column(DateTime(timezone=True), server_default=func.now())
    # posts = db.relationship("Post", cascade="all,delete", backref="author", order_by='Post.time_created.desc()')
    # comments = db.relationship("Comment", cascade="all,delete", backref="author")
    # liked_posts = db.relationship("Post", secondary=post_likes, backref="liked_users")
    # liked_comments = db.relationship("Comment", secondary=comment_likes, backref="liked_users")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return "User object" + self.email