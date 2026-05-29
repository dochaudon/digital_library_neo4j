from database.neo4j_connection import neo4j_conn


# =========================
# COMMON MATCH ENTITY
# =========================
ENTITY_MATCH = """
MATCH (e)
WHERE e.id = $id OR e.name = $id
"""


# =========================
# PREVIEW (POPUP)
# =========================
def get_preview(entity_type, entity_id):

    relation_map = {
        "author": "HAS_AUTHOR",
        "subject": "HAS_SUBJECT",
        "keyword": "HAS_KEYWORD",
        "publisher": "PUBLISHED_BY",
        "university": "OWNED_BY",
        "journal": "PUBLISHED_IN",
        "category": "HAS_CATEGORY",
        "language": "IN_LANGUAGE"
    }

    # ===== DOCUMENT =====
    if entity_type in ["document", "book", "article", "thesis"]:
        query = """
        MATCH (d)
        WHERE d.id = $id AND (d.status IS NULL OR d.status = 'active')
        RETURN 
            d.id AS id,
            coalesce(d.title, d.name) AS title,
            d.year AS year
        """
        result = neo4j_conn.query(query, {"id": entity_id})

        return {
            "type": "document",
            "data": result[0] if result else {}
        }

    if entity_type not in relation_map:
        return {"documents": []}

    rel = relation_map[entity_type]

    query = f"""
    {ENTITY_MATCH}
    MATCH (e)<-[:{rel}]-(d)
    WHERE d.status IS NULL OR d.status = 'active'
    RETURN 
        d.id AS id,
        coalesce(d.title, d.name) AS title,
        CASE
            WHEN toLower(d.type) = 'book' THEN 'book'
            WHEN toLower(d.type) = 'article' THEN 'article'
            WHEN toLower(d.type) = 'thesis' THEN 'thesis'
            ELSE coalesce(toLower(d.type), "document")
        END AS type
    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    LIMIT 5
    """

    result = neo4j_conn.query(query, {"id": entity_id})

    return {
        "type": entity_type,
        "documents": result
    }


# =========================
# ENTITY DETAIL (LEFT PANEL)
# =========================
def get_entity_detail(entity_type, entity_id, page=1, limit=10):

    skip = (page - 1) * limit

    relation_map = {
        "author": "HAS_AUTHOR",
        "subject": "HAS_SUBJECT",
        "keyword": "HAS_KEYWORD",
        "publisher": "PUBLISHED_BY",
        "university": "OWNED_BY",
        "journal": "PUBLISHED_IN",
        "category": "HAS_CATEGORY",
        "language": "IN_LANGUAGE"
    }

    # ===== DOCUMENT =====
    if entity_type in ["document", "book", "article", "thesis"]:
        query = """
        MATCH (d)
        WHERE d.id = $id AND (d.status IS NULL OR d.status = 'active')
        OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
        OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
        OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Publisher)
        OPTIONAL MATCH (d)-[:OWNED_BY]->(u:University)
        OPTIONAL MATCH (d)-[:PUBLISHED_IN]->(j:Journal)
        OPTIONAL MATCH (d)-[:HAS_CATEGORY]->(c:Category)
        OPTIONAL MATCH (d)-[:IN_LANGUAGE]->(l:Language)

        RETURN
            d.id AS id,
            coalesce(d.title, d.name) AS title,
            d.year AS year,
            d.image_url AS image_url,
            collect(DISTINCT a.name) AS authors,
            collect(DISTINCT s.name) AS subjects,
            collect(DISTINCT p.name) AS publishers,
            collect(DISTINCT u.name) AS universities,
            j.name AS journal,
            collect(DISTINCT c.name) AS categories,
            collect(DISTINCT l.name) AS languages
        """

        result = neo4j_conn.query(query, {"id": entity_id})

        return {
            "type": "document",
            "data": result[0] if result else {}
        }

    if entity_type not in relation_map:
        return {}

    rel = relation_map[entity_type]

    # ===== DATA =====
    query = f"""
    {ENTITY_MATCH}
    MATCH (e)<-[:{rel}]-(d)
    WHERE d.status IS NULL OR d.status = 'active'
    RETURN 
        d.id AS id,
        coalesce(d.title, d.name) AS title,
        d.year AS year,
        CASE
            WHEN toLower(d.type) = 'book' THEN 'book'
            WHEN toLower(d.type) = 'article' THEN 'article'
            WHEN toLower(d.type) = 'thesis' THEN 'thesis'
            ELSE coalesce(toLower(d.type), "document")
        END AS type
    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    SKIP $skip LIMIT $limit
    """

    # ===== COUNT =====
    count_query = f"""
    {ENTITY_MATCH}
    MATCH (e)<-[:{rel}]-(d)
    WHERE d.status IS NULL OR d.status = 'active'
    RETURN count(d) AS total
    """

    docs = neo4j_conn.query(query, {
        "id": entity_id,
        "skip": skip,
        "limit": limit
    })

    total = neo4j_conn.query(count_query, {
        "id": entity_id
    })[0]["total"]

    # ===== NAME =====
    name_query = f"""
    {ENTITY_MATCH}
    RETURN e.name AS name
    """
    name_res = neo4j_conn.query(name_query, {"id": entity_id})
    entity_name = name_res[0]["name"] if name_res else "N/A"

    return {
        "type": entity_type,
        "name": entity_name,
        "documents": docs,
        "total": total,
        "page": page
    }


# =========================
# GRAPH BY ENTITY
# =========================
def get_graph_by_entity(entity_type, entity_id):

    if entity_type in ["document", "book", "article", "thesis"]:
        from services.graph_service import get_graph_data
        return get_graph_data(entity_id)

    relation_map = {
        "author": "HAS_AUTHOR",
        "subject": "HAS_SUBJECT",
        "keyword": "HAS_KEYWORD",
        "publisher": "PUBLISHED_BY",
        "university": "OWNED_BY",
        "journal": "PUBLISHED_IN",
        "category": "HAS_CATEGORY",
        "language": "IN_LANGUAGE"
    }

    if entity_type not in relation_map:
        return {"nodes": [], "edges": []}

    rel = relation_map[entity_type]

    query = f"""
    {ENTITY_MATCH}
    MATCH (e)<-[:{rel}]-(d)
    WHERE d.status IS NULL OR d.status = 'active'
    RETURN e, collect(d) AS docs, collect(d.type) AS type_list
    """

    results = neo4j_conn.query(query, {"id": entity_id})

    if not results:
        return {"nodes": [], "edges": []}

    nodes = []
    edges = []
    node_ids = set()

    # ===== CENTER NODE =====
    record = results[0]
    e = record["e"]
    e_id = e.get("id") or entity_id

    nodes.append({
        "id": e_id,
        "label": e.get("name") or e_id,
        "name": e.get("name"),
        "group": entity_type,
        "size": 30
    })
    node_ids.add(e_id)

    all_docs = record.get("docs", [])
    all_types = record.get("type_list", [])

    for i in range(len(all_docs)):
        d = all_docs[i]
        d_type = all_types[i] if i < len(all_types) else "book"
        doc_id = d.get("id")

        if not doc_id: continue

        # Detect group
        doc_group = (d_type or "book").lower()

        if doc_id not in node_ids:
            nodes.append({
                "id": doc_id,
                "label": d.get("title") or d.get("name") or "Unknown",
                "title": d.get("title") or d.get("name") or "Unknown",
                "group": doc_group
            })
            node_ids.add(doc_id)

        edges.append({
            "from": e_id,
            "to": doc_id,
            "label": rel
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "center_id": e_id
    }