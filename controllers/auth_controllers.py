from datetime import datetime, timedelta

import jwt
from flask import request, jsonify, Blueprint
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from marshmallow import post_load, ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from app import app
from models.models import User, db

cache = Cache(app)
ma = Marshmallow(app)

user_controller = Blueprint('user_controller', __name__)


class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "username", "email", "imageUrl", "password")


class UserDisplaySchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "username", "email", "imageUrl")


class UserSignupSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("username", "email", "password")

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


user_schema = UserSchema()
user_signup_schema = UserSignupSchema()
user_display_schema = UserDisplaySchema()
users_display_schema = UserDisplaySchema(many=True)


def validate_token(func):
    def w_func(*args, **kwargs):
        token = None
        if "x-token" in request.headers:
            token = request.headers["x-token"]
        if not token:
            return jsonify({"message": "token_absent"}), 401
        try:
            decoded_data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=['HS256'])
            user_id_from_token = decoded_data["user_id"]
            user = User.query.filter(User.id == user_id_from_token).first()
            kwargs["user_from_token"] = user
            val = func(*args, **kwargs)
        except Exception as e:
            print(e)
            return jsonify({"message": "invalid_token"}), 401
        return val

    w_func.__name__ = func.__name__

    return w_func


@cache.cached(timeout=30)
@user_controller.route("/api/user", methods=["POST"])
def api_user_signup():
    try:
        user_from_request = request.json
        print(request.json)
        user = user_signup_schema.load(user_from_request)
        print(user.username)
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
