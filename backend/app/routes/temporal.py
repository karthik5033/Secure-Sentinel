"""
Temporal Analysis API Endpoint
Provides detailed temporal pressure analysis for popups/dialogs
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import re

router = APIRouter(prefix="/api/v1/temporal", tags=["Temporal Analysis"])

# Trigger patterns for temporal pressure detection
TRIGGER_PATTERNS = {
    "URGENCY": {
        "patterns": [
            "immediately", "urgent", "now", "asap", "hurry", "quick", "expire", 
            "expiring", "deadline", "limited time", "act now", "don't wait",
            "right now", "instant", "today only", "expires soon", "last chance",
            "ending soon", "while supplies last", "limited offer", "time sensitive",
            "running out", "don't miss", "before it's too late", "act fast"
        ],
        "weight": 0.9
    },
    "FEAR": {
        "patterns": [
            "locked", "suspended", "terminated", "blocked", "compromised", 
            "unauthorized", "suspicious", "fraud", "security alert", "breach",
            "hacked", "virus", "malware", "danger", "warning", "critical",
            "account closed", "access denied", "banned", "sensitive content",
            "inappropriate", "not appropriate", "restricted", "flagged",
            "reported", "violation", "threat", "risk", "unsafe"
        ],
        "weight": 0.85
    },
    "AUTHORITY": {
        "patterns": [
            "verify", "confirm", "update", "required", "must", "mandatory", 
            "compliance", "official", "authorized", "government", "legal",
            "regulation", "policy", "terms", "obligation", "duty", "need to",
            "have to", "years old", "age verification", "age restriction",
            "content policy", "community guidelines", "terms of service"
        ],
        "weight": 0.75
    },
    "IMPERSONATION": {
        "patterns": [
            "account", "password", "credentials", "login", "log in", "sign in",
            "security", "bank", "payment", "billing", "credit card", 
            "social security", "ssn", "paypal", "amazon", "microsoft", 
            "google", "apple", "facebook", "twitter", "instagram", "continue on",
            "open app", "download app", "view this media", "to view"
        ],
        "weight": 0.8
    },
    "SCARCITY": {
        "patterns": [
            "only", "only available", "left", "remaining", "few", "last", 
            "final", "exclusive", "limited stock", "selling fast", "almost gone", 
            "low stock", "limited access", "members only", "invite only"
        ],
        "weight": 0.7
    },
    "REWARD": {
        "patterns": [
            "free", "win", "winner", "prize", "reward", "gift", "bonus",
            "congratulations", "selected", "lucky", "claim", "redeem",
            "earn", "discount", "offer", "deal", "save", "special"
        ],
        "weight": 0.65
    },
    "GEOLOCATION": {
        "patterns": [
            "region", "location", "country", "area", "zone", "optimized for",
            "users from", "not available in", "restricted in", "your area"
        ],
        "weight": 0.6
    },
    "NAVIGATION": {
        "patterns": [
            "proceed", "stay", "leave", "go back", "click here", "press", 
            "enter", "submit", "continue", "redirect", "forward"
        ],
        "weight": 0.5
    }
}

class TemporalAnalysisRequest(BaseModel):
    text: str
    context: Optional[str] = None
    url: Optional[str] = None

class Trigger(BaseModel):
    word: str
    category: str
    score: float
    position: int

class TemporalAnalysisResponse(BaseModel):
    text: str
    risk_score: float
    risk_level: str
    triggers: List[Trigger]
    categories: Dict[str, float]
    explanation: str

# Global list to store recent temporal scans for the dashboard
recent_temporal_scans = []
MAX_TEMPORAL_HISTORY = 20  # Store up to 20 recent scans

def analyze_temporal_pressure(text: str) -> TemporalAnalysisResponse:
    """
    Analyze text for temporal pressure tactics
    """
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    text_lower = text.lower()
    triggers = []
    category_scores = {cat: 0.0 for cat in TRIGGER_PATTERNS.keys()}
    
    # Find all triggers
    for category, config in TRIGGER_PATTERNS.items():
        patterns = config["patterns"]
        weight = config["weight"]
        
        for pattern in patterns:
            # Find all occurrences
            pattern_lower = pattern.lower()
            start = 0
            while True:
                pos = text_lower.find(pattern_lower, start)
                if pos == -1:
                    break
                
                triggers.append(Trigger(
                    word=pattern,
                    category=category,
                    score=weight,
                    position=pos
                ))
                
                # Update category score (max score for category)
                category_scores[category] = max(category_scores[category], weight)
                
                start = pos + 1
    
    # Sort triggers by position (temporal order)
    triggers.sort(key=lambda t: t.position)
    
    # Calculate overall risk score
    if not triggers:
        risk_score = 0.0
        active_categories = []
    else:
        # Weighted average of category scores
        active_categories = [score for score in category_scores.values() if score > 0]
        if active_categories:
            risk_score = sum(active_categories) / len(active_categories)
            
            # Boost if multiple categories present
            if len(active_categories) > 2:
                risk_score = min(1.0, risk_score * 1.2)
            
            # Boost if many triggers
            if len(triggers) > 5:
                risk_score = min(1.0, risk_score * 1.1)
        else:
            risk_score = 0.0
    
    # Determine risk level
    if risk_score > 0.7:
        risk_level = "HIGH_RISK"
    elif risk_score > 0.4:
        risk_level = "MODERATE"
    else:
        risk_level = "SAFE"
    
    # Generate explanation
    if risk_score > 0.7:
        explanation = f"High temporal pressure detected. Found {len(triggers)} manipulation triggers across {len(active_categories)} categories."
    elif risk_score > 0.4:
        explanation = f"Moderate pressure tactics detected. Found {len(triggers)} triggers."
    else:
        explanation = "No significant temporal pressure detected."
    
    result = TemporalAnalysisResponse(
        text=text,  # Keep full text for the dashboard
        risk_score=risk_score,
        risk_level=risk_level,
        triggers=triggers[:15],  # Limit to top 15
        categories=category_scores,
        explanation=explanation
    )

    # Store in history for dashboard retrieval
    global recent_temporal_scans
    recent_temporal_scans.insert(0, result.dict())
    if len(recent_temporal_scans) > MAX_TEMPORAL_HISTORY:
        recent_temporal_scans.pop()
        
    return result

@router.post("/analyze", response_model=TemporalAnalysisResponse)
async def analyze_temporal(request: TemporalAnalysisRequest):
    """
    Analyze text for temporal pressure and manipulation tactics
    """
    try:
        return analyze_temporal_pressure(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/latest", response_model=Optional[TemporalAnalysisResponse])
async def get_latest_temporal():
    """
    Retrieve the most recent temporal analysis scan
    """
    if recent_temporal_scans:
        return recent_temporal_scans[0]
    return None

@router.get("/history", response_model=List[TemporalAnalysisResponse])
async def get_temporal_history():
    """
    Retrieve history of recent temporal analysis scans
    """
    return recent_temporal_scans

@router.get("/health")
async def temporal_health():
    """
    Health check for temporal analysis service
    """
    return {
        "status": "ok",
        "service": "temporal_analysis",
        "version": "1.0.0",
        "categories": list(TRIGGER_PATTERNS.keys())
    }
