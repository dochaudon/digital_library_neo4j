from database.neo4j_connection import neo4j_conn


# =========================
# GET DOCUMENT BY TITLE (BASE)
# =========================
def get_document_match_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type
    LIMIT 1
    """

    return neo4j_conn.query(query, {"title": title})


# =========================
# GET AUTHOR BY TITLE
# =========================
def get_author_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        d.id AS id,
        d.title AS title,
        collect(DISTINCT a.name) AS authors
    LIMIT 1
    """

    return neo4j_conn.query(query, {"title": title})


# =========================
# GET YEAR BY TITLE
# =========================
def get_year_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year
    LIMIT 1
    """

    return neo4j_conn.query(query, {"title": title})


# =========================
# GET SUBJECT BY TITLE
# =========================
def get_subject_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)

    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)

    RETURN
        d.id AS id,
        d.title AS title,
        collect(DISTINCT s.name) AS subjects
    LIMIT 1
    """

    return neo4j_conn.query(query, {"title": title})


# =========================
# GET PUBLISHER BY TITLE
# =========================
def get_publisher_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)

    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Institution)

    RETURN
        d.id AS id,
        d.title AS title,
        p.name AS publisher
    LIMIT 1
    """

    return neo4j_conn.query(query, {"title": title})


# =========================
# GET UNIVERSITY BY TITLE
# =========================
def get_university_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)

    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:Institution)

    RETURN
        d.id AS id,
        d.title AS title,
        u.name AS university
    LIMIT 1
    """

    return neo4j_conn.query(query, {"title": title})