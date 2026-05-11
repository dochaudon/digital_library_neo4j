import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_service import search_documents

def test_cases():
    print("Running Verification Tests...")
    
    # 1. Subject Mapping
    print("\nCase 1: Subject Mapping ('sach co chu de cong nghe thong tin')")
    results = search_documents("sach co chu de cong nghe thong tin")
    for r in results[:2]:
        # Avoid printing titles directly to terminal due to UnicodeEncodeError
        print(f"- ID: {r['id']} (Type: {r.get('type')}, Score: {r.get('score')})")

    # 2. Semantic Matching
    print("\nCase 2: Semantic Matching ('robot thong minh')")
    results = search_documents("robot thong minh")
    for r in results[:2]:
        print(f"- ID: {r['id']} (Type: {r.get('type')}, Score: {r.get('score')})")

    # 3. Empty Query
    print("\nCase 3: Empty Query")
    results = search_documents("")
    print(f"Returned {len(results)} latest documents.")

if __name__ == "__main__":
    test_cases()
