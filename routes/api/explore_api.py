from flask import Blueprint, jsonify, request
from services.explore_service import (
    get_preview,
    get_entity_detail,
    get_graph_by_entity
)


# =========================
# BLUEPRINT
# =========================
explore_api = Blueprint(
    "explore_api",
    __name__,
    url_prefix="/api"
)


# =========================
# PREVIEW (POPUP)
# =========================
@explore_api.route("/preview/<entity_type>/<entity_id>")
def preview(entity_type, entity_id):
    """
    Dùng cho:
    - click node (popup nhỏ)
    """

    try:
        data = get_preview(entity_type, entity_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================
# ENTITY DETAIL (LEFT PANEL)
# =========================
@explore_api.route("/entity/<entity_type>/<entity_id>")
def entity(entity_type, entity_id):
    """
    Dùng cho:
    - panel bên trái (explore page)
    - có pagination
    """

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))

        data = get_entity_detail(entity_type, entity_id, page, limit)

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================
# GRAPH DATA (RIGHT PANEL)
# =========================
@explore_api.route("/graph/<entity_type>/<entity_id>")
def graph(entity_type, entity_id):
    """
    Dùng cho:
    - render graph
    - update graph khi click node
    """

    try:
        data = get_graph_by_entity(entity_type, entity_id)
        return jsonify(data)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# =========================
# HEALTH CHECK (OPTIONAL)
# =========================
@explore_api.route("/explore-health")
def explore_health():
    return jsonify({
        "status": "ok"
    })