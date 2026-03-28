from database.neo4j_connection import neo4j_conn


# =========================
# BOOK GRAPH
# =========================
def get_book_graph_data(document_id):

    query = """
    MATCH (b:Book {id:$id})

    OPTIONAL MATCH (b)-[:WRITTEN_BY]->(a:Author)
    OPTIONAL MATCH (b)-[:BELONGS_TO]->(t:Topic)
    OPTIONAL MATCH (b)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (b)-[:WRITTEN_IN]->(l:Language)
    OPTIONAL MATCH (b)-[:PUBLISHED_BY]->(p:Publisher)
    OPTIONAL MATCH (b)-[:RELATED_TO]->(rb:Book)

    RETURN
        b,
        collect(DISTINCT a) AS authors,
        collect(DISTINCT t) AS topics,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT l) AS languages,
        collect(DISTINCT p) AS publishers,
        collect(DISTINCT rb) AS related_books
    """

    result = neo4j_conn.query(query, {"id": document_id})

    if not result:
        return {"nodes": [], "edges": []}

    r = result[0]

    nodes = []
    edges = []

    center_id = document_id

    # ===== CENTER NODE =====
    nodes.append({
        "id": center_id,
        "label": r["b"]["title"],
        "group": "book",
        "title": r["b"]["title"]
    })

    # ===== AUTHORS =====
    for a in r["authors"]:
        if a:
            aid = f"author-{a.get('id') or a.get('name')}"
            nodes.append({
                "id": aid,
                "label": a.get("name"),
                "group": "author",
                "title": a.get("affiliation", "Tác giả")
            })
            edges.append({"from": center_id, "to": aid})

    # ===== TOPICS =====
    for t in r["topics"]:
        if t:
            tid = f"topic-{t.get('id') or t.get('name')}"
            nodes.append({
                "id": tid,
                "label": t.get("name"),
                "group": "topic",
                "title": t.get("description", "Chủ đề")
            })
            edges.append({"from": center_id, "to": tid})

    # ===== KEYWORDS =====
    for k in r["keywords"]:
        if k:
            kid = f"keyword-{k.get('id') or k.get('name')}"
            nodes.append({
                "id": kid,
                "label": k.get("name"),
                "group": "keyword",
                "title": "Từ khóa"
            })
            edges.append({"from": center_id, "to": kid})

    # ===== LANGUAGES =====
    for l in r["languages"]:
        if l:
            lid = f"lang-{l.get('id') or l.get('name')}"
            nodes.append({
                "id": lid,
                "label": l.get("name"),
                "group": "language",
                "title": "Ngôn ngữ"
            })
            edges.append({"from": center_id, "to": lid})

    # ===== PUBLISHERS =====
    for p in r["publishers"]:
        if p:
            pid = f"pub-{p.get('id') or p.get('name')}"
            nodes.append({
                "id": pid,
                "label": p.get("name"),
                "group": "publisher",
                "title": p.get("country", "NXB")
            })
            edges.append({"from": center_id, "to": pid})

    # ===== RELATED BOOKS =====
    for rb in r["related_books"]:
        if rb:
            rid = f"rel-{rb.get('id')}"
            nodes.append({
                "id": rid,
                "label": rb.get("title"),
                "group": "related",
                "title": "Sách liên quan"
            })
            edges.append({"from": center_id, "to": rid})

    return {
        "nodes": nodes,
        "edges": edges
    }


# =========================
# ARTICLE GRAPH
# =========================
def get_article_graph_data(article_id):

    query = """
    MATCH (a:Article {id:$id})

    OPTIONAL MATCH (a)-[:WRITTEN_BY]->(au:Author)
    OPTIONAL MATCH (a)-[:BELONGS_TO]->(t:Topic)
    OPTIONAL MATCH (a)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (a)-[:PUBLISHED_IN]->(j:Journal)
    OPTIONAL MATCH (a)-[:WRITTEN_IN]->(l:Language)
    OPTIONAL MATCH (a)-[:RELATED_TO]->(ra:Article)

    RETURN
        a,
        collect(DISTINCT au) AS authors,
        collect(DISTINCT t) AS topics,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT j) AS journals,
        collect(DISTINCT l) AS languages,
        collect(DISTINCT ra) AS related_articles
    """

    result = neo4j_conn.query(query, {"id": article_id})

    if not result:
        return {"nodes": [], "edges": []}

    r = result[0]

    nodes = []
    edges = []

    center_id = f"article-{article_id}"

    # ===== CENTER =====
    nodes.append({
        "id": center_id,
        "label": r["a"]["title"],
        "kind": "article",
        "group": "article",
        "title": r["a"]["title"]
    })

    # ===== AUTHORS =====
    for a in r["authors"]:
        if a:
            aid = f"author-{a.get('id') or a.get('name')}"
            nodes.append({
                "id": aid,
                "label": a.get("name"),
                "kind": "author",
                "group": "author",
                "title": a.get("affiliation", "Tác giả")
            })
            edges.append({"from": center_id, "to": aid})

    # ===== TOPICS =====
    for t in r["topics"]:
        if t:
            tid = f"topic-{t.get('id') or t.get('name')}"
            nodes.append({
                "id": tid,
                "label": t.get("name"),
                "kind": "topic",
                "group": "topic",
                "title": t.get("description", "Chủ đề")
            })
            edges.append({"from": center_id, "to": tid})

    # ===== KEYWORDS =====
    for k in r["keywords"]:
        if k:
            kid = f"keyword-{k.get('id') or k.get('name')}"
            nodes.append({
                "id": kid,
                "label": k.get("name"),
                "kind": "keyword",
                "group": "keyword",
                "title": "Từ khóa"
            })
            edges.append({"from": center_id, "to": kid})

    # ===== JOURNAL =====
    for j in r["journals"]:
        if j:
            jid = f"journal-{j.get('id') or j.get('name')}"
            nodes.append({
                "id": jid,
                "label": j.get("name"),
                "kind": "journal",
                "group": "journal",
                "title": "Tạp chí"
            })
            edges.append({"from": center_id, "to": jid})

    # ===== LANGUAGE =====
    for l in r["languages"]:
        if l:
            lid = f"lang-{l.get('id') or l.get('name')}"
            nodes.append({
                "id": lid,
                "label": l.get("name"),
                "kind": "language",
                "group": "language",
                "title": "Ngôn ngữ"
            })
            edges.append({"from": center_id, "to": lid})

    # ===== RELATED =====
    for ra in r["related_articles"]:
        if ra:
            rid = f"rel-{ra.get('id')}"
            nodes.append({
                "id": rid,
                "label": ra.get("title"),
                "kind": "related_article",
                "group": "related_article",
                "title": "Bài báo liên quan"
            })
            edges.append({"from": center_id, "to": rid})

    return {
        "nodes": nodes,
        "edges": edges
    }


