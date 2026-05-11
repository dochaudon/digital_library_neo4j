import re

from models.qa_model import (
    get_author_by_title,
    get_year_by_title,
    get_subject_by_title,
    get_publisher_by_title,
    get_university_by_title,
    get_abstract_by_title,
    get_keyword_by_title,
    get_related_by_title
)

from services.search_service import search_documents
from services.llm_service import (
    call_gemini,
    build_rag_prompt,
    is_out_of_scope,
    is_academic_intent,
    get_out_of_scope_response,
    build_context_from_docs
)
from services.external_search_service import get_external_academic_papers




# =========================
# INTENT DETECTION (SMART)

# =========================
def detect_intent(question):
    q = (question or "").lower()

    # factual (graph)
    if any(x in q for x in ["ai viết", "tác giả", "người viết", "viết bởi"]):
        return "author"

    if any(x in q for x in ["xuất bản", "nhà xuất bản", "nxb"]):
        return "publisher"

    if any(x in q for x in ["năm", "năm nào", "vào năm"]):
        return "year"

    if any(x in q for x in ["chủ đề", "lĩnh vực", "về chủ đề", "về lĩnh vực"]):
        return "subject"

    if any(x in q for x in ["trường", "đại học", "học viện"]):
        return "university"

    if any(x in q for x in ["bao nhiêu", "số lượng", "có mấy"]):
        return "count"


    # semantic
    if any(x in q for x in ["giống", "liên quan", "tương tự", "cùng chủ đề", "tương đồng"]):
        return "similar"

    if any(x in q for x in ["tóm tắt", "nội dung"]):
        return "summary"

    if "từ khóa" in q:
        return "keyword"

    return "search"


# =========================
# EXTRACT TITLE

# =========================
def get_title_from_history(history):
    if not history or len(history) <= 1:
        return ""
    
    import re

    for msg in reversed(history[:-1]):
        content = msg.get("content", "")
        role = msg.get("role")
        
        # 1. Từ câu trả lời của Assistant — Độ chính xác cao nhất
        if role == "assistant":
            # Pattern 1: **"Tên sách"** (template với markdown bold + quotes)
            match = re.search(r'\*\*"([^"]+)"\*\*', content)
            if match:
                return match.group(1)

            # Pattern 2: "Tên sách" (ngoặc kép thường)
            match = re.search(r'"([^"]{10,})"', content)
            if match:
                return match.group(1)

            # Pattern 3: Tài liệu ... thuộc/được/xuất bản (Gemini không dùng quotes)
            match = re.search(
                r'[Tt]ài liệu\s+"?([^""\n]{10,})"?\s+(?:thuộc|được|xuất bản|có từ khóa|viết bởi)',
                content
            )
            if match:
                return match.group(1).strip()

            # Pattern 4: Danh sách gợi ý "- **Tên sách**"
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('- **') and line.endswith('**'):
                    candidate = line[4:-2].strip()
                    if len(candidate) > 5:
                        return candidate
                elif line.startswith('- ') and len(line) > 7:
                    candidate = line[2:].strip()
                    # Bỏ qua dòng là giải thích ngắn
                    if len(candidate) > 15 and not candidate.startswith('_'):
                        return candidate

        # 2. Từ câu hỏi cũ của User (Dự phòng) — lấy phần sau "của"
        elif role == "user":
            q = content
            # Chỉ lấy từ user message có chứa tên sách thực sự (>20 ký tự sau "của")
            if "của" in q.lower():
                after = q.split("của")[-1].strip()
                # Loại bỏ các hư từ cuối
                after = re.sub(r'\s*(là gì|là ai|như thế nào|vậy|nhỉ|hả|ạ|\?)+\s*$', '', after, flags=re.IGNORECASE).strip()
                if len(after) > 10:
                    return after
            
    return ""

import re

def normalize_input(text):
    text = text.lower()
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    # Dọn dẹp dấu câu ở đầu và cuối (nhưng giữ lại dấu : ở giữa)
    text = re.sub(r'^[?!.\s]+|[?!.\s]+$', '', text)
    return text

def remove_stopwords(text):
    tail_words = [
        r"là gì", r"là ai", r"viết năm nào", r"xuất bản năm nào", 
        r"năm nào", r"ở đâu", r"như thế nào", r"thế nào", 
        r"vậy", r"nhỉ", r"không", r"hả", r"ạ"
    ]
    
    changed = True
    while changed:
        changed = False
        new_text = re.sub(r'[?\.!\s]+$', '', text)
        if new_text != text:
            text = new_text
            changed = True
            
        for w in tail_words:
            pattern = rf'\b{w}$'
            if re.search(pattern, text):
                text = re.sub(pattern, '', text).strip()
                changed = True
                
    return text

