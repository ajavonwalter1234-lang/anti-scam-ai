import json
import os
from typing import Dict, Any, List

from ..config import get_config

_cfg = get_config()

KEYWORDS_PATH = os.path.join(os.getcwd(), "data", "keywords", "scam_keywords.json")

# Load keywords at import time for simplicity in this prototype
try:
    with open(KEYWORDS_PATH, "r") as f:
        KEYWORDS = json.load(f)
except Exception:
    KEYWORDS = ["urgent", "bank", "password", "transfer", "win", "prize", "click", "verify", "update"]


def analyze_text(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    matches = [k for k in KEYWORDS if k.lower() in text_lower]

    # Simple urgency detection: look for exclamation marks or common urgency words
    urgency_markers = ["urgent", "immediately", "now", "asap", "limited time", "act now"]
    urgency = any(w in text_lower for w in urgency_markers)

    # Simple link detection
    has_link = "http://" in text_lower or "https://" in text_lower or "www." in text_lower

    # Construct a deterministic confidence score between 0 and 1
    score = min(0.95, 0.25 + 0.2 * len(matches) + (0.15 if urgency else 0) + (0.1 if has_link else 0))

    explanation = []
    if matches:
        explanation.append(f"Found keywords: {', '.join(matches)}")
    if urgency:
        explanation.append("Urgency language detected")
    if has_link:
        explanation.append("Contains a URL or link-like string")

    return {
        "scam_score": round(score, 3),
        "matches": matches,
        "urgency": urgency,
        "has_link": has_link,
        "explanation": explanation,
    }
