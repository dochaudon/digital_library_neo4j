from flask import Blueprint, request, jsonify, render_template

from services.qa_service import get_qa_response


qa = Blueprint("qa", __name__, url_prefix="/qa")


# =========================
# PAGE
# =========================
@qa.route("/")
def qa_page():
    return render_template("library/pages/qa/index.html")


# =========================
# API - ASK QUESTION
# =========================
@qa.route("/api", methods=["POST"])
def qa_api():
    data = request.get_json() or {}

    question = (data.get("question") or "").strip()

    result = get_qa_response(question)

    return jsonify(result)