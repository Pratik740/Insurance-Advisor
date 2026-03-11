import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("NO API KEY FOUND IN .ENV")
else:
    print(f"Key loaded! Starts with: {api_key[:5]}... Ends with: {api_key[-5:]}")
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents="say hello exactly once"
        )
        print("API CALL SUCCESS:", response.text.strip())
    except Exception as e:
        print("API CALL FAILED:", e)
