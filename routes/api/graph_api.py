from flask import Blueprint, jsonify

from services.graph_service import get_graph_data


graph_api = Blueprint("graph_api", __name__, url_prefix="/api/graph")


# =========================
# GET GRAPH BY ENTITY ID
# =========================
@graph_api.route("/<id>", methods=["GET"])
def get_graph(id):

    try:
        data = get_graph_data(id)

        return jsonify({
            "success": True,
            "nodes": data.get("nodes", []),
            "edges": data.get("edges", [])
        })

    except Exception as e:
        print("GRAPH ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Failed to load graph"
        }), 500