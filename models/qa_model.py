import re

from database.neo4j_connection import neo4j_conn


QA_SCHEMA_CONTEXT = """
Knowledge graph schema:
- Nodes:
  - Document with labels Book, Article, Thesis
  - Author
  - Subject
  - Keyword
  - Category
  - Institution
  - Language
  - Journal
- Document properties:
  - id, title, alternative_title, type, year, pages, image_url, file_url, abstract
- Author properties:
  - id, name
- Subject properties:
  - id, name
- Keyword properties:
  - id, name
- Category properties:
  - id, name
- Institution properties:
  - id, name, type
- Language properties:
  - id, name
- Journal properties:
  - id, name
- Relationships:
  - (d)-[:HAS_AUTHOR {role}]->(a)
  - (d)-[:HAS_SUBJECT]->(s)
  - (d)-[:HAS_KEYWORD]->(k)
  - (d)-[:HAS_CATEGORY]->(c)
  - (d)-[:PUBLISHED_BY]->(i)
  - (d)-[:SUBMITTED_TO]->(i)
  - (d)-[:IN_LANGUAGE]->(l)
  - (d)-[:PUBLISHED_IN]->(j)
  - (d)-[:RELATED_TO]->(related)
- Use labels Book, Article, Thesis when possible.
- Use read-only Cypher only.
- Prefer LIMIT 10 for list queries unless the user asks for totals.
"""


FORBIDDEN_CYPHER_PATTERNS = [
    r"\bCREATE\b",
    r"\bMERGE\b",
    r"\bDELETE\b",
    r"\bDETACH\b",
    r"\bSET\b",
    r"\bREMOVE\b",
    r"\bDROP\b",
    r"\bLOAD\s+CSV\b",
    r"\bFOREACH\b",
    r"\bCALL\s+dbms\b",
    r"\bCALL\s+apoc\b",
    r";",
]


def get_qa_schema_context():
    return QA_SCHEMA_CONTEXT.strip()


def is_safe_readonly_cypher(cypher):
    if not cypher or not cypher.strip():
        return False

    normalized = re.sub(r"\s+", " ", cypher.strip(), flags=re.MULTILINE)

    if "return" not in normalized.lower():
        return False

    for pattern in FORBIDDEN_CYPHER_PATTERNS:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return False

    return True


def normalize_param_value(value):
    if value is None:
        return None

    if isinstance(value, (int, float, bool)):
        return value

    text = str(value).strip()
    if not text:
        return ""

    if re.fullmatch(r"-?\d+", text):
        try:
            return int(text)
        except Exception:
            return text

    return text


def params_array_to_dict(params):
    result = {}

    for item in params or []:
        if not isinstance(item, dict):
            continue

        key = str(item.get("key") or "").strip()
        if not key:
            continue

        result[key] = normalize_param_value(item.get("value"))

    return result


def execute_readonly_qa_cypher(cypher, params=None, max_records=10):
    if not is_safe_readonly_cypher(cypher):
        raise ValueError("Unsafe Cypher query rejected")

    records = neo4j_conn.query(cypher, params or {})
    return records[:max_records]


def get_author_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)
    MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    RETURN
        d.id AS id,
        d.title AS title,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
            ELSE coalesce(d.type, "Document")
        END AS type,
        d.year AS year,
        collect(DISTINCT a.name) AS authors
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})


def get_year_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)
    RETURN
        d.id AS id,
        d.title AS title,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
            ELSE coalesce(d.type, "Document")
        END AS type,
        d.year AS year
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})


def get_subject_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)
    MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    RETURN
        d.id AS id,
        d.title AS title,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
            ELSE coalesce(d.type, "Document")
        END AS type,
        d.year AS year,
        collect(DISTINCT s.name) AS subjects
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})


def get_publisher_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)
    MATCH (d)-[:PUBLISHED_BY]->(p:Institution)
    RETURN
        d.id AS id,
        d.title AS title,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
            ELSE coalesce(d.type, "Document")
        END AS type,
        d.year AS year,
        p.name AS publisher
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})


def get_university_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)
    MATCH (d)-[:SUBMITTED_TO]->(u:Institution)
    RETURN
        d.id AS id,
        d.title AS title,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
            ELSE coalesce(d.type, "Document")
        END AS type,
        d.year AS year,
        u.name AS university
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})


def get_document_match_by_title(title):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($title)
    RETURN
        d.id AS id,
        d.title AS title,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
            ELSE coalesce(d.type, "Document")
        END AS type,
        d.year AS year
    LIMIT 1
    """
    return neo4j_conn.query(query, {"title": title})
