import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neo4j_connection import neo4j_conn
from services.document_service import create_document_service, delete_document_service

def test_delete():
    # Tạo doc test
    test_data = {
        "id": "test_doc_delete_999",
        "type": "Book",
        "title": "Test Delete Document",
        "abstract": "Test delete",
        "year": "2026",
        "pages": "100"
    }
    
    # Clean old
    neo4j_conn.query("MATCH (d {id: 'test_doc_delete_999'}) DETACH DELETE d")
    
    print("Creating test document...")
    create_document_service(test_data)
    
    # Kiểm tra tồn tại
    res = neo4j_conn.query("MATCH (d {id: 'test_doc_delete_999'}) RETURN d.id AS id")
    if res:
        print("Document created successfully.")
    else:
        print("Failed to create document!")
        return

    # Xóa doc
    print("Deleting test document via service...")
    try:
        delete_document_service("test_doc_delete_999")
        print("Delete service executed without exception.")
    except Exception as e:
        print(f"Exception during delete: {e}")
        return
        
    # Kiểm tra đã xóa chưa
    res_after = neo4j_conn.query("MATCH (d {id: 'test_doc_delete_999'}) RETURN d.id AS id")
    if not res_after:
        print("[SUCCESS] Document deleted successfully from Neo4j.")
    else:
        print("[FAIL] Document still exists in Neo4j!")

if __name__ == "__main__":
    test_delete()
