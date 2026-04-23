from flask import Blueprint, request, render_template, redirect
from services.graph_service import get_document_graph_service
from services.document_service import (
    create_document_service,
    update_document_service,
    delete_document_service,
    get_documents_service,
    get_document_detail_service,
    count_documents_service
)

document_admin = Blueprint("document_admin", __name__, url_prefix="/admin/documents")


# =========================
# LIST PAGE
# =========================
@document_admin.route("/")
def list_page():
    page = int(request.args.get("page", 1))
    limit = 10

    documents = get_documents_service(page, limit)
    total = count_documents_service()

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "admin/pages/document/index.html",
        documents=documents,
        page=page,
        total_pages=total_pages
    )


# =========================
# CREATE PAGE
# =========================
@document_admin.route("/create")
def create_page():
    return render_template("admin/pages/document/form.html")


# =========================
# EDIT PAGE
# =========================
@document_admin.route("/edit/<id>")
def edit_page(id):
    document = get_document_detail_service(id)

    return render_template(
        "admin/pages/document/form.html",
        document=document
    )


# =========================
# CREATE
# =========================
@document_admin.route("/create", methods=["POST"])
def create():
    data = request.form.to_dict()

    try:
        create_document_service(data)
        return redirect("/admin/documents")

    except Exception as e:
        print("CREATE ERROR:", e)
        return "Create failed", 500


# =========================
# UPDATE
# =========================
@document_admin.route("/update/<id>", methods=["POST"])
def update(id):
    data = request.form.to_dict()

    try:
        update_document_service(id, data)
        return redirect("/admin/documents")

    except Exception as e:
        print("UPDATE ERROR:", e)
        return "Update failed", 500


# =========================
# DELETE
# =========================
@document_admin.route("/delete/<id>")
def delete(id):
    try:
        delete_document_service(id)
        return redirect("/admin/documents")

    except Exception as e:
        print("DELETE ERROR:", e)
        return "Delete failed", 500

@document_admin.route("/view/<id>")
def view_page(id):
    document = get_document_detail_service(id)
    graph_data = get_document_graph_service(id)

    return render_template(
        "admin/pages/document/detail.html",
        document=document,
        graph_data=graph_data
    )