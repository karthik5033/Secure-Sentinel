import requests
import json

# Test the backend API directly
url = "http://localhost:8000/api/v1/detect"

test_urls = [
    "rvce.edu.in",
    "rvce.edu.in/home",
    "youtube.com",
    "google.com",
    "paypal-secure-login.com"  # Should be high risk
]

print("Testing Backend Whitelist")
print("=" * 60)

for test_url in test_urls:
    try:
        response = requests.post(url, json={"text": test_url})
        data = response.json()
        
        risk_score = data.get("max_risk_score", -1)
        print(f"\nURL: {test_url}")
        print(f"Risk Score: {risk_score:.4f}")
        print(f"Status: {'✅ SAFE (Whitelisted)' if risk_score == 0.0 else '⚠️ FLAGGED'}")
    except Exception as e:
        print(f"\nURL: {test_url}")
        print(f"Error: {e}")

print("\n" + "=" * 60)
