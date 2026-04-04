from database.neo4j_connection import neo4j_conn


# =========================
# GET BOOK DETAIL (FULL)
# =========================
def get_book_detail(book_id):
    query = """
    MATCH (b:Book {id:$id})

    OPTIONAL MATCH (b)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (b)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (b)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (b)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (b)-[:PUBLISHED_BY]->(p:Institution)

    RETURN
        b.id AS id,
        b.title AS title,
        b.year AS year,
        b.isbn AS isbn,
        b.pages AS pages,
        b.abstract AS abstract,
        b.file_url AS file_url,

        collect(DISTINCT a.name) AS authors,
        collect(DISTINCT s.name) AS subjects,
        collect(DISTINCT k.name) AS keywords,
        collect(DISTINCT l.name) AS languages,

        head(collect(DISTINCT p.name)) AS publisher
    """

    result = neo4j_conn.query(query, {"id": book_id})
    return result[0] if result else None


# =========================
# CREATE
# =========================
def create_book(data):
    query = """
    CREATE (b:Book {
        id: $id,
        title: $title,
        year: $year,
        isbn: $isbn,
        pages: $pages,
        abstract: $abstract,
        file_url: $file_url
    })
    RETURN b
    """
    return neo4j_conn.query(query, data)


# =========================
# GET ALL + PAGINATION
# =========================
def get_all_books(skip=0, limit=20):
    query = """
    MATCH (b:Book)

    OPTIONAL MATCH (b)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        b.id AS id,
        b.title AS title,
        b.year AS year,
        collect(DISTINCT a.name) AS authors

    ORDER BY b.year DESC
    SKIP $skip LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "skip": skip,
        "limit": limit
    })


# =========================
# COUNT
# =========================
def count_books():
    query = """
    MATCH (b:Book)
    RETURN count(b) AS total
    """
    result = neo4j_conn.query(query)
    return result[0]["total"] if result else 0


# =========================
# UPDATE
# =========================
def update_book(book_id, data):
    query = """
    MATCH (b:Book {id:$id})
    SET b.title = $title,
        b.year = $year,
        b.isbn = $isbn,
        b.pages = $pages,
        b.abstract = $abstract,
        b.file_url = $file_url
    RETURN b
    """

    params = {"id": book_id, **data}
    return neo4j_conn.query(query, params)


# =========================
# DELETE
# =========================
def delete_book(book_id):
    query = """
    MATCH (b:Book {id:$id})
    DETACH DELETE b
    """
    return neo4j_conn.query(query, {"id": book_id})