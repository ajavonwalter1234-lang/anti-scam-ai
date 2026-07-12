"""Index a small collection of richer scam examples into the local vector store.

This script reads data/examples/scam_examples.json and indexes each example's combined title+text
as a document. It also writes a metadata file (data/vector_store_metadata.json) mapping ids to metadata
so retrieved hits can be shown with context.

Usage:
    python scripts/index_examples.py

"""
import os
import json
from app.rag.vector_store import VectorStore


def main():
    examples_path = os.path.join(os.getcwd(), "data", "examples", "scam_examples.json")
    if not os.path.exists(examples_path):
        print("No examples file found at", examples_path)
        return

    with open(examples_path, "r", encoding="utf-8") as f:
        examples = json.load(f)

    docs = []
    ids = []
    metadata = {}
    for ex in examples:
        doc_text = f"{ex.get('title','')} - {ex.get('text','')}"
        docs.append(doc_text)
        ids.append(ex.get('id'))
        metadata[ex.get('id')] = {k: v for k, v in ex.items() if k != 'text'}

    vs = VectorStore()
    if vs.disabled:
        print("Vector store dependencies missing (sentence-transformers/faiss). Install requirements-rag.txt to enable RAG.")
        return

    vs.add_texts(docs, ids)

    # write metadata mapping
    meta_path = os.path.join(os.getcwd(), "data", "vector_store_metadata.json")
    try:
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(metadata, mf, ensure_ascii=False, indent=2)
        print("Wrote metadata to", meta_path)
    except Exception as e:
        print("Failed to write metadata:", e)

    info = vs.info()
    print("Indexed examples. Vector store info:", info)


if __name__ == "__main__":
    main()
