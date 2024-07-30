from flask import Blueprint, jsonify
from flask_caching import Cache
from flask_marshmallow import Marshmallow

from app import app
from controllers.jwt_util import validate_token, check_role
from models.models import Request, db
from serializers.book_serializers import requests_display_schema, requests_populated_display_schema

cache = Cache(app)
ma = Marshmallow(app)

request_controller = Blueprint('request_controller', __name__)


@request_controller.route('/api/book-request/<int:bid>', methods=["POST"])
@validate_token
def post_request(user_from_token, bid):
    if len(user_from_token.requests) == 5:
        return jsonify({'message': 'Book already requested'}), 400
    for request in user_from_token.requests:
        if request.book_id == bid:
            return jsonify({'message': 'Book already requested'}), 400
    new_request = Request(user_id=user_from_token.id, book_id=bid)
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Book request post request received'}), 201


@request_controller.route('/api/book-request/<int:bid>', methods=["DELETE"])
@validate_token
def delete_request(user_from_token, bid):
    if bid not in [request.book_id for request in user_from_token.requests]:
        return jsonify({'message': 'No request exists for this book'}), 400
    request = [request for request in user_from_token.requests if request.book_id == bid][0]
    db.session.delete(request)
    db.session.commit()
    return jsonify({'message': 'Book request deleted'}), 200


@request_controller.route('/api/user-book-requests', methods=["GET"])
@validate_token
def get_user_requests(user_from_token, bid):
    user_requests = user_from_token.requests
    if len(user_requests) == 0:
        return jsonify({'message': "no requests found"}), 404
    return jsonify({'requests': requests_display_schema.dump(user_requests)}), 201


@request_controller.route('/api/requests', methods=["GET"])
@validate_token
@check_role
def get_all_requests(user_from_token):
    all_requests = Request.query.all()
    return jsonify({'requests': requests_populated_display_schema.dump(all_requests)}), 200
