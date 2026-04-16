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


def clean(value):
    if not value:
        return None
    return value.strip()


def extract_qa_title(q: str, intent: str | None):
    if not q or not intent:
        return None

    patterns_by_intent = {
        "ask_author": [
            r"(?:ai la tac gia(?: cua)?|tac gia(?: cua)?|ai viet(?: cua)?|ai viet)\s+(?:sach|bai bao|luan van|tai lieu)?\s*(.+)$",
        ],
        "ask_year": [
            r"(?:nam xuat ban cua|nam cua|bao nhieu nam cua)\s+(?:sach|bai bao|luan van|tai lieu)?\s*(.+)$",
        ],
        "ask_subject": [
            r"(?:chu de cua|linh vuc cua)\s+(?:sach|bai bao|luan van|tai lieu)?\s*(.+)$",
        ],
        "ask_publisher": [
            r"(?:nha xuat ban cua|ai xuat ban|xuat ban boi ai)\s+(?:sach|bai bao|luan van|tai lieu)?\s*(.+)$",
        ],
        "ask_university": [
            r"(?:truong cua|luan van cua truong nao|duoc thuc hien tai truong nao|nop tai truong nao)\s+(?:sach|bai bao|luan van|tai lieu)?\s*(.+)$",
        ],
    }

    for pattern in patterns_by_intent.get(intent, []):
        match = re.search(pattern, q, flags=re.IGNORECASE)
        if match:
            title = match.group(1).strip(" ?!.,:;\"'")
            for suffix in ["la ai", "la gi", "o dau", "la truong nao", "la nha xuat ban nao"]:
                if title.endswith(suffix):
                    title = title[: -len(suffix)].strip(" ?!.,:;\"'")
            return title or None

    return None


# =========================
# NLP PARSER
# =========================
def parse_nl_query(query: str):
    raw = clean(query) or ""
    q = normalize(raw)

    filters = {
        "doc_type": None,
        "author": None,
        "subject": None,
        "publisher": None,
        "university": None,
        "year": None,
        "category": None,
        "intent": None,
    }

    # ===== TYPE =====
    if "sach" in q:
        filters["doc_type"] = "Book"
    elif "bai bao" in q:
        filters["doc_type"] = "Article"
    elif "luan van" in q:
        filters["doc_type"] = "Thesis"

    # ===== CATEGORY =====
    if "giao trinh" in q:
        filters["category"] = "Giao trinh"
    elif "tham khao" in q:
        filters["category"] = "Tham khao"

    # ===== INTENT =====
    if "tac gia" in q or "ai viet" in q:
        filters["intent"] = "ask_author"
    elif any(phrase in q for phrase in ["nam xuat ban cua", "nam cua", "bao nhieu nam cua"]):
        filters["intent"] = "ask_year"
    elif "chu de cua" in q or "linh vuc cua" in q:
        filters["intent"] = "ask_subject"
    elif any(phrase in q for phrase in ["nha xuat ban cua", "ai xuat ban", "xuat ban boi ai"]):
        filters["intent"] = "ask_publisher"
    elif any(phrase in q for phrase in ["truong cua", "luan van cua truong nao", "duoc thuc hien tai truong nao", "nop tai truong nao"]):
        filters["intent"] = "ask_university"

    # ===== YEAR FILTER =====
    year_match = re.search(r"\b(19|20)\d{2}\b", q)
    if year_match:
        filters["year"] = int(year_match.group())

    # ===== TITLE FOR QA =====
    title_candidate = extract_qa_title(q, filters["intent"])
    if title_candidate:
        filters["subject"] = title_candidate

    # QA questions should stop here so entity extraction does not pollute filters.
    if filters["intent"]:
        return filters

    # ===== AUTHOR =====
    author_match = re.search(r"(?:cua|tac gia|viet boi)\s+([a-zA-Z\s]+)", q)
    if author_match:
        filters["author"] = author_match.group(1).strip()

    # ===== PUBLISHER =====
    pub_match = re.search(r"(?:nha xuat ban|xuat ban boi)\s+([a-zA-Z\s]+)", q)
    if pub_match:
        filters["publisher"] = pub_match.group(1).strip()

    # ===== UNIVERSITY =====
    uni_match = re.search(r"(?:truong dai hoc|truong)\s+([a-zA-Z\s]+)", q)
    if uni_match:
        filters["university"] = uni_match.group(1).strip()

    # ===== SUBJECT =====
    temp = q
    remove_words = [
        "sach", "bai bao", "luan van",
        "giao trinh", "tham khao",
        "cua", "tac gia", "viet boi",
        "nha xuat ban", "xuat ban boi",
        "truong", "truong dai hoc", "nam",
    ]

    for word in remove_words:
        temp = temp.replace(word, "")

    temp = re.sub(r"\b(19|20)\d{2}\b", "", temp)
    temp = re.sub(r"\s+", " ", temp).strip()

    if temp and temp != filters["author"]:
        filters["subject"] = temp

    return filters


# =========================
# MAIN SEARCH (HYBRID)
# =========================
def search_documents(query="", filters=None, limit=20):
    filters = filters or {}
    parsed = parse_nl_query(query)

    final_filters = {}
    for key in [
        "doc_type",
        "author",
        "subject",
        "publisher",
        "university",
        "year",
        "category",
    ]:
        final_filters[key] = filters.get(key) or parsed.get(key)

    return hybrid_search(query, final_filters, limit)


# =========================
# LATEST DOCUMENTS
# =========================
def get_latest(limit=20):
    return get_latest_documents(limit)
