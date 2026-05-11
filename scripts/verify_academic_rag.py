import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.qa_service import get_qa_response

def test_academic_rag():
    print("=== Testing Academic RAG Pipeline ===\n")
    
    # Case 1: Local Retrieval
    print("Case 1: Local Retrieval ('machine learning')")
    resp = get_qa_response("tài liệu về machine learning")
    print(f"Answer length: {len(resp['answer'])}")
    print(f"Intent: {resp['intent']}")
    print(f"Docs count: {len(resp['documents'])}\n")

    # Case 2: External Retrieval
    print("Case 2: External Retrieval ('quantum computing in healthcare')")
    resp = get_qa_response("tài liệu về quantum computing in healthcare")
    print(f"Answer length: {len(resp['answer'])}")
    print(f"Intent: {resp['intent']}")
    # Check if any doc is external
    external_count = sum(1 for d in resp['documents'] if d.get('is_external'))
    print(f"External docs count: {external_count}\n")

    # Case 3: Out-of-scope
    print("Case 3: Out-of-scope ('thoi tiet hom nay')")
    resp = get_qa_response("thời tiết hôm nay")
    print(f"Answer length: {len(resp['answer'])}")
    print(f"Intent: {resp['intent']}\n")

if __name__ == "__main__":
    test_academic_rag()
