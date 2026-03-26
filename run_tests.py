import sys
import os

sys.path.append(r'd:\coding_files\Projects\DTLshit')

import asyncio
from backend.main import detect_phishing
from fastapi import Request

class MockRequest:
    def __init__(self, json_data):
        self._json = json_data
    async def json(self):
        return self._json

class MockSession:
    def query(self, *args, **kwargs):
        class MockQuery:
            def filter(self, *args, **kwargs):
                return self
            def first(self, *args, **kwargs):
                return None
        return MockQuery()
    def add(self, *args, **kwargs):
        pass
    def commit(self, *args, **kwargs):
        pass

class MockLlm:
    async def analyze_url(self, url):
        return {'confidence': 1.0, 'signals': []}

async def run_tests():
    db = MockSession()
    llm = MockLlm()
    urls = [
        'https://google.com',
        'https://accounts.google.com/signin',
        'https://microsoft.com',
        'https://paypal-verify-account.xyz/login',
        'https://secure-banking-update.tk/verify',
        'https://github.com/login'
    ]
    for url in urls:
        req = MockRequest({'url': url})
        try:
            res = await detect_phishing(req, db, llm)
            print(f"URL: {res['url']}")
            print(f"Confidence (Blended): {res['confidence_score']}")
            print(f"Risk Level: {res['risk_level']}")
            print("-" * 40)
        except Exception as e:
            print(f"Error checking {url}: {e}")

asyncio.run(run_tests())
