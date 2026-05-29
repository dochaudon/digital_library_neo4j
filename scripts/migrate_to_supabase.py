import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database.neo4j_connection import neo4j_conn
from services.supabase_service import get_public_url_from_supabase

def migrate_urls():
    print("Fetching documents from Neo4j...")
    query = """
    MATCH (d:Document)
    RETURN d.id AS id, d.file_url AS file_url, d.image_url AS image_url
    """
    
    docs = neo4j_conn.query(query)
    print(f"Found {len(docs)} documents.")
    
    updated_count = 0
    for doc in docs:
        doc_id = doc["id"]
        file_url = doc.get("file_url")
        image_url = doc.get("image_url")
        
        new_file_url = file_url
        new_image_url = image_url
        needs_update = False
        
        # Check and migrate file_url
        if file_url and file_url.startswith("/static/uploads/"):
            filename = file_url.split("/")[-1]
            public_url = get_public_url_from_supabase(filename, "document")
            if public_url:
                new_file_url = public_url
                needs_update = True
                print(f"[{doc_id}] Mapped file: {filename} -> {public_url}")
            else:
                print(f"[{doc_id}] WARNING: Could not get Supabase URL for document {filename}")
                
        # Check and migrate image_url
        if image_url and image_url.startswith("/static/uploads/"):
            filename = image_url.split("/")[-1]
            public_url = get_public_url_from_supabase(filename, "image")
            if public_url:
                new_image_url = public_url
                needs_update = True
                print(f"[{doc_id}] Mapped image: {filename} -> {public_url}")
            else:
                print(f"[{doc_id}] WARNING: Could not get Supabase URL for image {filename}")
                
        # Update Neo4j if needed
        if needs_update:
            update_query = """
            MATCH (d:Document {id: $id})
            SET d.file_url = $file_url, d.image_url = $image_url
            """
            neo4j_conn.query(update_query, {
                "id": doc_id,
                "file_url": new_file_url,
                "image_url": new_image_url
            })
            updated_count += 1
            
    print(f"Migration completed. Updated {updated_count} documents.")

if __name__ == "__main__":
    migrate_urls()
