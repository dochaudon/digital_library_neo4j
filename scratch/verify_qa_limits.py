import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.qa_service import get_qa_response

def test_qa_limits():
    question = "Cho tôi tài liệu về trí tuệ nhân tạo"
    print(f"Testing question: {question}")
    response = get_qa_response(question)
    
    local_count = len(response.get('local_documents', []))
    external_count = len(response.get('external_documents', []))
    
    print(f"Answer: {response['answer'][:100]}...")
    print(f"Local documents: {local_count} (Expected: 1-5)")
    print(f"External documents: {external_count} (Expected: 1-3)")
    
    if 0 <= local_count <= 5 and 0 <= external_count <= 3:
        print("SUCCESS: Limits enforced correctly.")
    else:
        print("FAILURE: Limits NOT enforced.")

if __name__ == "__main__":
    test_qa_limits()
