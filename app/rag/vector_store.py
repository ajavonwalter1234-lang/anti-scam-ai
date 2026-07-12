import os
import json
from typing import List, Tuple, Optional

# Try imports; allow graceful fallback
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import faiss
except Exception:
    SentenceTransformer = None
    np = None
    faiss = None


class VectorStore:
    """Simple FAISS-backed vector store using sentence-transformers for embeddings.

    Stores embeddings in a FAISS IndexFlatIP index with normalized vectors (cosine sim via inner product).
    Keeps a parallel JSON file of texts and metadata.

    Data files (in repo working directory):
      data/vector_store.index (binary faiss index)
      data/vector_store_texts.json (list of {"id":..., "text":...})
    """

    def __init__(self, persist_dir: str = "data", model_name: str = "all-MiniLM-L6-v2"):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index_path = os.path.join(self.persist_dir, "vector_store.index")
        self.texts_path = os.path.join(self.persist_dir, "vector_store_texts.json")
        self.model_name = model_name

        self.model = None
        self.index = None
        self.texts = []  # list of dicts {"id": id, "text": text}

        # Initialize if libs available
        if SentenceTransformer is None or faiss is None or np is None:
            # Libraries not available; vector store disabled
            self.disabled = True
        else:
            self.disabled = False
            self._init_model()
            self._load_or_create_index()

    def _init_model(self):
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def _load_or_create_index(self):
        # Load texts list if exists
        if os.path.exists(self.texts_path):
            try:
                with open(self.texts_path, "r", encoding="utf-8") as f:
                    self.texts = json.load(f)
            except Exception:
                self.texts = []
        else:
            self.texts = []

        dim = self.model.get_sentence_embedding_dimension()
        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
                return
            except Exception:
                # fallback to creating a new index
                pass

        # create new index
        self.index = faiss.IndexFlatIP(dim)
        # if we have existing texts but no saved index, build it
        if self.texts:
            embeddings = self._embed_texts([t["text"] for t in self.texts])
            embeddings = self._normalize(embeddings)
            self.index.add(embeddings)
            self._save_index()

    def _save_index(self):
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.texts_path, "w", encoding="utf-8") as f:
                json.dump(self.texts, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _embed_texts(self, texts: List[str]):
        return np.array(self.model.encode(texts, convert_to_numpy=True))

    def _normalize(self, vectors):
        # normalize to unit length for cosine similarity via inner product
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        return vectors / norms

    def add_texts(self, texts: List[str], ids: Optional[List[str]] = None):
        """Add texts to the vector store. ids is optional list of same length."""
        if self.disabled:
            raise RuntimeError("VectorStore dependencies missing (sentence-transformers/faiss).")

        ids = ids or [str(len(self.texts) + i) for i in range(len(texts))]
        embeddings = self._embed_texts(texts)
        embeddings = self._normalize(embeddings)
        self.index.add(embeddings)
        for _id, text in zip(ids, texts):
            self.texts.append({"id": _id, "text": text})
        self._save_index()

    def query(self, query_text: str, k: int = 5) -> List[Tuple[str, str, float]]:
        """Return top-k matches as list of (id, text, score). Score is cosine similarity in [0,1]."""
        if self.disabled:
            return []
        emb = self._embed_texts([query_text])
        emb = self._normalize(emb)
        D, I = self.index.search(emb, k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.texts):
                continue
            item = self.texts[idx]
            results.append((item["id"], item["text"], float(score)))
        return results

    def info(self):
        if self.disabled:
            return {"enabled": False}
        return {"enabled": True, "n_items": len(self.texts), "model": self.model_name}
