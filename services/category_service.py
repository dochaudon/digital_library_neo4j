from models.category_model import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category
)


def create_category_service(data):
    if not data.get("name"):
        raise ValueError("Name is required")
    return create_category(data)


def get_categories_service():
    return get_all_categories()


def get_category_detail_service(id):
    return get_category_by_id(id)


def update_category_service(id, data):
    if not data.get("name"):
        raise ValueError("Name is required")
    update_category(id, data)


def delete_category_service(id):
    delete_category(id)