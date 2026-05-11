from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
        print("Model loaded")

    return _model

def create_embedding(text: str):
    if not text:
        return []

    model = get_model()
    # SentenceTransformer.encode handles the tokenizer and pooling automatically
    embedding = model.encode(text)
    return embedding.tolist()

def build_document_text(title=None, abstract=None):
    title = title or ""
    abstract = abstract or ""
    return f"{title}. {abstract}".strip()