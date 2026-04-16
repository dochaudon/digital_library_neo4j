from flask import Blueprint, request, jsonify, render_template

from services.journal_service import (
    create_journal_service,
    get_journals_service,
    get_journal_detail_service,
    update_journal_service,
    delete_journal_service
)

journal_bp = Blueprint("journal_admin", __name__)


# ================= HTML =================
@journal_bp.route("/admin/journals/page")
def journal_page():
    return render_template("admin/pages/journal/index.html")


@journal_bp.route("/admin/journals/create")
def create_page():
    return render_template("admin/pages/journal/form.html")


@journal_bp.route("/admin/journals/edit/<id>")
def edit_page(id):
    return render_template("admin/pages/journal/form.html")


# ================= API =================
@journal_bp.route("/admin/journals", methods=["GET"])
def list_journals():
    return jsonify(get_journals_service())


@journal_bp.route("/admin/journals/<id>", methods=["GET"])
def detail(id):
    return jsonify(get_journal_detail_service(id))


@journal_bp.route("/admin/journals", methods=["POST"])
def create():
    data = request.get_json()
    journal_id = create_journal_service(data)
    return jsonify({"message": "Created", "id": journal_id})


@journal_bp.route("/admin/journals/<id>", methods=["PUT"])
def update(id):
    data = request.get_json()
    update_journal_service(id, data)
    return jsonify({"message": "Updated"})


@journal_bp.route("/admin/journals/<id>", methods=["DELETE"])
def delete(id):
    delete_journal_service(id)
    return jsonify({"message": "Deleted"})