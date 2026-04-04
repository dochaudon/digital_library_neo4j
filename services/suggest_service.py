from models.suggest_model import suggest_documents_query


# =========================
# CLEAN INPUT
# =========================
def clean_query(query):
    if not query:
        return None
    return query.strip()


# =========================
# SUGGEST (AUTOCOMPLETE)
# =========================
def suggest_documents(query):

    query = clean_query(query)

    if not query:
        return []

    try:
        return suggest_documents_query(query)
    except Exception:
        return []