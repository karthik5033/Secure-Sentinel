import requests

test_urls = [
    "https://campus2college.com/rv-college-of-engineering",
    "https://icoeca.com/about-rvce",
    "https://www.highereducationdigest.com/rv-college-of-e",
    "https://rvce.ac.in/admission",
    "https://google.com",
    "https://paypal-verify-account.xyz/login",
]

results = []
for url in test_urls:
    try:
        r = requests.post(
            "http://127.0.0.1:8002/api/v1/detect",
            json={"url": url},
            timeout=15
        )
        data = r.json()
        score = data.get('max_risk_score', data.get('risk_score', 0))
        level = data.get('risk_level', 'N/A')
        line = f"{level:8} {score:.3f}  {url}"
        results.append(line)
        print(line)
    except Exception as e:
        line = f"ERROR: {e} — {url}"
        results.append(line)
        print(line)

# Write to file for reliable reading
with open("fix3_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results) + "\n")
