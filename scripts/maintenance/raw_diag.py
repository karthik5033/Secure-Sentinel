
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Force load
load_dotenv(".env.local", override=True)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print(f"API KEY: {api_key[:5]}...{api_key[-4:]}")

test_models = [
    'models/gemini-1.5-flash',
    'models/gemini-1.5-flash-8b',
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b'
]

for m in test_models:
    print(f"\n--- Testing {m} ---")
    try:
        model = genai.GenerativeModel(m)
        print(f"Model ID in object: {model.model_name}")
        res = model.generate_content("ping")
        print(f"SUCCESS: {res.text[:10]}")
    except Exception as e:
        print(f"FAILURE: {str(e)}")
