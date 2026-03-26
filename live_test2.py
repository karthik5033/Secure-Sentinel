import requests

test_urls = [
    "https://google.com",
    "https://accounts.google.com/signin",
    "https://paypal-verify-account.xyz/login",
    "https://secure-banking-update.tk/verify",
    "https://github.com/login",
    "https://www.amazon.com/ap/signin",
    "http://192.168.1.1/admin/login",
    "https://totally-not-facebook.xyz/login/verify",
]

with open("live_out.txt", "w", encoding="utf-8") as f:
    for url in test_urls:
        try:
            r = requests.post(
                "http://127.0.0.1:8002/api/v1/detect",
                json={"url": url},
                timeout=10
            )
            data = r.json()
            score = data.get('max_risk_score', data.get('risk_score', 0))
            level = data.get('risk_level', 'N/A')
            f.write(f"{level:8} {score:.3f}  {url}\n")
            print(f"{level:8} {score:.3f}  {url}")
        except Exception as e:
            f.write(f"ERROR: {e} — {url}\n")
            print(f"ERROR: {e} — {url}")
