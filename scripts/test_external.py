import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.qa_service import get_qa_response

def test_academic_rag():
    print("=== Testing Academic RAG Pipeline ===\n")
    
    # Case 2: External Retrieval (using a very specific query)
    print("Case 2: External Retrieval ('black holes event horizon')")
    resp = get_qa_response("tài liệu về black holes event horizon")
    print(f"Answer length: {len(resp['answer'])}")
    print(f"Intent: {resp['intent']}")
    # Check if any doc is external
    external_count = sum(1 for d in resp['documents'] if d.get('is_external'))
    print(f"External docs count: {external_count}\n")

if __name__ == "__main__":
    test_academic_rag()
