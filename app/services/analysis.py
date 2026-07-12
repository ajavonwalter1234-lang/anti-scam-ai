import os
import json
from typing import Dict, Any, List, Tuple

from app.rag.middleware import build_grounded_prompt
from app.rag.vector_store import VectorStore
from app.llm.adapter import call_llm


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
      3. Calls the configured LLM adapter with the augmented prompt
      4. Returns a structured response including rag matches and the debug prompt
    """
    # 1) Retrieve RAG matches
    rag_results = query_vector_store(user_text, top_k=3)
    rag_matches = rag_results.get("matches", []) if rag_results else []

    # 2) Build grounded prompt
    grounded_prompt = build_grounded_prompt(user_text, rag_matches)

    # 3) Call LLM adapter
    llm_output = call_llm(grounded_prompt)

    # Normalize output to expected fields
    scam_score = llm_output.get("scam_score")
    explanation = llm_output.get("explanation") or []

    response = {
        "scam_score": scam_score,
        "explanation": explanation,
        "rag_matches": rag_matches,
        "debug_prompt": grounded_prompt,
        "_llm_raw": llm_output.get("raw"),
    }

    # include any extra LLM fields (suggestions, etc.)
    for k in ("suggestions",):
        if k in llm_output:
            response[k] = llm_output[k]

    return response
