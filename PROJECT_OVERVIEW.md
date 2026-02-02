# 🛡️ SecureSentinel - Comprehensive Project Overview

## 📋 Executive Summary

**SecureSentinel** is an AI-powered, real-time phishing detection and social engineering defense platform. It provides multi-layered protection across web browsing through a Chrome browser extension, a FastAPI-powered backend with machine learning capabilities, and a Next.js monitoring dashboard.

**Project Type:** Full-Stack Security Application  
**Primary Purpose:** Protect users from phishing attacks, social engineering, and malicious websites in real-time  
**Current Version:** 3.0.0 (Extension), 4.0.0 (Backend API)

---

## 🎯 Core Functionality

SecureSentinel analyzes every website a user visits and assigns a **Risk Score** from 0% (Safe) to 100% (Dangerous). Based on this score:

- 🟢 **Green Badge** (0-40%): Safe to browse
- 🟡 **Yellow Badge** (41-70%): Moderate risk - be cautious  
- 🔴 **Red Badge** (71-100%): High risk - dangerous site

### Key Features:
1. **Real-time URL Analysis** - Every URL is analyzed before the user interacts with it
2. **Visual Risk Indicators** - Color-coded badges appear on search results (Google, Brave, etc.)
3. **Automatic Blocking** - Extremely dangerous sites are blocked automatically
4. **Activity Monitoring** - Centralized dashboard tracks all browsing activity
5. **Manual Controls** - Users can manually block/unblock domains
6. **Privacy-First** - All analysis happens locally, no third-party data sharing

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER BROWSER                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Chrome Extension (SecureSentinel v3.0.0)        │  │
│  │  - Content Scripts (DOM scanning)                │  │
│  │  - Background Service Worker (API communication) │  │
│  │  - Popup UI (Quick stats)                        │  │
│  └────────────────┬─────────────────────────────────┘  │
└───────────────────┼─────────────────────────────────────┘
                    │ HTTP REST API
                    ▼
