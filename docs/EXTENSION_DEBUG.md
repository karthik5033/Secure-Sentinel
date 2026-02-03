# Extension Blocking Diagnostic Guide

## Quick Fix Steps

### 1. Reload the Extension
After blocking a domain in the dashboard:
1. Open `chrome://extensions`
2. Find "SecureSentinel"
3. Click the **reload icon** (circular arrow)
4. Try visiting the blocked site again

### 2. Check Extension Console
1. Open `chrome://extensions`
2. Find "SecureSentinel"
3. Click "service worker" (or "Inspect views: service worker")
4. Look for these logs:
   ```
   [SecureSentinel] 📥 Received blocklist data: ...
   [SecureSentinel] 📋 Synced X permanently blocked domains: [...]
   ```

### 3. Verify Backend is Running
```bash
curl http://127.0.0.1:8000/api/v1/blocklist
```

Should return:
```json
{
  "domains": [
    {"domain": "masto.ai", "timestamp": "..."}
  ]
}
```

### 4. Manual Extension Sync
In the extension console, run:
```javascript
// Check current blocklist
console.log(permanentBlocklist);

// Force sync
syncBlocklist();
```

## Common Issues

### Issue: "Extension shows empty blocklist"
**Cause:** Backend API format mismatch or CORS issue

**Fix:** 
- Backend must return `{domains: [...]}` not just `[...]`
- Check backend logs for errors
- Verify CORS is enabled

### Issue: "Domain blocked in dashboard but not in browser"
**Cause:** Extension hasn't synced yet

**Fix:**
- Wait 30 seconds (auto-sync interval)
- OR reload extension manually
- OR restart browser

### Issue: "Extension not blocking at all"
**Cause:** Protection disabled or permission issues

**Fix:**
1. Check extension has `webNavigation` permission
2. Check settings: `blockingEnabled` should be `true`
3. In extension console:
   ```javascript
   chrome.storage.local.get(['protectionEnabled'], (r) => console.log(r));
   ```

## Testing Blocking

### Test Script
```bash
cd d:\Downloads\DTLshit
python backend/test_blocking.py
```

### Manual Test
1. Block `example.com` in dashboard
2. Reload extension
3. Visit `https://example.com`
4. Should see red blocking page

## Extension Architecture

```
User blocks domain in Dashboard
         ↓
    POST /api/v1/block
         ↓
    Domain saved to SQLite
         ↓
    Extension syncs every 5 min
         ↓
    GET /api/v1/blocklist
         ↓
    permanentBlocklist updated
         ↓
    webNavigation listener checks
         ↓
    Redirect to blocked.html
```

## Debug Commands

### Check if extension is loaded:
```javascript
// In any page console
chrome.runtime.sendMessage({action: "ping"}, (response) => {
  console.log("Extension alive:", response);
});
```

### Force blocklist sync:
```javascript
// In extension console (chrome://extensions > service worker)
syncBlocklist().then(() => {
  console.log("Blocklist:", Array.from(permanentBlocklist));
});
```

### Check domain normalization:
```javascript
// In extension console
const testUrl = "https://Masto.AI/explore";
const urlObj = new URL(testUrl);
const domain = urlObj.hostname.toLowerCase();
console.log("Normalized:", domain);
console.log("Is blocked?", permanentBlocklist.has(domain));
```
