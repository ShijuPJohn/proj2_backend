import os
from datetime import datetime, timedelta

import jwt
from flask import request, jsonify, Blueprint
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from controllers.book_controllers import generate_unique_filename
from controllers.jwt_util import validate_token, check_role
from serializers.user_serializers import user_signup_schema, user_display_schema, users_display_schema
from app import app
from models.models import User, db

cache = Cache(app)
ma = Marshmallow(app)

user_controller = Blueprint('user_controller', __name__)


def is_librarian(user):
    return user.role == 'librarian'


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
                 "user_role": user.role,
                 "exp": datetime.utcnow() + timedelta(days=30)},
                app.config["SECRET_KEY"]
            )
            return {"user": user_display_schema.dump(user), "token": token}, 201
    except ValidationError as v:
        return jsonify({"status": "bad_request"}), 400
    except Exception as e:
        print("Exception", e)
        return jsonify({"status": "internal_server_error"}), 500


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
                 "user_role": user.role,
                 "exp": datetime.utcnow() + timedelta(days=30)},
                app.config["SECRET_KEY"]
            )
            return jsonify({"message": "login_success", "token": token}), 200
        return {"status": "invalid_credentials"}, 400
    return {"status": "invalid_data"}, 400


@user_controller.route('/api/users', methods=['GET'])
@validate_token
@check_role
@cache.cached(timeout=50)
def get_all_users(user_from_token):
    try:
        users = [user for user in User.query.all() if user != user_from_token]
        return jsonify({"users": users_display_schema.dump(users)}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "internal_server_error"}), 500


@user_controller.route('/api/user/', methods=['GET'])
@validate_token
@cache.cached(timeout=50)
def get_user_by_id(user_from_token):
    return jsonify({"user": user_display_schema.dump(user_from_token)}), 200


@user_controller.route('/api/users/<int:user_id>', methods=['PUT'])
@validate_token
def update_user(user_from_token, user_id):
    try:
        if user_from_token.id != user_id and not is_librarian(user_from_token):
            return jsonify({"message": "unauthorized"}), 403

        data = request.json
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "user_not_found"}), 404

        if 'username' in data:
            user.username = data['username']
        if not is_librarian(user_from_token) and 'email' in data:
            user.email = data['email']
        if 'about' in data:
            user.about = data['about']
        if 'imageUrl' in data:
            user.imageUrl = data['imageUrl']
        # if 'password' in data:
        #     user.password = generate_password_hash(data['password'], method="scrypt")
        db.session.add(user)
        db.session.commit()
        return jsonify({"user": user_display_schema.dump(user)}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "internal_server_error"}), 500


@user_controller.route('/api/users-password/<int:user_id>', methods=['PUT'])
@validate_token
def change_password(user_from_token, user_id):
    try:
        if user_from_token.id != user_id and not is_librarian(user_from_token):
            return jsonify({"message": "unauthorized"}), 403
        data = request.json
        user = User.query.get(user_id)
        if "current_password" not in data or "new_password" not in data:
            return jsonify({"message": "bad request"}), 400
        current_password_from_request = data["current_password"]
        new_password_from_request = data["new_password"]
        if not check_password_hash(user_from_token.password, current_password_from_request):
            return jsonify({"message": "unauthorized"}), 403
        user.password = generate_password_hash(new_password_from_request, method="scrypt")
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "password changed successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "internal_server_error"}), 500


@user_controller.route('/api/users/<int:user_id>', methods=['DELETE'])
@validate_token
def delete_user(user_from_token, user_id):
    try:
        if user_from_token.id != user_id and not is_librarian(user_from_token):
            return jsonify({"message": "unauthorized"}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "user_not_found"}), 404

        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "user_deleted"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "internal_server_error"}), 500


@user_controller.route('/api/profile-photo', methods=['POST'])
@validate_token
def upload_cover_image(user_from_token):
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    extension = file.filename.rsplit('.', 1)[1].lower()
    if file and extension in ["jpeg", "jpg", "png", "gif", "svg", "bmp"]:
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(app.config['UPLOADS_DIR'], 'user_thumbs', unique_filename)
        file.save(file_path)
        return jsonify({'message': 'File successfully uploaded', 'filename': unique_filename}), 201
    else:
        return jsonify({'error': 'Invalid file type'}), 400
