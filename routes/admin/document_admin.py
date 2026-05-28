import os
import json
from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from database.neo4j_connection import neo4j_conn
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


import uuid

def save_upload(file, folder, allowed_set):
    if not file or file.filename == "":
        return None
    if not allowed(file.filename, allowed_set):
        return None
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    file.save(path)
    return "/" + path.replace("\\", "/")


def get_next_doc_id():
    """Tạo ID dạng D1, D2, D3 tự động."""
    result = neo4j_conn.query("""
        MATCH (d) 
        WHERE (d:Document)
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
        "documents": neo4j_conn.query(
            "MATCH (d) WHERE d:Document RETURN d.id AS id, d.title AS title ORDER BY d.title"
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

    documents   = get_documents_service(page, limit, q=q, include_hidden=True)
    total       = count_documents_service(q=q, include_hidden=True)
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
    page = request.args.get("page", 1)
    return render_template("admin/pages/document/edit.html",
                           document=document, metadata=metadata, page=page)


def safe_json_loads(val, default=None):
    if default is None:
        default = []
    if not val or val.strip() == "":
        return default
    try:
        return json.loads(val)
    except Exception:
        return default

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

    # Parse JSON arrays từ form an toàn
    data["authors_json"]      = safe_json_loads(data.get("authors_json"))
    data["institutions_json"] = safe_json_loads(data.get("institutions_json"))
    data["subjects"]          = safe_json_loads(data.get("subjects"))
    data["keywords"]          = safe_json_loads(data.get("keywords"))
    data["categories"]        = safe_json_loads(data.get("categories"))
    data["languages"]         = safe_json_loads(data.get("languages"))
    data["related_docs"]      = safe_json_loads(data.get("related_docs"))

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
    page = request.args.get("page", 1)

    image_url = save_upload(request.files.get("image_file"), UPLOAD_IMAGE_DIR, ALLOWED_IMAGES)
    file_url  = save_upload(request.files.get("doc_file"),   UPLOAD_FILE_DIR,  ALLOWED_FILES)

    if image_url:
        data["image_url"] = image_url
    if file_url:
        data["file_url"] = file_url

    data["authors_json"]      = safe_json_loads(data.get("authors_json"))
    data["institutions_json"] = safe_json_loads(data.get("institutions_json"))
    data["subjects"]          = safe_json_loads(data.get("subjects"))
    data["keywords"]          = safe_json_loads(data.get("keywords"))
    data["categories"]        = safe_json_loads(data.get("categories"))
    data["languages"]         = safe_json_loads(data.get("languages"))
    data["related_docs"]      = safe_json_loads(data.get("related_docs"))

    try:
        update_document_service(id, data)
        return redirect(url_for("document_admin.list_page", page=page))
    except Exception as e:
        print("UPDATE ERROR:", e)
        return "Update failed", 500



# =========================
# DELETE
# =========================
@document_admin.route("/delete/<id>")
def delete(id):
    page = request.args.get("page", 1)
    try:
        delete_document_service(id)
        return redirect(url_for("document_admin.list_page", page=page))
    except Exception as e:
        print("DELETE ERROR:", e)
        return "Delete failed", 500


# =========================
# TOGGLE STATUS (AJAX)
# =========================
@document_admin.route("/toggle-status/<id>", methods=["POST"])
def toggle_status(id):
    try:
        document = get_document_detail_service(id)
        if not document:
            return jsonify({"success": False, "error": "Document not found"}), 404
        
        current_status = document.get("status") or "active"
        new_status = "hidden" if current_status == "active" else "active"
        
        query = """
        MATCH (d {id: $id})
        SET d.status = $status
        RETURN d
        """
        neo4j_conn.query(query, {"id": id, "status": new_status})
        
        from services.vector_search_service import reset_faiss_index
        reset_faiss_index()
        
        return jsonify({"success": True, "new_status": new_status})
    except Exception as e:
        print("TOGGLE STATUS ERROR:", e)
        return jsonify({"success": False, "error": str(e)}), 500


# =========================
# VIEW
# =========================
@document_admin.route("/view/<id>")
def view_page(id):
    document = get_document_detail_service(id)
    if not document:
        return "Không tìm thấy tài liệu", 404

    page = request.args.get("page", 1)
    from services.graph_service import get_graph_data
    graph_data = get_graph_data(id, include_hidden=True)

    return render_template(
        "admin/pages/document/detail.html",
        document=document,
        graph_data=graph_data,
        page=page
    )
