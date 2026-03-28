from neo4j import GraphDatabase

class Neo4jConnection:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, cypher_query, parameters=None):

        with self.driver.session(database="digitallibrary") as session:

            result = session.run(cypher_query, parameters)

            data = []

            for record in result:
                data.append(record.data())

            return data


neo4j_conn = Neo4jConnection()