from models.graph_search_model import graph_search
from models.hybrid_search_model import hybrid_search
from models.qa_model import (
    get_document_match_by_title,
    get_author_by_title,
    get_publisher_by_title,
    get_subject_by_title,
    get_university_by_title,
    get_year_by_title,
)
from services.search_service import normalize, parse_nl_query


QA_RESULT_LIMIT = 5
REFERENCE_WORDS = {
    "no",
    "tai lieu do",
    "cuon do",
    "bai bao do",
    "luan van do",
    "sach do",
}


def clean_question(question):
    return (question or "").strip()


def clean_history(history):
    cleaned = []

    for item in history or []:
        if not isinstance(item, dict):
            continue

        cleaned.append(
            {
                "role": item.get("role", "user"),
                "content": clean_question(item.get("content")),
                "documents": item.get("documents") or [],
            }
        )

    return cleaned[-8:]


def has_search_filters(filters):
    return any(
        filters.get(key)
        for key in ["doc_type", "author", "subject", "publisher", "university", "year"]
    )


def build_document_url(doc_type, doc_id):
    if doc_type == "Book":
        return f"/book/{doc_id}"
    if doc_type == "Article":
        return f"/article/{doc_id}"
    if doc_type == "Thesis":
        return f"/thesis/{doc_id}"
    return "#"


def prepare_documents(documents):
    prepared = []

    for doc in documents or []:
        item = dict(doc)
        item["url"] = build_document_url(item.get("type"), item.get("id"))
        prepared.append(item)

    return prepared


def get_doc_type_label(doc_type):
    if doc_type == "Book":
        return "sach"
    if doc_type == "Article":
        return "bai bao"
    if doc_type == "Thesis":
        return "luan van"
    return "tai lieu"


def join_items(items):
    values = [str(item).strip() for item in items if str(item).strip()]
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} va {values[1]}"
    return ", ".join(values[:-1]) + f" va {values[-1]}"


def build_document_citations(documents):
    citations = []

    for doc in (documents or [])[:3]:
        detail_parts = []
        if doc.get("year"):
            detail_parts.append(str(doc["year"]))
        if doc.get("authors"):
            detail_parts.append(join_items(doc["authors"][:2]))
        elif doc.get("publisher"):
            detail_parts.append(str(doc["publisher"]))
        elif doc.get("university"):
            detail_parts.append(str(doc["university"]))

        citations.append(
            {
                "label": get_doc_type_label(doc.get("type")).capitalize(),
                "title": doc.get("title") or "Khong co tieu de",
                "url": doc.get("url") or "#",
                "detail": " | ".join(detail_parts),
            }
        )

    return citations


def get_last_referenced_title(history):
    for item in reversed(clean_history(history)):
        documents = item.get("documents") or []
        if documents:
            return documents[0].get("title")
    return None


def resolve_title(question, parsed, history=None):
    title = clean_question(parsed.get("subject"))
    if title and normalize(title) not in REFERENCE_WORDS:
        return title

    normalized_question = normalize(question)
    if normalized_question in REFERENCE_WORDS or any(word in normalized_question for word in REFERENCE_WORDS):
        return get_last_referenced_title(history)

    return None


def build_search_filters(parsed):
    return {
        "doc_type": parsed.get("doc_type"),
        "author": parsed.get("author"),
        "subject": parsed.get("subject"),
        "publisher": parsed.get("publisher"),
        "university": parsed.get("university"),
        "year": parsed.get("year"),
    }


def search_fallback(question, parsed):
    filters = build_search_filters(parsed)
    intent = parsed.get("intent")

    if intent:
        query_text = parsed.get("subject") or question
        documents = hybrid_search(query_text, {}, QA_RESULT_LIMIT)
        if parsed.get("doc_type"):
            documents = [doc for doc in documents if doc.get("type") == parsed["doc_type"]]
    elif has_search_filters(filters):
        documents = graph_search(filters, QA_RESULT_LIMIT)
    else:
        documents = hybrid_search(question, filters, QA_RESULT_LIMIT)

    prepared = prepare_documents(documents)
    if intent:
        answer = f"Tim thay {len(prepared)} tai lieu gan voi cau hoi cua ban."
    else:
        answer = f"Tim thay {len(prepared)} tai lieu lien quan voi cau hoi cua ban."
    return {
        "answer": answer,
        "documents": prepared,
        "citations": build_document_citations(prepared),
    }


def build_document_payload(row, extra=None):
    payload = {
        "id": row.get("id"),
        "title": row.get("title"),
        "type": row.get("type"),
        "year": row.get("year"),
    }

    if extra:
        payload.update(extra)

    return prepare_documents([payload])


def get_base_document_payload(title):
    result = get_document_match_by_title(title)
    if not result:
        return None, []

    row = result[0]
    return row, build_document_payload(row)


