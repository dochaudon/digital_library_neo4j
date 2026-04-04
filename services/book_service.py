from models.book_model import (
    create_book,
    get_all_books,
    get_book_detail,
    update_book,
    delete_book,
    count_books
)

import uuid


# =========================
# CREATE
# =========================
def create_book_service(data):
    data["id"] = str(uuid.uuid4())
    return create_book(data)


# =========================
# GET LIST + PAGINATION
# =========================
def get_books_service(page=1, limit=20):
    skip = (page - 1) * limit
    return get_all_books(skip, limit)


# =========================
# COUNT
# =========================
def count_books_service():
    return count_books()


# =========================
# GET DETAIL
# =========================
def get_book_detail_service(book_id):
    return get_book_detail(book_id)


# =========================
# UPDATE
# =========================
def update_book_service(book_id, data):
    return update_book(book_id, data)


# =========================
# DELETE
# =========================
def delete_book_service(book_id):
    return delete_book(book_id)