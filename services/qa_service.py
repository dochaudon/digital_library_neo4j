import re

from models.qa_model import (
    get_author_by_title,
    get_year_by_title,
    get_subject_by_title,
    get_publisher_by_title,
    get_university_by_title,
    get_abstract_by_title,
    get_keyword_by_title,
    get_related_by_title,
    get_docs_by_subject_with_related
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

DEBUG_QA = True

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        try:
            print(msg.encode('ascii', 'ignore').decode('ascii'))
        except:
            pass

# =========================
# INTENT DETECTION
# =========================
def detect_intent(question):
    q = (question or "").lower()
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
    if any(x in q for x in ["giống", "liên quan", "tương tự", "cùng chủ đề", "tương đồng"]):
        return "similar"
    if any(x in q for x in ["tóm tắt", "nội dung"]):
        return "summary"
    if "từ khóa" in q:
        return "keyword"
    return "search"

# =========================
# EXTRACTION HELPERS
# =========================
def get_title_from_history(history):
    if not history or len(history) <= 1:
        return ""
    for msg in reversed(history[:-1]):
        content = msg.get("content", "")
        role = msg.get("role")
        if role == "assistant":
            match = re.search(r'\*\*"([^"]+)"\*\*', content)
            if match: return match.group(1)
            match = re.search(r'"([^"]{10,})"', content)
            if match: return match.group(1)
        elif role == "user":
            if "của" in content.lower():
                after = content.split("của")[-1].strip()
                after = re.sub(r'\s*(là gì|là ai|như thế nào|vậy|nhỉ|hả|ạ|\?)+\s*$', '', after, flags=re.IGNORECASE).strip()
                if len(after) > 10: return after
    return ""

def normalize_input(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
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
    prefixes = ["của cuốn sách", "của tài liệu", "của bài báo", "của luận văn", "của cuốn", "của sách", "của", "về"]
    for prefix in prefixes:
        pattern = rf'\b{prefix}\b'
        match = re.search(pattern, text)
        if match:
            extracted = text[match.end():].strip()
            extracted = re.sub(r'^[:\-\s]+', '', extracted).strip()
            break
    context_keywords = ["trên", "đó", "này", "vừa rồi", "ấy", "nó", "đầu tiên", "quyển đầu"]
    if any(re.search(rf'\b{k}\b', extracted) or re.search(rf'\b{k}\b', original_q) for k in context_keywords):
        prev_title = get_title_from_history(history)
        if prev_title: return prev_title
    return extracted

def extract_title(question, history=None):
    normalized = normalize_input(question)
    cleaned = remove_stopwords(normalized)
    return extract_core_title(cleaned, normalized, history)

def parse_filters(question):
    q = question.lower()
    filters = {}
    if "luận văn" in q: filters["doc_type"] = "Thesis"
    elif "bài báo" in q: filters["doc_type"] = "Article"
    elif "sách" in q: filters["doc_type"] = "Book"
    year_match = re.search(r'\b(19|20)\d{2}\b', q)
    if year_match: filters["year"] = int(year_match.group())
    from services.search_service import SUBJECT_ALIASES
    for official_name, aliases in SUBJECT_ALIASES.items():
        if any(alias in q for alias in aliases):
            filters["subject"] = official_name
            break
    return filters

def apply_highlights(docs, query):
    if not query or not docs: return docs
    keywords = [k.strip() for k in query.lower().split() if len(k.strip()) > 1]
    for doc in docs:
        title = doc.get("title", "")
        highlighted = title
        for kw in keywords:
            pattern = re.compile(rf'({re.escape(kw)})', re.IGNORECASE)
            highlighted = pattern.sub(r'<mark>\1</mark>', highlighted)
        doc["title_highlighted"] = highlighted
    return docs

def build_answer(answer_text, explanation=None, local_suggestions=None, external_suggestions=None):
    parts = [answer_text]
    if explanation: parts.append(f"\n_{explanation}_")
    if local_suggestions:
        titles = [f'- **[{d["title"]}](/document/{d["id"]})**' for d in local_suggestions[:5]]
        parts.append("\n\n**Tài liệu từ Thư viện:**\n" + "\n".join(titles))
    if external_suggestions:
        titles = [f'- **[{d["title"]}]({d.get("url", "#")})**' for d in external_suggestions[:3]]
        parts.append("\n\n**Tài liệu tham khảo ngoài:**\n" + "\n".join(titles))
    return "\n".join(parts)

def format_smart_answer(results, intent, query=""):
    if not results:
        return build_answer("Mình chưa tìm thấy tài liệu phù hợp.", explanation="Hãy thử từ khóa khác nhé.")
    total = len(results)
    top_titles = [f'- **{d["title"]}**' + (f' ({d["year"]})' if d.get("year") else "") for d in results[:3]]
    answer_text = (f'Tìm thấy **{total} tài liệu** liên quan đến "{query}".' if query else f'Tìm thấy **{total} tài liệu**.') + "\n\nGợi ý:\n" + "\n".join(top_titles)
    return build_answer(answer_text, local_suggestions=results)

# =========================
# MAIN QA LOGIC
# =========================
def get_qa_response(question, history=None, filters=None):
    try:
        return _get_qa_response_impl(question, history, filters)
    except Exception as e:
        safe_print(f"!!! [QA ERROR] !!!: {e}")
        import traceback
        traceback.print_exc()
        return {"answer": "Lỗi hệ thống, vui lòng thử lại.", "documents": []}

def _get_qa_response_impl(question, history=None, filters=None):
    filters = filters or {}
    history = history or []
    intent = detect_intent(question)
    title = extract_title(question) or get_title_from_history(history)

    # Subject Relationship Expansion
    from services.search_service import expand_subject_relationship
    expansion = expand_subject_relationship(question)
    main_subject = None
    related_subjects = []
    metadata_context = ""
    if expansion:
        main_subject = expansion["main_subject"]
        related_subjects = expansion["related_subjects"]
        metadata_context += f"Detected Main Subject in Library Knowledge Graph: {main_subject}\n"
        metadata_context += f"Related Subjects in Library Knowledge Graph (traversed via RELATED_TO): {', '.join(related_subjects)}\n"

    if DEBUG_QA:
        safe_print(f"[QA DEBUG] Question: {question} | Intent: {intent} | Title: {title}")

    if is_out_of_scope(question) or not is_academic_intent(question):
        return {"answer": get_out_of_scope_response(), "intent": "out_of_scope", "documents": []}

    # BRANCH A: Factual (Early Return)
    if intent == "author":
        res = get_author_by_title(title)
        if res:
            r = res[0]
            authors = r.get('authors', [])
            ans = build_answer(f'Tài liệu **"{r["title"]}"** được viết bởi **{", ".join(authors)}**.')
            return {
                "answer": ans,
                "intent": intent,
                "documents": res[:1],
                "main_subject": main_subject,
                "related_subjects": related_subjects
            }
    
    if intent == "publisher":
        res = get_publisher_by_title(title)
        if res and res[0].get("publisher"):
            ans = build_answer(f'Tài liệu **"{res[0]["title"]}"** xuất bản bởi **{res[0]["publisher"]}**.')
            return {
                "answer": ans,
                "intent": intent,
                "documents": res[:1],
                "main_subject": main_subject,
                "related_subjects": related_subjects
            }

    if intent == "year":
        res = get_year_by_title(title)
        if res and res[0].get("year"):
            ans = build_answer(f'Tài liệu **"{res[0]["title"]}"** xuất bản năm **{res[0]["year"]}**.')
            return {
                "answer": ans,
                "intent": intent,
                "documents": res[:1],
                "main_subject": main_subject,
                "related_subjects": related_subjects
            }

    if intent == "subject":
        # Case 1: đã detect được chủ đề từ Knowledge Graph → tìm trực tiếp bằng graph
        if expansion and main_subject:
            all_detected = expansion.get("all_detected_subjects", [main_subject])
            primary_docs, secondary_docs = get_docs_by_subject_with_related(
                main_subjects=all_detected,
                related_subjects=related_subjects,
                limit=10
            )
            total = len(primary_docs) + len(secondary_docs)
            if primary_docs or secondary_docs:
                related_names = ", ".join(related_subjects[:5]) if related_subjects else "không có"
                ans_lines = [
                    f'Tìm thấy **{len(primary_docs)} tài liệu** thuộc chủ đề **"{main_subject}"**'
                    + (f' và **{len(secondary_docs)} tài liệu** từ các chủ đề liên quan.' if secondary_docs else '.')
                ]
                if related_subjects:
                    ans_lines.append(f'\n_Các chủ đề liên quan đã duyệt: {related_names}_')
                all_docs = primary_docs + secondary_docs
                titles = [f'- **[{d["title"]}](/document/{d["id"]})**' + (f' ({d.get("year")})' if d.get('year') else '') for d in all_docs[:5]]
                ans_lines.append('\n\n**Tài liệu từ Thư viện:**\n' + '\n'.join(titles))
                return {
                    "answer": '\n'.join(ans_lines),
                    "intent": intent,
                    "documents": all_docs,
                    "local_documents": all_docs,
                    "external_documents": [],
                    "main_subject": main_subject,
                    "related_subjects": related_subjects
                }
        # Case 2: không detect được chủ đề → hỏi về tiêu đề cụ thể
        else:
            res = get_subject_by_title(title)
            if res and res[0].get("subjects"):
                ans = build_answer(f'Tài liệu **"{res[0]["title"]}"** thuộc các chủ đề: **{", ".join(res[0]["subjects"])}**.')
                return {
                    "answer": ans,
                    "intent": intent,
                    "documents": res[:1],
                    "main_subject": main_subject,
                    "related_subjects": related_subjects
                }

    if intent == "university":
        res = get_university_by_title(title)
        if res and res[0].get("university"):
            ans = build_answer(f'Luận văn **"{res[0]["title"]}"** được thực hiện tại **{res[0]["university"]}**.')
            return {
                "answer": ans,
                "intent": intent,
                "documents": res[:1],
                "main_subject": main_subject,
                "related_subjects": related_subjects
            }

    if intent == "summary":
        res = get_abstract_by_title(title)
        if res and res[0].get("abstract"):
            prompt = build_rag_prompt(f"Tóm tắt: {question}", local_docs=res[:1], data=f"Tóm tắt: {res[0]['abstract']}")
            ans = call_gemini(prompt) or f'Tóm tắt: {res[0]["abstract"]}'
            return {
                "answer": ans,
                "intent": intent,
                "documents": res[:1],
                "main_subject": main_subject,
                "related_subjects": related_subjects
            }

    if intent == "similar":
        res = get_related_by_title(title)
        if res:
            ans = build_answer(f'Tìm thấy **{len(res)} tài liệu** tương tự với **"{title}"**.', local_suggestions=res)
            return {
                "answer": ans,
                "intent": intent,
                "documents": res[:5],
                "main_subject": main_subject,
                "related_subjects": related_subjects
            }

    if intent == "count":
        res = search_documents("", filters, 100)
        ans = build_answer(f'Hệ thống có khoảng **{len(res)} tài liệu** phù hợp.')
        return {
            "answer": ans,
            "intent": intent,
            "documents": res[:5],
            "main_subject": main_subject,
            "related_subjects": related_subjects
        }

    # BRANCH B: Search/Recommendation
    # Nếu đã có subject filter cứng, dùng query rỗng để ưu tiên graph search chính xác
    search_query = "" if filters.get("subject") else question
    results = search_documents(search_query, filters, 10)
    top_score = results[0].get("score", 0) if results else 0
    
    external_results = []
    # ALWAYS trigger for search/recommendation to fulfill requirements
    if intent in ["search", "similar", "keyword"] or len(results) < 5 or top_score < 0.5:
        external_results = get_external_academic_papers(question, limit=5)

    prompt = build_rag_prompt(question, local_docs=results[:8], external_docs=external_results, history=history, data=metadata_context)
    answer = call_gemini(prompt) or format_smart_answer(results + external_results, intent, query=question)

    results = apply_highlights(results, question)
    external_results = apply_highlights(external_results, question)

    final_local = results[:5]
    final_external = external_results[:3]

    return {
        "answer": answer,
        "intent": intent,
        "local_documents": final_local,
        "external_documents": final_external,
        "documents": final_local + final_external,
        "main_subject": main_subject,
        "related_subjects": related_subjects
    }
