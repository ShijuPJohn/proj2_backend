from flask_marshmallow import Marshmallow
from marshmallow import post_load
from marshmallow_sqlalchemy import fields

from app import app
from models.models import Section, EBook, Author, Request, Issue, Purchase, Review
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
        model = Author
        fields = ("id", "name", "date_time_created")


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)


class AuthorMinimalSchema(ma.Schema):
    class Meta:
        model = Author
        fields = ("id", "name",)


author_minimal_schema = AuthorSchema()
authors_minimal_schema = AuthorSchema(many=True)


class EBookSchema(ma.Schema):
    class Meta:
        model = EBook
        fields = (
            "id", "price", "title", "description", "cover_image", "content", "publication_year", "created_by",
            "sections",
            "authors", "filename", "number_of_pages")

    authors = fields.Nested(authors_minimal_schema)
    sections = fields.Nested(sections_minimal_display_schema)
    created_by = fields.Nested(user_display_schema)


ebook_schema = EBookSchema()
ebooks_schema = EBookSchema(many=True)


class EBookCreateSchema(ma.Schema):
    class Meta:
        model = EBook
        fields = (
            "title", "price", "description", "filename", "cover_image", "content", "publication_year", "created_by_id",
            "number_of_pages")

    @post_load
    def make_ebook(self, data, **kwargs):
        return EBook(**data)


ebook_create_schema = EBookCreateSchema()


class EBookMinimalDisplaySchema(ma.Schema):
    class Meta:
        model = EBook
        fields = ("id", "title", "cover_image", "publication_year", "sections",
                  "authors", "filename", "price", "number_of_pages")

    authors = fields.Nested(authors_minimal_schema)
    sections = fields.Nested(sections_minimal_display_schema)


ebook_minimal_display_schema = EBookMinimalDisplaySchema()
ebooks_minimal_display_schema = EBookMinimalDisplaySchema(many=True)


class RequestDisplaySchema(ma.Schema):
    class Meta:
        model = Request
        fields = ("id", "user_id", "book_id")


request_display_schema = RequestDisplaySchema()
requests_display_schema = RequestDisplaySchema(many=True)


class RequestPopulatedDisplaySchema(ma.Schema):
    class Meta:
        model = Request
        fields = ("id", "user", "book")

    user = fields.Nested(user_minimal_display_schema)
    book = fields.Nested(ebook_minimal_display_schema)


request_populated_display_schema = RequestPopulatedDisplaySchema()
requests_populated_display_schema = RequestPopulatedDisplaySchema(many=True)


class IssueDisplaySchema(ma.Schema):
    class Meta:
        model = Issue
        fields = ("id", "user_id", "book_id", "created_time", "returned_time")


issue_display_schema = IssueDisplaySchema()
issues_display_schema = IssueDisplaySchema(many=True)


class IssuePopulatedDisplaySchema(ma.Schema):
    class Meta:
        model = Issue
        fields = ("id", "book", "user", "date_time_issued")

    book = fields.Nested(ebook_minimal_display_schema)
    user = fields.Nested(user_minimal_display_schema)


issue_populated_display_schema = IssuePopulatedDisplaySchema()
issues_populated_display_schema = IssuePopulatedDisplaySchema(many=True)


class PurchaseCreateSchema(ma.Schema):
    class Meta:
        model = Purchase
        fields = (
            "user_id", "book_id", "date_time", "card_number", "card_name", "card_expiry", "card_cvv")

    @post_load
    def make_purchase(self, data, **kwargs):
        return Purchase(**data)


purchase_create_schema = PurchaseCreateSchema()


class PurchasePopulatedSchema(ma.Schema):
    class Meta:
        model = Purchase
        fields = (
            "id", "user", "book", "date_time")

    book = fields.Nested(ebook_minimal_display_schema)
    user = fields.Nested(user_minimal_display_schema)


purchase_populated_schema = PurchasePopulatedSchema()
purchases_populated_schema = PurchasePopulatedSchema(many=True)


class PurchaseMinimalDisplaySchema(ma.Schema):
    class Meta:
        model = Purchase
        fields = (
            "id", "book_id", "user_id", "date_time")


purchase_minimal_display_schema = PurchaseMinimalDisplaySchema()
purchases_minimal_display_schema = PurchaseMinimalDisplaySchema(many=True)


class ReviewCreateSchema(ma.Schema):
    class Meta:
        model = Review
        fields = ("user_id", "book_id", "rating_score", "review_text", "date_time_created", "date_time_edited")

    @post_load
    def make_review(self, data, **kwargs):
        return Review(**data)


review_create_schema = ReviewCreateSchema()


class ReviewMinimalDisplaySchema(ma.Schema):
    class Meta:
        model = Review
        fields = ("id", "rating_score", "review_text", "date_time_created")


review_minimal_display_schema = ReviewMinimalDisplaySchema()
reviews_minimal_display_schema = ReviewMinimalDisplaySchema(many=True)


class ReviewPopulatedDisplaySchema(ma.Schema):
    class Meta:
        model = Review
        fields = ("id", "rating_score", "review_text", "date_time_created", "date_time_edited", "user", "book")

    user = fields.Nested(user_minimal_display_schema)
    book = fields.Nested(ebook_minimal_display_schema)


review_populated_display_schema = ReviewPopulatedDisplaySchema()
reviews_populated_display_schema = ReviewPopulatedDisplaySchema(many=True)
