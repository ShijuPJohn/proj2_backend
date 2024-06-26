import os
from flask import Flask
from flask_cors import CORS
from config.config import ProductionConfig, LocalDevelopmentConfig
from models.models import db
from flask_caching import Cache


def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(LocalDevelopmentConfig)
    app.config['UPLOADS_DIR'] = 'static/uploads/'
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


app = create_app()
with app.app_context():
    db.create_all()
