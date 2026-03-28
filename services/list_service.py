from models.list_model import (
    get_books,
    count_books,
    get_articles,
    count_articles,
    get_thesis,
    count_thesis
)


def get_books_service(skip, limit):
    return get_books(skip, limit)


def count_books_service():
    return count_books()


def get_articles_service(skip, limit):
    return get_articles(skip, limit)


def count_articles_service():
    return count_articles()


def get_thesis_service(skip, limit):
    return get_thesis(skip, limit)


def count_thesis_service():
    return count_thesis()