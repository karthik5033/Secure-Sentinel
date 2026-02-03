# 🚀 Quick Start Guide - Auto Popup Detection

## What's New?

Your SecureSentinel extension now **automatically scans ALL popups and notifications** that appear while browsing - no manual input needed!

## Setup (Already Done ✅)

1. ✅ Backend running on `http://127.0.0.1:8000`
2. ✅ Frontend running on `http://localhost:3000`
3. ✅ Extension files updated with new scanner

## How to Test

### Step 1: Reload the Extension

1. Open Chrome and go to `chrome://extensions/`
2. Find **SecureSentinel**
3. Click the **reload icon** (🔄) to load the new code

### Step 2: Open the Test Page

1. Navigate to: `file:///d:/Downloads/DTLshit/extension-clean/test-popup-detection.html`
2. Or open the file directly in Chrome

### Step 3: Watch the Magic! ✨

The test page will automatically show a popup after 2 seconds. You should see:

1. **Console logs** (Press F12):
   ```
   [SecureSentinel] Dialog Interceptor Active
   [SecureSentinel] DOM Popup Scanner Active
   [SecureSentinel] 🔍 Auto-scanning popup: "🎁 Special Offer Limited time only!..."
   [SecureSentinel] ⚠️ Risky popup detected! Score: 65%
   ```

2. **SecureSentinel Overlay** appears showing:
   - Risk score (e.g., 65%)
   - Risk level (MODERATE)
   - Detected triggers ("limited time", "act now", "expires")
   - Options to Block or Allow

### Step 4: Test Different Scenarios

Click the buttons on the test page:

#### 🚨 High-Risk (Should show RED overlay)
- "Urgent Account Alert" - Phishing attempt
- "Fake Security Warning" - Account suspension scam
- "Prize Scam" - Lottery/reward scam

#### ⚠️ Moderate-Risk (Should show ORANGE overlay)
- "Update Required" - Verification request
- "Limited Time Offer" - Scarcity tactics

#### ✅ Safe (Should NOT show overlay)
- "Newsletter Signup" - Legitimate signup
- "Cookie Notice" - Standard cookie banner

## What Happens Automatically

### 1. **Popup Appears**
Any modal, dialog, notification, or banner on ANY website

### 2. **Text Extracted**
SecureSentinel reads the text content automatically

### 3. **Sent to Backend**
Text is analyzed for manipulation tactics:
- URGENCY: "immediately", "urgent", "now"
- FEAR: "suspended", "blocked", "compromised"
- AUTHORITY: "verify", "required", "mandatory"
- IMPERSONATION: "account", "password", "bank"
- SCARCITY: "limited", "only X left"
- REWARD: "free", "win", "prize"

### 4. **Risk Calculated**
Backend returns risk score (0-100%)

### 5. **Overlay Shown** (if risky)
Beautiful overlay with detailed analysis

## Real-World Usage

### Browse Any Website
Just browse normally! The extension will automatically:
- Detect popups on e-commerce sites
- Scan promotional banners
- Analyze cookie consent dialogs
- Check notification toasts
- Intercept fake security alerts

### Example Sites to Test
- **News sites** - Cookie banners (usually safe)
- **Shopping sites** - "Limited time offer" popups (moderate risk)
- **Suspicious sites** - Fake virus warnings (high risk)

## Checking Backend Connection

### Verify Backend is Running
Open: http://127.0.0.1:8000/docs

You should see:
- `/api/v1/detect` - Main detection endpoint
- `/api/v1/temporal/analyze` - NEW temporal analysis endpoint
- `/health` - Health check

### Test Temporal Analysis Directly
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/temporal/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENT! Your account will be suspended immediately!"}'
```

Expected response:
```json
{
  "risk_score": 0.85,
  "risk_level": "HIGH_RISK",
  "triggers": [
    {"word": "urgent", "category": "URGENCY", "score": 0.9},
    {"word": "suspended", "category": "FEAR", "score": 0.85}
  ]
}
```

## Troubleshooting

### ❌ "Backend offline" in console
**Solution**: Backend should auto-reload. If not, restart it:
```bash
cd d:\Downloads\DTLshit
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### ❌ Overlay not showing
**Check**:
1. Is the popup text > 20 characters?
2. Is the risk score > 40%?
3. Open console (F12) and look for logs

### ❌ "Temporal Analysis Router" not registered
**Solution**: Backend needs to reload. Check terminal for:
```
Temporal Analysis Router registered successfully.
```

## Features Summary

### ✅ What Works Now
- ✓ Automatic popup detection (no user input!)
- ✓ Real-time text extraction
- ✓ Backend temporal analysis
- ✓ Beautiful risk overlay
- ✓ Trigger word highlighting
- ✓ Block/Allow options

### 🎯 Smart Detection
- Scans every 500ms for new popups
- Caches analyzed content (no duplicates)
- Debounces rapid changes
- Only analyzes visible elements
- Filters by text length

### 🧠 Advanced Analysis
- 6 manipulation categories
- Weighted scoring system
- Temporal trigger timeline
- Multi-category detection
- Risk level classification

## Next Steps

1. **Browse the web** with the extension active
2. **Visit the test page** to see it in action
3. **Check the dashboard** at http://localhost:3000 to see scan history
4. **Customize triggers** in `backend/app/routes/temporal.py`

## Dashboard Integration

The scanned popups are automatically logged to your dashboard:
1. Open http://localhost:3000
2. Go to "Features" → "Temporal Analysis"
3. See recent scans with risk scores

## Questions?

- **How often does it scan?** Every 500ms
- **Does it slow down browsing?** No, minimal CPU usage
- **Can I whitelist sites?** Yes, use the dashboard
- **Does it work offline?** Yes, if backend is local
- **Is my data private?** Yes, all local processing

## Success Indicators

You'll know it's working when:
1. ✅ Console shows "DOM Popup Scanner Active"
2. ✅ Popups are logged in console
3. ✅ Risk scores are calculated
4. ✅ Overlay appears for risky content
5. ✅ Dashboard shows scan history

---

**Enjoy your smart, automatic phishing protection! 🛡️**
