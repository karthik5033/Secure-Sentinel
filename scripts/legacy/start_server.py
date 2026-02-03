
import uvicorn
import os
import sys

# Ensure the project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

if __name__ == "__main__":
    print(f"Starting server from {PROJECT_ROOT}")
    # Run the uvicorn server programmatically
    # equivalent to: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[PROJECT_ROOT])
