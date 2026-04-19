from flask import Blueprint, render_template, request


# =========================
# BLUEPRINT
# =========================
explore_bp = Blueprint(
    "explore",
    __name__,
    url_prefix=""
)


# =========================
# EXPLORE PAGE
# =========================
@explore_bp.route("/explore/<entity_type>/<entity_id>")
def explore_page(entity_type, entity_id):
    """
    Trang explore chính:
    - chia 2 cột (left + graph)
    - dữ liệu load bằng JS (API)
    """

    # validate entity type (tránh lỗi linh tinh)
    valid_types = ["author", "subject", "document"]

    if entity_type not in valid_types:
        entity_type = "document"

    return render_template(
        "library/pages/explore/explore.html",
        entity_type=entity_type,
        entity_id=entity_id
    )


# =========================
# OPTIONAL: REDIRECT HELPER
# =========================
@explore_bp.route("/explore/document/<doc_id>")
def explore_document_redirect(doc_id):
    """
    redirect nhanh nếu cần dùng riêng document
    """
    return render_template(
        "library/pages/explore/explore.html",
        entity_type="document",
        entity_id=doc_id
    )


# =========================
# DEBUG (OPTIONAL)
# =========================
@explore_bp.route("/explore-test")
def explore_test():
    """
    route test nhanh UI
    """
    return render_template(
        "library/pages/explore/explore.html",
        entity_type="author",
        entity_id="test"
    )