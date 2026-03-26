import requests
import json

urls = [
    'https://www.cti.org',
    'https://www.cti-cert.com',
    'https://cti.international',
    'https://www.first.org',
    'https://www.ddcli.ac.in',
    'https://campus2college.com'
]

print(f"{'LEVEL':8} {'SCORE':6} {'URL'}")
print("-" * 50)

for url in urls:
    try:
        r = requests.post('http://127.0.0.1:8002/api/v1/detect', json={'url': url}, timeout=10)
        data = r.json()
        level = data.get('risk_level', 'N/A')
        score = data.get('max_risk_score', 0)
        heuristics = data.get('heuristics', {})
        print(f"{level:8} {score:.3f} {url}")
        print(f"  Heuristics: {heuristics}")
    except Exception as e:
        print(f"ERROR {url}: {e}")
