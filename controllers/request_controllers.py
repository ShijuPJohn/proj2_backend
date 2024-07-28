from flask import Blueprint
from flask_caching import Cache
from flask_marshmallow import Marshmallow

from app import app

cache = Cache(app)
ma = Marshmallow(app)

request_controller = Blueprint('request_controller', __name__)

@request_controller.post(methods=["POST"])
def post_request():

