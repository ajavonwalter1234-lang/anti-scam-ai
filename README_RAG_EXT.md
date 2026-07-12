### Example dataset ingestion for RAG

This folder adds scripts to index a small, richer example dataset into the local FAISS-backed vector store and to demo queries.

Files added
- data/examples/scam_examples.json: small sample dataset with id, title, text, source, date
- scripts/index_examples.py: indexes the examples into the vector store and writes data/vector_store_metadata.json
- scripts/demo_query.py: runs a query against the vector store and prints matches with metadata

How to use
1. Ensure you have installed RAG deps in a separate venv (see README_RAG.md):

```bash
python -m venv .venv.rag
source .venv.rag/bin/activate
pip install -r requirements-rag.txt
```

2. Index examples

```bash
python scripts/index_examples.py
```

3. Demo a query

```bash
python scripts/demo_query.py --query "You won a prize, send UPI to claim"
```

Notes
- The metadata file data/vector_store_metadata.json is written by index_examples.py and used by demo_query.py to show additional context for each hit.
- Extend data/examples/scam_examples.json with more labeled examples for improved retrieval quality.
