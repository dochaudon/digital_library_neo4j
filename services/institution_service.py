from models.institution_model import (
    create_institution,
    get_all_institutions,
    get_institution_by_id,
    update_institution,
    delete_institution
)


def create_institution_service(data):
    if not data.get("name"):
        raise ValueError("Name is required")

    if data.get("type") not in ["Publisher", "University"]:
        raise ValueError("Type must be Publisher or University")

    return create_institution(data)


def get_institutions_service():
    return get_all_institutions()


def get_institution_detail_service(id):
    return get_institution_by_id(id)


def update_institution_service(id, data):
    update_institution(id, data)


def delete_institution_service(id):
    delete_institution(id)