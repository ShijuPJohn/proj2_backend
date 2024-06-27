from flask_marshmallow import Marshmallow
from marshmallow import post_load
from marshmallow_sqlalchemy import fields

from app import app
from models.models import User, Section, EBook, Author
from serializers.user_serializers import user_display_schema

ma = Marshmallow(app)


class SectionMinimalDisplaySchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("name", "id")


section_minimal_display_schema = SectionMinimalDisplaySchema()


class SectionCreateSchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("name", "description", "image_url", "created_by_id")

    @post_load
    def make_section(self, data, **kwargs):
        return Section(**data)


section_create_schema = SectionCreateSchema()


class SectionSchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("id", "name", "date_time_created", "description", "image_url", "created_by_id")


section_schema = SectionSchema()


class EBookSchema(ma.Schema):
    class Meta:
        model = EBook

    authors = fields.Nested(user_display_schema)
    sections = fields.Nested(section_minimal_display_schema)


ebook_schema = EBookSchema()


class EBookCreateSchema(ma.Schema):
    class Meta:
        model = EBook
        fields = ("title", "description", "cover_image", "content", "publication_year", "created_by_id", "section_id",
                  "author_id")

    @post_load
    def make_post(self, data, **kwargs):
        return EBook(**data)


ebook_create_schema = EBookCreateSchema()


# -------------------------------------------------------------------------------------

class AuthorCreateSchema(ma.Schema):
    class Meta:
        model = Author
        fields = ("name", "created_by_id")

    @post_load
    def make_author(self, data, **kwargs):
        return Author(**data)


author_create_schema = AuthorCreateSchema()


class AuthorSchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("id", "name", "date_time_created", "description", "image_url", "created_by_id")


author_schema = SectionSchema()

#
# class PostDisplaySchema(ma.Schema):
#     class Meta:
#         model = Post
#         fields = (
#             "id", "title", "meta_description", "description", "author", "archived", "cover_image", "draft",
#             "categories", "time_created", "approved",
#             "seo_slug")
#
#     author = fields.Nested(user_display_schema)
#     categories = fields.Nested(categories_minimal_schema)
#
#
# class PostMinimalDisplaySchema(ma.Schema):
#     class Meta:
#         model = Post
#         fields = (
#             "id", "title", "meta_description", "description", "author", "archived", "cover_image", "draft",
#             "categories", "time_created",
#             "seo_slug", "approved")
#
#     author = fields.Nested(user_display_schema)
#     categories = fields.Nested(categories_minimal_schema)
#
#
# class CategoryCreateSchema(ma.Schema):
#     class Meta:
#         model = Category
#         fields = ("name", "author_id")
#
#     @post_load
#     def make_category(self, data, **kwargs):
#         return Category(**data)
