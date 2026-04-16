from flask import Blueprint, request, jsonify, render_template

from services.institution_service import (
    create_institution_service,
    get_institutions_service,
    get_institution_detail_service,
    update_institution_service,
    delete_institution_service
)

institution_bp = Blueprint("institution_admin", __name__)


# ================= HTML =================
@institution_bp.route("/admin/institutions/page")
def institution_page():
    return render_template("admin/pages/institution/index.html")


@institution_bp.route("/admin/institutions/create")
def create_page():
    return render_template("admin/pages/institution/form.html")


@institution_bp.route("/admin/institutions/edit/<id>")
def edit_page(id):
    return render_template("admin/pages/institution/form.html")


# ================= API =================
@institution_bp.route("/admin/institutions", methods=["GET"])
def list_institutions():
    return jsonify(get_institutions_service())


@institution_bp.route("/admin/institutions/<id>", methods=["GET"])
def detail(id):
    return jsonify(get_institution_detail_service(id))


@institution_bp.route("/admin/institutions", methods=["POST"])
def create():
    data = request.get_json()
    inst_id = create_institution_service(data)
    return jsonify({"message": "Created", "id": inst_id})


@institution_bp.route("/admin/institutions/<id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    update_institution_service(id, data)
    return jsonify({"message": "Updated"})


@institution_bp.route("/admin/institutions/<id>", methods=["DELETE"])
def delete(id):
    delete_institution_service(id)
    return jsonify({"message": "Deleted"})