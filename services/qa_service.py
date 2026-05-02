import re

from models.qa_model import (
    get_author_by_title,
    get_year_by_title,
    get_subject_by_title,
    get_publisher_by_title,
    get_university_by_title
)

from services.search_service import search_documents


# =========================
# 🔥 INTENT DETECTION (SMART)
# =========================
def detect_intent(question):
    q = (question or "").lower()

    # factual (graph)
    if any(x in q for x in ["ai viết", "tác giả"]):
        return "author"

    if "xuất bản" in q:
        return "publisher"

    if "năm" in q:
        return "year"

    if any(x in q for x in ["chủ đề", "lĩnh vực"]):
        return "subject"

    if any(x in q for x in ["trường", "đại học"]):
        return "university"

    if any(x in q for x in ["bao nhiêu", "số lượng"]):
        return "count"

    # semantic
    if any(x in q for x in ["giống", "liên quan", "tương tự"]):
        return "semantic"

    return "search"


# =========================
# 🔥 EXTRACT TITLE
# =========================
def extract_title(question):
    q = question.lower()

    if "của" in q:
        return q.split("của")[-1].strip()

    return question.strip()


# =========================
# 🔥 PARSE FILTER (SMART)
# =========================
def parse_filters(question):
    q = question.lower()
    filters = {}

    if "luận văn" in q:
        filters["doc_type"] = "Thesis"
    elif "bài báo" in q:
        filters["doc_type"] = "Article"
    elif "sách" in q:
        filters["doc_type"] = "Book"

    # year
    year_match = re.search(r'\b(19|20)\d{2}\b', q)
    if year_match:
        filters["year"] = int(year_match.group())

    # subject mapping
    if "ai" in q or "trí tuệ nhân tạo" in q:
        filters["subject"] = "Artificial Intelligence"

    if "học máy" in q:
        filters["subject"] = "Machine Learning"

    return filters


# =========================
# 🔥 FORMAT ANSWER (NÂNG CẤP)
# =========================
def format_smart_answer(results, intent):

    if not results:
        return "Mình chưa tìm thấy tài liệu phù hợp trong hệ thống."

    top = results[0]

    # factual
    if intent == "author":
        authors = top.get("authors", [])
        if authors:
            return f'Tài liệu "{top["title"]}" được viết bởi {", ".join(authors)}.'

    if intent == "year":
        if top.get("year"):
            return f'Tài liệu "{top["title"]}" xuất bản năm {top["year"]}.'

    # semantic explanation
    titles = [r["title"] for r in results[:3]]

    return (
        f'Mình tìm thấy {len(results)} tài liệu liên quan.\n\n'
        f'📚 Gợi ý nổi bật:\n'
        f'- ' + '\n- '.join(titles)
    )


# =========================
# 🔥 MAIN QA (HYBRID)
# =========================
def get_qa_response(question):

    if not question:
        return {
            "answer": "Bạn hãy nhập câu hỏi nhé.",
            "documents": []
        }

    intent = detect_intent(question)
    filters = parse_filters(question)
    title = extract_title(question)

    # =========================
    # 🔥 GRAPH QA (CHÍNH XÁC)
    # =========================
    if intent == "author":
        result = get_author_by_title(title)
        if result and result[0].get("authors"):
            return {
                "answer": f'Tài liệu "{result[0]["title"]}" được viết bởi {", ".join(result[0]["authors"])}.',
                "documents": []
            }

    if intent == "publisher":
        result = get_publisher_by_title(title)
        if result and result[0].get("publisher"):
            return {
                "answer": f'Tài liệu "{result[0]["title"]}" được xuất bản bởi {result[0]["publisher"]}.',
                "documents": []
            }

    if intent == "year":
        result = get_year_by_title(title)
        if result and result[0].get("year"):
            return {
                "answer": f'Tài liệu "{result[0]["title"]}" xuất bản năm {result[0]["year"]}.',
                "documents": []
            }

    if intent == "subject":
        result = get_subject_by_title(title)
        if result and result[0].get("subjects"):
            return {
                "answer": f'Tài liệu "{result[0]["title"]}" thuộc lĩnh vực {", ".join(result[0]["subjects"])}.',
                "documents": []
            }

    if intent == "university":
        result = get_university_by_title(title)
        if result and result[0].get("university"):
            return {
                "answer": f'Luận văn "{result[0]["title"]}" được thực hiện tại {result[0]["university"]}.',
                "documents": []
            }

    # =========================
    # 🔥 COUNT
    # =========================
    if intent == "count":
        results = search_documents("", filters, 100)

        return {
            "answer": f"Có khoảng {len(results)} tài liệu phù hợp.",
            "documents": results[:5]
        }

    # =========================
    # 🔥 SEMANTIC SEARCH (CHÍNH)
    # =========================
    results = search_documents(question, filters, 10)

    if not results:
        results = search_documents(question, {}, 10)

    if not results:
        results = search_documents("", {}, 10)

    answer = format_smart_answer(results, intent)

    return {
        "answer": answer,
        "documents": results
    }