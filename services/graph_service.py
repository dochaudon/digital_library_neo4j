from database.neo4j_connection import neo4j_conn


# =========================
# GET GRAPH DATA (UNIFIED)
# =========================
def get_graph_data(document_id):

    if not document_id:
        return {"nodes": [], "edges": []}

    query = """
    MATCH (d {id: $id})

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Institution)
    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:Institution)

    RETURN
        d,
        labels(d) AS labels,
        collect(DISTINCT a) AS authors,
        collect(DISTINCT s) AS subjects,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT p) AS publishers,
        collect(DISTINCT u) AS universities
    """

    result = neo4j_conn.query(query, {"id": document_id})

    if not result:
        return {"nodes": [], "edges": []}

    record = result[0]

    nodes = []
    edges = []
    node_ids = set()

    d = record.get("d") or {}
    labels = record.get("labels") or []

    # =========================
    # DETECT DOCUMENT TYPE
    # =========================
    doc_group = "book"

    if "Article" in labels:
        doc_group = "article"
    elif "Thesis" in labels:
        doc_group = "thesis"

    doc_id = d.get("id")
    doc_title = d.get("title") or "Unknown"

    # =========================
    # ADD DOCUMENT NODE
    # =========================
    nodes.append({
        "id": doc_id,
        "label": doc_title,
        "group": doc_group
    })

    node_ids.add(doc_id)

    # =========================
    # HELPER FUNCTION (FIXED)
    # =========================
    def add_nodes_and_edges(items, group, rel_type):
        if not items:
            return

        for item in items:
            if not item:
                continue

            name = item.get("name") or item.get("title") or "Unknown"

            # 🔥 FIX DUPLICATE NODE
            node_id = item.get("id") or f"{group}_{name}"

            if node_id not in node_ids:
                nodes.append({
                    "id": node_id,
                    "label": name,
                    "group": group
                })
                node_ids.add(node_id)

            edges.append({
                "from": doc_id,
                "to": node_id,
                "label": rel_type
            })

    # =========================
    # ADD RELATIONS (FIXED)
    # =========================
    add_nodes_and_edges(record.get("authors"), "author", "HAS_AUTHOR")
    add_nodes_and_edges(record.get("subjects"), "subject", "HAS_SUBJECT")
    add_nodes_and_edges(record.get("keywords"), "keyword", "HAS_KEYWORD")
    add_nodes_and_edges(record.get("publishers"), "publisher", "PUBLISHED_BY")
    add_nodes_and_edges(record.get("universities"), "university", "SUBMITTED_TO")  # 🔥 FIX

    return {
        "nodes": nodes,
        "edges": edges,
        "center_id": doc_id
    }


# =========================
# WRAPPER (GIỮ CHUẨN SERVICE)
# =========================
def get_document_graph_service(document_id):
    return get_graph_data(document_id)


def get_graph_auto(document_id):
    return get_graph_data(document_id)