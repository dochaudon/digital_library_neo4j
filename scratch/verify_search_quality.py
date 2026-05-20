import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vector_search_service import get_faiss_index, vector_search

def test_search():
    print("Testing FAISS Rebuild...")
    index = get_faiss_index()
    print(f"FAISS index loaded successfully. Number of vectors: {index.ntotal}")
    
    if index.ntotal == 0:
        print("FAIL: FAISS index is empty!")
        return
        
    print("\n--- Testing Vector Search (Query: 'học máy trí tuệ nhân tạo') ---")
    results = vector_search("học máy trí tuệ nhân tạo", limit=5)
    for i, res in enumerate(results, 1):
        print(f"{i}. [{res['id']}] {res['title']} (Score: {res['score']:.4f})")

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    test_search()
