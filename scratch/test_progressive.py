
import os
from services.search_service import hybrid_search, parse_query

def test_query(q):
    text, filters = parse_query(q)
    results = hybrid_search(q, filters, limit=10)
    
    with open("d:\\DATN\\digitallibrary\\scratch\\progressive_results.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- Query: {q} ---\n")
        f.write(f"Filters: {filters}\n")
        for i, doc in enumerate(results):
            f.write(f"[{i+1}] Priority: {doc.get('priority')}, Stage: {doc.get('retrieval_stage')}, Source: {doc.get('source')}\n")
            f.write(f"    Title: {doc.get('title')}\n")
            f.write(f"    Subjects: {doc.get('subjects')}\n")
            f.write(f"    Keywords: {doc.get('keywords')}\n")
            f.write("-" * 20 + "\n")

# Clear file
with open("d:\\DATN\\digitallibrary\\scratch\\progressive_results.txt", "w", encoding="utf-8") as f:
    f.write("Progressive Retrieval Test Results\n")

test_query("Sách có chủ đề Công nghệ thông tin")
test_query("Documents about Information Technology")
test_query("Tìm tài liệu của trường Đại học Nha Trang")
test_query("Tìm sách có từ khóa AI")
