from flask import Blueprint, jsonify, request
from flask_caching import Cache
from flask_marshmallow import Marshmallow

from app import app
from controllers.jwt_util import validate_token, check_role
from models.models import Request, db, Issue, Purchase
from serializers.book_serializers import requests_display_schema, requests_populated_display_schema, \
    issue_display_schema, issues_populated_display_schema, purchase_create_schema, purchase_populated_schema, \
    purchases_populated_schema

cache = Cache(app)
ma = Marshmallow(app)

request_controller = Blueprint('request_controller', __name__)


@request_controller.route('/api/book-request/<int:bid>', methods=["POST"])
@validate_token
def create_request(user_from_token, bid):
    if len([req for req in user_from_token.requests if req.status == "open"]) >= 5:
        return jsonify({'message': 'Request limit reached'}), 400
    if bid in [issue.book_id for issue in user_from_token.issues if not issue.returned]:
        return jsonify({'message': 'Book already issued'}), 400
    for book_id in [r.book_id for r in user_from_token.requests if r.status == "open"]:
        if book_id == bid:
            return jsonify({'message': 'Book already requested'}), 400
    new_request = Request(user_id=user_from_token.id, book_id=bid)
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Book request post request received'}), 201


@request_controller.route('/api/book-request/<int:bid>', methods=["DELETE"])
@validate_token
def delete_request(user_from_token, bid):
    if bid not in [r.book_id for r in user_from_token.requests if r.status == "open"]:
        return jsonify({'message': 'No request exists for this book'}), 400
    rq = [r for r in user_from_token.requests if r.status == "open" and r.book_id == bid][0]
    rq.status = "closed"
    db.session.add(rq)
    db.session.commit()
    return jsonify({'message': 'Request Removed'}), 200


@request_controller.route('/api/request_librarian/<int:rid>', methods=["DELETE"])
@validate_token
@check_role
def delete_request_by_requestid(user_from_token, rid):
    rq = Request.query.get(rid)
    if not request:
        return jsonify({"message": "Request not found"}), 404
    rq.status = "rejected"
    db.session.add(rq)
    db.session.commit()
    return jsonify({'message': 'Request Rejected'}), 200


@request_controller.route('/api/user-book-requests', methods=["GET"])
@validate_token
@cache.cached(timeout=50)
def get_user_requests(user_from_token, bid):
    user_requests = [rqs for rqs in user_from_token.requests if rqs.status == "open"]
    if len(user_requests) == 0:
        return jsonify({'message': "no requests found"}), 404
    return jsonify({'requests': requests_display_schema.dump(user_requests)}), 201


@request_controller.route('/api/requests', methods=["GET"])
@validate_token
@cache.cached(timeout=50)
def get_all_requests(user_from_token):
    if user_from_token.role == "librarian":
        open_requests = Request.query.filter_by(status='open').all()
    else:
        open_requests = [request for request in user_from_token.requests if request.status == "open"]
    return jsonify({'requests': requests_populated_display_schema.dump(open_requests)}), 200


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
    issue = Issue(user_id=request_object.user_id, book_id=request_object.book_id, request_id=request_id)
    request_object.status = "issued"
    db.session.add(issue)
    db.session.add(request_object)
    db.session.commit()
    return jsonify({'message': 'Issue created', "issue": issue_display_schema.dump(issue)}), 201


@request_controller.route('/api/issues', methods=["GET"])
@validate_token
@cache.cached(timeout=50)
def get_user_issues(user_from_token):
    issues = None
    if user_from_token.role == "librarian":
        issues = Issue.query.filter_by(returned=False).all()
    else:
        issues = [issue for issue in user_from_token.issues if not issue.returned]
    if not issues:
        return jsonify({'message': "no live issues found"}), 404
    return jsonify({"issues": issues_populated_display_schema.dump(issues)}), 200


@request_controller.route('/api/return-book/<bid>', methods=["PUT"])
@validate_token
def return_book(user_from_token, bid):
    print(bid)
    print(user_from_token.issues)
    issues = [issue for issue in user_from_token.issues if issue.book_id == int(bid) and not issue.returned]
    if not issues:
        return jsonify({'message': "no issues found"}), 404
    issue = issues[0]
    issue.returned = True
    db.session.add(issue)
    db.session.commit()
    return jsonify({'message': 'Book returned', "issue": issue_display_schema.dump(issue)}), 200


@request_controller.route('/api/return-book-iid/<iid>', methods=["PUT"])
@validate_token
def return_book_by_issue_id(user_from_token, iid):
    if user_from_token.role != "librarian" and int(iid) not in [issue.id for issue in user_from_token.issues if
                                                                not issue.returned]:
        return jsonify({'message': "no issues found"}), 404
    issue = Issue.query.get(int(iid))
    issue.returned = True
    db.session.add(issue)
    db.session.commit()
    return jsonify({'message': 'Book returned', "issue": issue_display_schema.dump(issue)}), 200


@request_controller.route('/api/purchases', methods=['POST'])
@validate_token
def create_purchase(user_from_token):
    try:
        data = request.json
        print(data)
        data["user_id"] = user_from_token.id
        purchase_object = purchase_create_schema.load(data)
        db.session.add(purchase_object)
        db.session.commit()
        return {"purchase": purchase_populated_schema.dump(purchase_object)}, 201

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@request_controller.route('/api/purchases', methods=['GET'])
@validate_token
@cache.cached(timeout=50)
def get_all_purchase(user_from_token):
    try:
        if user_from_token.role == "librarian":
            purchases = Purchase.query.all()
        else:
            purchases = user_from_token.purchases
        return {"purchases": purchases_populated_schema.dump(purchases)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500
