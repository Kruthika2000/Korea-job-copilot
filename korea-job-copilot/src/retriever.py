"""Loads resume markdown chunks, embeds them once, and retrieves the
chunks most relevant to a given job description.
"""
import glob
import os

from . import config
from .embeddings import embed_texts, embed_query
from .vector_store import VectorStore


def _load_resume_chunks() -> list[str]:
    chunks: list[str] = []
    for path in sorted(glob.glob(os.path.join(config.RESUME_DIR, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Split on '---' so each resume file can hold multiple chunks
        # (e.g. one per project/role) without needing one file per chunk.
        for piece in content.split("\n---\n"):
            piece = piece.strip()
            if piece:
                chunks.append(piece)
    return chunks


class ResumeRetriever:
    def __init__(self):
        self.store = VectorStore()
        chunks = _load_resume_chunks()
        if chunks:
            embeddings = embed_texts(chunks)
            self.store.add(chunks, embeddings)
        self._chunk_count = len(chunks)

    def retrieve(self, job_description: str, top_k: int = 4) -> list[str]:
        if self._chunk_count == 0:
            return []
        query_emb = embed_query(job_description)
        results = self.store.search(query_emb, top_k=top_k)
        return [text for text, _score in results]
