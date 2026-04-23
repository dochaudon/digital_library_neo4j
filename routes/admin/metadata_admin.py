from flask import Blueprint, request, jsonify, render_template

from services.metadata_service import (
    create_author_service,
    get_authors_service,
    get_author_detail_service,
    update_author_service,
    delete_author_service,

    create_subject_service,
    get_subjects_service,
    get_subject_detail_service,
    update_subject_service,
    delete_subject_service,

    create_keyword_service,
    get_keywords_service,
    get_keyword_detail_service,
    update_keyword_service,
    delete_keyword_service,

    create_category_service,
    get_categories_service,
    get_category_detail_service,
    update_category_service,
    delete_category_service,

    create_institution_service,
    get_institutions_service,
    get_institution_detail_service,
    update_institution_service,
    delete_institution_service
)


metadata_admin = Blueprint("metadata_admin", __name__, url_prefix="/admin")


# =====================================================
# 🔥 DASHBOARD (THÊM VÀO ĐÂY)
# =====================================================
@metadata_admin.route("/dashboard")
def dashboard():
    return render_template("admin/pages/dashboard/index.html")


# =====================================================
# 🔥 GENERIC PAGE ROUTE
# =====================================================
@metadata_admin.route("/metadata/<entity>/page")
def list_page(entity):
    return render_template(f"admin/pages/{entity}/index.html")


@metadata_admin.route("/metadata/<entity>/create")
def create_page(entity):
    return render_template(f"admin/pages/{entity}/form.html")


@metadata_admin.route("/metadata/<entity>/edit/<id>")
def edit_page(entity, id):
    return render_template(f"admin/pages/{entity}/form.html")


# =====================================================
# 🔥 SERVICE MAP
# =====================================================
def get_service(entity):
    return {
        "author": {
            "get": get_authors_service,
            "get_one": get_author_detail_service,
            "create": create_author_service,
            "update": update_author_service,
            "delete": delete_author_service,
        },
        "subject": {
            "get": get_subjects_service,
            "get_one": get_subject_detail_service,
            "create": create_subject_service,
            "update": update_subject_service,
            "delete": delete_subject_service,
        },
        "keyword": {
            "get": get_keywords_service,
            "get_one": get_keyword_detail_service,
            "create": create_keyword_service,
            "update": update_keyword_service,
            "delete": delete_keyword_service,
        },
        "category": {
            "get": get_categories_service,
            "get_one": get_category_detail_service,
            "create": create_category_service,
            "update": update_category_service,
            "delete": delete_category_service,
        },
        "institution": {
            "get": get_institutions_service,
            "get_one": get_institution_detail_service,
            "create": create_institution_service,
            "update": update_institution_service,
            "delete": delete_institution_service,
        }
    }.get(entity)


# =====================================================
# LIST
# =====================================================
@metadata_admin.route("/metadata/<entity>", methods=["GET"])
def list_items(entity):
    service = get_service(entity)
    if not service:
        return jsonify({"error": "Invalid entity"}), 400
    return jsonify(service["get"]())


# =====================================================
# DETAIL
# =====================================================
@metadata_admin.route("/metadata/<entity>/<id>", methods=["GET"])
def detail(entity, id):
    service = get_service(entity)
    if not service:
        return jsonify({"error": "Invalid entity"}), 400
    return jsonify(service["get_one"](id))


# =====================================================
# CREATE
# =====================================================
@metadata_admin.route("/metadata/<entity>", methods=["POST"])
def create(entity):
    service = get_service(entity)
    if not service:
        return jsonify({"error": "Invalid entity"}), 400

    data = request.get_json()
    item_id = service["create"](data)
    return jsonify({"message": "Created", "id": item_id})


# =====================================================
# UPDATE
# =====================================================
@metadata_admin.route("/metadata/<entity>/<id>", methods=["PUT"])
def update(entity, id):
    service = get_service(entity)
    if not service:
        return jsonify({"error": "Invalid entity"}), 400

    data = request.get_json()
    service["update"](id, data)
    return jsonify({"message": "Updated"})


# =====================================================
# DELETE
# =====================================================
@metadata_admin.route("/metadata/<entity>/<id>", methods=["DELETE"])
def delete(entity, id):
    service = get_service(entity)
    if not service:
        return jsonify({"error": "Invalid entity"}), 400

    service["delete"](id)
    return jsonify({"message": "Deleted"})