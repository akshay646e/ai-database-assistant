"""
Chat & Query Routes — BAAP AI v2
Thin HTTP adapter. All business logic lives in core/smart_router.py.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.smart_router import route
from rag.vector_store import get_store_stats

router = APIRouter()


class DBConfig(BaseModel):
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str


class QueryRequest(BaseModel):
    db_config: DBConfig
    question: str
    sql_override: Optional[str] = None
    chat_context: Optional[str] = None

@router.get("/documents")
def list_documents():
    """Returns a list of all currently indexed documents in the RAG store."""
    try:
        stats = get_store_stats()
        return {"documents": stats.get("documents", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
def run_query(req: QueryRequest):
    """
    Unified BAAP AI v2 query endpoint.

    Classifies intent and routes to the appropriate engine:
      - chat / greeting   → Conversational response
      - database_query    → NL → SQL → Execute → Metrics → Chart → Insights
      - document_query    → RAG pipeline (FAISS + Gemini)
      - hybrid_query      → SQL + RAG merged response

    Response always includes:
      mode, answer, and conditionally:
      sql_query, data, metrics, chart_config, insights, suggestions
    """
    try:
        result = route(
            question=req.question,
            db_config=req.db_config.model_dump(),
            sql_override=req.sql_override,
            chat_context=req.chat_context,
        )
        return result
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Resource exhausted" in error_msg:
            friendly_msg = "Google Gemini Free-Tier limit reached. The AI requires a short cooldown. Please wait 1 minute and try your question again!"
            raise HTTPException(status_code=500, detail=friendly_msg)
            
        raise HTTPException(status_code=500, detail=error_msg)
