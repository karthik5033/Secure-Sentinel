
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(".env.local", override=True)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print(f"API KEY: {api_key[:5]}...{api_key[-4:]}")
print("\n--- AVAILABLE MODELS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Name: {m.name}")
            print(f"  Description: {m.description}")
            print(f"  Supported: {m.supported_generation_methods}")
except Exception as e:
    print(f"ERROR: {e}")
