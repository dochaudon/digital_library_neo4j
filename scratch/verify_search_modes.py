import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_service import search_documents

def verify_modes():
    print("Testing Search Modes backend integration...\n")
    
    query = "học máy trí tuệ nhân tạo"
    
    for mode in ["hybrid", "keyword", "semantic"]:
        print(f"=== TESTING MODE: {mode.upper()} ===")
        results = search_documents(query, limit=3, search_type=mode)
        print(f"Returned {len(results)} documents:")
        for idx, doc in enumerate(results, 1):
            print(f"  {idx}. [{doc['id']}] {doc['title']} (Stage: {doc.get('retrieval_stage')})")
        print()

if __name__ == "__main__":
    verify_modes()
