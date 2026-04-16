from flask import Blueprint, request, jsonify, render_template

from services.subject_service import (
    create_subject_service,
    get_subjects_service,
    get_subject_detail_service,
    update_subject_service,
    delete_subject_service
)

subject_bp = Blueprint("subject_admin", __name__)


# ================= HTML =================
@subject_bp.route("/admin/subjects/page")
def subject_page():
    return render_template("admin/pages/subject/index.html")


@subject_bp.route("/admin/subjects/create")
def create_page():
    return render_template("admin/pages/subject/form.html")


@subject_bp.route("/admin/subjects/edit/<id>")
def edit_page(id):
    return render_template("admin/pages/subject/form.html")


# ================= API =================
@subject_bp.route("/admin/subjects", methods=["GET"])
def list_subjects():
    return jsonify(get_subjects_service())


@subject_bp.route("/admin/subjects/<id>", methods=["GET"])
def detail(id):
    return jsonify(get_subject_detail_service(id))


@subject_bp.route("/admin/subjects", methods=["POST"])
def create():
    data = request.get_json()
    subject_id = create_subject_service(data)
    return jsonify({"message": "Created", "id": subject_id})


@subject_bp.route("/admin/subjects/<id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    update_subject_service(id, data)
    return jsonify({"message": "Updated"})


@subject_bp.route("/admin/subjects/<id>", methods=["DELETE"])
def delete(id):
    delete_subject_service(id)
    return jsonify({"message": "Deleted"})