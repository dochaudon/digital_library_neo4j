import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def check_gemini_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in .env")
        return

    try:
        client = genai.Client(api_key=api_key)
        print("\n--- Testing simple generation with gemini-2.5-flash ---")
        model_name = "gemini-2.5-flash"
        response = client.models.generate_content(
            model=model_name,
            contents="Hello, are you connected? Respond in 10 words or less."
        )
        print(f"Success! Response: {response.text.strip()}")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_gemini_connection()
