from datetime import datetime, timedelta

import jwt
from flask import request, jsonify, Blueprint
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from serializers.user_serializers import user_signup_schema, user_display_schema
from app import app
from models.models import User, db

cache = Cache(app)
ma = Marshmallow(app)

user_controller = Blueprint('user_controller', __name__)


@cache.cached(timeout=30)
@user_controller.route("/api/user", methods=["POST"])
def api_user_signup():
    try:
        user_from_request = request.json
        user_from_request["role"] = "user"
        user = user_signup_schema.load(user_from_request)
        if user:
            hashed_password = generate_password_hash(user.password, method="scrypt")
            user.password = hashed_password
            db.session.add(user)
            db.session.commit()
            token = jwt.encode(
                {"user_id": user.id,
                 "exp": datetime.utcnow() + timedelta(days=30)},
                app.config["SECRET_KEY"]
            )
            return {"user": user_display_schema.dump(user), "token": token}
    except ValidationError:
        return jsonify({"message": "bad_request"}), 400
    except Exception as e:
        print("Exception", e)
        return jsonify({"message": "internal_server_error"}), 500


@user_controller.route('/api/user/login', methods=["POST"])
def api_user_login():
    body_data = request.get_json()
    if body_data["email"] and body_data["password"]:
        email_from_request = body_data["email"]
        password_from_request = body_data["password"]
        user = User.query.filter(User.email == email_from_request).first()
        if user and check_password_hash(user.password, password_from_request):
            token = jwt.encode(
                {"user_id": user.id,
                 "exp": datetime.utcnow() + timedelta(days=30)},
                app.config["SECRET_KEY"]
            )
            return jsonify({"message": "login_success", "token": token}), 200
        return {"message": "invalid_credentials"}, 400
    return {"message": "invalid_data"}, 400
