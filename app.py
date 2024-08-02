import os
from flask import Flask
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from config.config import ProductionConfig, LocalDevelopmentConfig
from models.models import db, User
from flask_caching import Cache


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    if os.getenv('ENV', "development") == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(LocalDevelopmentConfig)
    app.config['UPLOADS_DIR'] = os.path.join(app.static_folder, 'uploads')
    app.config['PROTECTED_UPLOADS_DIR'] = os.path.join('protected_uploads')
    db.init_app(app)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config["SECRET_KEY"] = "THIS_IS_MY_SUPER_SECRET"
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = 'localhost'  # or the hostname of your Redis server
    app.config['CACHE_REDIS_PORT'] = 6379  # or the port number of your Redis server
    app.config['CACHE_REDIS_DB'] = 0  # the database number (0 by default)
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'  # alternative way to set Redis URL

    return app


def create_librarian():
    existing_user = User.query.filter_by(email="spjohnninth@gmail.com").first()
    if existing_user is None:
        hashed_password = generate_password_hash(os.getenv("adminpassword"), method="scrypt")
        librarian = User(username="Librarian", email="spjohnninth@gmail.com", password=hashed_password,
                         about="Librarian of the E-Library app", role="librarian")
        db.session.add(librarian)
        db.session.commit()
        print("Librarian created")
    else:
        print("Librarian already exists")


app = create_app()
with app.app_context():
    db.create_all()
    create_librarian()
