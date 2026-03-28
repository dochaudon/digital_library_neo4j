from models.book_model import get_book_by_id

def get_book_detail(id):
    return get_book_by_id(id)

import uuid
from models.book_model import (
    create_book,
    get_all_books,
    get_book_by_id,
    update_book,
    delete_book
)


def create_book_service(data):
    data["id"] = str(uuid.uuid4())
    return create_book(data)


def get_books_service():
    return get_all_books()


def get_book_detail_service(id):
    return get_book_by_id(id)


def update_book_service(id, data):
    return update_book(id, data)


def delete_book_service(id):
    return delete_book(id)