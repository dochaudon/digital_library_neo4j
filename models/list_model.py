from database.neo4j_connection import neo4j_conn


# ===== BOOK =====
def get_books(skip, limit):
    query = """
    MATCH (b:Book)
    OPTIONAL MATCH (b)-[:WRITTEN_BY]->(a:Author)
    OPTIONAL MATCH (b)-[:PUBLISHED_BY]->(p:Publisher)
    RETURN b.id AS id, b.title AS title, b.year AS year,
           b.isbn AS isbn,
           collect(a.name) AS authors,
           p.name AS publisher
    SKIP $skip LIMIT $limit
    """
    return neo4j_conn.query(query, {"skip": skip, "limit": limit})


def count_books():
    return neo4j_conn.query(
        "MATCH (b:Book) RETURN count(b) AS total"
    )[0]["total"]


# ===== ARTICLE =====
def get_articles(skip, limit):
    query = """
    MATCH (a:Article)
    OPTIONAL MATCH (a)-[:WRITTEN_BY]->(au:Author)
    RETURN a.id AS id, a.title AS title, a.year AS year,
           a.journal AS journal,
           a.doi AS doi,
           collect(au.name) AS authors
    SKIP $skip LIMIT $limit
    """
    return neo4j_conn.query(query, {"skip": skip, "limit": limit})


def count_articles():
    return neo4j_conn.query(
        "MATCH (a:Article) RETURN count(a) AS total"
    )[0]["total"]


# ===== THESIS =====
def get_thesis(skip, limit):
    query = """
    MATCH (t:Thesis)
    OPTIONAL MATCH (t)-[:WRITTEN_BY]->(a:Author)
    OPTIONAL MATCH (t)-[:SUBMITTED_TO]->(u:University)
    RETURN t.id AS id, t.title AS title, t.year AS year,
           t.degree AS degree,
           collect(a.name) AS authors,
           u.name AS university
    SKIP $skip LIMIT $limit
    """
    return neo4j_conn.query(query, {"skip": skip, "limit": limit})


def count_thesis():
    return neo4j_conn.query(
        "MATCH (t:Thesis) RETURN count(t) AS total"
    )[0]["total"]