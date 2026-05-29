import os
from supabase import create_client, Client
from werkzeug.utils import secure_filename

url: str = os.getenv("SUPABASE_URL", "")
key: str = os.getenv("SUPABASE_KEY", "")

# Initialize only if keys are present
supabase: Client | None = None
if url and key:
    supabase = create_client(url, key)

def upload_file_to_supabase(file, bucket_name: str) -> str | None:
    """
    Uploads a file stream to Supabase Storage and returns the public URL.
    Returns None if upload fails or if file is invalid.
    """
    if not supabase:
        print("Supabase is not configured.")
        return None

    if not file or file.filename == "":
        return None

    filename = secure_filename(file.filename)
    
    try:
        # Read file content
        file_bytes = file.read()
        # Reset file pointer if someone else needs to read it
        file.seek(0)
        
        # Determine content type (optional, but good practice)
        content_type = file.content_type if hasattr(file, 'content_type') and file.content_type else "application/octet-stream"
        
        # Upload to Supabase
        res = supabase.storage.from_(bucket_name).upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(filename)
        return public_url
    except Exception as e:
        # File might already exist. If it exists, supabase raises an error.
        # We can try to just get the public URL if it's already there
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            return supabase.storage.from_(bucket_name).get_public_url(filename)
        print(f"Supabase upload error: {e}")
        return None

def get_public_url_from_supabase(filename: str, bucket_name: str) -> str | None:
    """
    Gets the public URL of a file from Supabase Storage.
    """
    if not supabase:
        return None
    try:
        return supabase.storage.from_(bucket_name).get_public_url(filename)
    except Exception as e:
        print(f"Error getting public url: {e}")
        return None
