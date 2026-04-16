from flask import Blueprint, request, jsonify, render_template, redirect

from services.document_service import (
    create_document,
    update_document,
    delete_document,
    get_documents_service,
    get_document_detail_service,
    count_documents_service
)

document_bp = Blueprint("document_admin", __name__)


# =========================
# LIST PAGE (JINJA PAGINATION)
# =========================
@document_bp.route("/admin/documents/page")
def document_page():
    page = int(request.args.get("page", 1))
    limit = 10

    docs = get_documents_service(page, limit)
    total = count_documents_service()

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "admin/pages/document/index.html",
        documents=docs,
        page=page,
        total_pages=total_pages
    )


# =========================
# CREATE PAGE
# =========================
@document_bp.route("/admin/documents/create")
def create_page():
    return render_template("admin/pages/document/form.html")


# =========================
# EDIT PAGE
# =========================
@document_bp.route("/admin/documents/edit/<id>")
def edit_page(id):
    doc = get_document_detail_service(id)

    return render_template(
        "admin/pages/document/form.html",
        document=doc
    )


# =========================
# CREATE
# =========================
@document_bp.route("/admin/documents", methods=["POST"])
def create():
    data = request.form.to_dict()

    try:
        create_document(data)
        return redirect("/admin/documents/page")

    except Exception as e:
        print("CREATE ERROR:", e)
        return "Create failed", 500


# =========================
# UPDATE
# =========================
@document_bp.route("/admin/documents/update/<id>", methods=["POST"])
def update(id):
    data = request.form.to_dict()

    try:
        update_document(id, data)
        return redirect("/admin/documents/page")

    except Exception as e:
        print("UPDATE ERROR:", e)
        return "Update failed", 500


# =========================
# DELETE
# =========================
@document_bp.route("/admin/documents/delete/<id>")
def delete(id):
    try:
        delete_document(id)
        return redirect("/admin/documents/page")

    except Exception as e:
        print("DELETE ERROR:", e)
        return "Delete failed", 500
    
    