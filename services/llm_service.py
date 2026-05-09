import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONFIG
# =========================
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        _client = genai.Client(api_key=api_key)
        print("✅ Gemini client loaded (new SDK)")
    return _client



# =========================
# OUT-OF-SCOPE DETECTION
# =========================
_OUT_OF_SCOPE_KEYWORDS = [
    "thời tiết", "weather", "bóng đá", "football", "nấu ăn", "recipe", "giá cổ phiếu",
    "chứng khoán", "tin tức", "news", "phim", "movie", "nhạc", "music", "game",
    "du lịch", "travel", "sức khỏe", "y tế", "thuốc", "thể thao", "sport"
]

def is_out_of_scope(question: str) -> bool:
    q = question.lower()
    for kw in _OUT_OF_SCOPE_KEYWORDS:
        if kw in q:
            return True
    return False


# =========================
# CONTEXT BUILDER
# =========================
def build_context_from_docs(docs: list) -> str:
    """Chuyển danh sách tài liệu thành đoạn context cho LLM."""
    if not docs:
        return "Không có tài liệu nào liên quan được tìm thấy."

    parts = []
    for i, doc in enumerate(docs[:5], 1):
        title = doc.get("title", "N/A")
        year = doc.get("year", "N/A")
        authors = ", ".join(doc.get("authors") or []) or "N/A"
        abstract = doc.get("abstract", "")
        subjects = ", ".join(doc.get("subjects") or []) or ""
        keywords = ", ".join(doc.get("keywords") or []) or ""

        block = f"[{i}] Tiêu đề: {title}\n"
        block += f"    Tác giả: {authors}\n"
        block += f"    Năm xuất bản: {year}\n"
        if subjects:
            block += f"    Chủ đề: {subjects}\n"
        if keywords:
            block += f"    Từ khóa: {keywords}\n"
        if abstract:
            block += f"    Tóm tắt: {abstract[:500]}\n"
        parts.append(block)

    return "\n".join(parts)


# =========================
# HISTORY BUILDER
# =========================
def build_history_text(history: list) -> str:
    """Chuyển lịch sử hội thoại thành dạng text cho prompt."""
    if not history:
        return ""
    
    lines = []
    for msg in history[-6:]:  # Chỉ lấy 6 lượt gần nhất
        role = "Người dùng" if msg.get("role") == "user" else "Trợ lý"
        content = msg.get("content", "")[:300]  # Giới hạn 300 ký tự mỗi lượt
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)


# =========================
# RAG PROMPT BUILDER
# =========================
def build_rag_prompt(question: str, context_docs: list, history: list = None, data: dict = None) -> str:
    """Xây dựng prompt đầy đủ theo chuẩn RAG."""

    context = build_context_from_docs(context_docs)
    history_text = build_history_text(history or [])

    # Nếu có dữ liệu factual trực tiếp từ Neo4j (dùng cho QA intent)
    factual_block = ""
    if data:
        factual_block = f"\n**Dữ liệu chính xác từ hệ thống:**\n{data}\n"

    system_prompt = """Bạn là trợ lý ảo hỗ trợ tìm kiếm tài liệu học thuật của Thư viện số.

NGUYÊN TẮC BẮT BUỘC:
1. Chỉ trả lời dựa trên thông tin được cung cấp trong phần TÀI LIỆU THAM CHIẾU bên dưới.
2. Nếu thông tin không có trong tài liệu được cung cấp, hãy trả lời: "Mình chưa có thông tin về điều này trong hệ thống."
3. KHÔNG sử dụng kiến thức bên ngoài. KHÔNG bịa đặt thông tin.
4. Trả lời bằng Tiếng Việt, tự nhiên và thân thiện như một thủ thư.
5. Khi trích dẫn, luôn đề cập tên tài liệu cụ thể.
6. Câu trả lời ngắn gọn, súc tích (tối đa 3-4 câu, trừ khi được yêu cầu tóm tắt dài).
"""

    prompt_parts = [system_prompt]

    if history_text:
        prompt_parts.append(f"\n---\nLỊCH SỬ HỘI THOẠI GẦN ĐÂY:\n{history_text}")

    prompt_parts.append(f"\n---\nTÀI LIỆU THAM CHIẾU:\n{context}{factual_block}")
    prompt_parts.append(f"\n---\nCÂU HỎI: {question}")
    prompt_parts.append("\nTRẢ LỜI (bằng Tiếng Việt, dựa hoàn toàn vào tài liệu trên):")

    return "\n".join(prompt_parts)


# =========================
# MAIN: CALL GEMINI
# =========================
def call_gemini(prompt: str) -> str:
    """Gọi Gemini API và trả về câu trả lời."""
    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={
                'temperature': 0.3,
                'max_output_tokens': 1024,
            }
        )
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return None



# =========================
# OUT-OF-SCOPE RESPONSE
# =========================
def get_out_of_scope_response() -> str:
    return (
        "Xin lỗi, mình chỉ hỗ trợ tìm kiếm và hỏi đáp về **tài liệu học thuật** trong Thư viện số.\n\n"
        "_Hãy thử hỏi về tác giả, chủ đề, tóm tắt hoặc tìm kiếm sách, bài báo, luận văn nhé!_"
    )
