from models.qa_model import (
    get_document_match_by_title,
    get_author_by_title,
    get_year_by_title,
    get_subject_by_title,
    get_publisher_by_title,
    get_university_by_title
)

from services.search_service import search_documents


# =========================
# SIMPLE NLP PARSER
# =========================
def parse_question(question):
    q = (question or "").lower()

    if "tac gia" in q or "ai viet" in q:
        return "author"

    if "nam" in q or "bao nhieu nam" in q:
        return "year"

    if "chu de" in q or "linh vuc" in q:
        return "subject"

    if "nha xuat ban" in q or "xuat ban" in q:
        return "publisher"

    if "truong" in q or "dai hoc" in q:
        return "university"

    return "search"


# =========================
# EXTRACT TITLE (NAIVE)
# =========================
def extract_title(question):
    # đơn giản: lấy phần sau "cua"
    parts = question.split("cua")
    if len(parts) > 1:
        return parts[-1].strip()

    return question.strip()


# =========================
# MAIN QA FUNCTION
# =========================
def get_qa_response(question):

    if not question:
        return {
            "answer": "Vui lòng nhập câu hỏi.",
            "documents": []
        }

    intent = parse_question(question)
    title = extract_title(question)

    # =========================
    # AUTHOR
    # =========================
    if intent == "author":
        result = get_author_by_title(title)

        if result:
            row = result[0]
            authors = row.get("authors") or []

            if authors:
                return {
                    "answer": f'Tác giả của "{row["title"]}" là {", ".join(authors)}.',
                    "documents": [row]
                }

    # =========================
    # YEAR
    # =========================
    if intent == "year":
        result = get_year_by_title(title)

        if result:
            row = result[0]
            if row.get("year"):
                return {
                    "answer": f'Tài liệu "{row["title"]}" xuất bản năm {row["year"]}.',
                    "documents": [row]
                }

    # =========================
    # SUBJECT
    # =========================
    if intent == "subject":
        result = get_subject_by_title(title)

        if result:
            row = result[0]
            subjects = row.get("subjects") or []

            if subjects:
                return {
                    "answer": f'Tài liệu "{row["title"]}" thuộc chủ đề {", ".join(subjects)}.',
                    "documents": [row]
                }

    # =========================
    # PUBLISHER
    # =========================
    if intent == "publisher":
        result = get_publisher_by_title(title)

        if result:
            row = result[0]
            if row.get("publisher"):
                return {
                    "answer": f'Nhà xuất bản của "{row["title"]}" là {row["publisher"]}.',
                    "documents": [row]
                }

    # =========================
    # UNIVERSITY
    # =========================
    if intent == "university":
        result = get_university_by_title(title)

        if result:
            row = result[0]
            if row.get("university"):
                return {
                    "answer": f'Luận văn "{row["title"]}" được thực hiện tại {row["university"]}.',
                    "documents": [row]
                }

    # =========================
    # 🔥 FALLBACK → SEARCH
    # =========================
    results = search_documents(question, {}, 5)

    if results:
        return {
            "answer": f"Tìm thấy {len(results)} tài liệu liên quan.",
            "documents": results
        }

    return {
        "answer": "Không tìm thấy kết quả phù hợp.",
        "documents": []
    }