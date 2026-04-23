from transformers import AutoTokenizer, AutoModel
import torch

_tokenizer = None
_model = None


def get_model():
    global _tokenizer, _model

    if _model is None:
        print("🔄 Loading embedding model...")
        _tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        _model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        print("✅ Model loaded")

    return _tokenizer, _model


def create_embedding(text: str):
    if not text:
        return []

    tokenizer, model = get_model()

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    # mean pooling
    embeddings = outputs.last_hidden_state.mean(dim=1)

    return embeddings[0].numpy().tolist()


def build_document_text(title=None, abstract=None):
    title = title or ""
    abstract = abstract or ""
    return f"{title}. {abstract}".strip()