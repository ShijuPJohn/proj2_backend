from flask_marshmallow import Marshmallow
from marshmallow import post_load
from marshmallow_sqlalchemy import fields

from app import app
from models.models import Section, EBook, Author
from serializers.user_serializers import user_display_schema, user_minimal_display_schema

ma = Marshmallow(app)


class SectionSchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("id", "name", "date_time_created", "description", "image_url", "created_by_id")


section_schema = SectionSchema()
sections_schema = SectionSchema(many=True)


class SectionMinimalDisplaySchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("name", "id")


section_minimal_display_schema = SectionMinimalDisplaySchema()
sections_minimal_display_schema = SectionMinimalDisplaySchema(many=True)


class SectionCreateSchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("name", "description", "image_url", "created_by_id")

    @post_load
    def make_section(self, data, **kwargs):
        return Section(**data)


section_create_schema = SectionCreateSchema()


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


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)


class AuthorMinimalSchema(ma.Schema):
    class Meta:
        model = Section
        fields = ("id", "name",)


author_minimal_schema = AuthorSchema()
authors_minimal_schema = AuthorSchema(many=True)


class EBookSchema(ma.Schema):
    class Meta:
        model = EBook
        fields = ("title", "description", "cover_image", "content", "publication_year", "created_by", "sections",
                  "authors")

    authors = fields.Nested(authors_minimal_schema)
    sections = fields.Nested(sections_minimal_display_schema)
    created_by = fields.Nested(user_display_schema)


ebook_schema = EBookSchema()
ebooks_schema = EBookSchema(many=True)


class EBookCreateSchema(ma.Schema):
    class Meta:
        model = EBook
        fields = ("title", "description", "filename", "cover_image", "content", "publication_year", "created_by_id")

    @post_load
    def make_post(self, data, **kwargs):
        return EBook(**data)


ebook_create_schema = EBookCreateSchema()


class EBookMinimalDisplaySchema(ma.Schema):
    class Meta:
        model = EBook
        fields = ("title", "description", "cover_image", "content", "publication_year", "created_by", "sections",
                  "authors")

    authors = fields.Nested(authors_minimal_schema)
    sections = fields.Nested(sections_minimal_display_schema)
    created_by = fields.Nested(user_minimal_display_schema)


ebook_minimal_display_schema = EBookMinimalDisplaySchema()
ebooks_minimal_display_schema = EBookMinimalDisplaySchema(many=True)
