"""
Vector Store — BAAP AI v2 RAG Engine
FAISS-backed vector store with disk persistence.

Storage layout (inside rag_store/):
    index.faiss    — FAISS binary index
    chunks.json    — metadata + text for each indexed chunk

Thread-safe for concurrent reads; writes use a module-level lock.
"""

import os
import json
import logging
import threading
import numpy as np
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "rag_store")
INDEX_PATH = os.path.join(STORE_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(STORE_DIR, "chunks.json")

# ── Module State ──────────────────────────────────────────────────────────────

_index = None           # faiss.IndexFlatIP
_chunks: List[Dict] = []     # parallel list of chunk metadata
_lock = threading.Lock()


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _ensure_store_dir():
    os.makedirs(STORE_DIR, exist_ok=True)


def _load_faiss():
    try:
        import faiss
        return faiss
    except ImportError:
        raise RuntimeError(
            "faiss-cpu is not installed. Run: pip install faiss-cpu"
        )


def _init_index(dim: int):
    """Create a new FAISS inner-product (cosine with L2 norms) index."""
    faiss = _load_faiss()
    return faiss.IndexFlatIP(dim)


# ── Persistence ───────────────────────────────────────────────────────────────

def load_store(embedding_dim: int) -> None:
    """
    Load an existing FAISS index and chunk list from disk,
    or initialise an empty store if nothing exists yet.

    Call once at startup from rag_engine.py.
    """
    global _index, _chunks

    faiss = _load_faiss()
    _ensure_store_dir()

    with _lock:
        if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
            try:
                _index = faiss.read_index(INDEX_PATH)
                with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                    _chunks = json.load(f)
                logger.info(
                    "Vector store loaded: %d chunks from disk.", len(_chunks)
                )
                return
            except Exception as e:
                logger.warning("Failed to load existing store (%s). Creating fresh.", e)

        _index = _init_index(embedding_dim)
        _chunks = []
        logger.info("Initialised new empty vector store (dim=%d).", embedding_dim)


def _save_store() -> None:
    """Persist index and chunks to disk. Must be called inside _lock."""
    faiss = _load_faiss()
    _ensure_store_dir()
    faiss.write_index(_index, INDEX_PATH)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(_chunks, f, ensure_ascii=False, indent=2)


# ── Public API ────────────────────────────────────────────────────────────────

def add_chunks(chunks: List[Dict], embeddings: np.ndarray) -> int:
    """
    Add new chunks + their embeddings to the store.

    Args:
        chunks:     List of chunk dicts (must have at least 'chunk_id', 'text').
        embeddings: numpy float32 array, shape (len(chunks), dim).

    Returns:
        Total number of chunks in the store after insertion.
    """
    global _index, _chunks

    if _index is None:
        raise RuntimeError("Vector store not initialised. Call load_store() first.")

    with _lock:
        _index.add(embeddings)
        _chunks.extend(chunks)
        _save_store()
        logger.info("Added %d chunks → store total: %d", len(chunks), len(_chunks))
        return len(_chunks)


def search(query_embedding: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieve the top-K most similar chunks for a query embedding.

    Args:
        query_embedding: numpy float32 array, shape (1, dim).
        top_k:           Number of results to return.

    Returns:
        List of result dicts:
            {
                "chunk_id":    str,
                "filename":    str,
                "text":        str,
                "score":       float,   # cosine similarity (higher = better)
                "chunk_index": int,
            }
    """
    if _index is None or len(_chunks) == 0:
        logger.warning("Search called on empty vector store.")
        return []

    actual_k = min(top_k, len(_chunks))
    scores, indices = _index.search(query_embedding, actual_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_chunks):
            continue
        chunk = _chunks[idx].copy()
        chunk["score"] = float(score)
        results.append(chunk)

    return results


def get_store_stats() -> Dict[str, Any]:
    """Return a summary of the current vector store state."""
    if _index is None:
        return {"status": "not_initialised", "total_chunks": 0, "documents": []}

    docs = list({c.get("filename", "unknown") for c in _chunks})
    return {
        "status": "ready",
        "total_chunks": len(_chunks),
        "documents": docs,
    }


def delete_document(filename: str) -> int:
    """
    Remove all chunks belonging to a specific document.
    Note: FAISS IndexFlatIP does not support in-place deletion,
    so we rebuild the index from the remaining chunks.

    Returns:
        Number of chunks removed.
    """
    global _index, _chunks

    if _index is None:
        return 0

    from rag.embedding_engine import embed_texts, get_embedding_dimension

    with _lock:
        remaining = [c for c in _chunks if c.get("filename") != filename]
        removed_count = len(_chunks) - len(remaining)

        if removed_count == 0:
            return 0

        dim = get_embedding_dimension()
        new_index = _init_index(dim)

        if remaining:
            texts = [c["text"] for c in remaining]
            new_embeddings = embed_texts(texts)
            new_index.add(new_embeddings)

        _index = new_index
        _chunks = remaining
        _save_store()
        logger.info("Removed %d chunks for '%s'.", removed_count, filename)
        return removed_count
