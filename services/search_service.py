from database.neo4j_connection import neo4j_conn
from services.vector_search_service import vector_search
import re

FULLTEXT_INDEX = "documentSearchIndex"


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
    doc["image_url"] = doc.get("image_url") or "/static/images/pdf.jpg"
    doc["authors"] = doc.get("authors") or []
    return doc

def search_title_index(query):
    cypher = """
    CALL db.index.fulltext.queryNodes("documentTitleIndex", $q)
    YIELD node, score
    RETURN
        node.id AS id,
        node.title AS title,
        node.year AS year,
        node.image_url AS image_url,
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

    WITH d,
         collect(DISTINCT a.name) AS authors,
         collect(DISTINCT s.name) AS subjects

    WHERE
        ($doc_type IS NULL OR
            ANY(label IN labels(d) WHERE label IN $doc_type)
        )

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) CONTAINS toLower($author)))

        AND ($subject IS NULL OR
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)))

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
        item["score"] = item["score"] * w1
        merged[item["id"]] = normalize_doc(item)

    # GRAPH
    for item in results_graph:
        item = normalize_doc(item)

        if item["id"] in merged:
            merged[item["id"]]["score"] += 0.1 # Boost nhỏ cho graph match
        else:
            item["score"] = 0.1
            merged[item["id"]] = item

    # VECTOR
    for item in results_vector:
        item = normalize_doc(item)
        weighted_score = (item.get("score") or 0) * w2

        if item["id"] in merged:
            merged[item["id"]]["score"] += weighted_score
        else:
            item["score"] = weighted_score
            merged[item["id"]] = item

    results = list(merged.values())
    results.sort(key=lambda x: (-x.get("score", 0), -(x.get("year") or 0)))

    return results[:limit]


# =========================
# MAIN SEARCH PIPELINE
# =========================
def search_documents(query="", filters=None, limit=20):

    filters = filters or {}

    # Làm sạch query để tránh lỗi Lucene (loại bỏ các ký tự đặc biệt có thể gây crash)
    query = re.sub(r'[\[\]\{\}\(\)\^\~\*\?\:\\\/\'\"]', ' ', query).strip()

    parsed_query, parsed_filters = parse_query(query)
    filters.update(parsed_filters)

    # Import inline để tránh circular import với qa_service
    from services.qa_service import detect_intent, extract_title

    intent = detect_intent(query)
    title = extract_title(query)

    # 1. STRONG QA INTENT
    if intent != "search":
        print(f"🚀 [Pipeline] Strong QA Intent detected. Title Search for: {title}")
        results = search_title_index(title)
        if results:
            return [normalize_doc(r) for r in results]

    # 2. WEAK QA INTENT (Check nếu extract_title đã cắt gọt được query)
    if title and title != query and len(title) > 3:
        print(f"🚀 [Pipeline] Weak QA Intent. Trying Title Search for: {title}")
        results = search_title_index(title)
        if results:
            return [normalize_doc(r) for r in results]

    # 3. HYBRID SEARCH
    print("🚀 [Pipeline] Hybrid Search")
    results = hybrid_search(parsed_query, filters, limit)

    # 4. FALLBACK 1: Hybrid without OTHER filters, but MUST keep doc_type
    if not results and any(filters.values()):
        print("⚠️ No results found with strict filters.")
        # Optional: you could try removing other filters but keeping doc_type
    # 5. FALLBACK 2: Only Fulltext
    if not results:
        print("⚠️ Fallback to Only Fulltext")
        results = search_fulltext(parsed_query, filters, limit)

    # 6. FALLBACK 3: Only Vector
    if not results:
        print("⚠️ Fallback to Only Vector")
        results = vector_search(parsed_query, filters, limit)

    # 7. FALLBACK 4: Only Graph
    if not results:
        print("⚠️ Fallback to Only Graph")
        results = search_graph(filters, limit)

    # 8. ANTI-FAIL
    if not results:
        print("⚠️ Fallback to Latest Documents (Anti-fail)")
        results = get_latest_documents(limit)

    return results


# =========================
# PARSE QUERY (NÂNG CAO)
# =========================
def parse_query(query):

    filters = {}
    text = query.lower()

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

    # INSTITUTION
    if "bách khoa" in text:
        filters["institution"] = "Bách Khoa"
        text = text.replace("bách khoa", "")

    # SUBJECT mapping
    if "kinh tế" in text:
        filters["subject"] = "Economics"

    if "trí tuệ nhân tạo" in text:
        filters["subject"] = "Artificial Intelligence"

    if "học máy" in text:
        filters["subject"] = "Machine Learning"

    # AUTHOR
    author_match = re.search(r'của\s+(.+)', text)
    if author_match:
        filters["author"] = author_match.group(1).strip()
        text = text.replace(author_match.group(0), "")

    # KEYWORD
    if re.search(r"\bai\b", text):
        filters["keyword"] = "AI"
    elif "machine learning" in text:
        filters["keyword"] = "machine learning"
    elif "deep learning" in text:
        filters["keyword"] = "deep learning"

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
            MATCH (d)-[:PUBLISHED_BY|SUBMITTED_TO]->(i)
            WHERE toLower(i.name) CONTAINS toLower($institution)
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

    return neo4j_conn.query(query, {"limit": limit})