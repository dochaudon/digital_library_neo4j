from flask import Blueprint, request, jsonify, render_template

from services.author_service import (
    create_author_service,
    get_authors_service,
    get_author_detail_service,
    update_author_service,
    delete_author_service
)

author_bp = Blueprint("author_admin", __name__)


# ================= HTML =================
@author_bp.route("/admin/authors/page")
def author_page():
    return render_template("admin/pages/author/index.html")


@author_bp.route("/admin/authors/create")
def create_page():
    return render_template("admin/pages/author/form.html")


@author_bp.route("/admin/authors/edit/<id>")
def edit_page(id):
    return render_template("admin/pages/author/form.html")


# ================= API =================

@author_bp.route("/admin/authors", methods=["GET"])
def list_authors():
    authors = get_authors_service()
    return jsonify(authors)


@author_bp.route("/admin/authors/<id>", methods=["GET"])
def detail(id):
    return jsonify(get_author_detail_service(id))


@author_bp.route("/admin/authors", methods=["POST"])
def create():
    data = request.get_json()
    author_id = create_author_service(data)
    return jsonify({"message": "Created", "id": author_id})


@author_bp.route("/admin/authors/<id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    update_author_service(id, data)
    return jsonify({"message": "Updated"})


@author_bp.route("/admin/authors/<id>", methods=["DELETE"])
def delete(id):
    delete_author_service(id)
    return jsonify({"message": "Deleted"})