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
        print("Gemini client loaded (new SDK)")

    return _client



# =========================
# OUT-OF-SCOPE DETECTION
# =========================
_OUT_OF_SCOPE_KEYWORDS = [
    "thời tiết", "weather", "bóng đá", "football", "nấu ăn", "recipe", "giá cổ phiếu",
    "chứng khoán", "tin tức", "news", "phim", "movie", "nhạc", "music", "game",
    "du lịch", "travel", "sức khỏe", "y tế", "thuốc", "thể thao", "sport",
    "chính trị", "politics", "ca sĩ", "giải trí", "showbiz", "đời sống", "tâm sự"
]

def is_out_of_scope(question: str) -> bool:
    q = question.lower()
    # 1. Blacklist keywords
    for kw in _OUT_OF_SCOPE_KEYWORDS:
        if kw in q:
            return True
    return False

def is_academic_intent(question: str) -> bool:
    """Kiểm tra xem câu hỏi có thuộc phạm vi học thuật không."""
    q = question.lower()
    academic_keywords = [
        "sách", "luận văn", "bài báo", "giáo trình", "nghiên cứu", "tác giả",
        "ai", "cntt", "robotics", "machine learning", "khoa học", "giáo dục",
        "tóm tắt", "tìm kiếm", "metadata", "thư viện", "chủ đề", "định nghĩa",
        "khái niệm", "giải thích", "deep learning", "kinh tế", "toán học"
    ]
    
    # Nếu câu hỏi quá ngắn và không có keyword academic thì coi như không phải academic
    if len(q.split()) < 3:
        return any(kw in q for kw in academic_keywords)
        
    # Cho phép các câu hỏi mang tính chất tìm hiểu, tra cứu
    return True



# =========================
# CONTEXT BUILDER
# =========================
def build_context_from_docs(docs: list, header: str = None) -> str:
    """Chuyển danh sách tài liệu thành đoạn context cho LLM."""
    if not docs:
        return ""

    parts = []
    if header:
        parts.append(f"=== {header} ===\n")

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
    # Chỉ lấy 3 lượt gần nhất để tránh loãng context
    for msg in history[-3:]: 
        role = "Người dùng" if msg.get("role") == "user" else "Trợ lý"
        content = msg.get("content", "")[:300]
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)



# =========================
# RAG PROMPT BUILDER
# =========================
def build_rag_prompt(question: str, local_docs: list, external_docs: list = None, history: list = None, data: str = None) -> str:
    """Xây dựng prompt đầy đủ theo chuẩn Grounded Academic QA."""

    local_context = build_context_from_docs(local_docs, "Local Library Documents")
    external_context = build_context_from_docs(external_docs or [], "External Academic References")
    
    history_text = build_history_text(history or [])

    # Dữ liệu factual trực tiếp từ Neo4j (nếu có)
    factual_block = ""
    if data:
        factual_block = f"\n=== Direct System Metadata ===\n{data}\n"

    system_prompt = """Bạn là trợ lý học thuật chuyên sâu cho hệ thống thư viện số.

NGUYÊN TẮC TRẢ LỜI (ACADEMIC RAG):
1. ƯU TIÊN CONTEXT: Luôn ưu tiên sử dụng thông tin từ các phần CONTEXT (Local Library và External Academic) bên dưới để trả lời.
2. KIẾN THỨC CHUNG: Đối với các câu hỏi về định nghĩa, khái niệm học thuật cơ bản (Ví dụ: "Machine Learning là gì?", "AI là gì?"), nếu context không có, bạn ĐƯỢC PHÉP sử dụng kiến thức chuyên môn sẵn có của mình để giải thích một cách chuẩn xác và khoa học.
3. TRÍCH DẪN: Khi đề cập đến tài liệu cụ thể, chỉ được sử dụng thông tin có trong context. Tuyệt đối không bịa đặt tên sách, tác giả hoặc năm xuất bản không có trong hệ thống.
4. ĐỊNH HƯỚNG: Nếu người dùng hỏi về một chủ đề rộng, hãy giải thích khái niệm đó và gợi ý các tài liệu liên quan có trong context.
5. PHONG CÁCH: Trả lời bằng Tiếng Việt, phong cách học thuật, chuyên nghiệp, khách quan.
6. PHẠM VI: Chỉ trả lời các câu hỏi về học thuật, nghiên cứu và thư viện. Từ chối các chủ đề ngoài lề (chính trị, đời sống, giải trí...).
"""



    prompt_parts = [system_prompt]

    if history_text:
        prompt_parts.append(f"\nLỊCH SỬ HỘI THOẠI GẦN ĐÂY:\n{history_text}\n---")

    prompt_parts.append(f"\nCONTEXT ĐƯỢC CUNG CẤP:\n{local_context}\n{external_context}\n{factual_block}")
    prompt_parts.append(f"\nCÂU HỎI HIỆN TẠI: {question}")
    prompt_parts.append("\nTRẢ LỜI (Grounded Academic Response):")

    return "\n".join(prompt_parts)



# =========================
# MAIN: CALL GEMINI
# =========================
def call_gemini(prompt: str) -> str:
    """Gọi Gemini API và trả về câu trả lời."""
    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-flash-latest",



            contents=prompt,
            config={
                'temperature': 0.3,
                'max_output_tokens': 1024,
            }
        )
        return response.text.strip()
    except Exception as e:
        print(f"[LLM] Gemini API error: {e}")

        return None



# =========================
# OUT-OF-SCOPE RESPONSE
# =========================
def get_out_of_scope_response() -> str:
    return (
        "Xin lỗi, mình chỉ hỗ trợ tìm kiếm và hỏi đáp về **tài liệu học thuật** trong Thư viện số.\n\n"
        "_Hãy thử hỏi về tác giả, chủ đề, tóm tắt hoặc tìm kiếm sách, bài báo, luận văn nhé!_"
    )

def translate_query_for_academic(query: str) -> str:
    """Sử dụng Gemini để dịch query Tiếng Việt sang keywords Tiếng Anh học thuật."""
    if not query:
        return ""
    
    prompt = f"""Dịch câu truy vấn tìm kiếm tài liệu học thuật sau đây từ Tiếng Việt sang các từ khóa Tiếng Anh (English Keywords) ngắn gọn, súc tích để tìm kiếm trên các hệ thống như Semantic Scholar hoặc arXiv.

Chỉ trả về các từ khóa Tiếng Anh, không giải thích gì thêm.
Câu truy vấn: {query}
Keywords (English only):"""

    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config={'temperature': 0.0}
        )
        translated = response.text.strip()
        # Loại bỏ các ký tự rác nếu có
        translated = re.sub(r'["\']', '', translated)
        return translated
    except:
        return query # Fallback về query gốc nếu lỗi

