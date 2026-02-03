# 🛡️ SecureSentinel Auto-Popup Detection

## Overview

SecureSentinel now **automatically detects and analyzes ALL popups, modals, notifications, and banners** that appear while you browse the web - **no user input required!**

## How It Works

### 1. **Automatic Detection**
The extension continuously monitors the webpage for:
- Modal dialogs (`role="dialog"`, `.modal`, `.popup`)
- Alert notifications (`role="alert"`, `.notification`, `.toast`)
- Cookie/GDPR banners
- Framework-specific modals (Material-UI, Bootstrap, Ant Design, etc.)
- Any new elements that appear on the page

### 2. **Smart Text Extraction**
When a popup is detected:
- Extracts all visible text content
- Removes scripts, styles, and hidden elements
- Cleans and normalizes the text
- Filters out very short or very long content

### 3. **Real-Time Analysis**
The extracted text is sent to the backend for:
- **Temporal pressure analysis** - Detects urgency, fear, authority tactics
- **Trigger word detection** - Identifies manipulation keywords
- **Risk scoring** - Calculates overall threat level (0-100%)
- **Category classification** - URGENCY, FEAR, AUTHORITY, IMPERSONATION, SCARCITY, REWARD

### 4. **Intelligent Overlay**
If the risk score exceeds 40%, SecureSentinel shows a beautiful overlay with:
- Risk percentage and level (SAFE, MODERATE, HIGH RISK)
- Detected trigger words with categories
- Timeline of manipulation tactics
- Options to block or allow the popup

## Features

### ✅ What's Detected
- ✓ Native browser alerts (`alert()`, `confirm()`, `prompt()`)
- ✓ DOM-based modals and popups
- ✓ Notification toasts and snackbars
- ✓ Cookie consent banners
- ✓ Promotional overlays
- ✓ Fake security warnings
- ✓ Phishing dialogs
- ✓ Scam prize notifications

### 🎯 Detection Patterns
The system looks for common popup selectors:
```javascript
- [role="dialog"]
- [role="alertdialog"]
- [aria-modal="true"]
- .modal, .popup, .dialog
- .notification, .alert, .toast
- .cookie-banner, .gdpr-banner
- Framework-specific classes
```

### 🧠 Temporal Analysis Categories

1. **URGENCY** (90% weight)
   - "immediately", "urgent", "now", "expire", "deadline"
   
2. **FEAR** (85% weight)
   - "suspended", "terminated", "blocked", "compromised", "breach"
   
3. **AUTHORITY** (75% weight)
   - "verify", "required", "mandatory", "official", "compliance"
   
4. **IMPERSONATION** (80% weight)
   - "account", "password", "bank", "payment", "credentials"
   
5. **SCARCITY** (70% weight)
   - "limited", "only X left", "last chance", "selling fast"
   
6. **REWARD** (65% weight)
   - "free", "win", "prize", "congratulations", "claim"

## Configuration

You can adjust the scanner behavior in `dom-popup-scanner.js`:

```javascript
const CONFIG = {
    minTextLength: 20,           // Minimum text length to analyze
    maxTextLength: 1000,         // Maximum text length to analyze
    scanInterval: 500,           // Check for new popups every 500ms
    riskThreshold: 0.4,          // Show overlay if risk > 40%
    debounceTime: 1000           // Debounce rapid changes
};
```

## Testing

### Test Page
Open `test-popup-detection.html` in your browser with the extension installed to test:
- High-risk popups (phishing, scams, urgent alerts)
- Moderate-risk popups (updates, verification requests)
- Safe popups (newsletters, cookies, welcome messages)
- Notifications and banners

### Expected Behavior
1. **High-Risk Popups** (70%+)
   - Immediate overlay with red theme
   - Multiple trigger words highlighted
   - Strong warning message

2. **Moderate-Risk Popups** (40-70%)
   - Overlay with orange/yellow theme
   - Some trigger words detected
   - Caution message

