import jwt
from flask import request, jsonify

from app import app
from models.models import User


def validate_token(func):
    def w_func(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split()[1]
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


def check_role(func):
    def w_func(*args, **kwargs):
        decoded_data = kwargs.get("user_from_token")
        if not decoded_data or decoded_data.role != "librarian":
            return jsonify({"message": "unauthorized"}), 403
        return func(*args, **kwargs)

    w_func.__name__ = func.__name__

    return w_func
