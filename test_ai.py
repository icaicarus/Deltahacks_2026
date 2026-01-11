import os
import json
from google import genai
from google.genai import types  # For schema configuration
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)
woah = 'whats your name'
response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents=types.Part.from_text(text=woah),
    config=types.GenerateContentConfig(
        temperature=0,
        top_p=0.95,
        top_k=20,
    ),
)

data = response.text
print(data)