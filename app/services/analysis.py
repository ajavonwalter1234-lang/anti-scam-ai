import os
import json
from typing import Dict, Any, List, Tuple

from app.rag.middleware import build_grounded_prompt
from app.rag.vector_store import VectorStore
from app.processors.text_processor import analyze_text as rule_analyze_text


def query_vector_store(text: str, top_k: int = 3) -> Dict[str, Any]:
    """Query the local vector store and return matches along with optional metadata."""
    vs = VectorStore()
    if vs.disabled:
        return {"matches": []}

    hits = vs.query(text, k=top_k)

    # load metadata if present
    meta_path = os.path.join(os.getcwd(), "data", "vector_store_metadata.json")
    metadata = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}

    matches = []
    for _id, htext, score in hits:
        matches.append({
            "id": _id,
            "text": htext,
            "score": score,
            "metadata": metadata.get(_id, {})
        })

    return {"matches": matches}


async def analyze_text_with_rag(user_text: str) -> Dict[str, Any]:
    """
    Complete text analysis that:
      1. Queries the vector store for relevant context
      2. Builds a grounded prompt using middleware
      3. Calls the existing rule-based analyzer (or an LLM) with the augmented prompt
      4. Returns a structured response including rag matches and the debug prompt
    """
    # 1) Retrieve RAG matches
    rag_results = query_vector_store(user_text, top_k=3)
    rag_matches = rag_results.get("matches", []) if rag_results else []

    # 2) Build grounded prompt
    grounded_prompt = build_grounded_prompt(user_text, rag_matches)

    # 3) For the prototype, use the rule-based text analyzer on the grounded prompt.
    # The analyzer accepts external_rag_matches as a list of tuples (id, text, score), so prepare that.
    external_rag_tuples: List[Tuple[str, str, float]] = [
        (m.get("id"), m.get("text"), float(m.get("score", 0.0))) for m in rag_matches
    ]

    model_response = rule_analyze_text(grounded_prompt, external_rag_matches=external_rag_tuples)

    # 4) Construct the unified response
    response = {
        "scam_score": model_response.get("scam_score"),
        "explanation": model_response.get("explanation"),
        "rag_matches": rag_matches,
        "debug_prompt": grounded_prompt,
    }

    # include raw model_response for debug if needed
    response["_model_response"] = model_response

    return response