def extract_core_title(text, original_q, history):
    extracted = text

    prefixes = [
        "của cuốn sách", "của tài liệu", "của bài báo", "của luận văn", "của cuốn", "của sách",
        "về cuốn sách", "về tài liệu", "về bài báo", "về luận văn", "về cuốn", "về sách",
        "của", "về"
    ]
    
    for prefix in prefixes:
        pattern = rf'\b{prefix}\b'
        match = re.search(pattern, text)
        if match:
            extracted = text[match.end():].strip()
            # Dọn dẹp dấu hai chấm, gạch ngang thừa ở ĐẦU chuỗi sau khi cắt
            # (VD: cắt xong còn lại ": Góc nhìn đa chiều" -> "Góc nhìn đa chiều")
            extracted = re.sub(r'^[:\-\s]+', '', extracted).strip()
            break

    context_keywords = ["trên", "đó", "này", "vừa rồi", "ấy", "nó", "đầu tiên", "quyển đầu"]
    has_context = False
    for k in context_keywords:
        if re.search(rf'\b{k}\b', extracted) or re.search(rf'\b{k}\b', original_q):
            has_context = True
            break
            
    if has_context:
        prev_title = get_title_from_history(history)
        if prev_title:
            return prev_title

    return extracted

def extract_title(question, history=None):
    # Bước 1: Chuẩn hóa input
    normalized = normalize_input(question)
    
    # Bước 2: Loại bỏ từ vô nghĩa ở cuối
    cleaned = remove_stopwords(normalized)
    
    # Bước 3: Tách lấy core title
    return extract_core_title(cleaned, normalized, history)


# =========================
# PARSE FILTER (SMART)

# =========================
def parse_filters(question):
    q = question.lower()
    filters = {}

    if "luận văn" in q:
        filters["doc_type"] = "Thesis"
    elif "bài báo" in q:
        filters["doc_type"] = "Article"
    elif "sách" in q:
        filters["doc_type"] = "Book"

    # year
    year_match = re.search(r'\b(19|20)\d{2}\b', q)
    if year_match:
        filters["year"] = int(year_match.group())

    # subject mapping
    from services.search_service import SUBJECT_MAPPINGS
    for key, val in SUBJECT_MAPPINGS.items():
        if key in q:
            filters["subject"] = val

    return filters



# =========================
# APPLY HIGHLIGHT

# =========================
def apply_highlights(docs, query):
    """Chèn thẻ <mark> vào title của tài liệu khớp với query."""
    if not query or not docs:
        return docs

    keywords = [k.strip() for k in query.lower().split() if len(k.strip()) > 1]

    for doc in docs:
        title = doc.get("title", "")
        highlighted = title
        for kw in keywords:
            pattern = re.compile(rf'({re.escape(kw)})', re.IGNORECASE)
            highlighted = pattern.sub(r'<mark>\1</mark>', highlighted)
        doc["title_highlighted"] = highlighted

    return docs


# =========================
# SMART ANSWER BUILDER

# =========================
def build_answer(answer_text, explanation=None, suggestion_docs=None):
    """Tổng hợp câu trả lời gồm: Trả lời + Giải thích + Gợi ý."""
    parts = [answer_text]

    if explanation:
        parts.append(f"\n_{explanation}_")

    if suggestion_docs and len(suggestion_docs) > 0:
        titles = [f'- **{d["title"]}**' for d in suggestion_docs[:3]]
        parts.append("\n\nBạn có thể xem thêm:\n" + "\n".join(titles))


    return "\n".join(parts)


# =========================
# FORMAT ANSWER (NLG)

