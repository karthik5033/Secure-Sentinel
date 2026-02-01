import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_endpoints():
    print("🚀 Starting API Self-Test...\n")
    
    # 1. Privacy Settings (New)
    try:
        resp = requests.get(f"{BASE_URL}/privacy/settings")
        print(f"✅ GET /privacy/settings: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"❌ GET /privacy/settings Failed: {e}")

    # 2. Detect Benign (Should use Whitelist or Model)
    try:
        payload = {"url": "https://www.google.com"}
        resp = requests.post(f"{BASE_URL}/detect", json=payload)
        data = resp.json()
        print(f"✅ POST /detect (Benign): {resp.status_code} - Risk: {data.get('risk_level')} ({data.get('confidence_score')})")
        if data.get('risk_level') != 'Low':
            print("   ⚠️ Warning: Benign site flagged!")
    except Exception as e:
        print(f"❌ POST /detect (Benign) Failed: {e}")

    # 3. Detect Malicious (Simulation)
    try:
        # random url to avoid whitelist
        payload = {"url": "http://evil-phishing-site-test.com/login.php"}
        resp = requests.post(f"{BASE_URL}/detect", json=payload)
        data = resp.json()
        print(f"✅ POST /detect (Suspicious): {resp.status_code} - Risk: {data.get('risk_level')} ({data.get('confidence_score')})")
    except Exception as e:
        print(f"❌ POST /detect (Suspicious) Failed: {e}")
        
    print("\n🎉 Test Complete.")

if __name__ == "__main__":
    test_endpoints()
