from models.subject_model import (
    create_subject,
    get_all_subjects,
    get_subject_by_id,
    update_subject,
    delete_subject
)


def create_subject_service(data):
    if not data.get("name"):
        raise ValueError("Name is required")
    return create_subject(data)


def get_subjects_service():
    return get_all_subjects()


def get_subject_detail_service(id):
    return get_subject_by_id(id)


def update_subject_service(id, data):
    if not data.get("name"):
        raise ValueError("Name is required")
    update_subject(id, data)


def delete_subject_service(id):
    delete_subject(id)