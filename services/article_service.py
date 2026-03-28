import uuid
from models.article_model import (
    create_article,
    get_all_articles,
    get_article_by_id,
    update_article,
    delete_article,
    count_articles
)

def get_article_detail(id):
    return get_article_by_id(id)

# =========================
# CREATE
# =========================
def create_article_service(data):
    data["id"] = str(uuid.uuid4())
    return create_article(data)


# =========================
# LIST + PAGINATION
# =========================
def get_articles_service(page=1, limit=5):
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
def get_article_detail_service(id):
    return get_article_by_id(id)


# =========================
# UPDATE
# =========================
def update_article_service(id, data):
    return update_article(id, data)


# =========================
# DELETE
# =========================
def delete_article_service(id):
    return delete_article(id)