"""A deliberately tiny vector store: for a resume-sized corpus (tens of
chunks, not thousands), an in-memory numpy cosine-similarity search is
simpler to read and debug than standing up Chroma/FAISS. See the README's
'design decisions' section for why, and swap this out via the same
interface if the corpus grows.
"""
import numpy as np


class VectorStore:
    def __init__(self):
        self._texts: list[str] = []
        self._embeddings: np.ndarray | None = None

    def add(self, texts: list[str], embeddings: list[list[float]]) -> None:
        arr = np.array(embeddings, dtype=np.float32)
        arr = arr / (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-8)
        self._texts.extend(texts)
        self._embeddings = arr if self._embeddings is None else np.vstack([self._embeddings, arr])

    def search(self, query_embedding: list[float], top_k: int = 4) -> list[tuple[str, float]]:
        if self._embeddings is None or len(self._texts) == 0:
            return []
        q = np.array(query_embedding, dtype=np.float32)
        q = q / (np.linalg.norm(q) + 1e-8)
        scores = self._embeddings @ q
        top_idx = np.argsort(-scores)[:top_k]
        return [(self._texts[i], float(scores[i])) for i in top_idx]
