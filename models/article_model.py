from database.neo4j_connection import neo4j_conn


# =========================
# GET ARTICLE DETAIL (FULL)
# =========================
def get_article_detail(article_id):
    query = """
    MATCH (a:Article {id:$id})

    OPTIONAL MATCH (a)-[:HAS_AUTHOR]->(au:Author)
    OPTIONAL MATCH (a)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (a)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (a)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (a)-[:PUBLISHED_IN]->(j:Journal)

    RETURN
        a.id AS id,
        a.title AS title,
        a.year AS year,
        a.doi AS doi,
        a.abstract AS abstract,

        collect(DISTINCT au.name) AS authors,
        collect(DISTINCT s.name) AS subjects,
        collect(DISTINCT k.name) AS keywords,
        collect(DISTINCT l.name) AS languages,

        head(collect(DISTINCT j.name)) AS journal
    """

    result = neo4j_conn.query(query, {"id": article_id})
    return result[0] if result else None


# =========================
# CREATE
# =========================
def create_article(data):
    query = """
    CREATE (a:Article {
        id: $id,
        title: $title,
        year: $year,
        doi: $doi,
        abstract: $abstract
    })
    RETURN a
    """
    return neo4j_conn.query(query, data)


# =========================
# GET ALL + PAGINATION
# =========================
def get_all_articles(skip=0, limit=20):
    query = """
    MATCH (a:Article)

    OPTIONAL MATCH (a)-[:HAS_AUTHOR]->(au:Author)

    RETURN
        a.id AS id,
        a.title AS title,
        a.year AS year,
        collect(DISTINCT au.name) AS authors

    ORDER BY a.year DESC
    SKIP $skip LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "skip": skip,
        "limit": limit
    })


# =========================
# COUNT
# =========================
def count_articles():
    query = """
    MATCH (a:Article)
    RETURN count(a) AS total
    """
    result = neo4j_conn.query(query)
    return result[0]["total"] if result else 0


# =========================
# UPDATE
# =========================
def update_article(article_id, data):
    query = """
    MATCH (a:Article {id:$id})
    SET a.title = $title,
        a.year = $year,
        a.doi = $doi,
        a.abstract = $abstract
    RETURN a
    """

    params = {"id": article_id, **data}
    return neo4j_conn.query(query, params)


# =========================
# DELETE
# =========================
def delete_article(article_id):
    query = """
    MATCH (a:Article {id:$id})
    DETACH DELETE a
    """
    return neo4j_conn.query(query, {"id": article_id})