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


# =========================
# FULLTEXT SEARCH
# =========================
def search_fulltext(query, limit=20):

    if not query:
        return []

    cypher = f"""
    CALL db.index.fulltext.queryNodes($index, $query)
    YIELD node, score

    WHERE node:Book OR node:Article OR node:Thesis

    OPTIONAL MATCH (node)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        node.id AS id,
        node.title AS title,
        node.year AS year,
        {TYPE_CASE} AS type,
        collect(DISTINCT a.name) AS authors,
        score AS score,
        'fulltext' AS source

    ORDER BY score DESC
    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "index": FULLTEXT_INDEX,
        "query": query,
        "limit": limit
    })


# =========================
# GRAPH SEARCH (FILTER)
# =========================
def search_graph(filters, limit=20):

    if not any(filters.values()):
        return []

    cypher = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)

    WITH d,
         collect(DISTINCT a.name) AS authors,
         collect(DISTINCT s.name) AS subjects

    WHERE
        ($doc_type IS NULL OR
            ($doc_type = "Book" AND d:Book) OR
            ($doc_type = "Article" AND d:Article) OR
            ($doc_type = "Thesis" AND d:Thesis)
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
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type,
        authors,
        1 AS score,
        'graph' AS source

    ORDER BY d.year DESC
    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "doc_type": filters.get("doc_type"),
        "author": filters.get("author"),
        "subject": filters.get("subject"),
        "year": filters.get("year"),
        "limit": limit
    })


# =========================
# HYBRID SEARCH (AI)
# =========================
def hybrid_search(query="", filters=None, limit=20):

    filters = filters or {}

    results_fulltext = search_fulltext(query, limit)
    results_graph = search_graph(filters, limit)
    results_vector = vector_search(query, limit)

    merged = {}

    for item in results_fulltext:
        merged[item["id"]] = item

    for item in results_graph:
        if item["id"] in merged:
            merged[item["id"]]["score"] += 1
        else:
            merged[item["id"]] = item

    for item in results_vector:
        if item["id"] in merged:
            merged[item["id"]]["score"] += item["score"] * 2
        else:
            merged[item["id"]] = item

    results = list(merged.values())
    results.sort(key=lambda x: (-x.get("score", 0), -(x.get("year") or 0)))

    return results[:limit]


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
            ($doc_type = "Book" AND d:Book) OR
            ($doc_type = "Article" AND d:Article) OR
            ($doc_type = "Thesis" AND d:Thesis)
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
        "limit": limit
    })


# =========================
# MAIN SEARCH
# =========================
def search_documents(query="", filters=None, limit=20):

    filters = filters or {}

    parsed_query, parsed_filters = parse_query(query)
    filters.update(parsed_filters)

    # 🔥 dùng hybrid search thay vì strict
    results = hybrid_search(parsed_query, filters, limit)

    # 🔥 fallback nếu không có
    if not results:
        results = hybrid_search(parsed_query, {}, limit)

    if not results:
        results = hybrid_search("", {}, limit)

    return results


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