from database.neo4j_connection import neo4j_conn
from models.author_model import (
    create_author,
    get_all_authors,
    get_author_by_id,
    update_author,
    delete_author
)

def get_author_documents_service(author_name, page=1, limit=5):

    skip = (page - 1) * limit

    # lấy documents
    query = """
    MATCH (a:Author)
    WHERE toLower(a.name) CONTAINS toLower($name)

    MATCH (d)-[:HAS_AUTHOR]->(a)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        labels(d)[0] AS type
    ORDER BY d.year DESC
    SKIP $skip LIMIT $limit
    """

    documents = neo4j_conn.query(query, {
        "name": author_name,
        "skip": skip,
        "limit": limit
    })

    # đếm total
    count_query = """
    MATCH (a:Author)
    WHERE toLower(a.name) CONTAINS toLower($name)

    MATCH (d)-[:HAS_AUTHOR]->(a)
    RETURN count(d) AS total
    """

    total = neo4j_conn.query(count_query, {"name": author_name})[0]["total"]

    total_pages = (total // limit) + (1 if total % limit else 0)

    return {
        "documents": documents,
        "total_pages": total_pages
    }



def create_author_service(data):
    if not data.get("name"):
        raise ValueError("Name is required")
    return create_author(data)


def get_authors_service():
    return get_all_authors()


def get_author_detail_service(id):
    return get_author_by_id(id)


def update_author_service(id, data):
    if not data.get("name"):
        raise ValueError("Name is required")
    update_author(id, data)


def delete_author_service(id):
    delete_author(id)