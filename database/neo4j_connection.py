import os
# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

class Neo4jConnection:

    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        print(f"[NEO4J] Connecting to {uri} with user {user}")
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    def close(self):
        self.driver.close()

    def query(self, cypher_query, parameters=None):
        with self.driver.session(database="digitallibrary") as session:
            result = session.run(cypher_query, parameters)
            return [record.data() for record in result]


# Tạo instance
neo4j_conn = Neo4jConnection()