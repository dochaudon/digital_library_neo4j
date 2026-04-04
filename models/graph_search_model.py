from database.neo4j_connection import neo4j_conn


# =========================
# GRAPH SEARCH MAIN
# =========================
def graph_search(filters, limit=20):

    if not any(filters.values()):
        return []

    cypher = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Institution)
    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:Institution)

    WITH d,
         collect(DISTINCT a.name) AS authors,
         collect(DISTINCT s.name) AS subjects,
         head(collect(DISTINCT p.name)) AS publisher,
         head(collect(DISTINCT u.name)) AS university

    WHERE
        ($doc_type IS NULL OR labels(d)[0] = $doc_type)

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) = toLower($author)))

        AND ($subject IS NULL OR
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)))

        AND ($publisher IS NULL OR
            (publisher IS NOT NULL AND toLower(publisher) CONTAINS toLower($publisher)))

        AND ($university IS NULL OR
            (university IS NOT NULL AND toLower(university) CONTAINS toLower($university)))

        AND ($year IS NULL OR d.year = $year)

    WITH d, authors, subjects, publisher, university,

    (
        CASE WHEN $doc_type IS NOT NULL AND labels(d)[0]=$doc_type THEN 1 ELSE 0 END +

        CASE 
            WHEN $author IS NOT NULL AND 
            ANY(x IN authors WHERE toLower(x) = toLower($author)) 
            THEN 3 ELSE 0 END +

        CASE 
            WHEN $subject IS NOT NULL AND 
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)) 
            THEN 2 ELSE 0 END +

        CASE 
            WHEN $publisher IS NOT NULL AND 
            publisher IS NOT NULL AND 
            toLower(publisher) CONTAINS toLower($publisher) 
            THEN 1 ELSE 0 END +

        CASE 
            WHEN $university IS NOT NULL AND 
            university IS NOT NULL AND 
            toLower(university) CONTAINS toLower($university) 
            THEN 1 ELSE 0 END +

        CASE 
            WHEN $year IS NOT NULL AND d.year = $year 
            THEN 1 ELSE 0 END
    ) AS score

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        labels(d)[0] AS type,
        authors,
        subjects,
        publisher,
        university,
        score AS relevance_score,
        'graph' AS source

    ORDER BY score DESC, d.year DESC
    LIMIT $limit
    """

    return neo4j_conn.query(
        cypher,
        {
            "doc_type": filters.get("doc_type"),
            "author": filters.get("author"),
            "subject": filters.get("subject"),
            "publisher": filters.get("publisher"),
            "university": filters.get("university"),
            "year": filters.get("year"),
            "limit": limit
        }
    )


# =========================
# QUICK SEARCH FUNCTIONS
# =========================

def search_by_author(author, limit=20):
    return graph_search({"author": author}, limit)


def search_by_subject(subject, limit=20):
    return graph_search({"subject": subject}, limit)


def search_by_publisher(publisher, limit=20):
    return graph_search({"publisher": publisher}, limit)


def search_by_university(university, limit=20):
    return graph_search({"university": university}, limit)


def search_by_year(year, limit=20):
    return graph_search({"year": year}, limit)