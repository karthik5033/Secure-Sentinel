import sys
try:
    import google.generativeai as genai
    import dotenv
    print("SUCCESS: Modules found.")
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
