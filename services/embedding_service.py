from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
        print("Model loaded")

    return _model

def create_embedding(text: str):
    if not text:
        return []

    model = get_model()
    # SentenceTransformer.encode handles the tokenizer and pooling automatically
    embedding = model.encode(text)
    return embedding.tolist()

def build_document_text(title=None, abstract=None, subjects=None, keywords=None):
    title = title or ""
    abstract = abstract or ""
    
    parts = [title, abstract]
    
    if subjects:
        if isinstance(subjects, str):
            parts.append(f"Subjects: {subjects}")
        elif isinstance(subjects, list):
            parts.append(f"Subjects: {', '.join(subjects)}")
            
    if keywords:
        if isinstance(keywords, str):
            parts.append(f"Keywords: {keywords}")
        elif isinstance(keywords, list):
            parts.append(f"Keywords: {', '.join(keywords)}")
            
    return ". ".join([p.strip() for p in parts if p.strip()]).strip()