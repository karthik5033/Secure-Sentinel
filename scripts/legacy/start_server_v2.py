
import uvicorn
import os
import sys

# Ensure the project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

if __name__ == "__main__":
    print(f"Starting server v2 from {PROJECT_ROOT} on port 8001")
    # Run server on port 8001 to bypass the stale process on 8000
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True, reload_dirs=[PROJECT_ROOT])
