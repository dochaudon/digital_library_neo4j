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

    # dùng set để tránh trùng node
    node_ids = set()

    # =========================
    # DETECT DOCUMENT TYPE
    # =========================
    d = record["d"]
    labels = record["labels"]

    doc_group = "book"  # default

    if "Article" in labels:
        doc_group = "article"
    elif "Thesis" in labels:
        doc_group = "thesis"

    # =========================
    # ADD DOCUMENT NODE (CENTER)
    # =========================
    nodes.append({
        "id": d.get("id"),
        "label": d.get("title"),
        "group": doc_group
    })

    node_ids.add(d.get("id"))

    # =========================
    # HELPER FUNCTION
    # =========================
    def add_nodes_and_edges(items, group, rel_type):
        for item in items:
            if not item:
                continue

            node_id = item.get("id") or item.get("name")

            if not node_id:
                continue

            # tránh trùng node
            if node_id not in node_ids:
                nodes.append({
                    "id": node_id,
                    "label": item.get("name"),
                    "group": group
                })
                node_ids.add(node_id)

            edges.append({
                "from": d.get("id"),
                "to": node_id,
                "label": rel_type
            })

    # =========================
    # ADD RELATIONS
    # =========================
    add_nodes_and_edges(record["authors"], "author", "HAS_AUTHOR")
    add_nodes_and_edges(record["subjects"], "subject", "HAS_SUBJECT")
    add_nodes_and_edges(record["keywords"], "keyword", "HAS_KEYWORD")
    add_nodes_and_edges(record["publishers"], "publisher", "PUBLISHED_BY")
    add_nodes_and_edges(record["universities"], "publisher", "SUBMITTED_TO")

    return {
        "nodes": nodes,
        "edges": edges,
        "center_id": d.get("id")   # 🔥 QUAN TRỌNG
    }


# =========================
# AUTO WRAPPER
# =========================
def get_graph_auto(document_id):
    return get_graph_data(document_id)