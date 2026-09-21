"""Embedding function used by the retriever.

Uses Voyage AI (Anthropic's recommended embeddings partner) when
VOYAGE_API_KEY is set. Falls back to a deterministic hash-based embedding
so the demo pipeline still runs end-to-end for anyone trying the repo
without signing up for another API key. Swap `embed_texts` for a real
embeddings call in production use.
"""
import hashlib
import os
import numpy as np

_VOYAGE_KEY = os.getenv("VOYAGE_API_KEY", "")
_DIM = 256


def _fallback_embed(text: str) -> list[float]:
    """Deterministic, dependency-free 'embedding': hash n-grams into a
    fixed-size vector. Not semantically meaningful like a real embedding
    model, but keeps exact/near-exact term overlap retrievable so the demo
    is runnable offline. Not intended for production retrieval quality."""
    vec = np.zeros(_DIM, dtype=np.float32)
    words = text.lower().split()
    for w in words:
        h = int(hashlib.sha256(w.encode()).hexdigest(), 16)
        vec[h % _DIM] += 1.0
    return vec.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    if _VOYAGE_KEY:
        import voyageai

        client = voyageai.Client(api_key=_VOYAGE_KEY)
        result = client.embed(texts, model="voyage-3", input_type="document")
        return result.embeddings
    return [_fallback_embed(t) for t in texts]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
