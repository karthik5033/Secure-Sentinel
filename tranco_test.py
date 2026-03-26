import requests

test_urls = [
    "https://campus2college.com",
    "https://www.paloaltonetworks.com/cyberpedia/what-is-cti",
    "https://www.highereducationdigest.com",
    "https://filigran.io",
    "https://citytradersimperium.com",
    "https://www.first.org",
    "https://rvce.ac.in",
    "https://google.com",
    "https://paypal-verify-account.xyz/login",
]

for url in test_urls:
    try:
        r = requests.post(
            "http://127.0.0.1:8002/api/v1/detect",
            json={"url": url},
            timeout=10
        )
        data = r.json()
        score = data.get('max_risk_score', data.get('risk_score', 'N/A'))
        level = data.get('risk_level', 'N/A')
        print(f"{level:8} {score:.3f}  {url}")
    except Exception as e:
        print(f"ERROR: {e} — {url}")
