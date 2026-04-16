from flask import Blueprint, request, jsonify, render_template

from services.category_service import (
    create_category_service,
    get_categories_service,
    get_category_detail_service,
    update_category_service,
    delete_category_service
)

category_bp = Blueprint("category_admin", __name__)


# ================= HTML =================
@category_bp.route("/admin/categories/page")
def category_page():
    return render_template("admin/pages/category/index.html")


@category_bp.route("/admin/categories/create")
def create_page():
    return render_template("admin/pages/category/form.html")


@category_bp.route("/admin/categories/edit/<id>")
def edit_page(id):
    return render_template("admin/pages/category/form.html")


# ================= API =================
@category_bp.route("/admin/categories", methods=["GET"])
def list_categories():
    return jsonify(get_categories_service())


@category_bp.route("/admin/categories/<id>", methods=["GET"])
def detail(id):
    return jsonify(get_category_detail_service(id))


@category_bp.route("/admin/categories", methods=["POST"])
def create():
    data = request.get_json()
    category_id = create_category_service(data)
    return jsonify({"message": "Created", "id": category_id})


@category_bp.route("/admin/categories/<id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    update_category_service(id, data)
    return jsonify({"message": "Updated"})


@category_bp.route("/admin/categories/<id>", methods=["DELETE"])
def delete(id):
    delete_category_service(id)
    return jsonify({"message": "Deleted"})