import os
import json
from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from database.neo4j_connection import neo4j_conn
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

UPLOAD_IMAGE_DIR = os.path.join("static", "uploads", "images")
UPLOAD_FILE_DIR  = os.path.join("static", "uploads", "files")
ALLOWED_IMAGES   = {"png", "jpg", "jpeg", "webp", "gif"}
ALLOWED_FILES    = {"pdf", "doc", "docx"}


def allowed(filename, allowed_set):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set


def save_upload(file, folder, allowed_set):
    if not file or file.filename == "":
        return None
    if not allowed(file.filename, allowed_set):
        return None
    filename = secure_filename(file.filename)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    file.save(path)
    return "/" + path.replace("\\", "/")


def get_next_doc_id():
    """Tạo ID dạng D1, D2, D3 tự động."""
    result = neo4j_conn.query("""
        MATCH (d) 
        WHERE (d:Book OR d:Article OR d:Thesis)
          AND d.id STARTS WITH 'D'
        RETURN d.id AS id
    """)
    max_num = 0
    for r in result:
        try:
            num = int(r["id"][1:])
            if num > max_num:
                max_num = num
        except (ValueError, TypeError, IndexError):
            pass
    return f"D{max_num + 1}"


def get_all_metadata():
    """Lấy tất cả entities cho select boxes."""
    def query_list(label, prop="name"):
        rows = neo4j_conn.query(f"MATCH (n:{label}) RETURN n.{prop} AS name ORDER BY n.{prop}")
        return [r["name"] for r in rows if r["name"]]

    return {
        "authors":    query_list("Author"),
        "subjects":   query_list("Subject"),
        "keywords":   query_list("Keyword"),
        "categories": query_list("Category"),
        "languages":  query_list("Language"),
        "journals":   query_list("Journal"),
        "publishers": neo4j_conn.query(
            "MATCH (p:Publisher) RETURN p.name AS name ORDER BY p.name"
        ),
        "universities": neo4j_conn.query(
            "MATCH (u:University) RETURN u.name AS name ORDER BY u.name"
        ),
    }


# =========================
# LIST PAGE
# =========================
@document_admin.route("/")
def list_page():
    page  = int(request.args.get("page", 1))
    q     = request.args.get("q", "")
    limit = 10

    documents   = get_documents_service(page, limit, q=q)
    total       = count_documents_service(q=q)
    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "admin/pages/document/index.html",
        documents=documents, page=page, total_pages=total_pages, q=q
    )


# =========================
# CREATE PAGE
# =========================
@document_admin.route("/create")
def create_page():
    next_id  = get_next_doc_id()
    metadata = get_all_metadata()
    return render_template("admin/pages/document/create.html",
                           next_id=next_id, metadata=metadata)


# =========================
# EDIT PAGE
# =========================
@document_admin.route("/edit/<id>")
def edit_page(id):
    document = get_document_detail_service(id)
    metadata = get_all_metadata()
    return render_template("admin/pages/document/edit.html",
                           document=document, metadata=metadata)


# =========================
# CREATE (POST)
# =========================
@document_admin.route("/create", methods=["POST"])
def create():
    data = request.form.to_dict()

    image_url = save_upload(request.files.get("image_file"), UPLOAD_IMAGE_DIR, ALLOWED_IMAGES)
    file_url  = save_upload(request.files.get("doc_file"),   UPLOAD_FILE_DIR,  ALLOWED_FILES)

    if image_url:
        data["image_url"] = image_url
    if file_url:
        data["file_url"] = file_url

    # Parse JSON arrays từ form
    data["authors_json"]      = json.loads(data.get("authors_json",      "[]"))
    data["institutions_json"] = json.loads(data.get("institutions_json", "[]"))
    data["subjects"]          = json.loads(data.get("subjects",          "[]"))
    data["keywords"]          = json.loads(data.get("keywords",          "[]"))
    data["categories"]        = json.loads(data.get("categories",        "[]"))
    data["languages"]         = json.loads(data.get("languages",         "[]"))

    try:
        create_document_service(data)
        return redirect(url_for("document_admin.list_page"))
    except Exception as e:
        print("CREATE ERROR:", e)
        return "Create failed", 500


# =========================
# UPDATE (POST)
# =========================
@document_admin.route("/update/<id>", methods=["POST"])
def update(id):
    data = request.form.to_dict()

    image_url = save_upload(request.files.get("image_file"), UPLOAD_IMAGE_DIR, ALLOWED_IMAGES)
    file_url  = save_upload(request.files.get("doc_file"),   UPLOAD_FILE_DIR,  ALLOWED_FILES)

    if image_url:
        data["image_url"] = image_url
    if file_url:
        data["file_url"] = file_url

    data["authors_json"]      = json.loads(data.get("authors_json",      "[]"))
    data["institutions_json"] = json.loads(data.get("institutions_json", "[]"))
    data["subjects"]          = json.loads(data.get("subjects",          "[]"))
    data["keywords"]          = json.loads(data.get("keywords",          "[]"))
    data["categories"]        = json.loads(data.get("categories",        "[]"))
    data["languages"]         = json.loads(data.get("languages",         "[]"))

    try:
        update_document_service(id, data)
        return redirect(url_for("document_admin.list_page"))
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
        return redirect(url_for("document_admin.list_page"))
    except Exception as e:
        print("DELETE ERROR:", e)
        return "Delete failed", 500


# =========================
# VIEW
# =========================
@document_admin.route("/view/<id>")
def view_page(id):
    document   = get_document_detail_service(id)
    graph_data = get_document_graph_service(id)
    return render_template("admin/pages/document/detail.html",
                           document=document, graph_data=graph_data)
