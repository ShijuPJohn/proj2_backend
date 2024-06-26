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