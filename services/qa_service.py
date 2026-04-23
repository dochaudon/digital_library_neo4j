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
# 🔥 PARSER
# =========================
def parse_question(question):
    q = (question or "").lower()

    intent = "search"
    filters = {}

    # =========================
    # INTENT
    # =========================
    if "tác giả" in q or "ai viết" in q:
        intent = "author"

    elif "xuất bản" in q:
        intent = "publisher"

    elif "năm" in q:
        intent = "year"

    elif "chủ đề" in q or "lĩnh vực" in q:
        intent = "subject"

    elif "trường" in q or "đại học" in q:
        intent = "university"

    elif "bao nhiêu" in q or "số lượng" in q:
        intent = "count"

    elif "liên quan" in q:
        intent = "related"

    # =========================
    # TYPE
    # =========================
    if "luận văn" in q:
        filters["doc_type"] = "Thesis"
    elif "bài báo" in q:
        filters["doc_type"] = "Article"
    elif "sách" in q or "giáo trình" in q:
        filters["doc_type"] = "Book"

    # =========================
    # YEAR
    # =========================
    years = re.findall(r'(20\d{2})', q)

    if len(years) == 1:
        filters["year"] = int(years[0])

    elif len(years) >= 2:
        filters["year_from"] = int(years[0])
        filters["year_to"] = int(years[1])

    # =========================
    # FIX BUG "ai"
    # =========================
    if re.search(r"\bai\b", q):
        filters["keyword"] = "AI"

    # =========================
    # SUBJECT mapping
    # =========================
    if "kinh tế" in q:
        filters["subject"] = "Economics"

    if "trí tuệ nhân tạo" in q:
        filters["subject"] = "Artificial Intelligence"

    return intent, filters


# =========================
# EXTRACT TITLE
# =========================
def extract_title(question):
    q = question.lower()

    if "của" in q:
        return q.split("của")[-1].strip()

    return question.strip()


# =========================
# FORMAT ANSWER
# =========================
def format_answer(results, intent):

    if not results:
        return "Mình đã tìm trong hệ thống nhưng chưa có dữ liệu phù hợp."

    top = results[0]

    if intent == "author":
        authors = top.get("authors") or []
        if authors:
            return f'Tài liệu "{top["title"]}" được viết bởi {", ".join(authors)}.'

    if intent == "publisher":
        if top.get("publisher"):
            return f'Tài liệu "{top["title"]}" được xuất bản bởi {top["publisher"]}.'

    if intent == "year":
        if top.get("year"):
            return f'Tài liệu "{top["title"]}" xuất bản năm {top["year"]}.'

    if intent == "subject":
        subjects = top.get("subjects") or []
        if subjects:
            return f'Tài liệu "{top["title"]}" thuộc lĩnh vực {", ".join(subjects)}.'

    if len(results) > 1:
        titles = [r["title"] for r in results[:3]]
        return f"Mình tìm thấy {len(results)} tài liệu, ví dụ: " + ", ".join(titles)

    return f'Mình tìm thấy tài liệu "{top["title"]}" phù hợp nhất.'


# =========================
# MAIN QA
# =========================
def get_qa_response(question):

    if not question:
        return {
            "answer": "Bạn hãy nhập câu hỏi nhé.",
            "documents": []
        }

    intent, filters = parse_question(question)
    title = extract_title(question)

    # =========================
    # 🔥 KNOWLEDGE QA
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
        results = search_documents("", filters, 1000)

        if not results:
            return {
                "answer": "Chưa có dữ liệu để thống kê.",
                "documents": []
            }

        return {
            "answer": f"Có khoảng {len(results)} tài liệu phù hợp.",
            "documents": results[:5]
        }

    # =========================
    # 🔥 SEARCH
    # =========================
    results = search_documents(question, filters, 10)

    if not results:
        results = search_documents(question, {}, 10)

    if not results:
        results = search_documents("", {}, 10)

    answer = format_answer(results, intent)

    return {
        "answer": answer,
        "documents": results
    }