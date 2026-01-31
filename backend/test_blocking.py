import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("🧪 Testing Blocking System\n")

# 1. Check current blocklist
print("1️⃣ Fetching current blocklist...")
resp = requests.get(f"{BASE_URL}/blocklist")
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.json()}\n")

# 2. Block a test domain
test_domain = "test-phishing-site.com"
print(f"2️⃣ Blocking domain: {test_domain}")
resp = requests.post(f"{BASE_URL}/block", json={"domain": test_domain})
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.json()}\n")

# 3. Verify it's in blocklist
print("3️⃣ Verifying blocklist...")
resp = requests.get(f"{BASE_URL}/blocklist")
data = resp.json()
print(f"   Blocked domains: {[d['domain'] for d in data.get('domains', [])]}\n")

# 4. Test detection of blocked domain
print(f"4️⃣ Testing detection of blocked domain...")
resp = requests.post(f"{BASE_URL}/detect", json={"url": f"https://{test_domain}/login"})
result = resp.json()
print(f"   Risk Level: {result.get('risk_level')}")
print(f"   Is Phishing: {result.get('is_phishing')}")
print(f"   Confidence: {result.get('confidence_score')}\n")

# 5. Unblock
print(f"5️⃣ Unblocking domain...")
resp = requests.post(f"{BASE_URL}/unblock", json={"domain": test_domain})
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.json()}\n")

print("✅ Test complete!")
