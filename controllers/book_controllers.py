import os
import time

from flask import request, Blueprint, jsonify, send_from_directory
from flask_caching import Cache
from flask_marshmallow import Marshmallow

from app import app
from controllers.jwt_util import validate_token, check_role
from models.models import db, EBook, Section, Author
from serializers.book_serializers import section_create_schema, section_schema, author_create_schema, author_schema, \
    ebook_create_schema, ebook_schema, ebook_minimal_display_schema, sections_schema, authors_schema, ebooks_schema, \
    requests_display_schema, issues_display_schema, author_minimal_schema, ebooks_minimal_display_schema

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
        data["created_by_id"] = user_from_token.id
        author_object = author_create_schema.load(data)
        db.session.add(author_object)
        db.session.commit()
        return {"author": author_minimal_schema.dump(author_object)}, 201

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


@book_controller.route('/api/books/<int:bid>', methods=['GET'])
@validate_token
def get_book_by_id(user_from_token, bid):
    requested = False
    issued = False
    try:
        book = EBook.query.get(bid)
        if not book:
            return {"message": "Book not found"}, 404
        if book.id in [r.book_id for r in user_from_token.requests if r.status == "open"]:
            requested = True
        if book.id in [i.book_id for i in user_from_token.issues if not i.returned]:
            issued = True
        return {"ebook": ebook_schema.dump(book), "requested": requested, "issued": issued}, 200

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
@check_role
def update_section(user_from_token, id):
    try:
        section = Section.query.get(id)
        if not section:
            return {"message": "Section not found"}, 404

        data = request.json
        section.name = data.get("name", section.name)
        section.description = data.get("description", section.description)
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
        db.session.add(author)
        db.session.commit()
        return {"author": author_schema.dump(author)}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/authors/<int:id>', methods=['DELETE'])
@validate_token
@check_role
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
        if user_from_token.role == "librarian":
            return jsonify({"ebooks": ebooks_minimal_display_schema.dump(books)}), 200
        issues = [issue for issue in user_from_token.issues if not issue.returned]
        return jsonify({"ebooks": ebooks_schema.dump(books),
                        "requests": requests_display_schema.dump(
                            [rq for rq in user_from_token.requests if rq.status == "open"]),
                        "issues": issues_display_schema.dump(issues)}), 200
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
@check_role
def delete_book(user_from_token, id):
    try:
        book = EBook.query.get(id)
        print(book)
        if not book:
            return {"message": "Book not found"}, 404

        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted"}, 200

    except Exception as e:
        print(e)
        return {"message": "error"}, 500


@book_controller.route('/api/book-file/<int:bid>', methods=['GET'])
@validate_token
def get_book(user_from_token, bid):
    book = EBook.query.get(bid)
    if not book:
        return jsonify({"message": "book not found"}), 404
    if (not user_from_token.role == "librarian") and book.id not in [issue.book_id for issue in user_from_token.issues
                                                                     if
                                                                     not issue.returned]:
        return jsonify({"message": "unauthorized"}), 401
    return send_from_directory(directory="protected_uploads", path=book.filename, as_attachment=True)
