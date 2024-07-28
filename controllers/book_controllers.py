import os
import time
import uuid

from flask import request, Blueprint, jsonify
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from werkzeug.utils import secure_filename

from app import app
from controllers.jwt_util import validate_token, check_role
from models.models import db, EBook, Section, Author
from serializers.book_serializers import section_create_schema, section_schema, author_create_schema, author_schema, \
    ebook_create_schema, ebook_schema, ebook_minimal_display_schema, sections_schema, authors_schema, ebooks_schema

cache = Cache(app)
ma = Marshmallow(app)

book_controller = Blueprint('book_controller', __name__)

ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    timestamp = int(time.time())
    extension = filename.rsplit('.', 1)[1].lower()
    return f"{filename.rsplit('.', 1)[0]}_{timestamp}.{extension}"


@book_controller.route('/api/upload-pdf', methods=['POST'])
@validate_token
@check_role
def upload_pdf(user_from_token):
    print(request.files)
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(app.config['PROTECTED_UPLOADS_DIR'], unique_filename)
        file.save(file_path)
        return jsonify({'message': 'File successfully uploaded', 'filename': unique_filename}), 201
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@book_controller.route('/api/upload-cover-image', methods=['POST'])
@validate_token
@check_role
def upload_cover_image(user_from_token):
    print(request.files)
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    extension = file.filename.rsplit('.', 1)[1].lower()
    if file and extension in ["jpeg", "jpg", "png", "gif", "svg", "bmp"]:
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(app.config['UPLOADS_DIR'], unique_filename)
        file.save(file_path)
        return jsonify({'message': 'File successfully uploaded', 'filename': unique_filename}), 201
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@book_controller.route('/api/sections', methods=['POST'])
@validate_token
def create_section(user_from_token):
    try:
        data = request.json
        print(data)
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
        print(data)
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


@book_controller.route('/api/sections', methods=['GET'])
@validate_token
@check_role
def get_all_sections(user_from_token):
    try:
        sections = Section.query.all()
        return {"sections": sections_schema.dump(sections)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/sections/<int:id>', methods=['GET'])
@validate_token
def get_section_by_id(user_from_token, id):
    try:
        section = Section.query.get(id)
        if not section:
            return {"message": "Section not found"}, 404

        return {"section": section_schema.dump(section)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/sections/<int:id>', methods=['PUT'])
@validate_token
def update_section(user_from_token, id):
    try:
        section = Section.query.get(id)
        if not section:
            return {"message": "Section not found"}, 404

        data = request.json
        section.name = data.get("name", section.name)
        section.description = data.get("description", section.description)
        section.image_url = data.get("image_url", section.image_url)
        db.session.commit()
        return {"section": section_schema.dump(section)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/sections/<int:id>', methods=['DELETE'])
@validate_token
def delete_section(user_from_token, id):
    try:
        section = Section.query.get(id)
        if not section:
            return {"message": "Section not found"}, 404

        db.session.delete(section)
        db.session.commit()
        return {"message": "Section deleted"}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/authors', methods=['GET'])
@validate_token
@check_role
def get_all_authors(user_from_token):
    try:
        authors = Author.query.all()
        return {"authors": authors_schema.dump(authors)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/authors/<int:id>', methods=['GET'])
@validate_token
def get_author_by_id(user_from_token, id):
    try:
        author = Author.query.get(id)
        if not author:
            return {"message": "Author not found"}, 404

        return {"author": author_schema.dump(author)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/authors/<int:id>', methods=['PUT'])
@validate_token
def update_author(user_from_token, id):
    try:
        author = Author.query.get(id)
        if not author:
            return {"message": "Author not found"}, 404

        data = request.json
        author.name = data.get("name", author.name)
        db.session.commit()
        return {"author": author_schema.dump(author)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/authors/<int:id>', methods=['DELETE'])
@validate_token
def delete_author(user_from_token, id):
    try:
        author = Author.query.get(id)
        if not author:
            return {"message": "Author not found"}, 404

        db.session.delete(author)
        db.session.commit()
        return {"message": "Author deleted"}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/books', methods=['GET'])
@validate_token
def get_all_books(user_from_token):
    try:
        books = EBook.query.all()
        return {"ebooks": ebooks_schema.dump(books)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/books/<int:id>', methods=['PUT'])
@validate_token
def update_book(user_from_token, id):
    try:
        book = EBook.query.get(id)
        if not book:
            return {"message": "Book not found"}, 404

        data = request.json
        book.title = data.get("title", book.title)
        book.description = data.get("description", book.description)
        book.cover_image = data.get("cover_image", book.cover_image)
        book.content = data.get("content", book.content)
        book.publication_year = data.get("publication_year", book.publication_year)
        db.session.commit()
        return {"ebook": ebook_schema.dump(book)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/books/<int:id>', methods=['DELETE'])
@validate_token
def delete_book(user_from_token, id):
    try:
        book = EBook.query.get(id)
        if not book:
            return {"message": "Book not found"}, 404

        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted"}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500
