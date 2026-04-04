import uuid

from models.thesis_model import (
    create_thesis,
    get_all_thesis,
    get_thesis_detail,
    update_thesis,
    delete_thesis,
    count_thesis
)


# =========================
# CREATE
# =========================
def create_thesis_service(data):
    data["id"] = str(uuid.uuid4())
    return create_thesis(data)


# =========================
# LIST + PAGINATION
# =========================
def get_thesis_service(page=1, limit=20):
    skip = (page - 1) * limit
    return get_all_thesis(skip, limit)


# =========================
# COUNT
# =========================
def count_thesis_service():
    return count_thesis()


# =========================
# DETAIL
# =========================
def get_thesis_detail_service(thesis_id):
    return get_thesis_detail(thesis_id)


# =========================
# UPDATE
# =========================
def update_thesis_service(thesis_id, data):
    return update_thesis(thesis_id, data)


# =========================
# DELETE
# =========================
def delete_thesis_service(thesis_id):
    return delete_thesis(thesis_id)