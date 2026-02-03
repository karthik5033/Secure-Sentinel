# 📖 Quick Reference Guide

A cheat sheet for using SecureSentinel.

---

## 🚀 Quick Start Commands

### Start Backend
```bash
python start_server_v3.py
```
Access: `http://127.0.0.1:8002`

### Start Dashboard
```bash
cd my-app && npm run dev
```
Access: `http://localhost:3000`

### Install Extension
1. `chrome://extensions/`
2. Enable Developer mode
3. Load unpacked → Select `extension-clean/`

---

## 🎨 Badge Meanings

| Badge | Score | Meaning | Action |
|-------|-------|---------|--------|
| 🟢 | 0-40% | Safe | Browse normally |
| 🟡 | 41-70% | Moderate | Be cautious |
| 🔴 | 71-100% | Dangerous | Avoid |

---

## 🔧 Common Tasks

### Block a Website
1. Dashboard → Activity Insights
2. Find domain → Click 🚫
3. Reload extension

### Unblock a Website
1. Dashboard → Activity Insights
2. Find blocked domain → Click 🔓
3. Reload extension

### Clear Extension Cache
1. `chrome://extensions/`
2. Find SecureSentinel → Click Reload

### Check Backend Status
Visit: `http://127.0.0.1:8002/docs`

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No badges | Check backend running, reload extension |
| Slow extension | Reload to clear cache (100-item limit) |
| Dashboard loading | Verify backend on port 8002 |
| Wrong score | Check backend logs, may need retraining |

---

## 📂 File Locations

```
DTLshit/
├── backend/main.py              # ML model & heuristics
├── backend/app/sql_app.db       # Database
├── extension-clean/src/         # Extension code
├── my-app/app/dashboard/        # Dashboard pages
└── models/                      # ML model files
```

---

## 🔌 API Endpoints

```
POST   /api/v1/detect       # Analyze URL
GET    /api/v1/dashboard    # Get stats
GET    /api/v1/activity     # Get logs
POST   /api/v1/block        # Block domain
POST   /api/v1/unblock      # Unblock domain
GET    /api/v1/blocklist    # Get blocked list
```

---

## 🎯 Risk Categories

- **Phishing**: Fake login pages
- **Social Engineering**: Psychological tricks
- **Piracy**: Illegal content sites
- **Suspicious Tools**: Bypass/solver utilities

---

**Full Docs**: See README.md, USER_GUIDE.md, FEATURES.md
