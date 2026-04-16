from models.keyword_model import (
    create_keyword,
    get_all_keywords,
    get_keyword_by_id,
    update_keyword,
    delete_keyword
)


def create_keyword_service(data):
    if not data.get("name"):
        raise ValueError("Name is required")
    return create_keyword(data)


def get_keywords_service():
    return get_all_keywords()


def get_keyword_detail_service(id):
    return get_keyword_by_id(id)


def update_keyword_service(id, data):
    if not data.get("name"):
        raise ValueError("Name is required")
    update_keyword(id, data)


def delete_keyword_service(id):
    delete_keyword(id)