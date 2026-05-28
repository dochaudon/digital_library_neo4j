import io
import csv
import zipfile
from database.neo4j_connection import neo4j_conn

# =====================================================
# EXPORT DATA CONFIGURATION MAP
# =====================================================
EXPORT_CONFIG = {
    "node_author.csv": {
        "description": "Dữ liệu Tác giả (Author Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:Author) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:Author) RETURN count(n) AS c"
    },
    "node_category.csv": {
        "description": "Dữ liệu Loại tài liệu (Category Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:Category) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:Category) RETURN count(n) AS c"
    },
    "node_document.csv": {
        "description": "Dữ liệu Tài liệu chính (Book/Article/Thesis)",
        "category": "node",
        "headers": ["id", "title", "alternative_title", "year", "pages", "abstract", "file_url", "image_url", "type", "status"],
        "query": """
            MATCH (n)
            WHERE n:Document
            RETURN 
                n.id AS id, 
                n.title AS title, 
                coalesce(n.alternative_title, n.other_title) AS alternative_title, 
                n.year AS year, 
                n.pages AS pages, 
                n.abstract AS abstract, 
                n.file_url AS file_url, 
                n.image_url AS image_url,
                CASE 
                    WHEN n.type = 'book' THEN 'Book'
                    WHEN n.type = 'article' THEN 'Article'
                    WHEN n.type = 'thesis' THEN 'Thesis'
                    ELSE "Other"
                END AS type,
                coalesce(n.status, "active") AS status
        """,
        "count_query": "MATCH (n) WHERE n:Document RETURN count(n) AS c"
    },
    "node_journal.csv": {
        "description": "Dữ liệu Tạp chí khoa học (Journal Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:Journal) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:Journal) RETURN count(n) AS c"
    },
    "node_keyword.csv": {
        "description": "Dữ liệu Từ khóa học thuật (Keyword Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:Keyword) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:Keyword) RETURN count(n) AS c"
    },
    "node_language.csv": {
        "description": "Dữ liệu Ngôn ngữ (Language Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:Language) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:Language) RETURN count(n) AS c"
    },
    "node_publisher.csv": {
        "description": "Dữ liệu Nhà xuất bản (Publisher Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:Publisher) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:Publisher) RETURN count(n) AS c"
    },
    "node_subject.csv": {
        "description": "Dữ liệu Chủ đề học thuật (Subject Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:Subject) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:Subject) RETURN count(n) AS c"
    },
    "node_university.csv": {
        "description": "Dữ liệu Trường đại học / Tổ chức (University Nodes)",
        "category": "node",
        "headers": ["id", "name"],
        "query": "MATCH (n:University) RETURN coalesce(n.id, n.name) AS id, n.name AS name",
        "count_query": "MATCH (n:University) RETURN count(n) AS c"
    },
    "node_user.csv": {
        "description": "Dữ liệu Người dùng (User Nodes)",
        "category": "node",
        "headers": ["id", "username", "email", "password", "role", "status"],
        "query": "MATCH (u:User) RETURN coalesce(u.id, '') AS id, coalesce(u.username, '') AS username, coalesce(u.email, '') AS email, coalesce(u.password, '') AS password, coalesce(u.role, 'user') AS role, coalesce(u.status, 'active') AS status",
        "count_query": "MATCH (u:User) RETURN count(u) AS c"
    },
    "rel_document_author.csv": {
        "description": "Quan hệ Tài liệu - Tác giả (HAS_AUTHOR)",
        "category": "relationship",
        "headers": ["doc_id", "author_id", "role"],
        "query": """
            MATCH (d)-[r:HAS_AUTHOR]->(a:Author) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(a.id, a.name) AS author_id, coalesce(r.role, 'author') AS role
        """,
        "count_query": "MATCH (d)-[:HAS_AUTHOR]->(a:Author) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_document_category.csv": {
        "description": "Quan hệ Tài liệu - Loại tài liệu (HAS_CATEGORY)",
        "category": "relationship",
        "headers": ["doc_id", "category_id"],
        "query": """
            MATCH (d)-[:HAS_CATEGORY]->(c:Category) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(c.id, c.name) AS category_id
        """,
        "count_query": "MATCH (d)-[:HAS_CATEGORY]->(c:Category) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_document_journal.csv": {
        "description": "Quan hệ Tài liệu - Tạp chí khoa học (PUBLISHED_IN)",
        "category": "relationship",
        "headers": ["doc_id", "journal_id"],
        "query": """
            MATCH (d)-[:PUBLISHED_IN]->(j:Journal) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(j.id, j.name) AS journal_id
        """,
        "count_query": "MATCH (d)-[:PUBLISHED_IN]->(j:Journal) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_document_keyword.csv": {
        "description": "Quan hệ Tài liệu - Từ khóa (HAS_KEYWORD)",
        "category": "relationship",
        "headers": ["doc_id", "keyword_id"],
        "query": """
            MATCH (d)-[:HAS_KEYWORD]->(k:Keyword) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(k.id, k.name) AS keyword_id
        """,
        "count_query": "MATCH (d)-[:HAS_KEYWORD]->(k:Keyword) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_document_language.csv": {
        "description": "Quan hệ Tài liệu - Ngôn ngữ (IN_LANGUAGE)",
        "category": "relationship",
        "headers": ["doc_id", "language_id"],
        "query": """
            MATCH (d)-[:IN_LANGUAGE]->(l:Language) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(l.id, l.name) AS language_id
        """,
        "count_query": "MATCH (d)-[:IN_LANGUAGE]->(l:Language) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_document_publisher.csv": {
        "description": "Quan hệ Tài liệu - Nhà xuất bản (PUBLISHED_BY)",
        "category": "relationship",
        "headers": ["doc_id", "publisher_id", "role"],
        "query": """
            MATCH (d)-[r:PUBLISHED_BY]->(p:Publisher) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(p.id, p.name) AS publisher_id, coalesce(r.role, 'publisher') AS role
        """,
        "count_query": "MATCH (d)-[:PUBLISHED_BY]->(p:Publisher) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_document_related.csv": {
        "description": "Quan hệ giữa các Tài liệu liên quan (RELATED_TO)",
        "category": "relationship",
        "headers": ["doc1_id", "doc2_id"],
        "query": """
            MATCH (d1)-[:RELATED_TO]->(d2) 
            WHERE (d1:Document) AND (d2:Document)
            RETURN d1.id AS doc1_id, d2.id AS doc2_id
        """,
        "count_query": """
            MATCH (d1)-[:RELATED_TO]->(d2) 
            WHERE (d1:Document) AND (d2:Document)
            RETURN count(*) AS c
        """
    },
    "rel_document_subject.csv": {
        "description": "Quan hệ Tài liệu - Chủ đề học thuật (HAS_SUBJECT)",
        "category": "relationship",
        "headers": ["doc_id", "subject_id"],
        "query": """
            MATCH (d)-[:HAS_SUBJECT]->(s:Subject) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(s.id, s.name) AS subject_id
        """,
        "count_query": "MATCH (d)-[:HAS_SUBJECT]->(s:Subject) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_document_university.csv": {
        "description": "Quan hệ Tài liệu - Trường đại học (OWNED_BY)",
        "category": "relationship",
        "headers": ["doc_id", "university_id", "role"],
        "query": """
            MATCH (d)-[r:OWNED_BY]->(u:University) 
            WHERE d:Document
            RETURN d.id AS doc_id, coalesce(u.id, u.name) AS university_id, coalesce(r.role, 'university') AS role
        """,
        "count_query": "MATCH (d)-[:OWNED_BY]->(u:University) WHERE d:Document RETURN count(*) AS c"
    },
    "rel_subject_related.csv": {
        "description": "Quan hệ các Chủ đề liên quan (RELATED_TO)",
        "category": "relationship",
        "headers": ["subject1_id", "subject2_id"],
        "query": """
            MATCH (s1:Subject)-[:RELATED_TO]->(s2:Subject) 
            RETURN coalesce(s1.id, s1.name) AS subject1_id, coalesce(s2.id, s2.name) AS subject2_id
        """,
        "count_query": "MATCH (s1:Subject)-[:RELATED_TO]->(s2:Subject) RETURN count(*) AS c"
    },
    "rel_user_document.csv": {
        "description": "Quan hệ Người dùng lưu Tài liệu (BOOKMARKED)",
        "category": "relationship",
        "headers": ["user_id", "doc_id"],
        "query": """
            MATCH (u:User)-[r:BOOKMARKED]->(d)
            WHERE (d:Document)
            RETURN u.id AS user_id, d.id AS doc_id
        """,
        "count_query": "MATCH (u:User)-[:BOOKMARKED]->(d) WHERE (d:Document) RETURN count(*) AS c"
    }
}


# =====================================================
# 1. GET ALL EXPORT FILES LIVE STATS
# =====================================================
def get_export_stats_service():
    """
    Queries Neo4j dynamically for the current record counts of each export type.
    Returns list of items containing metadata and real-time count.
    """
    stats_list = []
    
    for filename, config in EXPORT_CONFIG.items():
        try:
            count_res = neo4j_conn.query(config["count_query"])
            count = count_res[0]["c"] if count_res else 0
        except Exception as e:
            print(f"[Export Stats Error] Failed count for {filename}: {e}")
            count = 0
            
        stats_list.append({
            "filename": filename,
            "description": config["description"],
            "category": config["category"],
            "count": count
        })
        
    return stats_list


# =====================================================
# 2. GENERATE CSV BUFFER FOR A SINGLE FILE
# =====================================================
def generate_csv_data(filename):
    """
    Generates CSV formatted text in-memory for a given export filename.
    Returns string of the CSV data, or None if file config not found.
    """
    if filename not in EXPORT_CONFIG:
        return None
        
    config = EXPORT_CONFIG[filename]
    headers = config["headers"]
    query = config["query"]
    
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
    # Write CSV Header
    writer.writerow(headers)
    
    # Query Database
    records = neo4j_conn.query(query)
    
    # Write Rows
    for row in records:
        row_data = [row.get(h, "") for h in headers]
        writer.writerow(row_data)
        
    return output.getvalue()


# =====================================================
# 3. GENERATE ZIP ARCHIVE OF ALL CSV FILES
# =====================================================
def generate_all_zip_service():
    """
    Dynamically generates all 19 CSV files in-memory, packages them
    into a single ZIP file buffer, and returns it.
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in EXPORT_CONFIG.keys():
            csv_content = generate_csv_data(filename)
            if csv_content is not None:
                # Add to zip archive with UTF-8 encoding
                zip_file.writestr(filename, csv_content.encode("utf-8"))
                
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
