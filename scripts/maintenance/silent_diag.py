
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(".env.local", override=True)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

with open("silent_models.txt", "w") as f:
    f.write(f"KEY: {api_key[:5]}...{api_key[-4:]}\n")
    try:
        for m in genai.list_models():
            f.write(f"{m.name}\n")
    except Exception as e:
        f.write(f"ERROR: {str(e)}\n")
print("DONE")
