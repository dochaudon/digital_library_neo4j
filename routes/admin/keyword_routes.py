from flask import Blueprint, request, jsonify, render_template

from services.keyword_service import (
    create_keyword_service,
    get_keywords_service,
    get_keyword_detail_service,
    update_keyword_service,
    delete_keyword_service
)

keyword_bp = Blueprint("keyword_admin", __name__)


# ================= HTML =================
@keyword_bp.route("/admin/keywords/page")
def keyword_page():
    return render_template("admin/pages/keyword/index.html")


@keyword_bp.route("/admin/keywords/create")
def create_page():
    return render_template("admin/pages/keyword/form.html")


@keyword_bp.route("/admin/keywords/edit/<id>")
def edit_page(id):
    return render_template("admin/pages/keyword/form.html")


# ================= API =================
@keyword_bp.route("/admin/keywords", methods=["GET"])
def list_keywords():
    return jsonify(get_keywords_service())


@keyword_bp.route("/admin/keywords/<id>", methods=["GET"])
def detail(id):
    return jsonify(get_keyword_detail_service(id))


@keyword_bp.route("/admin/keywords", methods=["POST"])
def create():
    data = request.get_json()
    keyword_id = create_keyword_service(data)
    return jsonify({"message": "Created", "id": keyword_id})


@keyword_bp.route("/admin/keywords/<id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    update_keyword_service(id, data)
    return jsonify({"message": "Updated"})


@keyword_bp.route("/admin/keywords/<id>", methods=["DELETE"])
def delete(id):
    delete_keyword_service(id)
    return jsonify({"message": "Deleted"})