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
        "publisher": "PUBLISHED_BY|SUBMITTED_TO"
    }

    # ===== DOCUMENT =====
    if entity_type == "document":
        query = """
        MATCH (d {id:$id})
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
    RETURN 
        d.id AS id,
        coalesce(d.title, d.name) AS title,
        CASE
            WHEN d:Book THEN "book"
            WHEN d:Article THEN "article"
            WHEN d:Thesis THEN "thesis"
            ELSE "document"
        END AS type
    ORDER BY d.year DESC
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
        "publisher": "PUBLISHED_BY|SUBMITTED_TO"
    }

    # ===== DOCUMENT =====
    if entity_type == "document":
        query = """
        MATCH (d {id:$id})
        OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
        OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)

        RETURN
            d.id AS id,
            coalesce(d.title, d.name) AS title,
            d.year AS year,
            collect(DISTINCT a.name) AS authors,
            collect(DISTINCT s.name) AS subjects
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
    RETURN 
        d.id AS id,
        coalesce(d.title, d.name) AS title,
        d.year AS year,
        CASE
            WHEN d:Book THEN "book"
            WHEN d:Article THEN "article"
            WHEN d:Thesis THEN "thesis"
            ELSE "document"
        END AS type
    ORDER BY d.year DESC
    SKIP $skip LIMIT $limit
    """

    # ===== COUNT =====
    count_query = f"""
    {ENTITY_MATCH}
    MATCH (e)<-[:{rel}]-(d)
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

    if entity_type == "document":
        from services.graph_service import get_graph_data
        return get_graph_data(entity_id)

    relation_map = {
        "author": "HAS_AUTHOR",
        "subject": "HAS_SUBJECT",
        "keyword": "HAS_KEYWORD",
        "publisher": "PUBLISHED_BY|SUBMITTED_TO"
    }

    if entity_type not in relation_map:
        return {"nodes": [], "edges": []}

    rel = relation_map[entity_type]

    query = f"""
    {ENTITY_MATCH}
    MATCH (e)<-[:{rel}]-(d)
    RETURN e, collect(d) AS docs, collect(labels(d)) AS labels_list
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

    # ===== DOCUMENT NODES =====
    all_docs = record.get("docs", [])
    all_labels = record.get("labels_list", [])

    for i in range(len(all_docs)):
        d = all_docs[i]
        d_labels = all_labels[i] if i < len(all_labels) else []
        doc_id = d.get("id")

        if not doc_id: continue

        # Detect group
        doc_group = "book"
        if "Article" in d_labels: doc_group = "article"
        elif "Thesis" in d_labels: doc_group = "thesis"

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
            "to": doc_id
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "center_id": e_id
    }