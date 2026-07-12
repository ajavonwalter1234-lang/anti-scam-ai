"""Indexing script for the prototype vector store.

This script reads data/keywords/scam_keywords.json and indexes each keyword as a short document
into the local FAISS-backed vector store. Run this after installing sentence-transformers and faiss.

Usage:
    python scripts/index_corpus.py

"""
import os
import json
from app.rag.vector_store import VectorStore


def main():
    keywords_path = os.path.join(os.getcwd(), "data", "keywords", "scam_keywords.json")
    if not os.path.exists(keywords_path):
        print("No keywords file found at", keywords_path)
        return

    with open(keywords_path, "r", encoding="utf-8") as f:
        keywords = json.load(f)

    docs = []
    ids = []
    for i, kw in enumerate(keywords):
        # create a short document for each keyword; could be expanded with examples later
        docs.append(kw)
        ids.append(f"kw-{i}")

    vs = VectorStore()
    if vs.disabled:
        print("Vector store dependencies missing (sentence-transformers/faiss). Install requirements to enable RAG.")
        return

    vs.add_texts(docs, ids)
    info = vs.info()
    print("Indexed", info.get("n_items"), "items with model", info.get("model"))


if __name__ == "__main__":
    main()
