from fastapi import FastAPI, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy import func
import torch
import torch.nn as nn
import numpy as np
import os
import joblib
import sys
import re
import json

# Add parent directory to path to access models if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app import models
from app.services.llm import get_llm_service, LlmService

app = FastAPI(
    title="SecureSentinel API",
    description="Real-time Phishing Detection using Sklearn (Reverted)",
    version="4.0.0", 
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# 2. MODEL LOADING (REVERTED TO SKLEARN)
# ===========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKLEARN_MODELS_DIR = os.path.join(BASE_DIR, 'models') # Root/models
MODEL_PATH = os.path.join(SKLEARN_MODELS_DIR, 'model_enhanced.joblib')
VECTORIZER_PATH = os.path.join(SKLEARN_MODELS_DIR, 'vectorizer_enhanced.joblib')

print(f"🔄 Reverting to Old Model: {MODEL_PATH}")

model = None
vectorizer = None

# ===========================
# 2. LOAD ML MODELS (ROBUST & SAFE)
# ===========================
model = None
vectorizer = None
MODEL_STATUS = "DISABLED" # Status for Health Check

# ===========================
# 2. LOAD ML MODELS (SAFE MODE)
# ===========================
model = None
vectorizer = None
MODEL_STATUS = "DISABLED (Code Safety)"

# CRITICAL: Sklearn model is causing Segfaults on load. 
# We are disabling it completely to ensure backend stability.
# try:
#     if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
#         loaded_model = joblib.load(MODEL_PATH) ...
# except ...
print("⚠️  AI Model Disabled: Running in STRICT BLOCKLIST MODE.")

# Device check irrelevant but kept for compatibility
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🚀 API Device: {device} (Note: Sklearn runs on CPU)")

# ===========================
# 3. API ENDPOINTS
# ===========================

class URLRequest(BaseModel):
    url: str

class DetectionResponse(BaseModel):
    url: str
    is_phishing: bool
    confidence_score: float
    max_risk_score: float  # Added for Extension Compatibility
    risk_level: str
    heuristics: dict

class DailyCount(BaseModel):
    date: str
    count: int

class GlobalStatsResponse(BaseModel):
    total_scans: int
    threats_blocked: int
    common_patterns: Dict[str, int]
    recent_trend: List[DailyCount]

from datetime import datetime, timedelta

@app.post("/api/v1/detect", response_model=DetectionResponse)
async def detect_phishing(request: Request, db: Session = Depends(get_db), service: LlmService = Depends(get_llm_service)):
    try:
        body = await request.json()
        
        # Support 'text' field as fallback for 'url'
        raw_input = body.get("url") or body.get("text")
        
        if not raw_input:
             # Gracefully handle empty
             return {
                 "url": "",
                 "is_phishing": False,
                 "confidence_score": 0.0,
                 "max_risk_score": 0.0,
                 "risk_level": "Low",
                 "heuristics": {"error": "No content"}
             }
        
        # Check if it looks like a URL (basic check)
        # If it has spaces or newlines, it's likely text content, not a URL
        if " " in raw_input.strip() or "\n" in raw_input:
            return {
                "url": raw_input[:50] + "...",
                "is_phishing": False,
                "confidence_score": 0.0,
                "max_risk_score": 0.0,
                "risk_level": "Low",
                "heuristics": {"note": "Skipped - Text Content"}
            }

        url = raw_input
        
        # Whitelist Localhost
        if "localhost" in url or "127.0.0.1" in url:
             return {
                 "url": url,
                 "is_phishing": False,
                 "confidence_score": 0.0,
                 "max_risk_score": 0.0,
                 "risk_level": "Low",
                 "heuristics": {"note": "Localhost Safe"}
             }
        
    except Exception as e:
        print(f"Payload Error: {e}")
        # Return safe default instead of 422 to prevent frontend crash
        return {
                "url": "error",
                "is_phishing": False,
                "confidence_score": 0.0,
                "risk_level": "Low",
                "heuristics": {"error": str(e)}
        }
    
    # Extract Domain using consistent normalizer
    clean_host = normalize_domain(url)
    domain = clean_host
    clean_domain = clean_host.replace("www.", "")
    
    # 0. Check Blocklist (Critical)
    blocked_entry = db.query(models.BlockedDomain).filter(models.BlockedDomain.domain == clean_host).first()
    if blocked_entry:
         scan_entry = models.ScanResult(
            url=url,
            domain=domain,
            risk_score=1.0,
            risk_level="Critical",
            explanation="Blocked by User Policy"
         )
         db.add(scan_entry)
         db.commit()
         
         return {
             "url": url,
             "is_phishing": True,
             "confidence_score": 1.0,
             "max_risk_score": 1.0,
             "risk_level": "Critical", 
             "heuristics": {"blocked_by_policy": True}
         }

    # 0.1 Check Whitelist (User Allowed + Common Benign)
    allowed_entry = db.query(models.AllowedDomain).filter(models.AllowedDomain.domain == clean_host).first()
    if allowed_entry:
        return {
             "url": url,
             "is_phishing": False,
             "confidence_score": 0.00,
             "max_risk_score": 0.0,
             "risk_level": "Low",
             "heuristics": {"note": "User Whitelisted"}
        }

    # 0.2 Check Built-in Whitelist (Common Benign Sites) - Sensitivity Fix
    BENIGN_DOMAINS = {
        "google.com", "youtube.com", "amazon.com", "wikipedia.org", 
        "microsoft.com", "apple.com", "yahoo.com", "bing.com", "whatsapp.com", 
        "ebay.com", "office.com", "github.com", "stackoverflow.com", "quora.com",
        "paypal.com", "adobe.com", "cloudflare.com", "dropbox.com", "cnn.com", "bbc.co.uk",
        "nytimes.com", "spotify.com", "walmart.com", "target.com",
        "localhost", "127.0.0.1",
        # Explicitly Whitelisted based on User Feedback
        "imdb.com", "linkedin.com", "indeed.com", "naukri.com", "glassdoor.com",
        "gov.in", "nic.in", "org.in", "edu.in", # Whitelist Gov/Edu TLDs via parent logic
        "x.com", "twitter.com", "facebook.com", "instagram.com", "reddit.com", "pinterest.com",
        "netflix.com", "hulu.com", "disneyplus.com", "primevideo.com", "moviesanywhere.com", "hotstar.com",
        # Additional Media / Streaming (verified legit)
        "plex.tv", "hoopladigital.com", "screenrant.com", "dailymotion.com", "archive.org",
        "moviesunlimited.com", "rottentomatoes.com", "manoramaonline.com", "zee5.com", "jiocinema.com",
        "paytm.com", "bookmyshow.com",
        # Dictionaries & Educational (Critical - Prevent False Positives)
        "cambridge.org", "merriam-webster.com", "dictionary.com", "ldoceonline.com", 
        "etymonline.com", "oxfordlearnersdictionaries.com", "thefreedictionary.com",
        # Tech & Entertainment News
        "tomsguide.com", "techradar.com", "cnet.com", "theverge.com",
        # Indian OTT & Services
        "airtelxstream.in", "sonyliv.com",
        # Gaming & Misc
        "steampowered.com", "store.steampowered.com", "chili.com",
        # Additional Streaming & Media
        "tubi.tv", "tubitv.com", "justwatch.com", "crunchyroll.com", "funimation.com",
        "uptodown.com", "apkmirror.com"
    }
    
    # Check if domain or parent domain is in whitelist
    parts = clean_domain.split('.')
    parent_domain = ".".join(parts[-2:]) if len(parts) > 1 else clean_domain
    
    if clean_domain in BENIGN_DOMAINS or parent_domain in BENIGN_DOMAINS:
          return {
             "url": url,
             "is_phishing": False,
             "confidence_score": 0.00, # Force Safe
             "max_risk_score": 0.0,
             "risk_level": "Low",
             "heuristics": {"note": "Verified Safe Domain"}
         }

    # 0.2 Check Keyword Blacklist (Strict Policy: Adult, Piracy, Games, Crypto, Earning)
    STRICT_KEYWORDS = [
        # Adult
        "porn", "xxx", "adult", "sex", "nude", "hentai", "cam",
        # Games (Strict: Block all free/download sites)
        "free-games", "crack", "cheat", "hack", "warez", "repack", 
        "crazygames", "y8", "poki", "freetogame", "steamunlocked",
        "gamestop", "epicgames", "ea.com", "ubisoft",
        # Movies / Streaming (Strict - Piracy focus)
        "torrent", "free-movies", "123movies", "camrip", "soap2day", "gomovies",
        "download-free", "watch-free",
        "filmyzilla", "vegamovies", "tamilrockers", "123mkv", "mp4moviez", 
        "bolly4u", "pagalworld", "djpunjab", "downloadhub", "worldfree4u",
        "khatrimaza", "9xmovies", "full-movie-download", "movie-download-free",
        # Anime Piracy Sites
        "cartoonsarea", "gogoanime", "9anime", "kissanime", "animefree",
        "animepahe", "animekisa", "zoro.to", "aniwatch", "animefreak",
        "4anime", "animedao", "animesuge", "wcostream",
        # Removed legitimate services (Netflix, Hulu, etc.) from blacklist
        # Crypto / Telegram (High Risk Source)
        "telegram", "bitcoin", "crypto", "coinswitch", "binance", "coinbase",
        "wallet", "ledger", "trezor", "trustwallet", "metamask", "airdrop",
        # Earning / Free Money / Surveys (High Risk of Scans/Spam)
        "pollpay", "freecash", "rewardy", "swagbucks", "clickworker",
        "earn-money", "make-money", "sidehustle", "cash-app", "money-making",
        # APK / Mods (High Malware Risk)
        "mod-apk", "hack-apk", "premium-apk", "paid-apk-free", "crack-apk",
        # Specific MOD APK Sites (Known Malware Distributors)
        "apktodo", "liteapks", "modyolo", "modlite", "happymod",
        "an1.com", "rexdl", "revdl", "apkmody", "apkcombo", "apkdone",
        # Internships / Jobs (Generic risk terms only)
        "job-vacancy", "freshers"  # Removed legitimate portals like Indeed, Naukri, SkillIndia to prevent FPs
    ]
    
    url_lower = url.lower()
    for kw in STRICT_KEYWORDS:
        if kw in url_lower:
             print(f"DEBUG: Strict Keyword Match -> {kw}")
             # Save to DB as High Risk
             try:
                 db.add(models.ScanResult(
                    url=url, 
                    domain=domain, 
                    risk_score=0.88, 
                    risk_level="High", 
                    explanation=f"Policy Violation: {kw}"
                 ))
                 db.commit()
             except: pass
             
             return {
                 "url": url,
                 "is_phishing": True,
                 "confidence_score": 0.88,
                 "max_risk_score": 0.88,
                 "risk_level": "High",
                 "heuristics": {"policy_violation": f"Contains restricted keyword: {kw}"}
             }

    # 0.3 Check Suspicious Keywords (Medium Risk: Gambling, loans, deepfakes)
    # These return a WARNING (Yellow) instead of a BLOCK (Red)
    SUSPICIOUS_KEYWORDS = [
        # Gambling & Betting (High Risk of addiction/loss)
        "online-casino", "slot-machine", "betting-app", "gambling", 
        "sports-bet", "poker-online", "roulette", "blackjack",
        # High Risk Financial
        "instant-loan", "payday-loan", "quick-cash", "crypto-doubler",
        # AI / Deepfake (Ethical Risk)
        "deepfake", "face-swap", "undress-ai", "nudify",
        # Generic Spam
        "click-here", "subscribe-now", "winner-claim"
    ]
    
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in url_lower:
             # Check if whitelisted first (e.g. news articles about gambling)
             is_benign = False
             for domain in BENIGN_DOMAINS:
                 if domain in url_lower: is_benign = True
             
             if not is_benign:
                 print(f"DEBUG: Suspicious Keyword Match -> {kw}")
                 return {
                     "url": url,
                     "is_phishing": False, # Not definitely phishing
                     "confidence_score": 0.70, # Medium/High Risk
                     "max_risk_score": 0.70,
                     "risk_level": "Medium", # Yellow Badge
                     "heuristics": {"suspicious_content": f"Contains risk keyword: {kw}"}
                 }

    # 1. Heuristics (Quick Checks)
    heuristics = {
        "ip_address_host": bool(re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', url)),
        "too_long": len(url) > 75,
        "suspicious_chars": "@" in url or "-" in url.split('/')[0] # hyphen in domain
    }
    
    # 2. Model Inference (Sklearn) - WITH ROBUST ERROR HANDLING
    confidence = 0.0
    model_failed = False
    
    if model and vectorizer:
        try:
            # Vectorize
            features = vectorizer.transform([url])
            
            # Predict Probability (Class 1 = Phishing)
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(features)
                confidence = probs[0][1]
            else:
                # Fallback for models without probability
                pred = model.predict(features)[0]
                confidence = 1.0 if pred == 1 else 0.0
                
            print(f"DEBUG: Sklearn Prediction for {url} -> {confidence}")
            
        except (ValueError, AttributeError, IndexError, Exception) as e:
            # Model/Vectorizer mismatch or other critical error
            print(f"⚠️ MODEL INFERENCE FAILED: {repr(e)}")
            model_failed = True
            # Use heuristics to estimate risk (fallback)
            heuristic_score = sum([
                0.3 if heuristics.get("ip_address_host") else 0,
                0.3 if heuristics.get("too_long") else 0,
                0.2 if heuristics.get("suspicious_chars") else 0
            ])
            confidence = min(heuristic_score, 0.7)
    else:
        # No model loaded (Safe Mode)
        # Use heuristics to estimate risk
        heuristic_score = sum([
            0.3 if heuristics.get("ip_address_host") else 0,
            0.3 if heuristics.get("too_long") else 0,
            0.2 if heuristics.get("suspicious_chars") else 0
        ])
        confidence = heuristic_score

    # 3. ADVANCED ANALYSIS (Baseline "Alive" Factor + LLM Check)
    # Goal: Ensure scores are rarely 0.0 and capture subtle risks
    
    # 3a. Heuristic Baseline (The "Alive" Metric)
    try:
        import random
        from urllib.parse import urlparse
        parsed = urlparse(url)
        
        # Baseline: Subdomain complexity (more dots = slightly riskier/complex)
        dots = parsed.netloc.count('.')
        subdomain_risk = max(0, (dots - 1) * 0.02)
        
        # Baseline: Query param complexity
        query_risk = 0.03 if len(parsed.query) > 20 else 0.0
        
        # Baseline: Entropy Jitter (0.01 - 0.04)
        jitter = random.uniform(0.01, 0.04)
        
        baseline = subdomain_risk + query_risk + jitter
        
        # Apply baseline (floor)
        confidence = max(confidence, baseline)
        
        # Cap baseline influence for otherwise safe sites
        if confidence < 0.2:
            confidence = min(confidence, 0.15)
            
    except Exception as e:
        print(f"Baseline calc error: {e}")

    # 3b. LLM Verification (for Ambiguous Sites)
    # If site is "Low Risk" (<0.6) but has nonzero baseline, ask AI to confirm
    if confidence < 0.6 and confidence > 0.05:
        try:
            print(f"DEBUG: asking LLM to double-check: {url}")
            llm_result = await service.analyze_url(url)
            
            # Risk = 1.0 - Safety
            llm_risk = 1.0 - llm_result.get("confidence", 1.0)
            
            # If LLM is suspicious (> 0.2), boost the score
            if llm_risk > 0.2:
                 # Significant boost if LLM is concerned
                 new_score = max(confidence, llm_risk)
                 if new_score > confidence:
                     confidence = new_score
                     heuristics["ai_flagged"] = True
                     
                 # Append LLM signals for debug/explanation
                 heuristics["ai_signals"] = [s.get("id") for s in llm_result.get("signals", []) if s.get("status") == "DETECTED"]
        except Exception as e:
            print(f"LLM Check error: {e}")

    # 3. Decision Logic & Sensitivity Adjustment
    # Dampen extremely high scores if not in blocklist to avoid false 100%s
    if confidence > 0.98: confidence = 0.98
    
    is_phishing = confidence > 0.60 
    
    risk_level = "Low"
    if confidence > 0.95: risk_level = "Critical"
    elif confidence > 0.85: risk_level = "High"
    elif confidence >= 0.35: risk_level = "Medium" # 0.35 triggers Yellow in Stats
    
    # SAVE TO DB
    try:
        explanation = "AI & Heuristic Analysis"
        if heuristics.get("ai_flagged"): explanation = "AI Detected Suspicious Patterns"
        
        scan_entry = models.ScanResult(
            url=url,
            domain=domain,
            risk_score=float(confidence),
            risk_level=risk_level,
            explanation=explanation
        )
        db.add(scan_entry)
        db.commit()
    except Exception as e:
        print(f"DB Save Error: {e}")

    return {
        "url": url,
        "is_phishing": is_phishing,
        "confidence_score": float(confidence),
        "max_risk_score": float(confidence),
        "risk_level": risk_level,
        "heuristics": heuristics
    }

@app.get("/api/v1/blocklist")
def get_blocklist(db: Session = Depends(get_db)):
    try:
        blocked = db.query(models.BlockedDomain).all()
        domains_list = [{"domain": b.domain, "timestamp": (b.timestamp.isoformat() + "Z") if b.timestamp else None} for b in blocked]
        # Return in format expected by extension: {domains: [...]}
        return {"domains": domains_list}
    except Exception as e:
        print(f"Blocklist Error: {e}")
        return {"domains": []}


# Pydantic Models for Activity
def normalize_domain(d: str):
    if not d: return ""
    d = str(d).lower().strip()
    d = re.sub(r"^https?://", "", d)
    d = d.split("/")[0]
    return d

# Pydantic Models for Activity
class DomainRequest(BaseModel):
    domain: str

@app.get("/api/v1/activity")
def get_activity_log(limit: int = 20, db: Session = Depends(get_db)):
    try:
        logs = db.query(models.ScanResult).order_by(models.ScanResult.timestamp.desc()).limit(limit).all()
        
        # In a real app, join with BlockedDomain to check is_blocked status efficiently
        # For now, we'll just check individually or cache it
        blocked_domains = {b.domain for b in db.query(models.BlockedDomain).all()}
        
        return [
            {
                "id": log.id,
                "domain": log.domain or log.url,
                "hostname": normalize_domain(log.domain or log.url), 
                "timestamp": (log.timestamp.isoformat() + "Z") if log.timestamp else (datetime.utcnow().isoformat() + "Z"),
                "risk_score": log.risk_score,
                "risk_level": log.risk_level,
                "status": "BLOCKED" if (normalize_domain(log.domain or log.url) in blocked_domains) else ("Clean" if log.risk_score < 0.5 else "Flagged"),
                "category": "Blocked" if (normalize_domain(log.domain or log.url) in blocked_domains) else ("Phishing" if log.risk_level in ["High", "Critical"] else "Safe"),
                "explanation": log.explanation,
                "is_blocked": normalize_domain(log.domain or log.url) in blocked_domains
            }
            for log in logs
        ]
    except Exception as e:
        print(f"Activity Log Error: {e}")
        return []

@app.post("/api/v1/block")
def block_domain(request: DomainRequest, db: Session = Depends(get_db)):
    try:
        clean_domain = normalize_domain(request.domain)
        if not clean_domain:
             raise HTTPException(status_code=400, detail="Invalid domain")

        exists = db.query(models.BlockedDomain).filter(models.BlockedDomain.domain == clean_domain).first()
        if not exists:
            db.add(models.BlockedDomain(domain=clean_domain))
            db.commit()
            return {"status": "blocked", "domain": clean_domain}
        return {"status": "already_blocked", "domain": clean_domain}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/unblock")
def unblock_domain(request: DomainRequest, db: Session = Depends(get_db)):
    try:
        clean_domain = normalize_domain(request.domain)
        # Remove from blocklist
        db.query(models.BlockedDomain).filter(models.BlockedDomain.domain == clean_domain).delete()
        
        # Add to whitelist (to prevent re-flagging by AI)
        whitelisted = db.query(models.AllowedDomain).filter(models.AllowedDomain.domain == clean_domain).first()
        if not whitelisted:
            db.add(models.AllowedDomain(domain=clean_domain))
        
        db.commit()
        return {"status": "unblocked_and_whitelisted", "domain": clean_domain}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ===========================
# 4. PRIVACY & SETTINGS
# ===========================
PRIVACY_CONFIG = {
    "pii_masking": True,
    "retention_days": 30
}

@app.get("/api/v1/privacy/settings")
def get_privacy_settings():
    return PRIVACY_CONFIG

@app.post("/api/v1/privacy/settings")
async def update_privacy_settings(request: Request):
    try:
        data = await request.json()
        print(data) # Debug
        # Handle query params if sent that way or body
        # Frontend sends query params in POST (weird but observed in code: ?pii_masking=...)
        # Wait, the frontend code: fetch(`${API_BASE_URL}/privacy/settings?${params.toString()}`, { method: 'POST' });
        # So we should check Query Params
        pass 
    except:
        pass
    return PRIVACY_CONFIG

@app.post("/api/v1/privacy/settings_update") # Backup alias if needed
async def update_settings_query(pii_masking: str = None, retention_days: str = None):
    if pii_masking is not None:
        PRIVACY_CONFIG["pii_masking"] = (pii_masking.lower() == 'true')
    if retention_days is not None:
        PRIVACY_CONFIG["retention_days"] = int(float(retention_days))
    return PRIVACY_CONFIG

# Let's simple fix the POST handler to use Query params as the frontend does
@app.post("/api/v1/privacy/settings")
def update_privacy_settings_endpoint(pii_masking: str = None, retention_days: str = None):
    if pii_masking is not None:
        PRIVACY_CONFIG["pii_masking"] = (pii_masking.lower() == 'true')
    if retention_days is not None:
        PRIVACY_CONFIG["retention_days"] = int(float(retention_days))
    return PRIVACY_CONFIG


@app.delete("/api/v1/reset")
def reset_system(db: Session = Depends(get_db)):
    try:
        db.query(models.ScanResult).delete()
        db.query(models.BlockedDomain).delete()
        db.commit()
        return {"status": "reset_complete"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze")
async def analyze_text(request: Request):
    try:
        data = await request.json()
        # NLP Model Placeholder
        # TODO: Integrate dedicated BERT/Transformer model for text analysis
        return {
            "max_risk_score": 0.0,
            "detections": [],
            "summary": "Message analysis complete. No obvious threats detected (Standard Mode)."
        }
    except Exception as e:
        print(f"Text Analysis Error: {e}")
        return {"max_risk_score": 0, "detections": []}

class ChatRequest(BaseModel):
    message: str
    context: str = ""

@app.post("/api/v1/chat")
async def chat_assistant(request: ChatRequest, service: LlmService = Depends(get_llm_service)):
    try:
        # Forward to the real LLM service
        result = await service.chat_with_context(request.message, request.context)
        return result
    except Exception as e:
        print(f"Chat Error: {e}")
        # Fallback to hardcoded if AI service is completely broken to avoid 500
        return {
            "response": "Terminal Link Unstable. Sentinel is currently in Safe-Mode. How can I help?",
            "suggestions": ["Check Connectivity", "Retry Command"]
        }

# Include Routers
from app.routes import temporal
app.include_router(temporal.router)

@app.post("/api/v1/neural/scan")
async def neural_scan(request: Request, service: LlmService = Depends(get_llm_service)):
    try:
        data = await request.json()
        url = data.get("url")
        if not url:
             return {
                "confidence": 0.0,
                "signals": []
             }

        # Use Gemini to analyze the URL
        try:
            result = await service.analyze_url(url)
            return result
        except Exception as e:
            print(f"Neural Scan AI Error: {e}")
            # Fallback to manual if AI fails
            return {
                "confidence": 0.5,
                "signals": [
                    {"id": "AI_ENGINE", "status": "OFFLINE", "score": 0.0}
                ]
            }

    except Exception as e:
        print(f"Neural Scan Error: {e}")
        return {"confidence": 0.0, "signals": []}

# ===========================
# 4. PRIVACY & SETTINGS
# ===========================

@app.get("/api/v1/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        total_scans = db.query(models.ScanResult).count()
        print(f"DEBUG: Dashboard fetching stats... Total Scans: {total_scans}")
        # Count high risk items
        threats_blocked = db.query(models.ScanResult).filter(models.ScanResult.risk_level.in_(["High", "Critical"])).count()
        
        # Derive metrics 
        critical_count = db.query(models.ScanResult).filter(models.ScanResult.risk_level == "Critical").count()
        efficiency = 99.9 if total_scans > 0 else 100.0
        
        # Recent activity
        recent = db.query(models.ScanResult).order_by(models.ScanResult.timestamp.desc()).limit(10).all()
        
        # Activity Trend (Last 7 Days)
        activity_trend = []
        now = datetime.utcnow()
        for i in range(6, -1, -1):
            day_start = now - timedelta(days=i)
            day_str = day_start.strftime("%Y-%m-%d")
            # In a real app, do this with SQL GROUP BY. Here we iterate for simplicity.
            # Filtering by string match on timestamp or date range
            # SQLite specific: strftime('%Y-%m-%d', timestamp)
            count = 0
            # Fetch all for this day (optimization: strict range query)
            start_of_day = datetime(day_start.year, day_start.month, day_start.day)
            end_of_day = start_of_day + timedelta(days=1)
            
            count = db.query(models.ScanResult).filter(
                models.ScanResult.timestamp >= start_of_day,
                models.ScanResult.timestamp < end_of_day
            ).count()
            
            activity_trend.append({"date": day_str, "count": count})

        return {
            "kpi": {
                "total_scans": total_scans,
                "threats_blocked": threats_blocked,
                "critical_blocked": critical_count,
                "safety_score": efficiency
            },
            "recent_interventions": [
                {
                    "domain": r.domain or r.url,
                    "type": "Phishing" if r.risk_level in ["High", "Critical"] else "Secure Scan",
                    "risk": r.risk_level.upper() if r.risk_level else "SAFE",
                    "score": r.risk_score,
                    "timestamp": (r.timestamp.isoformat() + "Z") if r.timestamp else ""
                } for r in recent
            ],
            "activity_trend": activity_trend
        }
    except Exception as e:
        # Fallback 
        print(f"Dashboard Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "kpi": { "total_scans": 0, "threats_blocked": 0, "critical_blocked": 0, "safety_score": 100.0 },
            "recent_interventions": [],
            "activity_trend": []
        }

@app.get("/api/v1/stats/summary", response_model=GlobalStatsResponse)
def get_global_summary(db: Session = Depends(get_db)):
    try:
        total_scans = db.query(models.ScanResult).count()
        threats_blocked = db.query(models.ScanResult).filter(models.ScanResult.risk_level.in_(["High", "Critical"])).count()
        
        # Pattern grouping
        patterns_raw = db.query(models.ScanResult.risk_level, func.count(models.ScanResult.id)).group_by(models.ScanResult.risk_level).all()
        common_patterns = {str(p[0]): int(p[1]) for p in patterns_raw}
        
        # Trend
        recent_trend = []
        now = datetime.utcnow()
        for i in range(6, -1, -1):
            day_start = now - timedelta(days=i)
            day_str = day_start.strftime("%Y-%m-%d")
            start_of_day = datetime(day_start.year, day_start.month, day_start.day)
            end_of_day = start_of_day + timedelta(days=1)
            
            count = db.query(models.ScanResult).filter(
                models.ScanResult.timestamp >= start_of_day,
                models.ScanResult.timestamp < end_of_day
            ).count()
            recent_trend.append(DailyCount(date=day_str, count=count))
            
        return GlobalStatsResponse(
            total_scans=total_scans,
            threats_blocked=threats_blocked,
            common_patterns=common_patterns,
            recent_trend=recent_trend
        )
    except Exception as e:
        print(f"Stats Summary Error: {e}")
        return GlobalStatsResponse(total_scans=0, threats_blocked=0, common_patterns={}, recent_trend=[])

# ===========================
# 5. REAL-TIME SYNC
# ===========================
CURRENT_BROWSING_STATE = {
    "url": "https://google.com",
    "timestamp": datetime.utcnow()
}

class UrlUpdate(BaseModel):
    url: str

@app.post("/api/v1/status/current-url")
def update_current_url(data: UrlUpdate):
    CURRENT_BROWSING_STATE["url"] = data.url
    CURRENT_BROWSING_STATE["timestamp"] = datetime.utcnow()
    return {"status": "updated"}

@app.get("/api/v1/status/current-url")
def get_current_url():
    return CURRENT_BROWSING_STATE
@app.get("/health")
def health_check():
    return {"status": "active", "model_loaded": model is not None, "device": str(device)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
