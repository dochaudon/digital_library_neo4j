import os
import re
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

from functools import lru_cache

@lru_cache(maxsize=1024)
def classify_query_intent(question: str) -> str:
    q = question.lower().strip()
    if not q or len(q) < 2:
        return "OUT_OF_SCOPE"

    # 1. FAST PATH (0ms): Lời chào xã giao hoặc lời cảm ơn đơn giản
    chitchat_keywords = ["chào", "hello", "hi", "cảm ơn", "cám ơn", "thank", "tạm biệt", "bye", "ok", "oke", "alo"]
    if q in chitchat_keywords or any(q == ck for ck in chitchat_keywords):
        return "GENERAL_ACADEMIC"

    # 2. LLM CLASS-BASED INTENT DETECTION
    prompt = f"""Bạn là một trợ lý phân loại ý định người dùng (User Intent Classifier) cho một hệ thống Thư viện số học thuật.
Nhiệm vụ của bạn là phân loại câu hỏi/truy vấn của người dùng thành 1 trong 4 nhãn duy nhất: OUT_OF_SCOPE, GENERAL_ACADEMIC, LIBRARY_SEARCH, hoặc HYBRID.

Quy tắc phân loại:
1. OUT_OF_SCOPE:
   - Câu hỏi đời sống thường nhật không mang tính nghiên cứu/học thuật (thời tiết, giá vàng).
   - Giải trí, thể thao, bóng đá, showbiz, đời tư nghệ sĩ, nấu ăn, du lịch.

2. GENERAL_ACADEMIC:
   - Hỏi đáp học thuật, giải thích khái niệm khoa học, định nghĩa lý thuyết, công thức toán học (ví dụ: "Python là gì?", "Thuật toán DFS hoạt động thế nào?", "Đạo hàm là gì?").
   - Hỏi đáp về các nhân vật lịch sử, danh nhân văn hóa, sự kiện lịch sử (ví dụ: "Napoléon là ai?").
   - Các câu giao tiếp lịch sự cơ bản (ví dụ: "chào bạn", "hello").
   *Lưu ý: Nếu câu hỏi KHÔNG nhắc đến chữ sách, tài liệu, bài báo, luận văn... thì xếp vào nhóm này.

3. LIBRARY_SEARCH:
   - Truy vấn tìm kiếm tài liệu thuần túy trong thư viện (ví dụ: "Tìm sách về AI", "Cho tôi luận văn về Blockchain", "Có sách nào của tác giả Nguyễn Văn A không?").
   - Tra cứu metadata (năm xuất bản, tác giả, nhà xuất bản).

4. HYBRID:
   - Câu hỏi vừa yêu cầu giải thích kiến thức học thuật, vừa yêu cầu tìm/gợi ý tài liệu (ví dụ: "Giải thích Machine Learning và cho tôi tài liệu liên quan", "Transformer là gì, có sách nào nói về nó không?").

Hãy phân loại câu hỏi sau của người dùng:
"{question}"

Chỉ trả về đúng 1 trong 4 nhãn (OUT_OF_SCOPE, GENERAL_ACADEMIC, LIBRARY_SEARCH, HYBRID), tuyệt đối không viết thêm lời giải thích."""

    try:
        response_text = call_gemini(prompt)
        if response_text:
            classification = response_text.strip().upper()
            for label in ["OUT_OF_SCOPE", "GENERAL_ACADEMIC", "LIBRARY_SEARCH", "HYBRID"]:
                if label in classification:
                    print(f"[Guardrail] LLM classified query '{question}' as {label}")
                    return label
    except Exception as e:
        print(f"[Guardrail] LLM check failed: {e}. Falling back to smart heuristic.")
        
    # 4. FALLBACK: Nếu gọi LLM lỗi, fallback về HYBRID để đảm bảo không miss case
    for kw in _OUT_OF_SCOPE_KEYWORDS:
        if kw in q:
            return "OUT_OF_SCOPE"
    return "HYBRID"

def is_out_of_scope(question: str) -> bool:
    """Tương thích ngược: Kiểm tra xem có bị out of scope không."""
    return classify_query_intent(question) == "OUT_OF_SCOPE"

