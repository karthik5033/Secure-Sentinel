import requests

urls = [
    'https://www.cti.org',
    'https://www.cti-cert.com',
    'https://cti.international',
    'https://www.first.org',
    'https://www.ddcli.ac.in',
    'https://campus2college.com',
    'https://paloaltonetworks.com'
]

for url in urls:
    try:
        r = requests.post('http://127.0.0.1:8002/api/v1/detect', json={'url': url}, timeout=15)
        d = r.json()
        print(f"{d['risk_level']:8} {d['max_risk_score']:5.3f} {url}")
    except Exception as e:
        print(f"ERR  {url}: {e}")