def answer_author_question(title):
    result = get_author_by_title(title)
    if not result:
        row, documents = get_base_document_payload(title)
        if not row:
            return None

        return {
            "answer": f'He thong chua co thong tin tac gia cho tai lieu "{row["title"]}".',
            "documents": documents,
            "citations": build_document_citations(documents),
        }

    row = result[0]
    authors = row.get("authors") or []
    documents = build_document_payload(row, {"authors": authors})

    if not authors:
        answer = f"He thong chua co thong tin tac gia cho tai lieu \"{row['title']}\"."
    else:
        answer = f'Tac gia cua "{row["title"]}" la {join_items(authors)}.'

    return {
        "answer": answer,
        "documents": documents,
        "citations": build_document_citations(documents),
    }


def answer_year_question(title):
    result = get_year_by_title(title)
    if not result:
        row, documents = get_base_document_payload(title)
        if not row:
            return None

        return {
            "answer": f'He thong chua co thong tin nam cua tai lieu "{row["title"]}".',
            "documents": documents,
            "citations": build_document_citations(documents),
        }

    row = result[0]
    documents = build_document_payload(row)
    year = row.get("year")

    if not year:
        answer = f"He thong chua co thong tin nam cua tai lieu \"{row['title']}\"."
    else:
        answer = f'Tai lieu "{row["title"]}" xuat ban hoac bao ve nam {year}.'

    return {
        "answer": answer,
        "documents": documents,
        "citations": build_document_citations(documents),
    }


def answer_subject_question(title):
    result = get_subject_by_title(title)
    if not result:
        row, documents = get_base_document_payload(title)
        if not row:
            return None

        return {
            "answer": f'He thong chua co thong tin chu de cua tai lieu "{row["title"]}".',
            "documents": documents,
            "citations": build_document_citations(documents),
        }

    row = result[0]
    subjects = row.get("subjects") or []
    documents = build_document_payload(row)

    if not subjects:
        answer = f"He thong chua co thong tin chu de cua tai lieu \"{row['title']}\"."
    else:
        answer = f'Tai lieu "{row["title"]}" thuoc chu de {join_items(subjects)}.'

    return {
        "answer": answer,
        "documents": documents,
        "citations": build_document_citations(documents),
    }


def answer_publisher_question(title):
    result = get_publisher_by_title(title)
    if not result:
        row, documents = get_base_document_payload(title)
        if not row:
            return None

        return {
            "answer": f'He thong chua co thong tin nha xuat ban cua tai lieu "{row["title"]}".',
            "documents": documents,
            "citations": build_document_citations(documents),
        }

    row = result[0]
    publisher = row.get("publisher")
    documents = build_document_payload(row, {"publisher": publisher})

    if not publisher:
        answer = f"He thong chua co thong tin nha xuat ban cua tai lieu \"{row['title']}\"."
    else:
        answer = f'Nha xuat ban cua "{row["title"]}" la {publisher}.'

    return {
        "answer": answer,
        "documents": documents,
        "citations": build_document_citations(documents),
    }


def answer_university_question(title):
    result = get_university_by_title(title)
    if not result:
        row, documents = get_base_document_payload(title)
        if not row:
            return None

        return {
            "answer": f'He thong chua co thong tin truong cua tai lieu "{row["title"]}".',
            "documents": documents,
            "citations": build_document_citations(documents),
        }

    row = result[0]
    university = row.get("university")
    documents = build_document_payload(row, {"university": university})

    if not university:
        answer = f"He thong chua co thong tin truong cua tai lieu \"{row['title']}\"."
    else:
        answer = f'Luan van "{row["title"]}" duoc thuc hien tai {university}.'

    return {
        "answer": answer,
        "documents": documents,
        "citations": build_document_citations(documents),
    }


def build_qa_payload(question, history=None):
    parsed = parse_nl_query(question)
    intent = parsed.get("intent")
    title = resolve_title(question, parsed, history=history)

    if intent == "ask_author" and title:
        response = answer_author_question(title)
        if response:
            return response

    if intent == "ask_year" and title:
        response = answer_year_question(title)
        if response:
            return response

    if intent == "ask_subject" and title:
        response = answer_subject_question(title)
        if response:
            return response

    if intent == "ask_publisher" and title:
        response = answer_publisher_question(title)
        if response:
            return response

    if intent == "ask_university" and title:
        response = answer_university_question(title)
        if response:
            return response

    return search_fallback(question, parsed)


def answer_question(question, history=None):
    return build_qa_payload(question, history=history).get("answer")


def get_qa_response(question, history=None):
    question = clean_question(question)
    history = clean_history(history)

    if not question:
        return {
            "answer": "Vui long nhap cau hoi bang tieng Viet de he thong tra cuu du lieu thu vien.",
            "documents": [],
            "citations": [],
        }

    response = build_qa_payload(question, history=history)

    return {
        "answer": response.get("answer", "He thong chua co cau tra loi phu hop."),
        "documents": response.get("documents", []),
        "citations": response.get("citations", []),
    }
