# SecureSentinel Dialog Interceptor - Testing Guide

## What's New

Your browser extension now **intercepts and analyzes real browser messages** in real-time:

### Intercepted Elements:
1. **`alert()` dialogs** - JavaScript alerts
2. **`confirm()` dialogs** - Yes/No prompts
3. **`prompt()` dialogs** - Input requests
4. **Notification API** - Browser notifications

### How It Works:
1. When a website shows an alert/confirm/prompt, the extension intercepts it
2. The text is sent to your **Temporal Analysis Engine** (backend ML model)
3. Trigger words are extracted (urgency, fear, authority, impersonation)
4. A beautiful overlay shows the **risk assessment** with:
   - Risk percentage (0-100%)
   - Detected trigger words in temporal order
   - Category badges (URGENCY, FEAR, etc.)
   - Option to proceed or block

## Testing Instructions

### 1. Reload the Extension
```bash
# In Chrome/Brave:
1. Go to chrome://extensions/
2. Find "SecureSentinel"
3. Click the reload icon (circular arrow)
```

### 2. Test with Real Examples

#### Test Alert (High Risk):
Open browser console on any page and run:
```javascript
alert("URGENT: Your account session will expire immediately. Please update your credentials now to avoid being locked out permanently.");
```

#### Test Confirm (Moderate Risk):
```javascript
confirm("Your payment method requires verification. Click OK to update your billing information now.");
```

#### Test Prompt (Low Risk):
```javascript
prompt("Enter your email to receive updates:");
```

### 3. What You'll See

**If Risk > 30%:**
- Beautiful dark overlay appears
- Shows temporal pressure analysis
- Lists detected triggers with scores
- Displays the intercepted message
- Options: "Block & Close" or "Proceed Anyway"

**If Risk < 30%:**
- Normal browser dialog shows (safe)

### 4. Real-World Testing

Visit sites that use aggressive popups:
- News sites with subscription prompts
- E-commerce sites with urgency timers
- Any site using `alert()` for notifications

## Technical Details

### Files Modified:
1. `extension-clean/src/content/dialog-interceptor.js` - NEW
   - Intercepts window.alert, window.confirm, window.prompt
   - Intercepts Notification API
   - Shows temporal analysis overlay

2. `extension-clean/src/background/service-worker.js`
   - Added `analyzeDialog()` function
   - Added ANALYZE_DIALOG message handler
   - Extracts trigger words using same patterns as temporal service

3. `extension-clean/manifest.json`
   - Added dialog-interceptor.js to content_scripts
   - Runs at document_start (early injection)

### Backend Integration:
- Uses existing `/api/v1/detect` endpoint
- Combines ML risk score with pattern matching
- Tracks dialog analysis in stats

## Advanced Usage

### Custom Trigger Patterns
Edit `dialog-interceptor.js` or `service-worker.js` to add custom patterns:
```javascript
const TRIGGER_PATTERNS = {
  URGENCY: ["immediately", "urgent", "now", ...],
  FEAR: ["locked", "suspended", ...],
  // Add your own categories
};
```

### Adjust Risk Threshold
In `dialog-interceptor.js`, change the threshold:
```javascript
if (analysis && analysis.riskScore > 0.3) {  // Change 0.3 to your preference
    await showTemporalOverlay(text, analysis, "Alert Dialog");
}
```

## Troubleshooting

**Extension not intercepting?**
1. Make sure backend is running: `python -m uvicorn backend.main:app --reload`
2. Check console for errors: F12 → Console tab
3. Reload the extension

**Overlay not showing?**
1. Check if risk score is above threshold (default 30%)
2. Look for console logs: `[SecureSentinel] Dialog intercepted`

**Backend offline?**
- Extension will still extract local triggers
- Risk scores will be based on pattern matching only

## Next Steps

This creates a **real working security layer** that:
- ✅ Analyzes real browser dialogs
- ✅ Uses your ML model for risk assessment
- ✅ Shows temporal pressure indicators
- ✅ Gives users informed choices
- ✅ Tracks all analysis in stats

You can now protect users from social engineering attacks that use browser dialogs!
