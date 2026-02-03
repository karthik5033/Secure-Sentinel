
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(".env.local", override=True)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-2.0-flash-exp', 'gemini-1.5-pro']

print(f"Testing Key: {api_key[:5]}...{api_key[-4:]}")
for m in models:
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("hi")
        print(f"✅ {m}: Success! Response: {response.text.strip()[:20]}")
    except Exception as e:
        print(f"❌ {m}: Failed - {str(e)[:100]}")
