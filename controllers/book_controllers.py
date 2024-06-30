from flask import request, Blueprint
from flask_caching import Cache
from flask_marshmallow import Marshmallow

from app import app
from controllers.jwt_util import validate_token
from models.models import db, EBook, Section, Author
from serializers.book_serializers import section_create_schema, section_schema, author_create_schema, author_schema, \
    ebook_create_schema, ebook_schema, ebook_minimal_display_schema

cache = Cache(app)
ma = Marshmallow(app)

book_controller = Blueprint('book_controller', __name__)


@book_controller.route('/api/sections', methods=['POST'])
@validate_token
def create_section(user_from_token):
    try:
        data = request.json
        data["created_by_id"] = user_from_token.id
        section_object = section_create_schema.load(data)
        db.session.add(section_object)
        db.session.commit()
        return {"section": section_schema.dump(section_object)}, 201

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/authors', methods=['POST'])
@validate_token
def create_author(user_from_token):
    try:
        data = request.json
        data["created_by_id"] = user_from_token.id
        author_object = author_create_schema.load(data)
        print("author_object", author_object)
        db.session.add(author_object)
        db.session.commit()
        print(author_object)
        return {"message": author_schema.dump(data)}, 201

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/books', methods=['POST'])
@validate_token
def create_book(user_from_token):
    try:
        data = request.json
        data["created_by_id"] = user_from_token.id
        sections_from_request = data["sections"]
        authors_from_request = data["authors"]
        del (data["sections"])
        del (data["authors"])
        book_object = ebook_create_schema.load(data)
        sections_list = Section.query.filter(Section.id.in_(sections_from_request)).all()
        authors_list = Author.query.filter(Author.id.in_(authors_from_request)).all()
        for section in sections_list:
            book_object.sections.append(section)
        for author in authors_list:
            book_object.authors.append(author)
        db.session.add(book_object)
        db.session.commit()
        return {"ebook": ebook_minimal_display_schema.dump(book_object)}, 201

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/books/<int:id>', methods=['GET'])
@validate_token
def get_book_by_id(user_from_token, id):
    try:
        book = EBook.query.get(id)
        if not book:
            return {"message": "Book not found"}, 404

        return {"ebook": ebook_schema.dump(book)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500
