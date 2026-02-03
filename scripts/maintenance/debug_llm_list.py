
import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

def _load_env():
    load_dotenv(".env.local", override=True)
    return os.getenv("GEMINI_API_KEY")

def debug():
    print("--- Sentinel AI Model Diagnostic ---")
    api_key = _load_env()
    
    if not api_key:
        print("❌ No API key found in .env.local!")
        return
        
    print(f"✅ API Key Loaded (Preview: {api_key[:5]}...{api_key[-4:]})")
    genai.configure(api_key=api_key)
    
    print("\nListing available models:")
    try:
        models = genai.list_models()
        supported_gen = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name} ({m.display_name})")
                supported_gen.append(m.name)
        
        if not supported_gen:
            print("❌ No models support generateContent for this key.")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
    
if __name__ == "__main__":
    debug()
