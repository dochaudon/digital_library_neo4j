from database.neo4j_connection import neo4j_conn


# =========================
# COMMON BUILDER
# =========================
def build_graph(center_id, center_label, center_group, data):

    nodes = []
    edges = []

    nodes.append({
        "id": center_id,
        "label": center_label,
        "group": center_group,
        "title": center_label
    })

    def add_nodes(items, prefix, group):
        for item in items:
            if item:
                nid = f"{prefix}-{item.get('id') or item.get('name')}"
                nodes.append({
                    "id": nid,
                    "label": item.get("name"),
                    "group": group,
                    "title": group
                })
                edges.append({"from": center_id, "to": nid})

    add_nodes(data.get("authors", []), "author", "author")
    add_nodes(data.get("subjects", []), "subject", "subject")
    add_nodes(data.get("keywords", []), "keyword", "keyword")
    add_nodes(data.get("languages", []), "lang", "language")
    add_nodes(data.get("institutions", []), "inst", "institution")
    add_nodes(data.get("related", []), "rel", "related")

    return {"nodes": nodes, "edges": edges}


# =========================
# BOOK GRAPH
# =========================
def get_book_graph_data(document_id):

    query = """
    MATCH (b:Book {id:$id})

    OPTIONAL MATCH (b)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (b)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (b)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (b)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (b)-[:PUBLISHED_BY]->(p:Institution)
    OPTIONAL MATCH (b)-[:RELATED_TO]->(rb:Book)

    RETURN
        b,
        collect(DISTINCT a) AS authors,
        collect(DISTINCT s) AS subjects,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT l) AS languages,
        collect(DISTINCT p) AS institutions,
        collect(DISTINCT rb) AS related
    """

    result = neo4j_conn.query(query, {"id": document_id})
    if not result:
        return {"nodes": [], "edges": []}

    r = result[0]

    return build_graph(
        document_id,
        r["b"]["title"],
        "book",
        r
    )


# =========================
# ARTICLE GRAPH
# =========================
def get_article_graph_data(article_id):

    query = """
    MATCH (a:Article {id:$id})

    OPTIONAL MATCH (a)-[:HAS_AUTHOR]->(au:Author)
    OPTIONAL MATCH (a)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (a)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (a)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (a)-[:PUBLISHED_IN]->(j:Journal)
    OPTIONAL MATCH (a)-[:RELATED_TO]->(ra:Article)

    RETURN
        a,
        collect(DISTINCT au) AS authors,
        collect(DISTINCT s) AS subjects,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT l) AS languages,
        collect(DISTINCT j) AS institutions,
        collect(DISTINCT ra) AS related
    """

    result = neo4j_conn.query(query, {"id": article_id})
    if not result:
        return {"nodes": [], "edges": []}

    r = result[0]

    return build_graph(
        f"article-{article_id}",
        r["a"]["title"],
        "article",
        r
    )


# =========================
# THESIS GRAPH
# =========================
def get_thesis_graph_data(thesis_id):

    query = """
    MATCH (t:Thesis {id:$id})

    OPTIONAL MATCH (t)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (t)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (t)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (t)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (t)-[:SUBMITTED_TO]->(u:Institution)
    OPTIONAL MATCH (t)-[:RELATED_TO]->(rt:Thesis)

    RETURN
        t,
        collect(DISTINCT a) AS authors,
        collect(DISTINCT s) AS subjects,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT l) AS languages,
        collect(DISTINCT u) AS institutions,
        collect(DISTINCT rt) AS related
    """

    result = neo4j_conn.query(query, {"id": thesis_id})
    if not result:
        return {"nodes": [], "edges": []}

    r = result[0]

    return build_graph(
        f"thesis-{thesis_id}",
        r["t"]["title"],
        "thesis",
        r
    )