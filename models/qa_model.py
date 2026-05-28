from database.neo4j_connection import neo4j_conn


# =========================
# GET DOCUMENT BY TITLE (BASE)
# =========================
def get_document_match_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
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
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

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
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

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
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

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
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Publisher)

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
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

    OPTIONAL MATCH (d)-[:OWNED_BY]->(u:University)

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
    WHERE toLower(a.name) STARTS WITH toLower($author)
      AND (d.status IS NULL OR d.status = 'active')

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
        END AS type
    ORDER BY d.year DESC
    LIMIT 20
    """

    return neo4j_conn.query(query, {"author": author})
def get_documents_by_subject(subject):
    query = """
    MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    WHERE toLower(s.name) STARTS WITH toLower($subject)
      AND (d.status IS NULL OR d.status = 'active')

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
        END AS type
    ORDER BY d.year DESC
    LIMIT 20
    """

    return neo4j_conn.query(query, {"subject": subject})


# =========================
# GET DOCS BY SUBJECT + RELATED SUBJECTS (for QA subject intent)
# =========================
def get_docs_by_subject_with_related(main_subjects, related_subjects, limit=10):
    """
    Returns two separate lists:
    - primary: docs having at least one subject in main_subjects
    - secondary: docs having at least one subject in related_subjects (not already in primary)
    """
    main_lower = [s.lower() for s in main_subjects if s]
    related_lower = [s.lower() for s in related_subjects if s]

    # Primary: exact main subject match
    primary_rows = neo4j_conn.query("""
    MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    WHERE toLower(s.name) IN $subjects
      AND (d:Document)
      AND (d.status IS NULL OR d.status = 'active')
    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    RETURN DISTINCT
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.image_url AS image_url,
        CASE
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
        END AS type,
        collect(DISTINCT a.name) AS authors
    ORDER BY d.year DESC
    LIMIT $limit
    """, {"subjects": main_lower, "limit": limit})

    primary_ids = {r["id"] for r in primary_rows}

    # Secondary: related subject match (exclude primary)
    secondary_rows = []
    if related_lower:
        secondary_rows = neo4j_conn.query("""
        MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
        WHERE toLower(s.name) IN $subjects
          AND (d:Document)
          AND NOT d.id IN $exclude_ids
          AND (d.status IS NULL OR d.status = 'active')
        OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
        RETURN DISTINCT
            d.id AS id,
            d.title AS title,
            d.year AS year,
            d.image_url AS image_url,
            CASE
                WHEN d.type = 'book' THEN 'Book'
                WHEN d.type = 'article' THEN 'Article'
                WHEN d.type = 'thesis' THEN 'Thesis'
            END AS type,
            collect(DISTINCT a.name) AS authors
        ORDER BY d.year DESC
        LIMIT $limit
        """, {"subjects": related_lower, "exclude_ids": list(primary_ids), "limit": limit})

    return list(primary_rows), list(secondary_rows)
def get_documents_by_keyword(keyword):
    query = """
    MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    WHERE toLower(k.name) STARTS WITH toLower($keyword)
      AND (d.status IS NULL OR d.status = 'active')

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
        END AS type
    ORDER BY d.year DESC
    LIMIT 20
    """

    return neo4j_conn.query(query, {"keyword": keyword})

def get_related_documents(doc_id):
    query = """
    MATCH (d {id: $id})-[:HAS_SUBJECT]->(s)<-[:HAS_SUBJECT]-(related)
    WHERE d <> related
      AND (related.status IS NULL OR related.status = 'active')

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
    WHERE (d:Document)
      AND (d.status IS NULL OR d.status = 'active')
    RETURN count(d) AS total
    """

    return neo4j_conn.query(query)

def get_top_authors(limit=5):
    query = """
    MATCH (a:Author)<-[:HAS_AUTHOR]-(d)
    WHERE d.status IS NULL OR d.status = 'active'
    RETURN a.name AS author, count(d) AS total
    ORDER BY total DESC
    LIMIT $limit
    """

    return neo4j_conn.query(query, {"limit": limit})

# =========================
# GET ABSTRACT BY TITLE
# =========================
def get_abstract_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

    RETURN
        d.id AS id,
        d.title AS title,
        d.abstract AS abstract
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})

# =========================
# GET KEYWORD BY TITLE
# =========================
def get_keyword_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)

    RETURN
        d.id AS id,
        d.title AS title,
        collect(DISTINCT k.name) AS keywords
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})

# =========================
# GET RELATED BY TITLE
# =========================
def get_related_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Document)
      AND toLower(d.title) CONTAINS toLower($title)
      AND (d.status IS NULL OR d.status = 'active')

    MATCH (d)-[:HAS_SUBJECT]->(s)<-[:HAS_SUBJECT]-(related)
    WHERE d <> related
      AND (related.status IS NULL OR related.status = 'active')

    RETURN
        related.id AS id,
        related.title AS title,
        related.year AS year
    LIMIT 5
    """
    return neo4j_conn.query(query, {"title": title})