import uuid

from models.article_model import (
    create_article,
    get_all_articles,
    get_article_detail,
    update_article,
    delete_article,
    count_articles
)


# =========================
# CREATE
# =========================
def create_article_service(data):
    data["id"] = str(uuid.uuid4())
    return create_article(data)


# =========================
# LIST + PAGINATION
# =========================
def get_articles_service(page=1, limit=20):
    skip = (page - 1) * limit
    return get_all_articles(skip, limit)


# =========================
# COUNT
# =========================
def count_articles_service():
    return count_articles()


# =========================
# DETAIL
# =========================
def get_article_detail_service(article_id):
    return get_article_detail(article_id)


# =========================
# UPDATE
# =========================
def update_article_service(article_id, data):
    return update_article(article_id, data)


# =========================
# DELETE
# =========================
def delete_article_service(article_id):
    return delete_article(article_id)