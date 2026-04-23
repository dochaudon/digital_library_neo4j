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
    try:
        data = request.get_json() or {}

        question = (data.get("question") or "").strip()

        # 👉 validate input
        if not question:
            return jsonify({
                "answer": "Bạn chưa nhập câu hỏi. Hãy thử nhập nội dung bạn muốn tìm nhé.",
                "documents": []
            }), 200

        # 👉 gọi service
        result = get_qa_response(question)

        # 👉 đảm bảo luôn có format đúng
        return jsonify({
            "answer": result.get("answer", "Mình chưa có câu trả lời phù hợp."),
            "documents": result.get("documents", [])
        }), 200

    except Exception as e:
        print("QA ERROR:", e)

        return jsonify({
            "answer": "Có lỗi xảy ra khi xử lý câu hỏi. Bạn thử lại nhé.",
            "documents": []
        }), 500