from database.neo4j_connection import neo4j_conn
from services.vector_search_service import vector_search
import re

FULLTEXT_INDEX = "documentFulltextIndex"

SUBJECT_MAPPINGS = {
    "công nghệ thông tin": "Công nghệ thông tin",
    "cntt": "Công nghệ thông tin",
    "it": "Công nghệ thông tin",
    "ai": "Artificial Intelligence",
    "trí tuệ nhân tạo": "Artificial Intelligence",
    "học máy": "Machine Learning",
    "deep learning": "Deep Learning",
    "kinh tế": "Economics",
    "toán học": "Mathematics",
    "vật lý": "Physics",
    "hóa học": "Chemistry",
    "sinh học": "Biology"
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
    WHEN node:Book THEN "Book"
    WHEN node:Article THEN "Article"
    WHEN node:Thesis THEN "Thesis"
    ELSE coalesce(node.type, "Document")
END
"""
def normalize_doc(doc):
    """Chuẩn hóa metadata của document."""
    
    # Resolve type from labels if missing
    doc_type = doc.get("type")
    if not doc_type and doc.get("labels"):
        labels = doc.get("labels")
        if "Book" in labels: doc_type = "Book"
        elif "Article" in labels: doc_type = "Article"
        elif "Thesis" in labels: doc_type = "Thesis"

    return {
        "id": doc.get("id"),
        "title": doc.get("title", "Không có tiêu đề"),
        "type": doc_type or "Document",
        "year": doc.get("year"),

        "authors": doc.get("authors") or [],
        "publishers": doc.get("publishers") or [],
        "universities": doc.get("universities") or [],
        "subjects": doc.get("subjects") or [],
        "keywords": doc.get("keywords") or [],
        "abstract": doc.get("abstract", ""),
        "image_url": doc.get("image_url") or "/static/images/pdf.jpg",
        "score": doc.get("score", 0),
        "vector_score": doc.get("vector_score", 0),
        "fulltext_score": doc.get("fulltext_score", 0),
        "graph_score": doc.get("graph_score", 0),
        "rerank_score": doc.get("rerank_score", 0),
        "explanation": doc.get("explanation") or []
    }


def search_title_index(query):
    cypher = f"""
    CALL db.index.fulltext.queryNodes("documentTitleIndex", $q)
    YIELD node, score
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

    WHERE (node:Book OR node:Article OR node:Thesis)
    AND ($doc_type IS NULL OR ANY(label IN labels(node) WHERE label IN $doc_type))

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
        'fulltext' AS source

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
    WHERE (d:Book OR d:Article OR d:Thesis)
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
            ANY(label IN labels(d) WHERE label IN $doc_type)
        )

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) CONTAINS toLower($author)))

        AND ($subject IS NULL OR
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)))

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
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type,
        authors,
        publishers,
        universities,
        1 AS score,
        'graph' AS source

    ORDER BY d.year DESC
    SKIP $skip
    LIMIT $limit
    """

    results = neo4j_conn.query(cypher, {
        "doc_type": filters.get("doc_type"),
        "author": filters.get("author"),
        "subject": filters.get("subject"),
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
def hybrid_search(query="", filters=None, limit=20):

    filters = filters or {}

    results_fulltext = search_fulltext(query, filters, limit)
    
    # Only call search_graph if we have specific filters or no query
    # to avoid pulling all documents of a type into a keyword search
    has_specific_filters = any(k for k in filters if k not in ["doc_type", "skip"] and filters[k])
    
    if has_specific_filters or not query:
        results_graph = search_graph(filters, query, limit)
    else:
        results_graph = []
        
    results_vector = vector_search(query, filters=filters, limit=limit)

    merged = {}
    
    # Normalize fulltext scores
    if results_fulltext:
        max_ft = max((item.get("score") or 0) for item in results_fulltext)
        if max_ft > 0:
            for item in results_fulltext:
                item["score"] = item["score"] / max_ft
                
    w1 = 0.6  # Trọng số cho Fulltext
    w2 = 0.4  # Trọng số cho Vector

    # FULLTEXT
    for item in results_fulltext:
        item["fulltext_score"] = item.get("score", 0)
        item["score"] = item["fulltext_score"] * w1
        item["explanation"] = ["Khớp từ khóa trong nội dung hoặc tiêu đề"]
        merged[item["id"]] = normalize_doc(item)


    # GRAPH
    for item in results_graph:
        item_norm = normalize_doc(item)
        item_norm["graph_score"] = 0.1 # Constant for graph match in hybrid

        if item_norm["id"] in merged:
            merged[item_norm["id"]]["score"] += 0.1
            merged[item_norm["id"]]["graph_score"] = 0.1
            merged[item_norm["id"]]["explanation"].append("Khớp thông tin trong đồ thị kiến thức (Graph)")
        else:
            item_norm["score"] = 0.1
            item_norm["explanation"] = ["Tìm thấy qua liên kết dữ liệu"]
            merged[item_norm["id"]] = item_norm


    # VECTOR
    for item in results_vector:
        v_score = item.get("score", 0)
        item_norm = normalize_doc(item)
        item_norm["vector_score"] = v_score
        weighted_score = v_score * w2

        if item_norm["id"] in merged:
            merged[item_norm["id"]]["score"] += weighted_score
            merged[item_norm["id"]]["vector_score"] = v_score
            merged[item_norm["id"]]["explanation"].append(f"Khớp ngữ nghĩa (Độ tương đồng: {v_score:.2f})")
        else:
            item_norm["score"] = weighted_score
            item_norm["explanation"] = [f"Tìm thấy qua tìm kiếm ngữ nghĩa (AI)"]
            merged[item_norm["id"]] = item_norm



    results = list(merged.values())
    results.sort(key=lambda x: (-x.get("score", 0), -(x.get("year") or 0)))

    return results[:limit]


# =========================
# MAIN SEARCH PIPELINE
# =========================
def search_documents(query="", filters=None, limit=20):

    filters = filters or {}

    # Anti-empty query handling
    if not query:
        if any(filters.values()):
            print("[Pipeline] Empty query with filters. Using Graph Search.")
            return search_graph(filters, "", limit)
        print("[Pipeline] Empty query and no filters. Returning latest documents.")
        return get_latest_documents(limit)


    # Làm sạch query để tránh lỗi Lucene
    query = re.sub(r'[\[\]\{\}\(\)\^\~\*\?\:\\\/\'\"]', ' ', query).strip()


    parsed_query, parsed_filters = parse_query(query)
    filters.update(parsed_filters)

    # Import inline để tránh circular import với qa_service
    from services.qa_service import detect_intent, extract_title

    intent = detect_intent(query)
    title = extract_title(query)

    # 1. STRUCTURED FILTERS (Already updated via parse_query)
    # If we have filters but no query, search_graph is already strong.

    # 2. STRONG QA TITLE SEARCH (Only for specific factual intents)
    if intent in TITLE_QA_INTENTS and title:
        print(f"[Pipeline] Strong QA Intent detected: {intent}. Title Search for: {title}")
        results = search_title_index(title)
        if results:
            return [normalize_doc(r) for r in results]

    # 3. HYBRID SEARCH
    print("[Pipeline] Hybrid Search")
    results = hybrid_search(parsed_query, filters, limit)

    # 4. GRAPH SEARCH (Fallback if hybrid is thin but we have filters)
    if not results and any(filters.values()):
        print("[Pipeline] Fallback to Graph Search")
        results = search_graph(filters, parsed_query, limit)


    # 5. WEAK QA INTENT Fallback
    if not results and title and title != query and len(title) > 3:
        print(f"[Pipeline] Weak QA Intent fallback. Trying Title Search for: {title}")
        results = search_title_index(title)
        if results:
            return [normalize_doc(r) for r in results]


    return results



# =========================
# PARSE QUERY (NÂNG CAO)
# =========================
def parse_query(query):
    if not query:
        return "", {}

    filters = {}
    text = query.lower()

    # SUBJECT mapping (Priority)
    for key, val in SUBJECT_MAPPINGS.items():
        if key in text:
            filters["subject"] = val
            # Now we can remove the subject key from text to avoid it being in query
            text = text.replace(key, "")

            
    # YEAR

    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    if year_match:
        filters["year"] = int(year_match.group())
        text = text.replace(year_match.group(), "")

    # TYPE
    if "luận văn" in text:
        filters["doc_type"] = "Thesis"
        text = text.replace("luận văn", "")
    elif "sách" in text or "giáo trình" in text:
        filters["doc_type"] = "Book"
        text = text.replace("sách", "").replace("giáo trình", "")
    elif "bài báo" in text:
        filters["doc_type"] = "Article"
        text = text.replace("bài báo", "")

    # LANGUAGE
    if "tiếng anh" in text:
        filters["language"] = "English"
        text = text.replace("tiếng anh", "")
    elif "tiếng việt" in text:
        filters["language"] = "Vietnamese"
        text = text.replace("tiếng việt", "")

    # PUBLISHER / UNIVERSITY
    if "bách khoa" in text:
        filters["institution"] = "Bách Khoa"
        text = text.replace("bách khoa", "")



    # AUTHOR
    author_match = re.search(r'của\s+(.+)', text)
    if author_match:
        filters["author"] = author_match.group(1).strip()
        text = text.replace(author_match.group(0), "")

    # Remove INDICATOR words from text query
    indicator_words = [
        "chủ đề", "lĩnh vực", "về", "tài liệu", "cuốn sách", "bài báo", "luận văn",
        "từ khóa", "trường", "đại học", "học viện", "nhà xuất bản", "nxb", "có", "các", "những",
        "thuộc về", "thuộc", "là", "theo", "mang", "gồm", "của", "viết", "viết bởi", "được"
    ]
    for w in indicator_words:
        # Use regex for word boundary to avoid partial matches
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
    WHERE (d:Book OR d:Article OR d:Thesis)

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
            ANY(label IN labels(d) WHERE label IN $doc_type)
        )

        AND ($year IS NULL OR d.year = $year)

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) CONTAINS toLower($author)))

        AND ($subject IS NULL OR
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)))

        AND ($keyword IS NULL OR
            ANY(x IN keywords WHERE toLower(x) CONTAINS toLower($keyword)))

        AND ($language IS NULL OR EXISTS {
            MATCH (d)-[:IN_LANGUAGE]->(l)
            WHERE toLower(l.name) CONTAINS toLower($language)
        })

        AND ($institution IS NULL OR EXISTS {
            MATCH (d)-[:PUBLISHED_BY|OWNED_BY]->(i)
            WHERE (i:Publisher OR i:University)
            AND toLower(i.name) CONTAINS toLower($institution)
        })

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type,
        authors,
        [(d)-[:PUBLISHED_BY]->(p) | p.name] AS publishers,
        [(d)-[:OWNED_BY]->(u) | u.name] AS universities,
        1 AS score

    ORDER BY d.year DESC
    SKIP $skip
    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "query": query if query else None,
        "doc_type": filters.get("doc_type"),
        "year": filters.get("year"),
        "author": filters.get("author"),
        "subject": filters.get("subject"),
        "keyword": filters.get("keyword"),
        "language": filters.get("language"),
        "institution": filters.get("institution"),
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

    WHERE node:Book OR node:Article OR node:Thesis

    RETURN
        node.id AS id,
        node.title AS title,
        CASE
            WHEN node:Book THEN "Book"
            WHEN node:Article THEN "Article"
            WHEN node:Thesis THEN "Thesis"
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
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.image_url AS image_url,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type,
        collect(DISTINCT a.name) AS authors

    ORDER BY d.year DESC
    LIMIT $limit
    """

    results = neo4j_conn.query(query, {"limit": limit})
    return [normalize_doc(r) for r in results]