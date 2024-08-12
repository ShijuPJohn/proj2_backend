import os

from celery.result import AsyncResult
from celery.schedules import crontab
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash

from config.config import ProductionConfig, LocalDevelopmentConfig
from models.models import db, User
from celery import Celery, Task

from worker import celery_init_app
from tasks import celery_test, celery_beat, get_monthly_stats


def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static', template_folder='templates')
    celery_app = celery_init_app(app)
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
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379
    app.config['CACHE_REDIS_DB'] = 0
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'spjohnninth'
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    app.config['MAIL_DEFAULT_SENDER'] = 'spjohnninth@gmail.com'
    return app, celery_app


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


app, celery_app = create_app()

with app.app_context():
    db.create_all()
    create_librarian()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    print("setting up job")
    # sender.add_periodic_task(20, get_monthly_stats.s(), name='add every 10', expires=100)

    sender.add_periodic_task(
        crontab(day_of_month=1),
        celery_beat.s(),
    )

    # sender.add_periodic_task(
    #     crontab(minute=16, hour=6),
    #     celery_beat.s(),
    # )