3. **Safe Popups** (<40%)
   - No overlay shown
   - Logged in console for debugging
   - User sees original popup

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Webpage                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Popup/Modal Appears                                  │   │
│  └────────────────┬─────────────────────────────────────┘   │
│                   │                                          │
│                   ▼                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  dom-popup-scanner.js                                 │   │
│  │  - Detects element                                    │   │
│  │  - Extracts text                                      │   │
│  │  - Checks if analyzed before                          │   │
│  └────────────────┬─────────────────────────────────────┘   │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  service-worker.js                                           │
│  - Receives ANALYZE_DIALOG message                           │
│  - Forwards to backend                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend API (http://127.0.0.1:8000)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/v1/temporal/analyze                             │   │
│  │  - Analyzes text for triggers                         │   │
│  │  - Calculates risk score                              │   │
│  │  - Returns detailed analysis                          │   │
│  └────────────────┬─────────────────────────────────────┘   │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  dom-popup-scanner.js                                        │
│  - Receives analysis results                                 │
│  - Shows overlay if risky                                    │
│  - Allows user to block or continue                          │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Temporal Analysis
```
POST /api/v1/temporal/analyze
Content-Type: application/json

{
  "text": "URGENT: Your account will be suspended!",
  "context": "popup",
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "text": "URGENT: Your account will be suspended!",
  "risk_score": 0.85,
  "risk_level": "HIGH_RISK",
  "triggers": [
    {
      "word": "urgent",
      "category": "URGENCY",
      "score": 0.9,
      "position": 0
    },
    {
      "word": "suspended",
      "category": "FEAR",
      "score": 0.85,
      "position": 25
    }
  ],
  "categories": {
    "URGENCY": 0.9,
    "FEAR": 0.85,
    "AUTHORITY": 0.0,
    "IMPERSONATION": 0.0,
    "SCARCITY": 0.0,
    "REWARD": 0.0
  },
  "explanation": "High temporal pressure detected. Found 2 manipulation triggers across 2 categories."
}
```

## Performance

- **Scan Interval**: 500ms (configurable)
- **Cache**: Analyzed texts are cached to avoid duplicates
- **Debouncing**: Rapid DOM changes are debounced
- **Memory**: Limited to 50 cached texts (LRU)
- **CPU**: Minimal impact - only scans visible elements

## Privacy

- ✅ All analysis happens locally or on your backend
- ✅ No data sent to third parties
- ✅ Analyzed texts are not stored permanently
- ✅ Works offline (if backend is local)

## Troubleshooting

### Popups Not Being Detected
1. Check console for `[SecureSentinel] DOM Popup Scanner Active`
2. Verify the popup uses standard selectors
3. Ensure the popup is visible (not `display: none`)
4. Check if text length is within min/max range

### Backend Connection Issues
1. Ensure backend is running: `python -m uvicorn backend.main:app --reload`
2. Check backend URL in service-worker.js: `http://127.0.0.1:8000`
3. Look for CORS errors in console
4. Verify temporal router is registered

### Overlay Not Showing
1. Check if risk score > threshold (default 40%)
2. Look for console logs showing risk score
3. Verify overlay isn't blocked by CSP
4. Check z-index conflicts with page styles

## Future Enhancements

- [ ] Machine learning model for popup classification
- [ ] User feedback loop for false positives
- [ ] Whitelist for trusted domains
- [ ] Custom trigger word patterns
- [ ] Export analysis reports
- [ ] Integration with dashboard

## Contributing

To add new trigger patterns, edit `backend/app/routes/temporal.py`:

```python
TRIGGER_PATTERNS = {
    "YOUR_CATEGORY": {
        "patterns": ["word1", "word2", "phrase"],
        "weight": 0.75  # 0.0 to 1.0
    }
}
```

## License

Part of SecureSentinel - Real-time Phishing Detection System
