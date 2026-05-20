import os
import sys

# Ensure we run from the correct directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.document_model import get_document_by_id
from services.document_service import (
    create_document_service,
    update_document_service,
    delete_document_service
)
from database.neo4j_connection import neo4j_conn

def test_document_relations():
    print("=== TESTING DOCUMENT RELATIONSHIPS ===")
    
    # 1. Fetch some existing documents to relate to
    existing_docs = neo4j_conn.query(
        "MATCH (d) WHERE d:Book OR d:Article OR d:Thesis RETURN d.id AS id LIMIT 2"
    )
    if len(existing_docs) < 2:
        print("Error: Need at least 2 existing documents to run relation tests.")
        sys.exit(1)
        
    rel_ids = [r["id"] for r in existing_docs]
    print(f"Target documents to relate to: {rel_ids}")

    # 2. Create a dummy test document relating to these target documents
    test_id = "D_TEST_REL"
    # Clean up first if it already exists
    neo4j_conn.query("MATCH (d {id: $id}) DETACH DELETE d", {"id": test_id})
    
    dummy_data = {
        "id": test_id,
        "type": "Book",
        "title": "Document Relation Test Title",
        "year": 2026,
        "pages": "100",
        "abstract": "Test abstract content",
        "authors_json": [{"name": "Test Author", "role": "author"}],
        "institutions_json": [],
        "subjects": ["Test Subject"],
        "keywords": ["Test Keyword"],
        "categories": ["Test Category"],
        "languages": ["Vietnamese"],
        "related_docs": rel_ids
    }
    
    print("\n--- Creating dummy test document ---")
    created_id = create_document_service(dummy_data)
    print(f"Created document successfully with ID: {created_id}")

    # 3. Retrieve document and assert related_docs are stored
    print("\n--- Verifying related documents in database ---")
    doc = get_document_by_id(test_id)
    if not doc:
        print("Error: Could not retrieve the created document.")
        sys.exit(1)
        
    print(f"Retrieved document: {doc['title']}")
    print(f"Retrieved related_docs: {doc['related_docs']}")
    
    # Assert
    assert set(doc["related_docs"]) == set(rel_ids), f"Relation mismatch! Expected {rel_ids}, got {doc['related_docs']}"
    print("✓ Success: Related documents match exactly!")

    # 4. Update the relations (remove one, keep one)
    updated_rel_ids = [rel_ids[0]]
    print(f"\n--- Updating dummy test document (new relations: {updated_rel_ids}) ---")
    
    dummy_data["related_docs"] = updated_rel_ids
    success = update_document_service(test_id, dummy_data)
    print(f"Update service returned: {success}")

    # 5. Retrieve again and verify
    doc_updated = get_document_by_id(test_id)
    print(f"Retrieved updated related_docs: {doc_updated['related_docs']}")
    
    assert set(doc_updated["related_docs"]) == set(updated_rel_ids), f"Relation mismatch! Expected {updated_rel_ids}, got {doc_updated['related_docs']}"
    print("✓ Success: Updated related documents match exactly!")

    # 6. Clean up
    print("\n--- Cleaning up dummy test document ---")
    delete_document_service(test_id)
    doc_deleted = get_document_by_id(test_id)
    if doc_deleted is None:
        print("✓ Success: Dummy document deleted and verified clean.")
    else:
        print("Error: Dummy document still exists after deletion.")
        sys.exit(1)

    print("\nAll relationship tests passed successfully!")

if __name__ == "__main__":
    test_document_relations()
