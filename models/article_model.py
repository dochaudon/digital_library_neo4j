from database.neo4j_connection import neo4j_conn

def get_article_by_id(id):
    query = """
    MATCH (a:Article {id:$id})
    OPTIONAL MATCH (a)-[:WRITTEN_BY]->(au:Author)

    RETURN 
        a.id AS id,
        a.title AS title,
        a.year AS year,
        a.journal AS journal,
        a.doi AS doi,
        collect(au.name) AS authors
    """
    result = neo4j_conn.query(query, {"id": id})
    return result[0] if result else None

from database.neo4j_connection import neo4j_conn

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
        journal: $journal,
        abstract: $abstract
    })
    RETURN a
    """
    return neo4j_conn.query(query, data)


# =========================
# GET ALL + PAGINATION
# =========================
def get_all_articles(skip=0, limit=10):
    query = """
    MATCH (a:Article)
    RETURN a.id AS id, a.title AS title, a.year AS year
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
def update_article(id, data):
    query = """
    MATCH (a:Article {id:$id})
    SET a.title = $title,
        a.year = $year,
        a.doi = $doi,
        a.journal = $journal,
        a.abstract = $abstract
    RETURN a
    """
    params = {"id": id, **data}
    return neo4j_conn.query(query, params)


# =========================
# DELETE
# =========================
def delete_article(id):
    query = """
    MATCH (a:Article {id:$id})
    DETACH DELETE a
    """
    return neo4j_conn.query(query, {"id": id})