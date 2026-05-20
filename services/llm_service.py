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
    """Kiểm tra xem câu hỏi có thuộc phạm vi học thuật/thư viện không."""
    q = question.lower()
    
    # 1. Academic Whitelist
    academic_concepts = [
        "sách", "luận văn", "bài báo", "giáo trình", "nghiên cứu", "tài liệu",
        "tác giả", "nhà xuất bản", "năm xuất bản", "chủ đề", "từ khóa",
        "trường", "đại học", "học viện", "thư viện", "tra cứu", "tìm",
        "cntt", "công nghệ", "kinh tế", "toán", "vật lý", "hóa học", "sinh học",
        "cơ khí", "xây dựng", "môi trường", "ngôn ngữ", "triết học",
        "ai", "trí tuệ nhân tạo", "machine learning", "deep learning", "data science",
        "blockchain", "iot", "cloud", "security", "hệ thống", "phát triển",
        "tóm tắt", "nội dung", "giải thích", "khái niệm", "định nghĩa"
    ]
    
    # Check if any academic concept is present
    has_academic_word = any(kw in q for kw in academic_concepts)
    
    # 2. Structure check
    # Nếu câu hỏi quá ngắn mà không có keyword học thuật -> False
    if len(q.split()) < 3 and not has_academic_word:
        return False
        
    return has_academic_word



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

    for i, doc in enumerate(docs[:8], 1):
        # Relevance Filter
        score = doc.get("score", 1.0)
        is_external = doc.get("is_external", False)
        if not is_external and score < 0.1: # Giảm ngưỡng để lấy được nhiều metadata match hơn
            continue

        title = doc.get("title", "N/A")
        year = doc.get("year", "N/A")
        authors = ", ".join(doc.get("authors") or []) or "N/A"
        abstract = doc.get("abstract", "")
        subjects = ", ".join(doc.get("subjects") or []) or ""
        keywords = ", ".join(doc.get("keywords") or []) or ""
        url = doc.get("url", "")

        block = f"[{i}] Tiêu đề: {title}\n"
        block += f"    Tác giả: {authors}\n"
        block += f"    Năm xuất bản: {year}\n"
        if subjects:
            block += f"    Chủ đề: {subjects}\n"
        if url:
            block += f"    URL: {url}\n"
        
        source_type = "External (International Academic)" if is_external else f"Local Library ({', '.join(doc.get('sources', ['N/A']))})"
        block += f"    Nguồn: {source_type}\n"

        if abstract:
            block += f"    Tóm tắt: {abstract[:250]}...\n"
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
1. PHÂN LOẠI TÀI LIỆU:
   - "Local Library Documents" là tài liệu chính thức có trong hệ thống thư viện nội bộ.
   - "External Academic References" là các tài liệu tham khảo từ nguồn quốc tế (Semantic Scholar, arXiv).
2. CẤU TRÚC PHẢN HỒI (BẮT BUỘC):
   - Trình bày câu trả lời theo các phần rõ ràng:
     - **Giải thích/Trả lời**: Nội dung kiến thức hoặc câu trả lời trực tiếp.
     - **Tài liệu chính**: Liệt kê từ 1 đến 5 tài liệu Local (nội bộ) phù hợp nhất.
     - **Tài liệu liên quan**: Liệt kê từ 1 đến 3 tài liệu bổ trợ (ưu tiên từ External References).
3. LOGIC CHỌN TÀI LIỆU:
   - Bạn PHẢI đảm bảo phần "Tài liệu chính" có từ 1-5 tài liệu nội bộ nếu tìm thấy.
   - Bạn PHẢI đảm bảo phần "Tài liệu liên quan" có từ 1-3 tài liệu bên ngoài (External) hoặc tài liệu nội bộ bổ trợ.
4. ĐỘ LIÊN QUAN (QUAN TRỌNG): 
   - Chỉ sử dụng các tài liệu liên quan TRỰC TIẾP đến chủ đề người dùng hỏi.
   - Nếu tài liệu trong context không liên quan, hãy bỏ qua chúng hoàn toàn.
   - Luôn cố gắng cung cấp ít nhất 1 tài liệu bên ngoài nếu có trong context để mở rộng góc nhìn.
5. TRÍCH DẪN & LIÊN KẾT (BẮT BUỘC):
   - Khi nhắc đến tài liệu Local, BẮT BUỘC cung cấp link ở dạng: [Tên tài liệu](/document/ID).
   - Khi nhắc đến tài liệu External, BẮT BUỘC cung cấp link URL ở dạng: [Tên tài liệu](URL).
   - Tuyệt đối không bịa đặt tên sách hoặc link URL không có trong context.
   - Mỗi tài liệu bạn đề cử PHẢI đi kèm với một đường link tương ứng.
6. PHONG CÁCH: Trả lời bằng Tiếng Việt, học thuật, chuyên nghiệp.
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
            model="gemini-2.5-flash",



            contents=prompt,
            config={
                'temperature': 0.3,
                'max_output_tokens': 2048, # Tăng giới hạn token
            }
        )
        return response.text.strip()
    except Exception as e:
        if "429" in str(e):
            print(f"[LLM] Gemini Rate Limit hit! (429 Too Many Requests)")
        else:
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

Ví dụ:
- Câu truy vấn: "biến đổi khí hậu" -> Keywords: "climate change"
- Câu truy vấn: "trí tuệ nhân tạo" -> Keywords: "artificial intelligence"
- Câu truy vấn: "kinh tế học vĩ mô" -> Keywords: "macroeconomics"

Câu truy vấn: {query}
Keywords (English only):"""

    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={'temperature': 0.0}
        )
        translated = response.text.strip()
        # Loại bỏ các ký tự rác nếu có
        translated = re.sub(r'["\']', '', translated)
        return translated
    except:
        return query # Fallback về query gốc nếu lỗi

        return query # Fallback về query gốc nếu lỗi

