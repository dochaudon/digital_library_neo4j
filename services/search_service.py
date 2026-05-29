from database.neo4j_connection import neo4j_conn
from services.vector_search_service import vector_search
import re

FULLTEXT_INDEX = "documentFulltextIndex"

SUBJECT_ALIASES = {
    "Công nghệ thông tin": [
        "công nghệ thông tin", "information technology", "it", "cntt", "it chuyên nghiệp",
        "lập trình", "programming", "phần mềm", "software", "coder", "developer"
    ],
    "Artificial Intelligence": [
        "trí tuệ nhân tạo", "artificial intelligence", "ai", "thông minh nhân tạo"
    ],
    "Machine Learning": [
        "học máy", "machine learning", "ml"
    ],
    "Deep Learning": [
        "học sâu", "deep learning"
    ],
    "Economics": [
        "kinh tế", "economics", "economic", "economy", "kinh doanh", "quản trị kinh doanh"
    ],
    "Mathematics": [
        "toán học", "mathematics", "math", "toán"
    ],
    "Physics": [
        "vật lý", "physics", "vật lí"
    ],
    "Chemistry": [
        "hóa học", "chemistry", "hóa"
    ],
    "Biology": [
        "sinh học", "biology", "sinh"
    ],
    "Cyber Security": [
        "an ninh mạng", "cyber security", "cybersecurity", "bảo mật"
    ],
    "Data Science": [
        "khoa học dữ liệu", "data science"
    ],
    "Big data": [
        "big data", "dữ liệu lớn", "dư liệu lớn", "phân tích dữ liệu lớn", "dữ liệu khổng lồ"
    ],
    "Data mining": [
        "khai phá dữ liệu", "data mining", "khai thác dữ liệu"
    ],
    "Database management": [
        "quản trị cơ sở dữ liệu", "quản lý cơ sở dữ liệu", "database management", "cơ sở dữ liệu", "csdl"
    ],
    "Research- Data processing": [
        "xử lý dữ liệu", "research- data processing", "xử lý dữ liệu nghiên cứu"
    ],
    "Data warehousing": [
        "kho dữ liệu", "data warehousing", "kho dữ liệu warehousing"
    ],
    "Education": [
        "giáo dục", "education", "giảng dạy"
    ],
    "Environment": [
        "môi trường", "environment", "khí hậu", "climate", "biến đổi khí hậu", "bền vững"
    ],
    "Law": [
        "luật", "pháp luật", "law", "jurisprudence", "pháp lý"
    ],
    "Medicine": [
        "y học", "medicine", "y tế", "sức khỏe", "điều dưỡng"
    ]
}

TITLE_QA_INTENTS = [
    "author",
    "year",
    "summary",
    "keyword",
    "publisher",
    "university"
]



# =========================
# TYPE RESOLVER
# =========================
TYPE_CASE = """
CASE
    WHEN toLower(node.type) = 'book' THEN 'Book'
    WHEN toLower(node.type) = 'article' THEN 'Article'
    WHEN toLower(node.type) = 'thesis' THEN 'Thesis'
    ELSE coalesce(node.type, "Document")
END
"""
def resolve_subject(text):
    """Tìm chủ đề chính xác dựa trên danh sách aliases, dùng word-boundary để tránh false positive."""
    text_lower = text.lower()
    for official_name, aliases in SUBJECT_ALIASES.items():
        # Use word-boundary regex, NOT plain substring to avoid e.g. 'it' matching inside 'website'
        if any(re.search(rf'\b{re.escape(alias)}\b', text_lower) for alias in aliases):
            return official_name
    return None

