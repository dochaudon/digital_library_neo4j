from database.neo4j_connection import neo4j_conn

print("Starting DB migration...")

queries = [
    """
    MATCH (n:Book)
    SET n:Document
    SET n.type = 'Book'
    REMOVE n:Book
    """,
    """
    MATCH (n:Article)
    SET n:Document
    SET n.type = 'Article'
    REMOVE n:Article
    """,
    """
    MATCH (n:Thesis)
    SET n:Document
    SET n.type = 'Thesis'
    REMOVE n:Thesis
    """,
    """
    MATCH (n:Document)
    WHERE n.type = 'book' OR n.type = 'article' OR n.type = 'thesis'
    SET n.type = CASE
        WHEN n.type = 'book' THEN 'Book'
        WHEN n.type = 'article' THEN 'Article'
        WHEN n.type = 'thesis' THEN 'Thesis'
        ELSE coalesce(n.type, 'Document')
    END
    """
]

for q in queries:
    neo4j_conn.query(q)
    print("Executed query")

print("Migration done")
