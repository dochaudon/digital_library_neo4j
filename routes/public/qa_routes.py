from flask import Blueprint, request, jsonify, render_template
from services.llm_service import is_out_of_scope, get_out_of_scope_response
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
        history = data.get("history") or []

        # =========================
        # VALIDATE INPUT
        # =========================
        if not question:
            return jsonify({
                "answer": "Bạn chưa nhập câu hỏi. Hãy thử nhập nội dung bạn muốn tìm nhé.",
                "documents": []
            }), 200

        # =========================
        # OUT-OF-SCOPE GUARD
        # =========================

        if is_out_of_scope(question):
            return jsonify({
                "answer": get_out_of_scope_response(),
                "documents": []
            }), 200

        # =========================
        # CALL SERVICE (LEVEL 4)
        # =========================
        result = get_qa_response(question, history)

        # fallback tránh None
        if not result:
            result = {}
            
        from services.graph_service import get_multi_document_graph_service
        
        documents = result.get("documents", [])
        graph_data = {"nodes": [], "edges": []}
        
        if documents:
            doc_ids = [doc.get("id") for doc in documents if doc.get("id")]
            if doc_ids:
                try:
                    graph_data = get_multi_document_graph_service(doc_ids)
                except Exception as e:
                    print("QA GRAPH ERROR:", e)

        return jsonify({
            "answer": result.get("answer", "Mình chưa có câu trả lời phù hợp."),
            "documents": documents,
            "main_subject": result.get("main_subject"),
            "related_subjects": result.get("related_subjects", []),

            # 🔥 optional (dùng cho Level 3/4 UI)
            "suggestions": result.get("suggestions", []),
            "explanation": result.get("explanation", None),
            
            # 🔥 data cho graph component ở frontend
            "graph_data": graph_data
        }), 200

    except Exception as e:
        print("QA ERROR:", e)

        return jsonify({
            "answer": "Có lỗi xảy ra khi xử lý câu hỏi. Bạn thử lại nhé.",
            "documents": [],
            "suggestions": [],
            "explanation": None
        }), 500