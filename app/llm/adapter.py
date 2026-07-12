import os
import json
from typing import Dict, Any

# Optional OpenAI integration. If openai isn't installed or API key isn't set, we fall back to a deterministic mock.
try:
    import openai
except Exception:
    openai = None

# Configure via environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # currently supports 'openai' or 'mock'


def _safe_parse_json(text: str) -> Any:
    """Try to extract and parse the first JSON object in text."""
    try:
        return json.loads(text)
    except Exception:
        # try to find a JSON object substring
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                return None
        return None


def call_llm(prompt: str, max_tokens: int = 256) -> Dict[str, Any]:
    """
    Call the configured LLM provider with the provided prompt and return a structured dict.

    Expected return dictionary (prototype):
      {
        "scam_score": float (0..1),
        "explanation": ["...", ...],
        "suggestions": ["..."],  # optional
        "raw": "raw model output"
      }

    The function attempts to use OpenAI ChatCompletion if configured, otherwise returns a mock
    deterministic result based on simple heuristics so the pipeline remains runnable.
    """
    # Try OpenAI provider
    if LLM_PROVIDER == "openai" and openai is not None and (OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")):
        try:
            if OPENAI_API_KEY:
                openai.api_key = OPENAI_API_KEY

            # Use chat completion API
            messages = [
                {"role": "system", "content": "You are an assistant that analyzes messages for scams. Respond in JSON with fields: scam_score (0..1), explanation (list of strings), suggestions (optional list of strings)."},
                {"role": "user", "content": prompt}
            ]

            resp = openai.ChatCompletion.create(
                model=LLM_MODEL,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.0,
            )

            text = resp["choices"][0]["message"]["content"]
            parsed = _safe_parse_json(text)
            if isinstance(parsed, dict):
                parsed["raw"] = text
                return parsed
            else:
                # If parsing failed, return the raw text in 'raw' and a minimal heuristic
                return {
                    "scam_score": 0.5,
                    "explanation": ["LLM returned non-JSON output; see raw output"],
                    "raw": text
                }
        except Exception as e:
            # fall through to mock below
            return {"scam_score": 0.0, "explanation": [f"LLM call failed: {e}"], "raw": ""}

    # Fallback mock implementation (deterministic heuristics)
    # Simple heuristics: count occurrences of urgency/link/payment keywords
    text_lower = prompt.lower()
    keywords = ["urgent", "verify", "account", "password", "transfer", "win", "prize", "click", "invoice", "pay", "upi"]
    matches = [k for k in keywords if k in text_lower]
    urgency_markers = ["urgent", "immediately", "now", "asap", "act now", "limited time"]
    urgency = any(w in text_lower for w in urgency_markers)
    has_link = "http://" in text_lower or "https://" in text_lower or "www." in text_lower

    score = min(0.99, 0.2 + 0.18 * len(matches) + (0.15 if urgency else 0) + (0.1 if has_link else 0))

    explanation = []
    if matches:
        explanation.append(f"Found keywords: {', '.join(matches)}")
    if urgency:
        explanation.append("Urgency language detected")
    if has_link:
        explanation.append("Contains a URL or link-like string")

    return {
        "scam_score": round(score, 3),
        "explanation": explanation or ["No clear scam indicators detected by heuristic fallback"],
        "suggestions": ["Flag for review" if score > 0.6 else "Monitor"],
        "raw": "(mock response)"
    }
