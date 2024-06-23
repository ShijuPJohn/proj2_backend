import os
from flask import Flask
from flask_cors import CORS
from config.config import ProductionConfig, LocalDevelopmentConfig
from models.models import db


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

    return app


app = create_app()
