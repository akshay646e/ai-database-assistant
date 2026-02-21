"""
Document Processor — BAAP AI v2 RAG Engine
Extracts text from PDF/Docx files and splits into overlapping chunks
ready for embedding and vector storage.
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────

CHUNK_SIZE_WORDS = 600      # target words per chunk
CHUNK_OVERLAP_WORDS = 60    # overlap between consecutive chunks


# ── Text Extraction ───────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF byte stream.
    Uses pypdf (no external API required).
    """
    try:
        import pypdf
        import io

        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append(f"[Page {i+1}]\n{text}")
        return "\n\n".join(pages)
    except ImportError:
        raise RuntimeError("pypdf is not installed. Run: pip install pypdf")
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract plain text from a Docx byte stream.
    Uses python-docx.
    """
    try:
        import docx
        import io

        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except ImportError:
        raise RuntimeError("python-docx is not installed. Run: pip install python-docx")
    except Exception as e:
        raise RuntimeError(f"Docx extraction failed: {e}")


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_text(text: str, filename: str = "") -> List[dict]:
    """
    Split text into overlapping word-based chunks.

    Returns a list of dicts:
        {
            "chunk_id": "<filename>_chunk_<n>",
            "filename": "<filename>",
            "chunk_index": <n>,
            "text": "<chunk text>",
            "word_count": <int>,
        }
    """
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    total_words = len(words)

    if total_words == 0:
        logger.warning("Empty text passed to chunk_text for file: %s", filename)
        return []

    chunks = []
    start = 0
    chunk_idx = 0

    while start < total_words:
        end = min(start + CHUNK_SIZE_WORDS, total_words)
        chunk_words = words[start:end]
        chunk_text_str = " ".join(chunk_words)

        chunks.append({
            "chunk_id": f"{filename}_chunk_{chunk_idx}",
            "filename": filename,
            "chunk_index": chunk_idx,
            "text": chunk_text_str,
            "word_count": len(chunk_words),
        })

        chunk_idx += 1
        # Advance by (chunk_size - overlap) to create overlap
        start += CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS

        if start >= total_words:
            break

    logger.info(
        "Chunked '%s' → %d chunks (%d words total, ~%d words/chunk)",
        filename, len(chunks), total_words, CHUNK_SIZE_WORDS,
    )
    return chunks


# ── Unified Pipeline ──────────────────────────────────────────────────────────

def process_document(filename: str, file_bytes: bytes) -> List[dict]:
    """
    Extract text from a file and return overlapping chunks.

    Supported file types: .pdf, .docx

    Args:
        filename:   Original filename (used for chunk IDs).
        file_bytes: Raw file content as bytes.

    Returns:
        List of chunk dicts ready for embedding and storage.

    Raises:
        ValueError: If file type is unsupported.
        RuntimeError: If extraction fails.
    """
    name_lower = filename.lower()

    if name_lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif name_lower.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type for RAG: '{filename}'. "
            "Only .pdf and .docx are supported."
        )

    if not text.strip():
        raise ValueError(f"No text could be extracted from '{filename}'.")

    return chunk_text(text, filename)
