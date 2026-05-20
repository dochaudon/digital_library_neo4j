from flask import Blueprint, jsonify, request

from services.graph_service import get_graph_data, get_all_subjects_graph, relate_subjects_service

graph_api = Blueprint("graph_api", __name__, url_prefix="/api/graph")

# =========================
# SUBJECT GRAPH (ADMIN)
# =========================
@graph_api.route("/subject-group", methods=["GET"])
def subject_group_graph():
    try:
        data = get_all_subjects_graph()
        return jsonify({
            "success": True,
            "nodes": data.get("nodes", []),
            "edges": data.get("edges", [])
        })
    except Exception as e:
        print("SUBJECT GRAPH ERROR:", e)
        return jsonify({"success": False, "message": "Failed to load subject graph"}), 500

@graph_api.route("/subject-group/relate", methods=["POST"])
def relate_subjects_endpoint():
    try:
        data = request.json
        source_id = data.get("source_id")
        target_id = data.get("target_id")
        success = relate_subjects_service(source_id, target_id)
        return jsonify({"success": success})
    except Exception as e:
        print("SUBJECT RELATE ERROR:", e)
        return jsonify({"success": False, "message": str(e)}), 500

@graph_api.route("/subject-group/unrelate", methods=["POST"])
def unrelate_subjects_endpoint():
    try:
        from services.graph_service import unrelate_subjects_service
        data = request.json
        source_id = data.get("source_id")
        target_id = data.get("target_id")
        success = unrelate_subjects_service(source_id, target_id)
        return jsonify({"success": success})
    except Exception as e:
        print("SUBJECT UNRELATE ERROR:", e)
        return jsonify({"success": False, "message": str(e)}), 500


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