# =========================
def format_smart_answer(results, intent, query=""):
    """Tạo câu trả lời tự nhiên, có tóm tắt và gợi ý."""
    if not results:
        return build_answer(
            "Mình chưa tìm thấy tài liệu phù hợp trong hệ thống.",
            explanation="Hãy thử tìm kiếm với từ khóa khác hoặc đặt câu hỏi cụ thể hơn nhé."
        )

    total = len(results)
    top3 = results[:3]
    rest = results[3:6]

    # Tóm tắt số lượng
    if query:
        summary = f'Mình tìm thấy **{total} tài liệu** liên quan đến "{query}".'
    else:
        summary = f'Mình tìm thấy **{total} tài liệu** phù hợp.'

    top_titles = [f'- **{d["title"]}**' + (f' ({d["year"]})' if d.get("year") else "") for d in top3]
    answer_text = summary + "\n\nGợi ý nổi bật:\n" + "\n".join(top_titles)


    # Explanation (giải thích)
    explanation_map = {
        "search": "Kết quả được kết hợp từ Fulltext Search và Vector Search để đảm bảo độ chính xác.",
        "similar": "Các tài liệu trên có cùng chủ đề hoặc từ khóa với tài liệu bạn đang tham chiếu.",
        "count": "Tổng số tài liệu trong hệ thống khớp với bộ lọc bạn yêu cầu.",
    }
    explanation = explanation_map.get(intent, "Kết quả được xếp hạng theo mức độ liên quan.")

    # Gợi ý bổ sung (nếu có >3 kết quả)
    suggestion = rest if rest else None

    return build_answer(answer_text, explanation, suggestion)


# =========================
# MAIN QA (RAG + LLM)

