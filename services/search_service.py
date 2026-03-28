import re
import unicodedata

from models.search_model import (
    search_documents_by_title,
    search_documents_by_graph,
    get_latest_documents
)


# =========================
# NORMALIZE
# =========================
def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def clean(x):
    if not x:
        return None
    return x.strip()


# =========================
# NLP PARSER (GIỮ NGUYÊN)
# =========================
def parse_nl_query(query: str):

    raw = clean(query) or ""
    q = normalize(raw)

    filters = {
        "doc_type": None,
        "author": None,
        "topic": None,
        "publisher": None,
        "university": None,
        "year": None
    }

    # ===== TYPE =====
    if "sach" in q:
        filters["doc_type"] = "Book"
    elif "bai bao" in q:
        filters["doc_type"] = "Article"
    elif "luan van" in q:
        filters["doc_type"] = "Thesis"

    # ===== YEAR =====
    year_match = re.search(r"\b(19|20)\d{2}\b", q)
    if year_match:
        filters["year"] = int(year_match.group())

    # ===== AUTHOR =====
    author_match = re.search(r"(?:cua|tac gia|viet boi)\s+(.+)", q)
    if author_match:
        filters["author"] = author_match.group(1).strip()

    # ===== PUBLISHER =====
    pub_match = re.search(r"(?:nha xuat ban|xuat ban boi)\s+(.+)", q)
    if pub_match:
        filters["publisher"] = pub_match.group(1).strip()

    # ===== UNIVERSITY =====
    uni_match = re.search(r"(?:truong|truong dai hoc)\s+(.+)", q)
    if uni_match:
        filters["university"] = uni_match.group(1).strip()

    # ===== TOPIC (SMART)
    temp = q

    remove_words = [
        "sach", "bai bao", "luan van",
        "cua", "tac gia", "viet boi",
        "nha xuat ban", "truong", "truong dai hoc"
    ]

    for w in remove_words:
        temp = temp.replace(w, "")

    temp = re.sub(r"\b(19|20)\d{2}\b", "", temp)
    temp = temp.strip()

    if temp:
        filters["topic"] = temp

    return filters


# =========================
# MERGE HYBRID
# =========================
def merge_results(k_results, g_results, limit=20):

    merged = {}

    for r in k_results:
        merged[r["id"]] = r

    for r in g_results:
        if r["id"] in merged:
            merged[r["id"]]["relevance_score"] += r["relevance_score"]
        else:
            merged[r["id"]] = r

    return sorted(
        merged.values(),
        key=lambda x: x.get("relevance_score", 0),
        reverse=True
    )[:limit]


# =========================
# MAIN SEARCH
# =========================
def search_documents(query="", mode="auto", filters=None, limit=20):

    filters = filters or {}

    parsed = parse_nl_query(query)

    # merge NLP filters
    for k, v in parsed.items():
        if not filters.get(k):
            filters[k] = v

    has_filter = any(filters.values())

    keyword_results = []
    graph_results = []

    if query:
        keyword_results = search_documents_by_title(query, limit * 2)

    if has_filter:
        graph_results = search_documents_by_graph(filters, limit * 2)

    # ===== MODE =====
    if mode == "keyword":
        return keyword_results[:limit]

    if mode == "graph":
        return graph_results[:limit]

    # ===== AUTO / HYBRID =====
    if graph_results:
        return merge_results(keyword_results, graph_results, limit)

    return keyword_results[:limit]


# =========================
# LATEST DOCUMENTS
# =========================
def get_latest(limit=20):
    return get_latest_documents(limit)