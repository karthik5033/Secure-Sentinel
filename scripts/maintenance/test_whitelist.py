import re

# Test the whitelist patterns
text = "rvce.edu.in"

safe_patterns = [
    r'\.edu$',           # US educational
    r'\.edu\.[a-z]{2}$', # International educational (e.g., .edu.in, .edu.au)
    r'\.ac\.[a-z]{2}$',  # Academic (e.g., .ac.uk, .ac.in)
    r'\.gov$',           # US government
    r'\.gov\.[a-z]{2}$', # International government
    r'\.mil$',           # US military
    # Popular platforms
    r'youtube\.com',
    r'youtu\.be',
    r'google\.com',
    r'wikipedia\.org',
]

print(f"Testing: {text}")
print("-" * 50)

for pattern in safe_patterns:
    match = re.search(pattern, text.lower())
    print(f"Pattern: {pattern:30} Match: {bool(match)}")

# Test if ANY pattern matches
is_whitelisted = any(re.search(pattern, text.lower()) for pattern in safe_patterns)
print("-" * 50)
print(f"Is whitelisted: {is_whitelisted}")

# Test specific .edu.in pattern
print("\nSpecific test for .edu.in:")
pattern = r'\.edu\.[a-z]{2}$'
match = re.search(pattern, text)
print(f"Pattern: {pattern}")
print(f"Text: {text}")
print(f"Match: {match}")
if match:
    print(f"Matched: {match.group()}")
