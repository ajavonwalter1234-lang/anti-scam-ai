"""Demo script to query the local vector store and print results with metadata.

Usage:
    python scripts/demo_query.py --query "your suspicious message here"

If no query provided, a built-in sample query is used.
"""
import os
import json
import argparse
from app.rag.vector_store import VectorStore


def load_metadata():
    meta_path = os.path.join(os.getcwd(), "data", "vector_store_metadata.json")
    if not os.path.exists(meta_path):
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, help="Text query to search the vector store")
    args = parser.parse_args()

    query = args.query or "Verify your account immediately by visiting http://secure-bank.verify.example"

    vs = VectorStore()
    if vs.disabled:
        print("Vector store is not enabled (missing dependencies).")
        return

    results = vs.query(query, k=5)
    meta = load_metadata()

    out = {
        "query": query,
        "results": []
    }
    for _id, text, score in results:
        item = {"id": _id, "text": text, "score": round(score, 3)}
        if _id in meta:
            item["meta"] = meta[_id]
        out["results"].append(item)

    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
