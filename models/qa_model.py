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
def get_documents_by_author(author):
    query = """
    MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    WHERE toLower(a.name) CONTAINS toLower($author)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type
    ORDER BY d.year DESC
    LIMIT 20
    """

    return neo4j_conn.query(query, {"author": author})
def get_documents_by_subject(subject):
    query = """
    MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    WHERE toLower(s.name) CONTAINS toLower($subject)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type
    ORDER BY d.year DESC
    LIMIT 20
    """

    return neo4j_conn.query(query, {"subject": subject})
def get_documents_by_keyword(keyword):
    query = """
    MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    WHERE toLower(k.name) CONTAINS toLower($keyword)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type
    ORDER BY d.year DESC
    LIMIT 20
    """

    return neo4j_conn.query(query, {"keyword": keyword})

def get_related_documents(doc_id):
    query = """
    MATCH (d {id: $id})-[:HAS_SUBJECT]->(s)<-[:HAS_SUBJECT]-(related)
    WHERE d <> related

    OPTIONAL MATCH (related)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        related.id AS id,
        related.title AS title,
        related.year AS year,
        collect(DISTINCT a.name) AS authors
    LIMIT 10
    """

    return neo4j_conn.query(query, {"id": doc_id})

def count_documents():
    query = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis
    RETURN count(d) AS total
    """

    return neo4j_conn.query(query)

def get_top_authors(limit=5):
    query = """
    MATCH (a:Author)<-[:HAS_AUTHOR]-(d)
    RETURN a.name AS author, count(d) AS total
    ORDER BY total DESC
    LIMIT $limit
    """

    return neo4j_conn.query(query, {"limit": limit})