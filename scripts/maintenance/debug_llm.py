
import os
import sys
import asyncio

# Add current directory to path
sys.path.append(os.path.abspath("backend"))

from backend.app.services.llm import LlmService

async def debug():
    print("--- Sentinel AI Diagnostic ---")
    service = LlmService()
    
    if not service.api_key:
        print("❌ No API key found in LlmService!")
        return
        
    print(f"✅ API Key Loaded (Preview: {service.api_key[:5]}...{service.api_key[-4:]})")
    
    print("\nAttempting chat...")
    result = await service.chat_with_context("Testing connection", "Context: Diagnostic Script")
    
    print("\n--- RESULTS ---")
    print(f"Response: {result.get('response')[:200]}...")
    print(f"Suggestions: {result.get('suggestions')}")
    
if __name__ == "__main__":
    asyncio.run(debug())