# =========================
def get_qa_response(question, history=None):

    if not question:
        return {"answer": "Bạn hãy nhập câu hỏi nhé.", "documents": []}

    # --- DOMAIN GUARD (HYBRID) ---
    if is_out_of_scope(question) or not is_academic_intent(question):
        return {

            "answer": get_out_of_scope_response(),
            "intent": "out_of_scope",
            "documents": []
        }


    intent = detect_intent(question)
    filters = parse_filters(question)
    title = extract_title(question, history)

    # -------------------------------------------------------
    # BRANCH A: QA Intent → Neo4j Exact + Gemini NLG
    # -------------------------------------------------------

    # --- AUTHOR ---
    if intent == "author":
        result = get_author_by_title(title)
        if result:
            r = result[0]
            data_str = f"Tác giả: {', '.join(r.get('authors', []))}"
            doc_ctx = [{"title": r.get("title"), "authors": r.get("authors", [])}]
            prompt = build_rag_prompt(question, local_docs=doc_ctx, history=history, data=data_str)

            llm_answer = call_gemini(prompt)
            answer = llm_answer or build_answer(
                f'Tài liệu **"{r["title"]}"** được viết bởi **{", ".join(r.get("authors", []))}**.',

                explanation="Thông tin tác giả được trích xuất trực tiếp từ cơ sở dữ liệu thư viện."
            )
            return {"answer": answer, "intent": intent, "documents": []}

    # --- PUBLISHER ---
    if intent == "publisher":
        result = get_publisher_by_title(title)
        if result and result[0].get("publisher"):
            r = result[0]
            data_str = f"Nhà xuất bản: {r['publisher']}"
            doc_ctx = [{"title": r.get("title")}]
            prompt = build_rag_prompt(question, local_docs=doc_ctx, history=history, data=data_str)

            llm_answer = call_gemini(prompt)
            answer = llm_answer or build_answer(
                f'Tài liệu **"{r["title"]}"** được xuất bản bởi **{r["publisher"]}**.',

            )
            return {"answer": answer, "intent": intent, "documents": []}

    # --- YEAR ---
    if intent == "year":
        result = get_year_by_title(title)
        if result and result[0].get("year"):
            r = result[0]
            data_str = f"Năm xuất bản: {r['year']}"
            doc_ctx = [{"title": r.get("title"), "year": r.get("year")}]
            prompt = build_rag_prompt(question, local_docs=doc_ctx, history=history, data=data_str)

            llm_answer = call_gemini(prompt)
            answer = llm_answer or build_answer(f'Tài liệu **"{r["title"]}"** xuất bản năm **{r["year"]}**.')

            return {"answer": answer, "intent": intent, "documents": []}

    # --- SUBJECT ---
    if intent == "subject":
        result = get_subject_by_title(title)
        if result and result[0].get("subjects"):
            r = result[0]
            data_str = f"Chủ đề: {', '.join(r['subjects'])}"
            doc_ctx = [{"title": r.get("title"), "subjects": r.get("subjects")}]
            prompt = build_rag_prompt(question, local_docs=doc_ctx, history=history, data=data_str)

            llm_answer = call_gemini(prompt)
            answer = llm_answer or build_answer(
                f'Tài liệu **"{r["title"]}"** thuộc các chủ đề: **{", ".join(r["subjects"])}**.',

                explanation="Chủ đề được phân loại trong đồ thị kiến thức của hệ thống."
            )
            return {"answer": answer, "intent": intent, "documents": []}

    # --- UNIVERSITY ---
    if intent == "university":
        result = get_university_by_title(title)
        if result and result[0].get("university"):
            r = result[0]
            data_str = f"Trường đại học: {r['university']}"
            doc_ctx = [{"title": r.get("title")}]
            prompt = build_rag_prompt(question, local_docs=doc_ctx, history=history, data=data_str)

            llm_answer = call_gemini(prompt)
            answer = llm_answer or build_answer(f'Luận văn **"{r["title"]}"** được thực hiện tại **{r["university"]}**.')

            return {"answer": answer, "intent": intent, "documents": []}

    # --- SUMMARY ---
    if intent == "summary":
        result = get_abstract_by_title(title)
        if result:
            r = result[0]
            abstract = r.get("abstract", "")
            if abstract:
                data_str = f"Tóm tắt: {abstract}"
                doc_ctx = [{"title": r.get("title"), "abstract": abstract}]
                prompt = build_rag_prompt(
                    f"Hãy tóm tắt nội dung của tài liệu này thành 2-3 câu súc tích bằng Tiếng Việt: {question}",
                    local_docs=doc_ctx, history=history, data=data_str
                )

                llm_answer = call_gemini(prompt)
                answer = llm_answer or build_answer(
                    f'Tóm tắt tài liệu "{r["title"]}":\n\n{abstract}',

                    explanation="Đây là phần tóm tắt nội dung (abstract) được lưu trữ trong hệ thống."
                )
            else:
                answer = build_answer(f'Tài liệu **"{r["title"]}"** hiện chưa có thông tin tóm tắt.')

            return {"answer": answer, "intent": intent, "documents": []}

    # --- KEYWORD ---
    if intent == "keyword":
        result = get_keyword_by_title(title)
        if result and result[0].get("keywords"):
            r = result[0]
            data_str = f"Từ khóa: {', '.join(r['keywords'])}"
            doc_ctx = [{"title": r.get("title"), "keywords": r.get("keywords")}]
            prompt = build_rag_prompt(question, local_docs=doc_ctx, history=history, data=data_str)

            llm_answer = call_gemini(prompt)
            answer = llm_answer or build_answer(f'Từ khóa: **{", ".join(r["keywords"])}**.')

            return {"answer": answer, "intent": intent, "documents": []}

    # --- SIMILAR ---
    if intent == "similar":
        results = get_related_by_title(title)
        if results:
            highlighted_results = apply_highlights(results, title)
            prompt = build_rag_prompt(question, local_docs=results[:5], history=history)

            llm_answer = call_gemini(prompt)
            answer = llm_answer or build_answer(
                f'Tìm thấy **{len(results)} tài liệu** tương đồng với **"{title}"**.',

                suggestion_docs=results[3:]
            )
            return {"answer": answer, "intent": intent, "documents": highlighted_results[:6]}

    # --- COUNT ---
    if intent == "count":
        results = search_documents("", filters, 100)
        answer = build_answer(f'Hệ thống có khoảng **{len(results)} tài liệu** phù hợp.')

        return {"answer": answer, "intent": intent, "documents": results[:5]}

    # --- BRANCH B: Search Intent → Hybrid Search + External + RAG ---
    results = search_documents(question, filters, 10)
    top_score = results[0].get("score", 0) if results else 0
    print(f"[QA] Local results: {len(results)}, Top score: {top_score}")

    external_results = []
    # TRIGGER EXTERNAL SEARCH
    if len(results) <= 3 or top_score < 0.45:

        print(f"[QA] Insufficient local data. Triggering external retrieval...")
        external_results = get_external_academic_papers(question, limit=5)

        print(f"[QA] External papers fetched: {len(external_results)}")

    # RAG: feed cả local và external vào Gemini
    prompt = build_rag_prompt(
        question, 
        local_docs=results[:5], 
        external_docs=external_results, 
        history=history
    )
    
    llm_answer = call_gemini(prompt)

    if llm_answer:
        answer = llm_answer
    else:
        # Fallback answer if LLM fails
        answer = format_smart_answer(results + external_results, intent, query=title or question)

    # Combine for UI
    all_docs = results + external_results
    
    # Highlight keywords trong title của documents
    all_docs = apply_highlights(all_docs, question)

    return {
        "answer": answer,
        "intent": intent,
        "documents": all_docs
    }