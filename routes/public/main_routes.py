from flask import Blueprint, render_template, request, jsonify

from services.document_service import (
    get_documents_service,
    get_document_detail_service,
    count_documents_service,
    get_related_documents_by_author_service  # 🔥 RE-ADD
)

from services.search_service import search_documents, get_latest_documents
from services.graph_service import get_graph_data
from services.qa_service import get_qa_response
from services.metadata_service import get_subjects_service


main = Blueprint("main", __name__)


# =========================
# HOME
# =========================
@main.route("/")
def home():
    documents = get_latest_documents(10)
    subjects = get_subjects_service()

    return render_template(
        "library/pages/index.html",
        documents=documents,
        subjects=subjects
    )


# =========================
# SEARCH
# =========================
@main.route("/search")
def search():
    # Hàm làm sạch tham số (bóc tách các dấu ngoặc vuông lồng nhau)
    def clean_param(val):
        if not val: return ""
        s = str(val).strip()
        while (s.startswith('[') and s.endswith(']')) or (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
            if s.startswith('[') and s.endswith(']'): s = s[1:-1].strip()
            elif s.startswith("'") and s.endswith("'"): s = s[1:-1].strip()
            elif s.startswith('"') and s.endswith('"'): s = s[1:-1].strip()
            else: break
        return s

    query_raw = request.args.get("query") or ""
    query = clean_param(query_raw)
    
    print(f"DEBUG - request.args: {dict(request.args)}")
    search_type = clean_param(request.args.get("search_type", "hybrid"))
    print(f"DEBUG - search_type after clean: {search_type}")
    if search_type not in ["keyword", "semantic", "hybrid"]:
        search_type = "hybrid"

    page_raw = request.args.get("page", "1")
    page = int(clean_param(page_raw) or 1)
    
    sort = clean_param(request.args.get("sort", ""))

    limit = 5
    skip = (page - 1) * limit

    doc_types = request.args.getlist("doc_type")
    cleaned_doc_types = [clean_param(t) for t in doc_types if clean_param(t)]

    filters = {
        "doc_type": cleaned_doc_types or None,
        "author": clean_param(request.args.get("author")) or None,
        "subject": clean_param(request.args.get("subject")) or None,
        "publisher": clean_param(request.args.get("publisher")) or None,
        "university": clean_param(request.args.get("university")) or None,
        "year": None,
    }

    year_raw = (request.args.get("year") or "").strip()
    if year_raw.isdigit():
        filters["year"] = int(year_raw)

    # Tạo bản sao của filters để search_documents có thể thêm các filter từ query (parse_query)
    # mà không làm ảnh hưởng đến bộ lọc hiển thị trên giao diện (checkboxes)
    search_filters = filters.copy() if filters else {}
    results_all = search_documents(query=query, filters=search_filters, limit=100, search_type=search_type)

    # SORT
    if sort == "year_asc":
        results_all.sort(key=lambda x: x.get("year") or 0)
    elif sort == "year_desc":
        results_all.sort(key=lambda x: x.get("year") or 0, reverse=True)
    elif sort == "az":
        results_all.sort(key=lambda x: (x.get("title") or "").lower())
    elif sort == "za":
        results_all.sort(key=lambda x: (x.get("title") or "").lower(), reverse=True)

    total = len(results_all)
    total_pages = (total // limit) + (1 if total % limit else 0)

    results = results_all[skip: skip + limit]

    return render_template(
        "library/pages/results.html",
        query=query,
        filters=filters,
        results=results,
        page=page,
        total_pages=total_pages,
        sort=sort,
        search_type=search_type
    )


# =========================
# DOCUMENT DETAIL (UNIFIED)
# =========================
@main.route("/document/<id>")
def document_detail(id):
    document = get_document_detail_service(id)

    if not document:
        return "Không tìm thấy tài liệu", 404

    graph_data = get_graph_data(id)
    
    # 🔥 RE-ADD
    related_by_author = get_related_documents_by_author_service(id)

    return render_template(
        "library/pages/document/detail.html",
        document=document,
        graph_data=graph_data,
        related_by_author=related_by_author
    )


# =========================
# DOCUMENT LIST
# =========================
@main.route("/documents")
def documents_page():
    page = int(request.args.get("page", 1))
    limit = 10

    doc_type = request.args.get("doc_type")

    documents = get_documents_service(
        page=page,
        limit=limit,
        doc_type=doc_type
    )

    total = count_documents_service(doc_type=doc_type)

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "library/pages/document/list.html",
        documents=documents,
        page=page,
        total_pages=total_pages,
        doc_type=doc_type
    )


# =========================
# QA PAGE
# =========================
@main.route("/qa")
def qa_page():
    return render_template("library/pages/qa/index.html")

# =========================
# GRAPH API
# =========================
@main.route("/api/graph/<id>")
def graph_api(id):
    return jsonify(get_graph_data(id))