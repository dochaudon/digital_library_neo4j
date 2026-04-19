from flask import Blueprint, render_template, request, jsonify

from services.document_service import (
    get_documents_service,
    get_document_detail_service,
    count_documents_service
)

from services.search_service import search_documents, get_latest_documents
from services.graph_service import get_graph_data
from services.qa_service import get_qa_response


main = Blueprint("main", __name__)


# =========================
# HOME
# =========================
@main.route("/")
def home():
    documents = get_latest_documents(10)

    return render_template(
        "library/pages/index.html",
        documents=documents
    )


# =========================
# SEARCH
# =========================
@main.route("/search")
def search():
    query = (request.args.get("query") or "").strip()
    page = int(request.args.get("page", 1))
    sort = request.args.get("sort", "")

    limit = 5
    skip = (page - 1) * limit

    filters = {
        "doc_type": request.args.get("doc_type") or None,
        "author": request.args.get("author") or None,
        "subject": request.args.get("subject") or None,
        "publisher": request.args.get("publisher") or None,
        "university": request.args.get("university") or None,
        "year": None,
    }

    year_raw = (request.args.get("year") or "").strip()
    if year_raw.isdigit():
        filters["year"] = int(year_raw)

    results_all = search_documents(query=query, filters=filters, limit=100)

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
        sort=sort
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

    return render_template(
        "library/pages/document/detail.html",
        document=document,
        graph_data=graph_data
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
        doc_type=doc_type   # 🔥 THÊM DÒNG NÀY
    )

    total = count_documents_service(doc_type=doc_type)

    total_pages = (total // limit) + (1 if total % limit else 0)

    return render_template(
        "library/pages/document/list.html",
        documents=documents,
        page=page,
        total_pages=total_pages,
        doc_type=doc_type   # 🔥 để highlight UI
    )


# =========================
# QA PAGE
# =========================
@main.route("/qa")
def qa_page():
    return render_template("library/pages/qa/index.html")


@main.route("/api/qa", methods=["POST"])
def qa_api():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()

    return jsonify(get_qa_response(question))


# =========================
# GRAPH API
# =========================
@main.route("/api/graph/<id>")
def graph_api(id):
    return jsonify(get_graph_data(id))