def is_academic_intent(question: str) -> bool:
    """Tương thích ngược: Kiểm tra xem có thuộc học thuật không."""
    return classify_query_intent(question) != "OUT_OF_SCOPE"



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
3. LOGIC CHỌN TÀI LIỆU VÀ KIẾN THỨC:
   - Nếu Context có tài liệu liên quan, hãy ưu tiên sử dụng và trích dẫn chúng.
   - NẾU Context KHÔNG CÓ tài liệu liên quan hoặc KHÔNG ĐỦ THÔNG TIN, nhưng câu hỏi mang tính học thuật (như giải thích khái niệm, công thức toán học, nhân vật lịch sử, v.v.), BẠN ĐƯỢC PHÉP SỬ DỤNG KIẾN THỨC SẴN CÓ CỦA MÌNH (General Knowledge) để giảng giải và trả lời chi tiết cho người dùng.
   - Bạn PHẢI đảm bảo phần "Tài liệu chính" có từ 1-5 tài liệu nội bộ (nếu tìm thấy trong Context).
   - Bạn PHẢI đảm bảo phần "Tài liệu liên quan" có từ 1-3 tài liệu bên ngoài (nếu tìm thấy trong Context).
4. ĐỘ LIÊN QUAN (QUAN TRỌNG): 
   - Chỉ sử dụng các tài liệu trong Context nếu chúng thực sự liên quan.
   - Nếu tài liệu trong Context không liên quan, hãy bỏ qua chúng hoàn toàn và chỉ dùng kiến thức của bạn để trả lời phần "Giải thích/Trả lời".
5. TRÍCH DẪN & LIÊN KẾT (BẮT BUỘC):
   - Khi nhắc đến tài liệu Local, BẮT BUỘC cung cấp link ở dạng: [Tên tài liệu](/document/ID).
   - Khi nhắc đến tài liệu External, BẮT BUỘC cung cấp link URL ở dạng: [Tên tài liệu](URL).
   - Tuyệt đối KHÔNG BỊA ĐẶT tên sách, tài liệu, tác giả hoặc link URL không có trong Context. Nếu dùng kiến thức tự thân, không được bịa ra nguồn tài liệu.
6. PHONG CÁCH: Trả lời bằng Tiếng Việt, học thuật, chuyên nghiệp, rõ ràng và dễ hiểu.
"""



    prompt_parts = [system_prompt]

    if history_text:
        prompt_parts.append(f"\nLỊCH SỬ HỘI THOẠI GẦN ĐÂY:\n{history_text}\n---")

    prompt_parts.append(f"\nCONTEXT ĐƯỢC CUNG CẤP:\n{local_context}\n{external_context}\n{factual_block}")
    prompt_parts.append(f"\nCÂU HỎI HIỆN TẠI: {question}")
    prompt_parts.append("\nTRẢ LỜI (Grounded Academic Response):")

    return "\n".join(prompt_parts)

def build_general_knowledge_prompt(question: str, history: list = None) -> str:
    """Xây dựng prompt cho câu hỏi học thuật chung (Không dùng Neo4j Context)."""
    history_text = build_history_text(history or [])
    
    system_prompt = """Bạn là trợ lý học thuật chuyên sâu (Hybrid Academic Assistant) của thư viện số.

NGUYÊN TẮC TRẢ LỜI (GENERAL ACADEMIC MODE):
1. NGỮ CẢNH: Người dùng đang hỏi một câu hỏi mang tính học thuật tổng quát (giải thích khái niệm, lý thuyết, thuật toán, danh nhân lịch sử, toán học...).
2. NHIỆM VỤ: Hãy sử dụng toàn bộ kiến thức nội tại (Pretrained Knowledge) của bạn để trả lời một cách chi tiết, dễ hiểu, và chính xác nhất. Không cần xin lỗi vì thiếu tài liệu.
3. PHONG CÁCH: Trả lời bằng Tiếng Việt, văn phong học thuật, chuyên nghiệp, rõ ràng. Có thể dùng markdown để định dạng (in đậm, danh sách, khối code) cho dễ đọc.
"""
    prompt_parts = [system_prompt]
    if history_text:
        prompt_parts.append(f"\nLỊCH SỬ HỘI THOẠI GẦN ĐÂY:\n{history_text}\n---")

    prompt_parts.append(f"\nCÂU HỎI HIỆN TẠI: {question}")
    prompt_parts.append("\nTRẢ LỜI (General Academic Response):")
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