def clean_subject_query(query_text):
    if not query_text:
        return ""
    text = query_text.lower()
    indicator_words = [
        "chủ đề", "lĩnh vực", "về", "tài liệu", "cuốn sách", "sách", "giáo trình", "bài báo", "luận văn",
        "từ khóa", "trường", "đại học", "học viện", "nhà xuất bản", "nxb", "có", "các", "những",
        "thuộc về", "thuộc", "là", "theo", "mang", "gồm", "của", "viết", "viết bởi", "được", "tìm", "tìm kiếm"
    ]
    for w in indicator_words:
        text = re.sub(rf'\b{w}\b', ' ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def expand_subject_relationship(query_text):
    """
    Trực tiếp truy vấn Neo4j để tìm chủ đề và các chủ đề liên quan (1..2 hops).
    Tận dụng đồ thị tri thức (Knowledge Graph) thực sự của hệ thống.
    """
    if not query_text:
        return None

    # 1. Lấy toàn bộ danh sách các Subject hiện có trong database để đối chiếu
    cypher_all = "MATCH (s:Subject) RETURN s.name AS name, s.id AS id"
    try:
        all_subjects = neo4j_conn.query(cypher_all)
    except Exception as e:
        print(f"[Graph Expansion] Error fetching subjects: {e}")
        return None

    if not all_subjects:
        return None

    # 2. Clean query text
    clean_q = clean_subject_query(query_text)
    
    # 3. Detect subjects matching the clean query
    detected_subjects = []
    matched_aliases = []
    
    # First, try exact whole-word matching using SUBJECT_ALIASES
    # NOTE: Must use word-boundary regex, NOT plain substring match.
    # Plain 'alias in query_lower' causes false positives, e.g.
    # the alias 'it' (for 'Công nghệ thông tin') matches inside 'website'.
    query_lower = query_text.lower()
    for official_name, aliases in SUBJECT_ALIASES.items():
        for alias in aliases:
            # Use word-boundary regex to avoid matching 'it' inside 'website', etc.
            if re.search(rf'\b{re.escape(alias)}\b', query_lower):
                if official_name not in detected_subjects:
                    detected_subjects.append(official_name)
                if alias not in matched_aliases:
                    matched_aliases.append(alias)

    # Next, scan all subjects in DB
    # Use hyphen-normalisation so 'website thiết kế' can match DB subject 'Website- Thiết kế'
    def _norm_for_cmp(s):
        """Strips hyphens/slashes so 'Website- Thiết kế' compares equal to 'website thiết kế'."""
        return re.sub(r'\s+', ' ', re.sub(r'[-/\\]+', ' ', s)).strip()

    clean_q_norm = _norm_for_cmp(clean_q)
    if len(clean_q_norm) >= 3:
        for s in all_subjects:
            s_name = s["name"]
            s_name_lower = s_name.lower()
            s_name_norm = _norm_for_cmp(s_name_lower)

            # Guard short subject names (< 4 chars) to avoid matching e.g. 'AI', 'IT' as substrings
            name_in_query = len(s_name_norm) >= 4 and s_name_norm in clean_q_norm
            query_in_name = clean_q_norm in s_name_norm
            pattern = rf"\b{re.escape(clean_q_norm)}\b"

            if re.search(pattern, s_name_norm) or query_in_name or name_in_query:
                if s_name not in detected_subjects:
                    detected_subjects.append(s_name)
                if s_name_lower in query_lower and s_name_lower not in matched_aliases:
                    matched_aliases.append(s_name_lower)

    # Also keep direct pattern matching for completeness
    for s in all_subjects:
        s_name = s["name"]
        s_name_lower = s_name.lower()
        pattern = rf"\b{re.escape(s_name_lower)}\b"
        if re.search(pattern, query_lower):
            if s_name not in detected_subjects:
                detected_subjects.append(s_name)
            if s_name_lower not in matched_aliases:
                matched_aliases.append(s_name_lower)

    if not detected_subjects:
        return None

    # 4. Truy vấn các chủ đề liên quan (:RELATED_TO) trong khoảng 1..2 bước di chuyển (hops) cho TẤT CẢ các chủ đề đã nhận diện
    cypher_related = """
    MATCH (s:Subject)
    WHERE toLower(s.name) IN $subjects
    MATCH (s)-[:RELATED_TO*1..2]-(rs:Subject)
    WHERE NOT toLower(rs.name) IN $subjects
    RETURN DISTINCT rs.name AS name, rs.id AS id
    """
    try:
        subjects_lower = [s.lower() for s in detected_subjects]
        related_rows = neo4j_conn.query(cypher_related, {"subjects": subjects_lower})
        related_names = [r["name"] for r in related_rows]
        related_ids = [r["id"] for r in related_rows]
        print(f"[Graph Expansion] Detected Subjects: {detected_subjects} | Related: {related_names}")
        return {
            "main_subject": detected_subjects[0],
            "all_detected_subjects": detected_subjects,
            "related_subjects": related_names,
            "related_subject_ids": related_ids,
            "matched_aliases": matched_aliases
        }
    except Exception as e:
        print(f"[Graph Expansion] Cypher error: {e}")
        return {
            "main_subject": detected_subjects[0],
            "all_detected_subjects": detected_subjects,
            "related_subjects": [],
            "related_subject_ids": [],
            "matched_aliases": matched_aliases
        }

def expand_related_documents(results, limit=10):
    if not results:
        return []
    doc_ids = [d["id"] for d in results if d.get("id")]
    if not doc_ids:
        return []
        
    cypher = f"""
    // Tìm các chủ đề của tài liệu gốc
    MATCH (d1:Document)-[:HAS_SUBJECT]->(s1:Subject)
    WHERE d1.id IN $doc_ids
    
    // Tìm tài liệu có cùng chủ đề hoặc thuộc chủ đề liên quan
    MATCH (node:Document)-[:HAS_SUBJECT]->(s2:Subject)
    WHERE (s1 = s2 OR (s1)-[:RELATED_TO]-(s2))
    AND NOT node.id IN $doc_ids
    AND (node.status IS NULL OR node.status = 'active')
    
    OPTIONAL MATCH (node)-[:HAS_AUTHOR]->(a:Author)
    
    RETURN DISTINCT
        node.id AS id,
        node.title AS title,
        node.year AS year,
        node.image_url AS image_url,
        {TYPE_CASE} AS type,
        collect(DISTINCT a.name) AS authors,
        [(node)-[:PUBLISHED_BY]->(p) | p.name] AS publishers,
        [(node)-[:OWNED_BY]->(u) | u.name] AS universities,
        0.8 AS score,
        70 AS priority,
        'graph' AS source,
        ['graph'] AS sources,
        'graph_relation_expansion' AS retrieval_stage,
        d1.title AS matched_title
    LIMIT $limit
    """
    try:
        rows = neo4j_conn.query(cypher, {"doc_ids": doc_ids, "limit": limit})
        related_docs = []
        seen = set(doc_ids)
        for r in rows:
            doc_id = r["id"]
            if doc_id in seen:
                continue
            seen.add(doc_id)
            doc_norm = normalize_doc(r)
            doc_norm["explanation"] = [f"Liên quan đến tài liệu '{r['matched_title']}' trên sơ đồ tri thức"]
            related_docs.append(doc_norm)
        return related_docs
    except Exception as e:
        print(f"[Graph Document Expansion] Error: {e}")
        return []
def normalize_doc(doc):
    """Chuẩn hóa metadata của document với kiểu dữ liệu an toàn và đa nguồn."""
    
    # Resolve type
    doc_type = doc.get("type")
    if not doc_type and doc.get("labels"):
        labels = doc.get("labels")
        if "Book" in labels: doc_type = "Book"
        elif "Article" in labels: doc_type = "Article"
        elif "Thesis" in labels: doc_type = "Thesis"

    # Safe numeric casting (Anti-crash)
    try:
        year_val = doc.get("year")
        year = int(year_val) if year_val and str(year_val).strip() else 0
    except:
        year = 0
        
    try:
        score_val = doc.get("score")
        score = float(score_val) if score_val is not None else 0.0
    except:
        score = 0.0
        
    try:
        priority_val = doc.get("priority")
        priority = int(priority_val) if priority_val is not None else 0
    except:
        priority = 0

    # Multi-source tracking (List instead of String)
    sources = doc.get("sources", [])
    if not isinstance(sources, list):
        sources = [sources] if sources else []
        
    primary_source = doc.get("source")
    if primary_source and primary_source not in sources:
        sources.append(primary_source)

    return {
        "id": doc.get("id"),
        "title": doc.get("title", "Không có tiêu đề"),
        "type": doc_type or "Document",
        "year": year,
        "authors": doc.get("authors") or [],
        "publishers": doc.get("publishers") or [],
        "universities": doc.get("universities") or [],
        "subjects": doc.get("subjects") or [],
        "keywords": doc.get("keywords") or [],
        "abstract": doc.get("abstract", ""),
        "image_url": doc.get("image_url") or "/static/images/pdf.jpg",
        "score": score,
        "priority": priority,
        "sources": list(set(sources)), # Unique sources
        "retrieval_stage": doc.get("retrieval_stage", "unknown"),
        "vector_score": doc.get("vector_score", 0),
        "fulltext_score": doc.get("fulltext_score", 0),
        "graph_score": doc.get("graph_score", 0),
        "rerank_score": doc.get("rerank_score", 0),
        "explanation": doc.get("explanation") or []
    }


def search_title_index(query):
    cypher = f"""
    CALL db.index.fulltext.queryNodes("documentFulltextIndex", $q)
    YIELD node, score
    WHERE node.status IS NULL OR node.status = 'active'
    RETURN
        node.id AS id,
        node.title AS title,
        node.year AS year,
        node.image_url AS image_url,
        {TYPE_CASE} AS type,
        score
    ORDER BY score DESC
    LIMIT 5
    """
    return neo4j_conn.query(cypher, {"q": query})

# =========================
# FULLTEXT SEARCH
# =========================
def search_fulltext(query, filters=None, limit=20):
    filters = filters or {}
    doc_type = filters.get("doc_type")
    
    # Normalize to list
    if doc_type and isinstance(doc_type, str):
        doc_type = [doc_type]

    if not query:
        return []

    cypher = f"""
    CALL db.index.fulltext.queryNodes($index, $query)
    YIELD node, score

    WHERE (node:Document)
    AND (node.status IS NULL OR node.status = 'active')
    AND ($doc_type IS NULL OR 
        toLower(coalesce(node.type, "")) IN [x IN $doc_type | toLower(x)] OR
        ANY(lbl IN labels(node) WHERE toLower(lbl) IN [x IN $doc_type | toLower(x)])
    )

    OPTIONAL MATCH (node)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        node.id AS id,
        node.title AS title,
        node.year AS year,
        node.image_url AS image_url,
        {TYPE_CASE} AS type,
        collect(DISTINCT a.name) AS authors,
        [(node)-[:PUBLISHED_BY]->(p) | p.name] AS publishers,
        [(node)-[:OWNED_BY]->(u) | u.name] AS universities,
        score AS score,
        80 AS priority,
        'fulltext' AS source,
        ['fulltext'] AS sources,
        'fulltext_match' AS retrieval_stage

    ORDER BY score DESC
    LIMIT $limit
    """

    results = neo4j_conn.query(cypher, {
        "index": FULLTEXT_INDEX,
        "query": query,
        "doc_type": doc_type,
        "limit": limit
    })

    return [normalize_doc(r) for r in results]


# =========================
# GRAPH SEARCH
# =========================
def search_graph(filters, query="", limit=20):

    if not any(filters.values()):
        return []

    # Normalize doc_type to list for Neo4j
    if filters.get("doc_type") and isinstance(filters["doc_type"], str):
        filters["doc_type"] = [filters["doc_type"]]

    cypher = """
    MATCH (d)
    WHERE (d:Document)
    AND (d.status IS NULL OR d.status = 'active')
    AND ($query = "" OR toLower(d.title) CONTAINS toLower($query))

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Publisher)
    OPTIONAL MATCH (d)-[:OWNED_BY]->(u:University)

    WITH d,
         collect(DISTINCT a.name) AS authors,
         collect(DISTINCT s.name) AS subjects,
         collect(DISTINCT p.name) AS publishers,
         collect(DISTINCT u.name) AS universities

    WHERE
        ($doc_type IS NULL OR
            toLower(coalesce(d.type, "")) IN [x IN $doc_type | toLower(x)] OR
            ANY(lbl IN labels(d) WHERE toLower(lbl) IN [x IN $doc_type | toLower(x)])
        )

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) CONTAINS toLower($author)))

        AND ($subject IS NULL OR
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)) OR
            ($subject_aliases IS NOT NULL AND ANY(x IN subjects WHERE toLower(x) IN $subject_aliases)))

        AND ($publisher IS NULL OR
            ANY(x IN publishers WHERE toLower(x) CONTAINS toLower($publisher)))

        AND ($university IS NULL OR
            ANY(x IN universities WHERE toLower(x) CONTAINS toLower($university)))

        AND ($year IS NULL OR d.year = $year)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.image_url AS image_url,
        CASE
            WHEN toLower(d.type) = 'book' THEN 'Book'
            WHEN toLower(d.type) = 'article' THEN 'Article'
            WHEN toLower(d.type) = 'thesis' THEN 'Thesis'
            ELSE coalesce(d.type, 'Document')
        END AS type,
        authors,
        subjects,
        publishers,
        universities,
        1 AS score,
        100 AS priority,
        'graph' AS source,
        ['graph'] AS sources,
        'graph_metadata_match' AS retrieval_stage

    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    SKIP $skip
    LIMIT $limit
    """

    results = neo4j_conn.query(cypher, {
        "doc_type": filters.get("doc_type"),
        "author": filters.get("author"),
        "subject": filters.get("subject"),
        "subject_aliases": [s.lower() for s in filters.get("subject_aliases", [])],
        "publisher": filters.get("publisher"),
        "university": filters.get("university"),
        "year": filters.get("year"),
        "query": query or "",
        "skip": filters.get("skip", 0),
        "limit": limit
    })

    return [normalize_doc(r) for r in results]


# =========================
# HYBRID SEARCH
# =========================
def hybrid_search(query="", filters=None, limit=20, original_query=None, search_type="hybrid"):

    filters = filters or {}
    if not original_query:
        original_query = query

    if search_type == "keyword":
        # NOTE: keyword mode is handled early in search_documents (pure fulltext, no expansion)
        # This branch is kept as fallback only
        results_fulltext = search_fulltext(query, filters, limit)
        has_specific_filters = any(k for k in filters if k not in ["doc_type", "skip"] and filters[k])
        results_graph = search_graph(filters, "", limit) if has_specific_filters else []
        results_vector = []
    elif search_type == "semantic":
        # Semantic AI = Vector (embedding) + Graph search (subject/keyword expansion)
        results_fulltext = []
        results_vector = vector_search(original_query, filters=filters, limit=limit)
        has_specific_filters = any(k for k in filters if k not in ["doc_type", "skip"] and filters[k])
        results_graph = search_graph(filters, "", limit) if has_specific_filters else []
    else:  # hybrid = Fulltext + Vector + Graph (all 3)
        results_fulltext = search_fulltext(query, filters, limit)
        results_vector = vector_search(original_query, filters=filters, limit=limit)
        has_specific_filters = any(k for k in filters if k not in ["doc_type", "skip"] and filters[k])
        if has_specific_filters or not query:
            results_graph = search_graph(filters, query, limit)
        else:
            results_graph = []

    merged = {}
    
    # Normalize fulltext scores
    if results_fulltext:
        max_ft = max((item.get("score") or 0) for item in results_fulltext)
        if max_ft > 0:
            for item in results_fulltext:
                item["score"] = item["score"] / max_ft
                
    w1 = 0.6  # Trọng số cho Fulltext
    w2 = 0.4  # Trọng số cho Vector
 
    # Nếu query có chủ đề cụ thể, giảm mạnh trọng số Vector để tránh nhiễu chéo lĩnh vực
    if filters.get("subject"):
        w1 = 0.95
        w2 = 0.05

    # FULLTEXT
    for item in results_fulltext:
        item["fulltext_score"] = item.get("score", 0)
        item["score"] = item["fulltext_score"] * w1
        item["explanation"] = ["Khớp nội dung toàn văn (tiêu đề, tóm tắt, từ khóa, chủ đề, tác giả)"]
        merged[item["id"]] = normalize_doc(item)


    # GRAPH (Priority 100)
    for item in results_graph:
        item["graph_score"] = 0.1  # Gán giá trị điểm đồ thị chuẩn hóa mặc định (0.1 * 1000 = 100% trên giao diện)
        item_norm = normalize_doc(item)
        doc_id = item_norm["id"]
        
        if doc_id in merged:
            merged[doc_id]["sources"] = list(set(merged[doc_id]["sources"] + ["graph"]))
            merged[doc_id]["priority"] = max(merged[doc_id].get("priority", 0), 100)
            merged[doc_id]["graph_score"] = 0.1
            if "Tìm thấy qua liên kết dữ liệu" not in merged[doc_id]["explanation"]:
                merged[doc_id]["explanation"].append("Tìm thấy qua liên kết dữ liệu")
        else:
            item_norm["priority"] = 100
            item_norm["sources"] = ["graph"]
            item_norm["explanation"] = ["Tìm thấy qua liên kết dữ liệu"]
            merged[doc_id] = item_norm


    # VECTOR (Priority 50 in semantic mode, 40 in hybrid)
    vector_priority = 50 if search_type == "semantic" else 40
    for item in results_vector:
        item["vector_score"] = item.get("score", 0.0)
        doc_id = item["id"]
        
        if doc_id in merged:
            merged[doc_id]["sources"] = list(set(merged[doc_id]["sources"] + ["vector"]))
            merged[doc_id]["vector_score"] = item.get("score", 0.0)
            # Kết hợp điểm lai ghép (hybrid score) cho tài liệu khớp cả Fulltext và Vector
            if "fulltext" in merged[doc_id]["sources"]:
                merged[doc_id]["score"] = merged[doc_id].get("fulltext_score", 0) * w1 + item.get("score", 0) * w2
            else:
                merged[doc_id]["score"] = item.get("score", 0.0)
            
            if "Tìm thấy qua tìm kiếm ngữ nghĩa AI (embedding)" not in merged[doc_id]["explanation"]:
                merged[doc_id]["explanation"].append("Tìm thấy qua tìm kiếm ngữ nghĩa AI (embedding)")
        else:
            item_norm = normalize_doc(item)
            item_norm["priority"] = vector_priority
            item_norm["sources"] = ["vector"]
            item_norm["explanation"] = ["Tìm thấy qua tìm kiếm ngữ nghĩa AI (embedding)"]
            merged[doc_id] = item_norm



    # 2. PRIORITY BOOSTING (Metadata Match vs Keyword Match)
    has_metadata_filter = any(filters.get(k) for k in ["subject", "author", "university", "keyword"])
    
    for doc in list(merged.values()):
        title_lower = doc["title"].lower()
        query_lower = original_query.lower()
        priority = doc.get("priority", 0)

        # 1. EXACT TITLE BOOST (Priority 150)
        if query_lower == title_lower:
            doc["priority"] = 150
            doc["retrieval_stage"] = "exact_title_match"
        
        # 2. PARTIAL TITLE BOOST (Priority 130)
        elif query_lower in title_lower and len(query_lower) > 3:
            doc["priority"] = max(doc["priority"], 130)
            doc["retrieval_stage"] = "partial_title_match"

        # 3. EXACT METADATA BOOST (Priority 120)
        else:
            target_subject = filters.get("subject")
            detected_subjs = [s.lower() for s in filters.get("detected_subjects", [])]
            if target_subject and target_subject.lower() not in detected_subjs:
                detected_subjs.append(target_subject.lower())

            subject_aliases = [s.lower() for s in filters.get("subject_aliases", [])]
            related_subjs = [s for s in subject_aliases if s not in detected_subjs]

            doc_subjects = [s.lower() for s in doc.get("subjects", [])]

            is_exact_subject = False
            is_related_subject = False

            if any(s in doc_subjects for s in detected_subjs):
                is_exact_subject = True
            elif any(s in doc_subjects for s in related_subjs):
                is_related_subject = True

            if is_exact_subject:
                doc["priority"] = 120
                doc["retrieval_stage"] = "exact_metadata_match"
            elif is_related_subject:
                doc["priority"] = 110
                doc["retrieval_stage"] = "related_metadata_match"
            elif filters.get("university") and any(filters["university"].lower() in u.lower() for u in doc.get("universities", [])):
                doc["priority"] = 120
                doc["retrieval_stage"] = "exact_metadata_match"

            # PARTIAL METADATA / STRONG TITLE BOOST (Priority 100)
            elif filters.get("subject") and filters["subject"].lower() in title_lower:
                doc["priority"] = max(doc["priority"], 100)
                doc["retrieval_stage"] = "metadata_title_match"

        # VECTOR DEMOTION (If metadata query is active)
        merged[doc["id"]] = doc

    # Enforce metadata filters on all merged results
    filtered_merged = {}
    for doc_id, doc in merged.items():
        # doc_type filter
        doc_type_filter = filters.get("doc_type")
        if doc_type_filter:
            if isinstance(doc_type_filter, str):
                doc_type_filter = [doc_type_filter]
            dt_lower = [t.lower() for t in doc_type_filter]
            if doc.get("type", "").lower() not in dt_lower:
                continue

        # author filter
        auth_filter = filters.get("author")
        if auth_filter:
            doc_authors = [a.lower() for a in doc.get("authors", [])]
            if not any(auth_filter.lower() in a for a in doc_authors):
                continue

        # subject / subject_aliases filter
        subj_filter = filters.get("subject")
        subj_aliases = [s.lower() for s in filters.get("subject_aliases", [])]
        if subj_filter:
            doc_subjects = [s.lower() for s in doc.get("subjects", [])]
            matches_subj = any(subj_filter.lower() in s for s in doc_subjects)
            matches_aliases = any(s in doc_subjects for s in subj_aliases)
            if not (matches_subj or matches_aliases):
                continue

        # publisher filter
        pub_filter = filters.get("publisher")
        if pub_filter:
            doc_publishers = [p.lower() for p in doc.get("publishers", [])]
            if not any(pub_filter.lower() in p for p in doc_publishers):
                continue

        # university filter
        univ_filter = filters.get("university")
        if univ_filter:
            doc_univs = [u.lower() for u in doc.get("universities", [])]
            if not any(univ_filter.lower() in u for u in doc_univs):
                continue

        # year filter
        year_filter = filters.get("year")
        if year_filter:
            try:
                if int(doc.get("year", 0)) != int(year_filter):
                    continue
            except (ValueError, TypeError):
                pass

        filtered_merged[doc_id] = doc

    merged = filtered_merged

    results = list(merged.values())

    # PRIORITY-BASED RERANKING
    results.sort(key=lambda x: (
        -x.get("priority", 0),
        -x.get("score", 0),
        -(x.get("year", 0))
    ))

    return results[:limit]


# =========================
# MAIN SEARCH PIPELINE
# =========================
def search_documents(query="", filters=None, limit=20, search_type="hybrid"):

    filters = filters or {}

    # Anti-empty query handling
    if not query:
        if any(filters.values()):
            print("[Pipeline] Empty query with filters. Using Graph Search.")
            return search_graph(filters, "", limit)
        print("[Pipeline] Empty query and no filters. Returning latest documents.")
        return get_latest_documents(limit)

    # Làm sạch query để tránh lỗi Lucene
    query = re.sub(r'[\[\]\{\}\(\)\^\~\*\?\:\\\/\'\"]+', ' ', query).strip()

    # ===========================================================
    # FULLTEXT MODE: chỉ tìm trên title + abstract, không expansion
    # ===========================================================
    if search_type == "keyword":
        # Chỉ áp dụng các filter tường minh từ người dùng (doc_type, author, year)
        explicit_filters = {
            k: v for k, v in filters.items()
            if k in ["doc_type", "author", "year"] and v
        }
        ft_results = search_fulltext(query, explicit_filters, limit)
        # Gán fulltext_score đúng để UI hiển thị score bar
        if ft_results:
            max_ft = max((r.get("score") or 0) for r in ft_results) or 1
            for r in ft_results:
                r["fulltext_score"] = round(r.get("score", 0) / max_ft, 4)
                r["score"] = r["fulltext_score"]
        return ft_results

    parsed_query, parsed_filters = parse_query(query)
    filters.update(parsed_filters)

    # Subject Relationship Expansion (hybrid / semantic only)
    original_parsed_query = parsed_query
    expansion = expand_subject_relationship(query)
    if expansion:
        main_subj = expansion["main_subject"]
        related_subjs = expansion["related_subjects"]
        all_detected_subjs = expansion.get("all_detected_subjects", [main_subj])
        
        # Chỉ set subject filter nếu chưa được set từ caller (parse_filters của qa_service)
        if not filters.get("subject"):
            filters["subject"] = main_subj
        
        # Lưu trữ danh sách phân biệt để phục vụ tính điểm ưu tiên (ranking)
        filters["detected_subjects"] = all_detected_subjs
        filters["related_subjects"] = related_subjs
        
        # Luôn thêm subject_aliases để mở rộng graph search
        if "subject_aliases" not in filters:
            filters["subject_aliases"] = []
            
        for ds in all_detected_subjs:
            if ds.lower() not in [x.lower() for x in filters["subject_aliases"]]:
                filters["subject_aliases"].append(ds)
                
        for rs in related_subjs:
            if rs.lower() not in [x.lower() for x in filters["subject_aliases"]]:
                filters["subject_aliases"].append(rs)
                
        # Dọn dẹp parsed_query để tránh việc filter cứng tiêu đề trong search_graph
        matched_aliases = expansion.get("matched_aliases", [])
        for ma in matched_aliases:
            parsed_query = re.sub(rf'\b{re.escape(ma.lower())}\b', ' ', parsed_query, flags=re.IGNORECASE)
        for ds in all_detected_subjs:
            parsed_query = re.sub(rf'\b{re.escape(ds.lower())}\b', ' ', parsed_query, flags=re.IGNORECASE)
        clean_q = clean_subject_query(query)
        parsed_query = re.sub(rf'\b{re.escape(clean_q.lower())}\b', ' ', parsed_query, flags=re.IGNORECASE)
        parsed_query = re.sub(r'\s+', ' ', parsed_query).strip()

        # Chỉ expand Lucene query khi KHÔNG có subject filter cứng
        if related_subjs and not filters.get("subject"):
            expansion_terms = " OR ".join([f'"{rs}"' for rs in related_subjs[:3]])
            if parsed_query:
                parsed_query = f'({parsed_query}) OR {expansion_terms}'
            else:
                parsed_query = expansion_terms
            print(f"[Graph Expansion] Expanded Lucene query to: {parsed_query}")

    # Import inline để tránh circular import với qa_service
    from services.qa_service import detect_intent, extract_title

    intent = detect_intent(query)
    title = extract_title(query)

    # 2. STRONG QA TITLE SEARCH (Only for specific factual intents)
    if intent in TITLE_QA_INTENTS and title:
        print(f"[Pipeline] Strong QA Intent detected: {intent}. Title Search for: {title}")
        results = search_title_index(title)
        if results:
            return [normalize_doc(r) for r in results]

    # 3. HYBRID SEARCH
    print(f"[Pipeline] Performing search of type: {search_type}")
    results = hybrid_search(parsed_query, filters, limit, original_query=query, search_type=search_type)

    # 4. GRAPH SEARCH (Fallback if results are thin but we have filters)
    if not results and any(filters.values()):
        print("[Pipeline] Fallback to Graph Search")
        results = search_graph(filters, original_parsed_query, limit)

    # 5. WEAK QA INTENT Fallback
    if not results and title and title != query and len(title) > 3:
        print(f"[Pipeline] Weak QA Intent fallback. Trying Title Search for: {title}")
        results = search_title_index(title)
        if results:
            results = [normalize_doc(r) for r in results]

    # 6. GRAPH RELATION DOCUMENT EXPANSION (RELATED_TO document connections)
    if results:
        related_docs = expand_related_documents(results, limit=5)
        seen = {d["id"] for d in results}
        
        # doc_type filter
        doc_type_filter = filters.get("doc_type")
        if doc_type_filter and isinstance(doc_type_filter, str):
            doc_type_filter = [doc_type_filter]

        for rd in related_docs:
            if rd["id"] not in seen:
                # Check doc_type
                if doc_type_filter:
                    dt_lower = [t.lower() for t in doc_type_filter]
                    if rd.get("type", "").lower() not in dt_lower:
                        continue
                
                # Check author
                auth_filter = filters.get("author")
                if auth_filter:
                    doc_authors = [a.lower() for a in rd.get("authors", [])]
                    if not any(auth_filter.lower() in a for a in doc_authors):
                        continue
                
                # Check subject
                subj_filter = filters.get("subject")
                if subj_filter:
                    doc_subjects = [s.lower() for s in rd.get("subjects", [])]
                    if not any(subj_filter.lower() in s for s in doc_subjects):
                        continue
                        
                # Check publisher
                pub_filter = filters.get("publisher")
                if pub_filter:
                    doc_publishers = [p.lower() for p in rd.get("publishers", [])]
                    if not any(pub_filter.lower() in p for p in doc_publishers):
                        continue
                        
                # Check university
                univ_filter = filters.get("university")
                if univ_filter:
                    doc_univs = [u.lower() for u in rd.get("universities", [])]
                    if not any(univ_filter.lower() in u for u in doc_univs):
                        continue
                        
                # Check year
                year_filter = filters.get("year")
                if year_filter:
                    try:
                        if int(rd.get("year", 0)) != int(year_filter):
                            continue
                    except (ValueError, TypeError):
                        pass

                results.append(rd)

    return results



# =========================
# PARSE QUERY (NÂNG CAO)
# =========================
def parse_query(query):
    if not query:
        return "", {}

    filters = {}
    text = query.lower()

    # 1. SUBJECT RESOLUTION
    resolved_subj = resolve_subject(text)
    if resolved_subj:
        filters["subject"] = resolved_subj
        filters["subject_aliases"] = SUBJECT_ALIASES.get(resolved_subj, [])
        # Remove the matched subject part from text to avoid over-filtering titles in search_graph
        for alias in filters["subject_aliases"] + [resolved_subj]:
            text = re.sub(rf'\b{re.escape(alias)}\b', ' ', text, flags=re.IGNORECASE)

    # 2. KEYWORD Extraction
    kw_match = re.search(r'(?:từ khóa|keyword)\s+([^\s?]+)', text)
    if kw_match:
        filters["keyword"] = kw_match.group(1).strip()

    # 3. UNIVERSITY Extraction
    inst_match = re.search(r'(?:trường|đại học|học viện|university|institute)\s+([^\s?]+(?:\s+[^\s?]+){0,2})', text)
    if inst_match:
        filters["university"] = inst_match.group(1).strip()
        # Xóa phần đã khớp để không bị tác giả bắt lại
        text = text.replace(inst_match.group(0), "")

    # 4. YEAR
    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    if year_match:
        filters["year"] = int(year_match.group())
        text = text.replace(year_match.group(), "")

    # 5. TYPE
    if "luận văn" in text:
        filters["doc_type"] = "Thesis"
    elif "sách" in text or "giáo trình" in text:
        filters["doc_type"] = "Book"
    elif "bài báo" in text:
        filters["doc_type"] = "Article"

    # 6. AUTHOR
    author_match = re.search(r'(?:tác giả|của|bởi)\s+([^\s?]+(?:\s+[^\s?]+){0,2})', text)
    if author_match:
        filters["author"] = author_match.group(1).strip()

    # Remove INDICATOR words from text query
    indicator_words = [
        "chủ đề", "lĩnh vực", "về", "tài liệu", "cuốn sách", "sách", "giáo trình", "bài báo", "luận văn",
        "từ khóa", "trường", "đại học", "học viện", "nhà xuất bản", "nxb", "có", "các", "những",
        "thuộc về", "thuộc", "là", "theo", "mang", "gồm", "của", "viết", "viết bởi", "được"
    ]
    for w in indicator_words:
        text = re.sub(rf'\b{w}\b', ' ', text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text).strip()
    return text, filters



# =========================
# STRICT SEARCH (CHÍNH)
# =========================
def strict_search(query="", filters=None, limit=20):
    filters = filters or {}

    # Normalize doc_type to list for Neo4j
    if filters.get("doc_type") and isinstance(filters["doc_type"], str):
        filters["doc_type"] = [filters["doc_type"]]

    cypher = """
    MATCH (d)
    WHERE (d:Document)
      AND (d.status IS NULL OR d.status = 'active')

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)

    WITH d,
         collect(DISTINCT a.name) AS authors,
         collect(DISTINCT s.name) AS subjects,
         collect(DISTINCT k.name) AS keywords

    WHERE
        ($query IS NULL OR toLower(d.title) CONTAINS toLower($query))

        AND ($doc_type IS NULL OR
            toLower(coalesce(d.type, "")) IN [x IN $doc_type | toLower(x)] OR
            ANY(lbl IN labels(d) WHERE toLower(lbl) IN [x IN $doc_type | toLower(x)])
        )

        AND ($year IS NULL OR d.year = $year)

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) CONTAINS toLower($author)))

        AND ($subject IS NULL OR
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)) OR
            ($subject_aliases IS NOT NULL AND ANY(x IN subjects WHERE toLower(x) IN $subject_aliases)))

        AND ($keyword IS NULL OR
            ANY(x IN keywords WHERE toLower(x) CONTAINS toLower($keyword)))

        AND ($language IS NULL OR EXISTS {
            MATCH (d)-[:IN_LANGUAGE]->(l)
            WHERE toLower(l.name) CONTAINS toLower($language)
        })

        AND ($university IS NULL OR EXISTS {
            MATCH (d)-[:OWNED_BY]->(i:University)
            WHERE toLower(i.name) CONTAINS toLower($university)
        })

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
        END AS type,
        authors,
        [(d)-[:PUBLISHED_BY]->(p) | p.name] AS publishers,
        [(d)-[:OWNED_BY]->(u) | u.name] AS universities,
        1 AS score

    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    SKIP $skip
    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "query": query if query else None,
        "doc_type": filters.get("doc_type"),
        "year": filters.get("year"),
        "author": filters.get("author"),
        "subject": filters.get("subject"),
        "subject_aliases": [s.lower() for s in filters.get("subject_aliases", [])],
        "keyword": filters.get("keyword"),
        "language": filters.get("language"),
        "university": filters.get("university"),
        "skip": filters.get("skip", 0),
        "limit": limit
    })
# =========================
# SUGGEST
# =========================
def suggest_documents(query, limit=10):

    if not query:
        return []

    cypher = """
    CALL db.index.fulltext.queryNodes("documentSearchIndex", $query)
    YIELD node, score

    WHERE (node:Document)
      AND (node.status IS NULL OR node.status = 'active')

    RETURN
        node.id AS id,
        node.title AS title,
        CASE
            WHEN node.type = 'book' THEN 'Book'
            WHEN node.type = 'article' THEN 'Article'
            WHEN node.type = 'thesis' THEN 'Thesis'
        END AS type

    ORDER BY score DESC
    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "query": query + "*",
        "limit": limit
    })

def get_latest_documents(limit=20):

    query = """
    MATCH (d)
    WHERE (d:Document)
      AND (d.status IS NULL OR d.status = 'active')

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.image_url AS image_url,
        CASE
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
        END AS type,
        collect(DISTINCT a.name) AS authors

    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    LIMIT $limit
    """

    results = neo4j_conn.query(query, {"limit": limit})
    return [normalize_doc(r) for r in results]