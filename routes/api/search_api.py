from flask import Blueprint, request, jsonify

from services.search_service import search_documents, suggest_documents


search_api = Blueprint("search_api", __name__, url_prefix="/api/search")


# =========================
# SEARCH API
# =========================
@search_api.route("/", methods=["GET"])
def search():

    query = (request.args.get("query") or "").strip()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    sort = request.args.get("sort", "")

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

    # 🔥 SEARCH
    results_all = search_documents(query=query, filters=filters, limit=100)

    # =========================
    # SORT
    # =========================
    if sort == "year_asc":
        results_all.sort(key=lambda x: x.get("year") or 0)
    elif sort == "year_desc":
        results_all.sort(key=lambda x: x.get("year") or 0, reverse=True)
    elif sort == "az":
        results_all.sort(key=lambda x: (x.get("title") or "").lower())
    elif sort == "za":
        results_all.sort(key=lambda x: (x.get("title") or "").lower(), reverse=True)

    # =========================
    # PAGINATION
    # =========================
    total = len(results_all)
    total_pages = (total // limit) + (1 if total % limit else 0)

    start = (page - 1) * limit
    end = start + limit

    results = results_all[start:end]

    return jsonify({
        "query": query,
        "filters": filters,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "results": results
    })
@search_api.route("/suggest")
def suggest():
    query = request.args.get("q", "")

    results = suggest_documents(query)

    return jsonify({
        "results": results   # 🔥 PHẢI CÓ KEY NÀY
    })