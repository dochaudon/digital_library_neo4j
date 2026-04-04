from database.neo4j_connection import neo4j_conn


# =========================
# GET THESIS DETAIL (FULL)
# =========================
def get_thesis_detail(thesis_id):
    query = """
    MATCH (t:Thesis {id:$id})

    OPTIONAL MATCH (t)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (t)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (t)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (t)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (t)-[:SUBMITTED_TO]->(u:Institution)

    RETURN
        t.id AS id,
        t.title AS title,
        t.year AS year,
        t.degree AS degree,
        t.abstract AS abstract,

        collect(DISTINCT a.name) AS authors,
        collect(DISTINCT s.name) AS subjects,
        collect(DISTINCT k.name) AS keywords,
        collect(DISTINCT l.name) AS languages,

        head(collect(DISTINCT u.name)) AS university
    """

    result = neo4j_conn.query(query, {"id": thesis_id})
    return result[0] if result else None


# =========================
# CREATE
# =========================
def create_thesis(data):
    query = """
    CREATE (t:Thesis {
        id: $id,
        title: $title,
        year: $year,
        degree: $degree,
        abstract: $abstract
    })
    RETURN t
    """
    return neo4j_conn.query(query, data)


# =========================
# GET ALL + PAGINATION
# =========================
def get_all_thesis(skip=0, limit=20):
    query = """
    MATCH (t:Thesis)

    OPTIONAL MATCH (t)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        t.id AS id,
        t.title AS title,
        t.year AS year,
        t.degree AS degree,
        collect(DISTINCT a.name) AS authors

    ORDER BY t.year DESC
    SKIP $skip LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "skip": skip,
        "limit": limit
    })


# =========================
# COUNT
# =========================
def count_thesis():
    query = """
    MATCH (t:Thesis)
    RETURN count(t) AS total
    """
    result = neo4j_conn.query(query)
    return result[0]["total"] if result else 0


# =========================
# UPDATE
# =========================
def update_thesis(thesis_id, data):
    query = """
    MATCH (t:Thesis {id:$id})
    SET t.title = $title,
        t.year = $year,
        t.degree = $degree,
        t.abstract = $abstract
    RETURN t
    """

    params = {"id": thesis_id, **data}
    return neo4j_conn.query(query, params)


# =========================
# DELETE
# =========================
def delete_thesis(thesis_id):
    query = """
    MATCH (t:Thesis {id:$id})
    DETACH DELETE t
    """
    return neo4j_conn.query(query, {"id": thesis_id})