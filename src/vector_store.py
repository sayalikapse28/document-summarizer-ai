"""
vector_store.py
-----------------
A minimal in-memory vector index built on FAISS (Facebook AI Similarity
Search -- free, open source, runs locally, no external DB needed).

For each uploaded document we build a fresh index for the session,
store its chunk embeddings, and retrieve the most relevant chunks
for a given question (this is the "Retrieval" half of RAG).
"""

import faiss
import numpy as np


class VectorStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings: np.ndarray, texts: list):
        self.index.add(embeddings.astype("float32"))
        self.texts.extend(texts)

    def search(self, query_embedding: np.ndarray, top_k: int = 4) -> list:
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(
            query_embedding.astype("float32").reshape(1, -1), top_k
        )
        results = []
        for idx in indices[0]:
            if idx == -1:
                continue
            results.append(self.texts[idx])
        return results
