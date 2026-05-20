import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neo4j_connection import neo4j_conn
from services.metadata_service import create_author_service, delete_author_service

def test_delete_author():
    # Tạo author test
    test_data = {
        "id": "A_test_delete_999",
        "name": "Test Delete Author 999"
    }
    
    # Clean old
    neo4j_conn.query("MATCH (a:Author {id: 'A_test_delete_999'}) DETACH DELETE a")
    
    print("Creating test author...")
    create_author_service(test_data)
    
    # Kiểm tra tồn tại
    res = neo4j_conn.query("MATCH (a:Author {id: 'A_test_delete_999'}) RETURN a.id AS id")
    if res:
        print("Author created successfully.")
    else:
        print("Failed to create author!")
        return

    # Xóa
    print("Deleting test author via service...")
    try:
        delete_author_service("A_test_delete_999")
        print("Delete service executed without exception.")
    except Exception as e:
        print(f"Exception during delete: {e}")
        return
        
    # Kiểm tra đã xóa chưa
    res_after = neo4j_conn.query("MATCH (a:Author {id: 'A_test_delete_999'}) RETURN a.id AS id")
    if not res_after:
        print("[SUCCESS] Author deleted successfully from Neo4j.")
    else:
        print("[FAIL] Author still exists in Neo4j!")

if __name__ == "__main__":
    test_delete_author()
