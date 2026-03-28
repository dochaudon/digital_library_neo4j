from database.neo4j_connection import neo4j_conn

def get_book_by_id(id):
    query = """
    MATCH (b:Book {id:$id})

    CALL {
        WITH b
        OPTIONAL MATCH (b)-[:WRITTEN_BY]->(a:Author)
        WITH collect(DISTINCT a) AS items
        RETURN
            [x IN items WHERE x IS NOT NULL |
                {
                    name: x.name,
                    affiliation: x.affiliation,
                    country: x.country,
                    email: x.email
                }
            ] AS authors_info,
            [x IN items WHERE x IS NOT NULL | x.name] AS authors
    }

    CALL {
        WITH b
        OPTIONAL MATCH (b)-[:BELONGS_TO]->(t:Topic)
        WITH collect(DISTINCT t) AS items
        RETURN
            [x IN items WHERE x IS NOT NULL | x.name] AS topics
    }

    CALL {
        WITH b
        OPTIONAL MATCH (b)-[:HAS_KEYWORD]->(k:Keyword)
        WITH collect(DISTINCT k) AS items
        RETURN
            [x IN items WHERE x IS NOT NULL | x.name] AS keywords
    }

    CALL {
        WITH b
        OPTIONAL MATCH (b)-[:WRITTEN_IN]->(l:Language)
        WITH collect(DISTINCT l) AS items
        RETURN
            [x IN items WHERE x IS NOT NULL | x.name] AS languages
    }

    OPTIONAL MATCH (b)-[:PUBLISHED_BY]->(p:Publisher)

    RETURN
        b.id AS id,
        b.title AS title,
        b.year AS year,
        b.isbn AS isbn,
        b.pages AS pages,
        b.abstract AS abstract,
        b.file_url AS file_url,
        head(collect(DISTINCT p.name)) AS publisher,
        authors,
        authors_info,
        topics,
        keywords,
        languages
    """

    result = neo4j_conn.query(query, {"id": id})
    return result[0] if result else None

# CREATE
def create_book(data):
    query = """
    CREATE (b:Book {
        id: $id,
        title: $title,
        year: $year,
        isbn: $isbn,
        pages: $pages,
        abstract: $abstract
    })
    RETURN b
    """
    return neo4j_conn.query(query, data)


# GET ALL
def get_all_books():
    query = """
    MATCH (b:Book)
    RETURN b.id AS id, b.title AS title, b.year AS year
    ORDER BY b.year DESC
    """
    return neo4j_conn.query(query)


# GET BY ID
def get_book_by_id(id):
    query = """
    MATCH (b:Book {id:$id})
    RETURN b
    """
    result = neo4j_conn.query(query, {"id": id})
    return result[0]["b"] if result else None


# UPDATE
def update_book(id, data):
    query = """
    MATCH (b:Book {id:$id})
    SET b.title = $title,
        b.year = $year,
        b.isbn = $isbn,
        b.pages = $pages,
        b.abstract = $abstract
    RETURN b
    """
    params = {"id": id, **data}
    return neo4j_conn.query(query, params)


# DELETE
def delete_book(id):
    query = """
    MATCH (b:Book {id:$id})
    DETACH DELETE b
    """
    return neo4j_conn.query(query, {"id": id})