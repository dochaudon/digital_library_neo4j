import sys
import os

# Thêm đường dẫn thư mục gốc để import được
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neo4j_connection import neo4j_conn
from services.document_service import create_document_service

def verify():
    print("Testing auto ID generation for new metadata entities during document creation...")
    
    # 1. Định nghĩa dữ liệu test
    test_data = {
        "id": "test_doc_auto_id_123",
        "type": "Book",
        "title": "Sách Test Auto ID",
        "abstract": "Mô tả test",
        "year": "2026",
        "pages": "100",
        "file_url": "",
        "image_url": "",
        "authors_json": [
            {"name": "New Author 999", "role": "author"}
        ],
        "institutions_json": [
            {"name": "New University 999", "role": "university"},
            {"name": "New Publisher 999", "role": "publisher"}
        ],
        "subjects": ["New Subject 999"],
        "keywords": ["New Keyword 999"],
        "categories": ["New Category 999"],
        "languages": ["New Language 999"],
        "journal": "New Journal 999"
    }
    
    # Xóa sạch các node test trước đó nếu có
    cleanup_queries = [
        "MATCH (d {id: 'test_doc_auto_id_123'}) DETACH DELETE d",
        "MATCH (a:Author {name: 'New Author 999'}) DETACH DELETE a",
        "MATCH (u:University {name: 'New University 999'}) DETACH DELETE u",
        "MATCH (p:Publisher {name: 'New Publisher 999'}) DETACH DELETE p",
        "MATCH (s:Subject {name: 'New Subject 999'}) DETACH DELETE s",
        "MATCH (k:Keyword {name: 'New Keyword 999'}) DETACH DELETE k",
        "MATCH (c:Category {name: 'New Category 999'}) DETACH DELETE c",
        "MATCH (l:Language {name: 'New Language 999'}) DETACH DELETE l",
        "MATCH (j:Journal {name: 'New Journal 999'}) DETACH DELETE j"
    ]
    for q in cleanup_queries:
        neo4j_conn.query(q)
        
    print("Database cleaned up. Creating test document...")
    
    # 2. Tạo tài liệu
    created_id = create_document_service(test_data)
    print(f"Document created with ID: {created_id}")
    
    # 3. Kiểm tra các node metadata được tạo ra
    entities = {
        "Author": ("New Author 999", "A"),
        "University": ("New University 999", "U"),
        "Publisher": ("New Publisher 999", "P"),
        "Subject": ("New Subject 999", "S"),
        "Keyword": ("New Keyword 999", "K"),
        "Category": ("New Category 999", "C"),
        "Language": ("New Language 999", "L"),
        "Journal": ("New Journal 999", "J")
    }
    
    success = True
    for label, (name, prefix) in entities.items():
        q = f"MATCH (n:{label} {{name: $name}}) RETURN n.id AS id, n.name AS name"
        res = neo4j_conn.query(q, {"name": name})
        if res:
            node_id = res[0]["id"]
            node_name = res[0]["name"]
            print(f"[OK] [{label}] Name: {node_name} -> ID: {node_id} (Prefix: {prefix})")
            if not node_id or not node_id.startswith(prefix):
                print(f"[FAIL] Error: ID '{node_id}' does not start with correct prefix '{prefix}'")
                success = False
        else:
            print(f"[FAIL] Error: [{label}] with name '{name}' was not created!")
            success = False
            
    # Xóa sạch sau khi verify
    for q in cleanup_queries:
        neo4j_conn.query(q)
        
    if success:
        print("\nALL TESTS PASSED SUCCESSFULLY!")
    else:
        print("\nSOME TESTS FAILED!")

if __name__ == "__main__":
    verify()
