import re
import unicodedata

from models.hybrid_search_model import hybrid_search
from models.search_model import get_latest_documents


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
# NLP PARSER (UPDATED)
# =========================
def parse_nl_query(query: str):

    raw = clean(query) or ""
    q = normalize(raw)

    filters = {
        "doc_type": None,
        "author": None,
        "subject": None,   # 🔥 đổi từ topic → subject
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

    # ===== SUBJECT (SMART)
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
        filters["subject"] = temp   # 🔥 đổi topic → subject

    return filters


# =========================
# MAIN SEARCH (HYBRID)
# =========================
def search_documents(query="", filters=None, limit=20):

    filters = filters or {}

    # NLP parse
    parsed = parse_nl_query(query)

    # merge filters
    for k, v in parsed.items():
        if not filters.get(k):
            filters[k] = v

    return hybrid_search(query, filters, limit)


# =========================
# LATEST DOCUMENTS
# =========================
def get_latest(limit=20):
    return get_latest_documents(limit)