# =========================
# THESIS GRAPH
# =========================
def get_thesis_graph_data(thesis_id):

    query = """
    MATCH (t:Thesis {id:$id})

    OPTIONAL MATCH (t)-[:WRITTEN_BY]->(a:Author)
    OPTIONAL MATCH (t)-[:BELONGS_TO]->(tp:Topic)
    OPTIONAL MATCH (t)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (t)-[:SUBMITTED_TO]->(u:University)
    OPTIONAL MATCH (t)-[:WRITTEN_IN]->(l:Language)
    OPTIONAL MATCH (t)-[:RELATED_TO]->(rt:Thesis)

    RETURN
        t,
        collect(DISTINCT a) AS authors,
        collect(DISTINCT tp) AS topics,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT u) AS universities,
        collect(DISTINCT l) AS languages,
        collect(DISTINCT rt) AS related_thesis
    """

    result = neo4j_conn.query(query, {"id": thesis_id})

    if not result:
        return {"nodes": [], "edges": []}

    r = result[0]

    nodes = []
    edges = []

    center_id = f"thesis-{thesis_id}"

    # ===== CENTER =====
    nodes.append({
        "id": center_id,
        "label": r["t"]["title"],
        "kind": "thesis",
        "group": "thesis",
        "title": r["t"]["title"]
    })

    # ===== AUTHORS =====
    for a in r["authors"]:
        if a:
            aid = f"author-{a.get('id') or a.get('name')}"
            nodes.append({
                "id": aid,
                "label": a.get("name"),
                "kind": "author",
                "group": "author",
                "title": a.get("affiliation", "Tác giả")
            })
            edges.append({"from": center_id, "to": aid})

    # ===== TOPICS =====
    for t in r["topics"]:
        if t:
            tid = f"topic-{t.get('id') or t.get('name')}"
            nodes.append({
                "id": tid,
                "label": t.get("name"),
                "kind": "topic",
                "group": "topic",
                "title": t.get("description", "Chủ đề")
            })
            edges.append({"from": center_id, "to": tid})

    # ===== KEYWORDS =====
    for k in r["keywords"]:
        if k:
            kid = f"keyword-{k.get('id') or k.get('name')}"
            nodes.append({
                "id": kid,
                "label": k.get("name"),
                "kind": "keyword",
                "group": "keyword",
                "title": "Từ khóa"
            })
            edges.append({"from": center_id, "to": kid})

    # ===== UNIVERSITY =====
    for u in r["universities"]:
        if u:
            uid = f"uni-{u.get('id') or u.get('name')}"
            nodes.append({
                "id": uid,
                "label": u.get("name"),
                "kind": "university",
                "group": "university",
                "title": "Trường"
            })
            edges.append({"from": center_id, "to": uid})

    # ===== LANGUAGE =====
    for l in r["languages"]:
        if l:
            lid = f"lang-{l.get('id') or l.get('name')}"
            nodes.append({
                "id": lid,
                "label": l.get("name"),
                "kind": "language",
                "group": "language",
                "title": "Ngôn ngữ"
            })
            edges.append({"from": center_id, "to": lid})

    # ===== RELATED THESIS =====
    for rt in r["related_thesis"]:
        if rt:
            rid = f"rel-{rt.get('id')}"
            nodes.append({
                "id": rid,
                "label": rt.get("title"),
                "kind": "related_thesis",
                "group": "related",
                "title": "Luận văn liên quan"
            })
            edges.append({"from": center_id, "to": rid})

    return {
        "nodes": nodes,
        "edges": edges
    }