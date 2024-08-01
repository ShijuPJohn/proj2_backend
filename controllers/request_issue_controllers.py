from flask import Blueprint, jsonify, request
from flask_caching import Cache
from flask_marshmallow import Marshmallow

from app import app
from controllers.jwt_util import validate_token, check_role
from models.models import Request, db, Issue
from serializers.book_serializers import requests_display_schema, requests_populated_display_schema, \
    issue_display_schema, issues_display_schema, issues_populated_display_schema, issue_populated_display_schema

cache = Cache(app)
ma = Marshmallow(app)

request_controller = Blueprint('request_controller', __name__)


@request_controller.route('/api/book-request/<int:bid>', methods=["POST"])
@validate_token
def create_request(user_from_token, bid):
    if len(user_from_token.requests) == 5:
        return jsonify({'message': 'Request limit reached'}), 400
    if bid in [issue.book_id for issue in user_from_token.issues if not issue.returned]:
        return jsonify({'message': 'Book already issued'}), 400
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


@request_controller.route('/api/request_librarian/<int:rid>', methods=["DELETE"])
@validate_token
@check_role
def delete_request_by_id(user_from_token, rid):
    request = Request.query.get(rid)
    print(request)
    if not request:
        return jsonify({"message": "Request not found"}), 404
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


@request_controller.route('/api/book-issue', methods=["POST"])
@validate_token
@check_role
def create_issue(user_from_token):
    data = request.json
    request_id = data["request"]
    request_object = Request.query.get(request_id)
    is_book_already_issued = not not [book.book_id for book in user_from_token.issues if
                                      book.book_id == request_object.book_id and not book.returned]
    if is_book_already_issued:
        return jsonify({'message': "same book already issued"}), 400
    if not request_object:
        return jsonify({'message': "no requests found"}), 404
    issue = Issue(user_id=request_object.user_id, book_id=request_object.book_id)
    db.session.add(issue)
    db.session.delete(request_object)
    db.session.commit()
    return jsonify({'message': 'Issue created', "issue": issue_display_schema.dump(issue)}), 201


@request_controller.route('/api/user-issues', methods=["GET"])
@validate_token
def get_user_issues(user_from_token):
    issues = [issue for issue in user_from_token.issues if not issue.returned]
    print(issues)
    if not issues:
        return jsonify({'message': "no live issues found"}), 404
    return jsonify({"issues": issues_populated_display_schema.dump(issues)}), 200
