"""
Chat & Query Routes — BAAP AI v2
Thin HTTP adapter. All business logic lives in core/smart_router.py.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from core.smart_router import route

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
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
