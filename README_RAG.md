### Retrieval-Augmented Generation (RAG) - Local vector store

This prototype includes a simple local RAG implementation using sentence-transformers + FAISS.

How it works
- Embeddings are computed with the SentenceTransformer model (default: all-MiniLM-L6-v2).
- FAISS IndexFlatIP is used with normalized vectors so inner product approximates cosine similarity.
- Texts and metadata are stored under data/vector_store_texts.json and the FAISS index at data/vector_store.index.

How to enable and use
1. Install the RAG requirements (recommended in a separate virtualenv to avoid heavy deps in CI):

```bash
python -m venv .venv.rag
source .venv.rag/bin/activate
pip install -r requirements-rag.txt
```

2. Index the small keyword corpus included with the prototype:

```bash
python scripts/index_corpus.py
```

3. Run the FastAPI app as before. The text analysis endpoint will consult the local vector store when available and include a `rag_matches` field in the analysis response with top matches and similarity scores.

Notes and next steps
- This is a starting point. You can extend scripts/index_corpus.py to index a larger dataset (labeled scam examples, recent scam reports, etc.).
- For production or large datasets, consider a managed vector DB like Pinecone or Qdrant.
