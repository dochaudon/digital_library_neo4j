from database.neo4j_connection import neo4j_conn


# =========================
# PREVIEW (POPUP)
# =========================
def get_preview(entity_type, entity_id):

    # ===== AUTHOR =====
    if entity_type == "author":
        query = """
        MATCH (a:Author {id:$id})<-[:HAS_AUTHOR]-(d)
        RETURN d.id AS id, d.title AS title
        ORDER BY d.year DESC
        LIMIT 5
        """

        result = neo4j_conn.query(query, {"id": entity_id})

        return {
            "type": "author",
            "documents": result
        }

    # ===== SUBJECT =====
    if entity_type == "subject":
        query = """
        MATCH (s:Subject {name:$id})<-[:HAS_SUBJECT]-(d)
        RETURN d.id AS id, d.title AS title
        ORDER BY d.year DESC
        LIMIT 5
        """

        result = neo4j_conn.query(query, {"id": entity_id})

        return {
            "type": "subject",
            "documents": result
        }

    # ===== DOCUMENT =====
    if entity_type == "document":
        query = """
        MATCH (d {id:$id})
        RETURN d.id AS id, d.title AS title, d.year AS year
        """

        result = neo4j_conn.query(query, {"id": entity_id})

        return {
            "type": "document",
            "data": result[0] if result else {}
        }

    return {}


# =========================
# ENTITY DETAIL (LEFT PANEL)
# =========================
def get_entity_detail(entity_type, entity_id, page=1, limit=10):

    skip = (page - 1) * limit

    # ===== AUTHOR =====
    if entity_type == "author":

        query = """
        MATCH (a:Author {id:$id})<-[:HAS_AUTHOR]-(d)
        RETURN d.id AS id, d.title AS title, d.year AS year
        ORDER BY d.year DESC
        SKIP $skip LIMIT $limit
        """

        count_query = """
        MATCH (a:Author {id:$id})<-[:HAS_AUTHOR]-(d)
        RETURN count(d) AS total
        """

        docs = neo4j_conn.query(query, {
            "id": entity_id,
            "skip": skip,
            "limit": limit
        })

        total = neo4j_conn.query(count_query, {"id": entity_id})[0]["total"]

        return {
            "type": "author",
            "documents": docs,
            "total": total,
            "page": page
        }

    # ===== SUBJECT =====
    if entity_type == "subject":

        query = """
        MATCH (s:Subject {name:$id})<-[:HAS_SUBJECT]-(d)
        RETURN d.id AS id, d.title AS title, d.year AS year
        ORDER BY d.year DESC
        SKIP $skip LIMIT $limit
        """

        docs = neo4j_conn.query(query, {
            "id": entity_id,
            "skip": skip,
            "limit": limit
        })

        return {
            "type": "subject",
            "documents": docs,
            "page": page
        }

    # ===== DOCUMENT =====
    if entity_type == "document":

        query = """
        MATCH (d {id:$id})

        OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
        OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)

        RETURN
            d.id AS id,
            d.title AS title,
            d.year AS year,
            collect(DISTINCT a.name) AS authors,
            collect(DISTINCT s.name) AS subjects
        """

        result = neo4j_conn.query(query, {"id": entity_id})

        return {
            "type": "document",
            "data": result[0] if result else {}
        }

    return {}


# =========================
# GRAPH BY ENTITY
# =========================
def get_graph_by_entity(entity_type, entity_id):

    # ===== DOCUMENT =====
    if entity_type == "document":
        from services.graph_service import get_graph_data
        return get_graph_data(entity_id)

    nodes = []
    edges = []
    node_ids = set()

    # ===== AUTHOR GRAPH =====
    if entity_type == "author":

        query = """
        MATCH (a:Author {id:$id})<-[:HAS_AUTHOR]-(d)
        RETURN a, d
        """

        results = neo4j_conn.query(query, {"id": entity_id})

        # center node
        nodes.append({
            "id": entity_id,
            "label": "Author",
            "group": "author"
        })
        node_ids.add(entity_id)

        for r in results:
            d = r["d"]

            doc_id = d.get("id")

            if doc_id not in node_ids:
                nodes.append({
                    "id": doc_id,
                    "label": d.get("title"),
                    "group": "book"
                })
                node_ids.add(doc_id)

            edges.append({
                "from": entity_id,
                "to": doc_id
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "center_id": entity_id
        }

    # ===== SUBJECT GRAPH =====
    if entity_type == "subject":

        query = """
        MATCH (s:Subject {name:$id})<-[:HAS_SUBJECT]-(d)
        RETURN s, d
        """

        results = neo4j_conn.query(query, {"id": entity_id})

        nodes.append({
            "id": entity_id,
            "label": entity_id,
            "group": "subject"
        })
        node_ids.add(entity_id)

        for r in results:
            d = r["d"]

            doc_id = d.get("id")

            if doc_id not in node_ids:
                nodes.append({
                    "id": doc_id,
                    "label": d.get("title"),
                    "group": "book"
                })
                node_ids.add(doc_id)

            edges.append({
                "from": entity_id,
                "to": doc_id
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "center_id": entity_id
        }

    return {
        "nodes": [],
        "edges": []
    }