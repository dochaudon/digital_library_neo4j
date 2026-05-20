import os
import sys

# Ensure we run from the correct directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.export_service import (
    get_export_stats_service,
    generate_csv_data,
    generate_all_zip_service
)

def test_export():
    print("=== TESTING EXPORT STATS ===")
    stats = get_export_stats_service()
    total_records = 0
    for s in stats:
        print(f"File: {s['filename']} | Category: {s['category']} | Count: {s['count']}")
        total_records += s['count']
    print(f"Total live records mapped: {total_records}")

    print("\n=== TESTING SINGLE CSV GENERATION ===")
    author_csv = generate_csv_data("node_author.csv")
    if author_csv:
        lines = author_csv.strip().split("\n")
        print(f"node_author.csv successfully generated! Rows: {len(lines)}")
        print(f"Header: {lines[0]}")
        if len(lines) > 1:
            print(f"First data row: {lines[1]}")
    else:
        print("Failed to generate node_author.csv")
        sys.exit(1)

    print("\n=== TESTING ALL ZIP GENERATION ===")
    zip_bytes = generate_all_zip_service()
    if zip_bytes and len(zip_bytes) > 0:
        print(f"neo4j_export_all.zip successfully generated! Size: {len(zip_bytes)} bytes")
    else:
        print("Failed to generate ZIP archive")
        sys.exit(1)

    print("\nVerification completed successfully!")

if __name__ == "__main__":
    test_export()
