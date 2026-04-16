from flask import Blueprint, request, jsonify, render_template

from services.language_service import (
    create_language_service,
    get_languages_service,
    get_language_detail_service,
    update_language_service,
    delete_language_service
)

language_bp = Blueprint("language_admin", __name__)


# ================= HTML =================
@language_bp.route("/admin/languages/page")
def language_page():
    return render_template("admin/pages/language/index.html")


@language_bp.route("/admin/languages/create")
def create_page():
    return render_template("admin/pages/language/form.html")


@language_bp.route("/admin/languages/edit/<id>")
def edit_page(id):
    return render_template("admin/pages/language/form.html")


# ================= API =================
@language_bp.route("/admin/languages", methods=["GET"])
def list_languages():
    return jsonify(get_languages_service())


@language_bp.route("/admin/languages/<id>", methods=["GET"])
def detail(id):
    return jsonify(get_language_detail_service(id))


@language_bp.route("/admin/languages", methods=["POST"])
def create():
    data = request.get_json()
    lang_id = create_language_service(data)
    return jsonify({"message": "Created", "id": lang_id})


@language_bp.route("/admin/languages/<id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    update_language_service(id, data)
    return jsonify({"message": "Updated"})


@language_bp.route("/admin/languages/<id>", methods=["DELETE"])
def delete(id):
    delete_language_service(id)
    return jsonify({"message": "Deleted"})