"""
Embedding Engine — BAAP AI v2 RAG Engine
Wraps sentence-transformers to produce float32 embeddings.
Model: all-MiniLM-L6-v2 (~90MB, downloaded on first use)
"""

import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

# ── Model Cache ───────────────────────────────────────────────────────────────
# Loaded once, reused across all embedding calls.

_model = None

MODEL_NAME = "all-MiniLM-L6-v2"


def _get_model():
    """Lazy-load the embedding model (singleton pattern)."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading embedding model: %s (first-time may take a moment)…", MODEL_NAME)
            _model = SentenceTransformer(MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        except ImportError:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            )
    return _model


# ── Public API ────────────────────────────────────────────────────────────────

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of strings to embed.

    Returns:
        numpy array of shape (len(texts), embedding_dim) — float32.
    """
    if not texts:
        raise ValueError("embed_texts received an empty list.")

    model = _get_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,  # L2-normalized for cosine similarity via dot product
        show_progress_bar=False,
    )
    return embeddings.astype(np.float32)


def embed_query(query: str) -> np.ndarray:
    """
    Generate a single query embedding.

    Args:
        query: The user's search/question string.

    Returns:
        numpy array of shape (1, embedding_dim) — float32.
    """
    return embed_texts([query])


def get_embedding_dimension() -> int:
    """Return the embedding vector dimension for the loaded model."""
    model = _get_model()
    return model.get_sentence_embedding_dimension()