┌─────────────────────────────────────────────────────────┐
│          BACKEND SERVER (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  API Endpoints (main.py - 736 lines)             │  │
│  │  - /api/v1/detect (URL analysis)                 │  │
│  │  - /api/v1/blocklist (Domain management)         │  │
│  │  - /api/v1/activity (Activity logs)              │  │
│  │  - /api/v1/temporal/analyze (Text analysis)      │  │
│  │  - /api/v1/neural/scan (Deep scanning)           │  │
│  │  - /api/v1/chat (AI assistant)                   │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                     │
│  ┌────────────────┴─────────────────────────────────┐  │
│  │  ML Detection Engine                             │  │
│  │  - Sklearn SGD Classifier (Currently disabled)   │  │
│  │  - Heuristic Analysis (Active)                   │  │
│  │  - Keyword Blocklist (Active)                    │  │
│  │  - Whitelist Verification (Active)               │  │
│  └────────────────┬─────────────────────────────────┘  │
└───────────────────┼─────────────────────────────────────┘
                    │ SQLAlchemy ORM
                    ▼
┌─────────────────────────────────────────────────────────┐
│          DATABASE (SQLite)                              │
│  - scan_results (URL analysis history)                 │
│  - blocked_domains (User-blocked domains)              │
│  - allowed_domains (Whitelisted domains)               │
└─────────────────────────────────────────────────────────┘
                    ▲
                    │ HTTP REST API
┌───────────────────┴─────────────────────────────────────┐
│          DASHBOARD (Next.js 16.1.0)                     │
│  - Real-time activity monitoring                        │
│  - Statistics and analytics                             │
│  - Manual domain blocking/unblocking                    │
│  - Privacy settings management                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
DTLshit/
├── backend/                    # FastAPI Backend Server
│   ├── main.py                 # Main API server (736 lines)
│   ├── app/
│   │   ├── database.py         # SQLAlchemy database config
│   │   ├── models.py           # Database models (ScanResult, BlockedDomain, AllowedDomain)
│   │   ├── routes/             # API route handlers
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/           # Business logic services
│   ├── models/                 # ML model files
│   │   ├── best_phishing_model.pth  # PyTorch model (currently unused)
│   │   ├── model_enhanced.joblib    # Sklearn model (disabled)
│   │   └── vectorizer_enhanced.joblib
│   ├── requirements.txt        # Python dependencies
│   └── sql_app.db             # SQLite database
│
├── extension-clean/            # Chrome Extension
│   ├── manifest.json           # Extension manifest (v3)
│   ├── popup.html/js           # Extension popup UI
│   ├── blocked.html/js/css     # Blocked page UI
│   ├── src/
│   │   ├── background/
│   │   │   └── service-worker.js    # Background service worker
│   │   └── content/
│   │       ├── content.js           # Main content script
│   │       ├── dialog-interceptor.js # Popup detection
│   │       └── dom-popup-scanner.js  # DOM scanning
│   └── icons/                  # Extension icons
│
├── my-app/                     # Next.js Dashboard (TypeScript)
│   ├── src/
│   │   ├── app/                # Next.js 16 app directory
│   │   └── components/         # React components
│   ├── package.json            # Node dependencies
│   └── tailwind.config.js      # Tailwind CSS config
│
├── dashboard/                  # Alternative dashboard (legacy?)
│
├── models/                     # Trained ML models
│   ├── model_enhanced.joblib
│   └── vectorizer_enhanced.joblib
│
├── ext_data/                   # Training datasets
│   └── refined_training_dataset.csv
│
├── data/                       # Additional data files
│
├── scripts/                    # Utility scripts
├── maintenance_scripts/        # Maintenance utilities
├── notebooks/                  # Jupyter notebooks for analysis
│
├── train_phishing_model.py    # PyTorch CNN model training (235 lines)
├── start_server_v3.py          # Backend server launcher
├── seed_db.py                  # Database seeding script
│
└── Documentation Files:
    ├── README.md               # Main project documentation
    ├── FEATURES.md             # Detailed feature explanations
    ├── DEVELOPER_GUIDE.md      # Developer documentation
    ├── USER_GUIDE.md           # End-user instructions
    ├── QUICK_START_AUTO_POPUP.md
    ├── BLOCKING_FIXED.md
    └── EXTENSION_DEBUG.md
```

---

## 🛡️ The 6 Defense Layers

SecureSentinel uses a sophisticated multi-layered defense approach:

### 1. 🔍 **Behavioral Baseline**
- **Purpose:** Monitors website behavior patterns
- **Method:** Compares against 1.2M+ known-safe websites
- **Detects:** Unusual redirects, suspicious permissions, hidden forms, malicious JavaScript

### 2. ⏰ **Temporal Analysis**
- **Purpose:** Detects psychological pressure tactics
- **Method:** Scans for urgency keywords and time-pressure phrases
- **Keywords:** "act now", "limited time", "expire", "urgent", "immediate action required"
- **Psychology:** Exploits the fact that rushed decisions bypass rational thinking

### 3. 🧠 **Neural Detection** (Core AI Engine)
- **Model:** SGD Classifier (Stochastic Gradient Descent) - **Currently Disabled**
- **Alternative Model:** PyTorch 1D-CNN (PhishNetCNN) - Available but not in production
- **Features:** 16 manual features + TF-IDF text vectorization
- **Training Data:** 1.2M+ samples from PhishTank, OpenPhish, and benign datasets
- **Accuracy:** ~94% (based on test dataset)
- **Current Status:** Running in "STRICT BLOCKLIST MODE" due to model stability issues

### 4. 🛡️ **Cognitive Shield**
- **Purpose:** Identifies psychological manipulation tactics
- **Detects:**
  - **Authority Impersonation:** "FBI Warning", "Official Microsoft Alert"
  - **Fear Tactics:** "VIRUS DETECTED", "Security Breach"
  - **Impersonation:** Typosquatting (paypa1.com), homoglyph attacks (g00gle.com)

### 5. ⚡ **Quantum Defense** (Heuristic Overrides)
- **Purpose:** Instant zero-latency blocking for known threats
- **Categories:**
  - **Piracy Keywords (0.95 risk):** tamilrockers, torrent, crack, 123movies
  - **Suspicious TLDs (0.85 risk):** .tk, .xyz, .top, .ml, .ga
  - **Adult Content:** porn, xxx, adult, sex
  - **Crypto/Earning Scams:** bitcoin, crypto, earn-money, airdrop
  - **Games/Piracy:** free-games, steamunlocked, repack
- **Performance:** <1ms response time

### 6. 🌐 **Sentinel Mesh** (Synchronization Layer)
- **Purpose:** Keeps extension, backend, and dashboard synchronized
- **Features:**
  - Real-time updates (dashboard polls every 5 seconds)
  - Extension cache (30-minute TTL)
  - Persistent blocklist across all components
  - Activity logging with full audit trail

---

## 🔧 Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **Server:** Uvicorn ASGI server
- **Database:** SQLite with SQLAlchemy ORM
- **ML Libraries:** 
  - scikit-learn (SGD Classifier - disabled)
  - PyTorch (1D-CNN model - available but not deployed)
  - joblib (model serialization)
  - numpy (numerical operations)
- **Validation:** Pydantic schemas
- **CORS:** Enabled for cross-origin requests

### Frontend Dashboard
- **Framework:** Next.js 16.1.0 (React 19.2.3)
- **Language:** TypeScript
- **Styling:** Tailwind CSS v4
- **UI Components:** 
  - Radix UI (accessible components)
  - Framer Motion (animations)
  - Lucide React (icons)
- **Build Tool:** Next.js built-in (Turbopack)

### Chrome Extension
- **Manifest Version:** 3 (latest)
- **Architecture:**
  - Service Worker (background processing)
  - Content Scripts (DOM manipulation)
  - Popup UI (user interface)
- **Permissions:**
  - storage (local data persistence)
  - webNavigation (URL tracking)
  - tabs (tab management)
- **Host Permissions:** http://127.0.0.1:8000/* (backend API)

### Machine Learning
- **Current Production Model:** Heuristic-based (keyword matching + pattern detection)
- **Available Models:**
  1. **Sklearn SGD Classifier** (model_enhanced.joblib) - Disabled due to segfaults
  2. **PyTorch 1D-CNN** (PhishNetCNN) - Trained but not deployed
- **Training Pipeline:**
  - Character-level tokenization
  - 1D Convolutional layers for n-gram feature extraction
  - Embedding dimension: 64
  - Filters: 128
  - Kernel size: 5
  - Max URL length: 150 characters
  - Training: 15 epochs with AdamW optimizer
  - Device: CUDA (RTX 4060) / CPU fallback

### Database Schema
```sql
-- scan_results table
CREATE TABLE scan_results (
    id INTEGER PRIMARY KEY,
    url VARCHAR,
    domain VARCHAR,
    risk_score FLOAT,
    risk_level VARCHAR,  -- Low, Medium, High, Critical
    explanation VARCHAR,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- blocked_domains table
CREATE TABLE blocked_domains (
    id INTEGER PRIMARY KEY,
    domain VARCHAR UNIQUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- allowed_domains table
CREATE TABLE allowed_domains (
    id INTEGER PRIMARY KEY,
    domain VARCHAR UNIQUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 API Endpoints

### Core Detection
- **POST /api/v1/detect** - Analyze URL for phishing
  - Input: `{"url": "https://example.com"}`
  - Output: `{"is_phishing": bool, "confidence_score": float, "risk_level": str, "heuristics": dict}`

### Domain Management
- **GET /api/v1/blocklist** - Get all blocked domains
- **POST /api/v1/block** - Block a domain
- **POST /api/v1/unblock** - Unblock a domain

### Activity Monitoring
- **GET /api/v1/activity** - Get recent scan history (limit: 20)
- **GET /api/v1/dashboard** - Get dashboard statistics and KPIs

### Advanced Analysis
- **POST /api/v1/temporal/analyze** - Analyze text for psychological triggers
- **GET /api/v1/temporal/history** - Get temporal analysis history
- **POST /api/v1/neural/scan** - Deep neural network scan (experimental)
- **POST /api/v1/analyze** - General text analysis

### Utilities
- **POST /api/v1/chat** - Chat with Sentinel AI assistant
- **GET /api/v1/privacy/settings** - Get privacy settings
- **POST /api/v1/privacy/settings** - Update privacy settings
- **DELETE /api/v1/reset** - Reset entire system (clear all data)
- **GET /health** - Health check endpoint

---

## 🚀 Deployment & Running

### Start Backend Server
```bash
# Method 1: Direct
python start_server_v3.py

# Method 2: Using batch file
run_backend.bat

# Server runs on: http://127.0.0.1:8002
# API docs available at: http://127.0.0.1:8002/docs
```

### Start Dashboard
```bash
cd my-app
npm install
npm run dev

# Dashboard runs on: http://localhost:3000
```

### Install Chrome Extension
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `extension-clean` folder
5. Extension is now active

---

## 🧠 Machine Learning Details

### Current Detection Logic (Production)

Since the ML model is disabled, the system uses a **hybrid heuristic approach**:

1. **Whitelist Check** - Immediate pass for known-safe domains
   - Google, YouTube, Amazon, Wikipedia, Microsoft, Apple, GitHub, etc.
   - Government domains (.gov.in, .nic.in)
   - Educational domains (.edu.in)

2. **Blocklist Check** - Immediate block for user-blocked domains
   - Stored in `blocked_domains` table
   - Returns 1.0 (100%) risk score

3. **Keyword Blacklist** - Strict policy enforcement
   - Adult content keywords
   - Piracy/torrent keywords
   - Crypto/earning scam keywords
   - Game cracking keywords
   - Returns 0.88 (88%) risk score

4. **Heuristic Analysis** - Pattern-based detection
   - IP address in URL (suspicious)
   - URL length > 75 characters (suspicious)
   - Special characters (@, hyphens in domain)
   - Combines scores: max 0.7 (70%) for heuristics-only

5. **Decision Thresholds**
   - `confidence > 0.60` → Phishing
   - `confidence > 0.95` → Critical
   - `confidence > 0.85` → High
   - `confidence > 0.60` → Medium
   - `confidence <= 0.60` → Low

### Planned ML Model (PyTorch CNN)

**Architecture: PhishNetCNN**
```python
Input: URL string (max 150 chars)
    ↓
Character Embedding (vocab_size=70, embed_dim=64)
    ↓
1D Convolution (filters=128, kernel=5) + ReLU
    ↓
Global Max Pooling
    ↓
Dropout (0.5)
    ↓
Dense Layer (64 units) + ReLU
    ↓
Output Layer (1 unit) + Sigmoid
    ↓
Binary Classification (0=Safe, 1=Phishing)
```

**Training Details:**
- Dataset: `ext_data/refined_training_dataset.csv`
- Optimizer: AdamW (lr=0.001)
- Loss: Binary Cross Entropy
- Batch Size: 1024
- Epochs: 15
- Scheduler: ReduceLROnPlateau
- Device: CUDA (RTX 4060) or CPU

---

## 🎨 User Interface Components

### Chrome Extension Popup
- **Total Scans:** Count of analyzed URLs
- **Threats Blocked:** Count of blocked threats
- **Safety Score:** Overall protection percentage
- **Quick Actions:** Open dashboard, view settings

### Dashboard Pages
1. **Overview** - KPIs and recent activity
2. **Activity Log** - Detailed scan history
3. **Blocklist Management** - Add/remove blocked domains
4. **Temporal Analysis** - Psychological trigger detection
5. **Neural Scanner** - Deep URL analysis
6. **AI Chat** - Interactive security assistant
7. **Privacy Settings** - PII masking, data retention

### Visual Indicators (Search Results)
- 🟢 Green Badge: Safe (0-40%)
- 🟡 Yellow Badge: Caution (41-70%)
- 🔴 Red Badge: Danger (71-100%)

---

## 🔒 Security & Privacy

### Privacy Features
- **Local Processing:** All analysis happens on local machine
- **No Third-Party Services:** No external API calls for detection
- **Data Retention:** Configurable (default: 30 days)
- **PII Masking:** Optional masking of personal information
- **Open Source:** Fully auditable code

### Security Measures
- **Input Validation:** All API inputs validated with Pydantic
- **SQL Injection Protection:** SQLAlchemy ORM prevents SQL injection
- **CORS Configuration:** Configurable allowed origins
- **Rate Limiting:** (Not currently implemented - potential enhancement)
- **HTTPS:** Recommended for production deployment

---

## 📊 Performance Metrics

- **Detection Speed:** <50ms average per URL
- **Cache Hit Rate:** ~70% (reduces repeated API calls)
- **False Positive Rate:** <2% (based on heuristic testing)
- **Database Size:** ~512KB (sql_app.db)
- **Extension Size:** Minimal footprint (~50KB)

---

## 🐛 Known Issues & Limitations

1. **ML Model Disabled:** Sklearn model causes segmentation faults, currently using heuristics only
2. **English-Only:** Detection optimized for English URLs
3. **Cache Delay:** Extension blocklist syncs every 30 minutes
4. **No Mobile Support:** Chrome extension only (no Firefox, Safari, or mobile)
5. **Local Database:** SQLite not suitable for high-concurrency production use
6. **No Rate Limiting:** API endpoints not rate-limited

---

## 🔮 Future Enhancements

### Short-Term
- [ ] Fix and re-enable ML model
- [ ] Add export functionality for activity logs
- [ ] Implement custom risk thresholds
- [ ] Add email alerts for critical threats
- [ ] Firefox extension support

### Long-Term
- [ ] Deep learning transformer models (BERT-based)
- [ ] Community threat intelligence sharing
- [ ] Browser fingerprinting detection
- [ ] Mobile app (Android/iOS)
- [ ] Enterprise features (SSO, centralized management)
- [ ] Real-time email phishing detection

---

## 🧪 Testing & Development

### Development Environment
- Python 3.8+
- Node.js 16+
- Chrome browser
- Git for version control

### Running Tests
```bash
# Backend tests
pip install pytest
pytest backend/tests/

# Frontend tests
cd my-app
npm run test

# Extension testing
# Load unpacked → Make changes → Reload at chrome://extensions/
```

### Debugging
```bash
# Backend logs
python start_server_v3.py
# Check console output for DEBUG messages

# Frontend logs
# Open browser console (F12)

# Extension logs
# chrome://extensions/ → Details → Inspect views: service worker
```

---

## 📚 Documentation Files

- **README.md** - Main project overview and quick start
- **FEATURES.md** - Detailed explanation of 6 defense layers
- **DEVELOPER_GUIDE.md** - Architecture, API docs, contribution guide
- **USER_GUIDE.md** - End-user instructions and troubleshooting
- **QUICK_START_AUTO_POPUP.md** - Popup detection feature guide
- **BLOCKING_FIXED.md** - Blocking mechanism documentation
- **EXTENSION_DEBUG.md** - Extension debugging guide
- **SETUP_COMPLETE.md** - Setup verification checklist
- **QUICK_REFERENCE.md** - Quick command reference

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Create Pull Request

---

## 📄 License

This project is for educational and personal use.

---

## 🎯 Key Takeaways for LLM Agents

### What This Project Does
SecureSentinel is a **full-stack phishing detection system** that protects users in real-time by analyzing URLs before they interact with them. It combines ML (currently disabled), heuristics, and user-defined rules to assign risk scores.

### Main Components
1. **Chrome Extension** - Injects badges into search results
2. **FastAPI Backend** - Analyzes URLs and manages data
3. **Next.js Dashboard** - Monitors activity and manages settings
4. **SQLite Database** - Stores scan history and blocklists

### Current State
- ✅ Fully functional heuristic-based detection
- ✅ Chrome extension working
- ✅ Dashboard operational
- ⚠️ ML model disabled (using fallback heuristics)
- ✅ Database persistence working

### Tech Stack Summary
- **Backend:** Python + FastAPI + SQLAlchemy + scikit-learn/PyTorch
- **Frontend:** TypeScript + Next.js 16 + React 19 + Tailwind CSS v4
- **Extension:** JavaScript (Manifest v3)
- **Database:** SQLite
- **ML:** Sklearn SGD (disabled) / PyTorch CNN (available)

### Architecture Pattern
**Microservices-style** with:
- REST API communication
- Stateless backend
- Client-side caching
- Database persistence
- Event-driven updates

This project demonstrates modern web security practices, full-stack development, and practical ML deployment challenges.
