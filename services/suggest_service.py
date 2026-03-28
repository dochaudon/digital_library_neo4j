from models.suggest_model import suggest_documents_query

def suggest_documents(query):

    if not query:
        return []

    return suggest_documents_query(query)