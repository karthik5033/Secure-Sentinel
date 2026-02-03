import joblib
import sys

# Load the model
print("Loading model...")
clf = joblib.load("models/model_scalable.joblib")
vectorizer = joblib.load("models/vectorizer_scalable.joblib")

# Test URLs
test_urls = [
    "rvce.edu.in",
    "rvce.edu.in/home",
    "mit.edu",
    "paypal-secure-login.com",
    "google.com"
]

print("\nTesting URLs:")
print("-" * 60)

for url in test_urls:
    X = vectorizer.transform([url])
    probs = clf.predict_proba(X)[0]
    max_prob = max(probs)
    
    print(f"\nURL: {url}")
    print(f"Max Risk Score: {max_prob:.4f}")
    print(f"Classification: {'SAFE' if max_prob < 0.5 else 'THREAT'}")
    print(f"All probabilities: {probs}")
