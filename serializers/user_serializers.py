from flask_marshmallow import Marshmallow
from marshmallow import post_load

from app import app
from models.models import User

ma = Marshmallow(app)


class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "username", "email", "imageUrl", "password")


class UserDisplaySchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "username", "email", "imageUrl", "role")


class UserMinimalDisplaySchema(ma.Schema):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class UserSignupSchema(ma.Schema):
    class Meta:
        model = User
        fields = ("username", "email", "password", "role")

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_signup_schema = UserSignupSchema()
user_display_schema = UserDisplaySchema()
users_display_schema = UserDisplaySchema(many=True)
user_minimal_display_schema = UserMinimalDisplaySchema()
users_minimal_display_schema = UserMinimalDisplaySchema(many=True)
