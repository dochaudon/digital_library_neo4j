from models.language_model import (
    create_language,
    get_all_languages,
    get_language_by_id,
    update_language,
    delete_language
)


def create_language_service(data):
    if not data.get("name"):
        raise ValueError("Name is required")
    return create_language(data)


def get_languages_service():
    return get_all_languages()


def get_language_detail_service(id):
    return get_language_by_id(id)


def update_language_service(id, data):
    if not data.get("name"):
        raise ValueError("Name is required")
    update_language(id, data)


def delete_language_service(id):
    delete_language(id)