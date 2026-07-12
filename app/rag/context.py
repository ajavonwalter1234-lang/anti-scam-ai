import json
import os
from typing import List, Tuple, Optional

from app.rag.vector_store import VectorStore


def get_rag_context(text: str, k: int = 3) -> Tuple[List[Tuple[str, str, float]], str]:
    """
    Query the local vector store and return top-k matches plus a concatenated context string.

    Returns (matches, context_string) where matches is a list of (id, text, score)
    and context_string is a human-readable aggregation suitable for prepending to model inputs.
    """
    vs = VectorStore()
    if vs.disabled:
        return [], ""

    hits = vs.query(text, k=k)

    # try to load metadata for richer context
    meta_path = os.path.join(os.getcwd(), "data", "vector_store_metadata.json")
    metadata = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            metadata = {}

    context_parts = []
    for idx, (hid, htext, score) in enumerate(hits):
        meta = metadata.get(hid, {})
        title = meta.get("title") or (htext[:60] + "...")
        source = meta.get("source")
        date = meta.get("date")
        header = f"[{hid}] {title}"
        if source or date:
            header += f" ({source or 'unknown'}, {date or 'unknown'})"
        context_parts.append(f"{header}\n{htext}\n---")

    context_string = "\n".join(context_parts)
    return hits, context_string
