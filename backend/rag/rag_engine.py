"""
RAG Engine — BAAP AI v2
Full pipeline: document indexing + question answering using FAISS + Gemini.

Public surface:
    startup()            — call on app startup to warm up the store
    index_document()     — index a file into the vector store
    answer_question()    — embed query → retrieve → generate answer
"""

import logging
from typing import List, Dict, Any, Optional

from rag import document_processor, embedding_engine, vector_store
from core.llm import get_llm_model

logger = logging.getLogger(__name__)

TOP_K = 3   # Number of chunks to retrieve per query


# ── Startup ───────────────────────────────────────────────────────────────────

def startup() -> None:
    """
    Initialise the vector store. Call once from main.py lifespan or startup event.
    This triggers the sentence-transformers model download on first run.
    """
    try:
        dim = embedding_engine.get_embedding_dimension()
        vector_store.load_store(embedding_dim=dim)
        stats = vector_store.get_store_stats()
        logger.info("RAG engine ready. Store: %s", stats)
    except Exception as e:
        logger.error("RAG engine startup failed: %s", e)


# ── Indexing ──────────────────────────────────────────────────────────────────

def index_document(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Full pipeline: extract → chunk → embed → store.

    Args:
        filename:   Original filename (e.g. "report.pdf").
        file_bytes: Raw file bytes.

    Returns:
        Dict with indexing stats: chunks_added, total_in_store, filename.

    Raises:
        ValueError:  Unsupported file type or empty content.
        RuntimeError: Extraction or embedding failure.
    """
    logger.info("Indexing document: %s", filename)

    # 1. Extract & chunk
    chunks = document_processor.process_document(filename, file_bytes)
    if not chunks:
        raise ValueError(f"No content extracted from '{filename}'.")

    # 2. Embed
    texts = [c["text"] for c in chunks]
    embeddings = embedding_engine.embed_texts(texts)

    # 3. Store
    total = vector_store.add_chunks(chunks, embeddings)

    logger.info("Indexed '%s': %d chunks, store total: %d", filename, len(chunks), total)
    return {
        "filename": filename,
        "chunks_added": len(chunks),
        "total_in_store": total,
    }


# ── Retrieval + Generation ────────────────────────────────────────────────────

def answer_question(question: str) -> Dict[str, Any]:
    """
    Answer a document-related question using RAG.

    Pipeline:
        1. Embed the question
        2. Retrieve top-K relevant chunks from FAISS
        3. Build context from retrieved chunks
        4. Call Gemini with context + question
        5. Return structured response

    Args:
        question: The user's natural language question.

    Returns:
        {
            "answer":   str,            # Gemini's natural language answer
            "sources":  List[str],      # filenames of source documents
            "chunks_used": int,         # number of chunks in context
        }
    """
    # 1. Check store has content
    stats = vector_store.get_store_stats()
    if stats["total_chunks"] == 0:
        return {
            "answer": (
                "I don't have any documents indexed yet. "
                "Please upload a PDF or Word document first, then ask your question."
            ),
            "sources": [],
            "chunks_used": 0,
        }

    # 2. Embed query
    query_embedding = embedding_engine.embed_query(question)

    # 3. Retrieve
    results = vector_store.search(query_embedding, top_k=TOP_K)
    if not results:
        return {
            "answer": (
                "I couldn't find relevant information in the indexed documents "
                "to answer your question."
            ),
            "sources": [],
            "chunks_used": 0,
        }

    # 4. Build context (Never send raw DB data — only document chunks)
    context_parts = []
    sources = []
    for i, chunk in enumerate(results, 1):
        context_parts.append(
            f"[Source {i}: {chunk.get('filename', 'document')}]\n{chunk['text']}"
        )
        src = chunk.get("filename", "unknown")
        if src not in sources:
            sources.append(src)

    context = "\n\n---\n\n".join(context_parts)

    # 5. Generate answer via Gemini
    prompt = _build_rag_prompt(question, context)
    answer = _call_llm(prompt)

    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(results),
    }


# ── Prompt Templates ──────────────────────────────────────────────────────────

def _build_rag_prompt(question: str, context: str) -> str:
    return f"""You are BAAP AI, a professional Business Intelligence Assistant.

You have been given relevant excerpts from uploaded documents to answer the user's question.

RETRIEVED DOCUMENT CONTEXT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
- Answer ONLY based on the provided document context above.
- If the context does not contain enough information, say so clearly.
- Cite which source document the information came from when possible.
- Be precise, professional, and concise.
- Do NOT hallucinate or add information not present in the context.

ANSWER:"""


def _build_hybrid_prompt(question: str, doc_context: str, sql_summary: str) -> str:
    """Prompt for hybrid mode: merges document context + SQL result summary."""
    return f"""You are BAAP AI, a professional Business Intelligence Assistant.

You have two sources of information to answer the user's question:

1. DOCUMENT CONTEXT (from uploaded files):
{doc_context}

2. DATABASE QUERY RESULT SUMMARY:
{sql_summary}

USER QUESTION: {question}

INSTRUCTIONS:
- Synthesize both sources to provide a comprehensive answer.
- Highlight how the document findings relate to the database data.
- If sources conflict, point it out clearly.
- Cite which source each insight comes from (Document / Database).
- Be professional, analytical, and actionable.

COMBINED ANSWER:"""


def _call_llm(prompt: str) -> str:
    """Call Gemini with a prompt and return the response text."""
    model = get_llm_model()
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "exhausted" in error_str.lower():
            return "API rate limit reached. Please wait a moment and try again."
        logger.error("RAG LLM call failed: %s", error_str)
        return f"An error occurred while generating the answer: {error_str}"


# ── Hybrid Support ────────────────────────────────────────────────────────────

def answer_hybrid(question: str, sql_data_summary: str) -> str:
    """
    Retrieve doc context and merge with SQL summary via Gemini.
    Used by smart_router for hybrid_query intent.

    Args:
        question:         User's question.
        sql_data_summary: Plain-text summary of SQL result (NOT raw data).

    Returns:
        Merged natural language answer string.
    """
    stats = vector_store.get_store_stats()
    if stats["total_chunks"] == 0:
        # No documents — just return a SQL-focused answer
        return sql_data_summary

    query_embedding = embedding_engine.embed_query(question)
    results = vector_store.search(query_embedding, top_k=TOP_K)

    if not results:
        return sql_data_summary

    context_parts = [
        f"[Source: {r.get('filename','document')}]\n{r['text']}"
        for r in results
    ]
    doc_context = "\n\n---\n\n".join(context_parts)

    prompt = _build_hybrid_prompt(question, doc_context, sql_data_summary)
    return _call_llm(prompt)
