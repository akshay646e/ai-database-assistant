"""
Smart Router — BAAP AI v2
Orchestration hub. Classifies intent and dispatches to the correct engine(s).
Assembles the unified v2 response payload.

Response schema (all fields always present, null if not applicable):
{
    "mode":         "chat | sql | rag | hybrid",
    "answer":       str,
    "sql_query":    str | null,
    "columns":      list | null,
    "data":         list | null,
    "total_rows":   int | null,
    "metrics":      dict | null,
    "chart_config": dict | null,
    "insights":     list | null,
    "suggestions":  list | null,
}
"""

import json
import logging
from typing import Any, Dict, Optional

from core.intent_classifier import classify_intent
from core.chat_engine import handle_greeting, handle_chat

from ingestion.db_loader import get_connection, get_schema
from processing.sql_agent import natural_language_to_sql, execute_query
from intelligence.metrics_engine import generate_metrics
from intelligence.insight_generator import generate_insights
from intelligence.suggestion_engine import generate_suggestions
from visualization.chart_generator import generate_chart_config

# RAG is imported lazily so startup failures don't break the entire app
import rag.rag_engine as rag_engine

logger = logging.getLogger(__name__)


# ── Empty response template ───────────────────────────────────────────────────

def _empty_response(mode: str) -> Dict[str, Any]:
    return {
        "mode": mode,
        "answer": "",
        "sql_query": None,
        "columns": None,
        "data": None,
        "total_rows": None,
        "metrics": None,
        "chart_config": None,
        "insights": None,
        "suggestions": None,
    }


# ── SQL Pipeline ──────────────────────────────────────────────────────────────

def _run_sql_pipeline(
    question: str,
    db_config: Dict[str, Any],
    sql_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Full SQL analytics pipeline.
    Connects to DB, converts NL → SQL, executes, generates all analytics.
    Returns a merged response dict.
    """
    conn = get_connection(db_config)
    schema = get_schema(conn, db_config["db_type"])

    sql = sql_override or natural_language_to_sql(question, schema, db_config["db_type"])
    columns, rows = execute_query(conn, sql)
    conn.close()

    data = [dict(zip(columns, row)) for row in rows]

    metrics = generate_metrics(columns, data)
    chart = generate_chart_config(columns, data, question)
    insights = generate_insights(question, sql, data, metrics)
    suggestions = generate_suggestions(question, schema, data)

    # Build a plain-text summary for hybrid mode (never raw data)
    kpis = metrics.get("kpis", {})
    sql_summary = (
        f"SQL Query: {sql}\n"
        f"Rows returned: {kpis.get('total_rows', len(data))}\n"
        f"Key metrics: {json.dumps(kpis, default=str)}\n"
        f"Top insights: {'; '.join(insights[:2]) if insights else 'none'}"
    )

    return {
        "sql": sql,
        "columns": columns,
        "data": data[:500],
        "total_rows": len(data),
        "metrics": metrics,
        "chart": chart,
        "insights": insights,
        "suggestions": suggestions,
        "_sql_summary": sql_summary,   # internal use only
    }


# ── Public Router ─────────────────────────────────────────────────────────────

def route(
    question: str,
    db_config: Dict[str, Any],
    sql_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main routing function. Classifies intent and dispatches to engine(s).

    Args:
        question:     User's natural language question.
        db_config:    Database connection config dict.
        sql_override: Optional raw SQL to bypass NL→SQL step.

    Returns:
        Unified v2 response dict.
    """
    intent = classify_intent(question)
    logger.info("Routing question with intent='%s': %s", intent, question[:80])

    # ── Greeting ──────────────────────────────────────────────────────────────
    if intent == "greeting":
        resp = _empty_response("chat")
        resp["answer"] = handle_greeting(question)
        return resp

    # ── General Chat ──────────────────────────────────────────────────────────
    if intent == "general_chat":
        resp = _empty_response("chat")
        resp["answer"] = handle_chat(question)
        return resp

    # ── Document / RAG query ──────────────────────────────────────────────────
    if intent == "document_query":
        resp = _empty_response("rag")
        try:
            rag_result = rag_engine.answer_question(question)
            resp["answer"] = rag_result["answer"]
            # Store sources as part of the insights field (repurposed for RAG)
            if rag_result.get("sources"):
                resp["insights"] = [f"Source: {s}" for s in rag_result["sources"]]
        except Exception as e:
            logger.error("RAG engine error: %s", e)
            resp["answer"] = f"Document query failed: {e}"
        return resp

    # ── SQL / Analytics query ─────────────────────────────────────────────────
    if intent in ("database_query", "analytics_query"):
        resp = _empty_response("sql")
        try:
            sql_result = _run_sql_pipeline(question, db_config, sql_override)
            resp["answer"] = (
                sql_result["insights"][0]
                if sql_result.get("insights")
                else f"Query executed successfully. {sql_result['total_rows']} rows returned."
            )
            resp["sql_query"] = sql_result["sql"]
            resp["columns"] = sql_result["columns"]
            resp["data"] = sql_result["data"]
            resp["total_rows"] = sql_result["total_rows"]
            resp["metrics"] = sql_result["metrics"]
            resp["chart_config"] = sql_result["chart"]
            resp["insights"] = sql_result["insights"]
            resp["suggestions"] = sql_result["suggestions"]
        except Exception as e:
            logger.error("SQL pipeline error: %s", e)
            raise   # Re-raise so FastAPI returns a proper 500
        return resp

    # ── Hybrid query ──────────────────────────────────────────────────────────
    if intent == "hybrid_query":
        resp = _empty_response("hybrid")
        sql_result = None
        sql_error = None

        # Run SQL first
        try:
            sql_result = _run_sql_pipeline(question, db_config, sql_override)
            resp["sql_query"] = sql_result["sql"]
            resp["columns"] = sql_result["columns"]
            resp["data"] = sql_result["data"]
            resp["total_rows"] = sql_result["total_rows"]
            resp["metrics"] = sql_result["metrics"]
            resp["chart_config"] = sql_result["chart"]
            resp["insights"] = sql_result["insights"]
            resp["suggestions"] = sql_result["suggestions"]
        except Exception as e:
            sql_error = str(e)
            logger.warning("Hybrid SQL step failed: %s", sql_error)

        # Run RAG + merge
        try:
            sql_summary = sql_result["_sql_summary"] if sql_result else f"SQL failed: {sql_error}"
            merged_answer = rag_engine.answer_hybrid(question, sql_summary)
            resp["answer"] = merged_answer
        except Exception as e:
            logger.error("Hybrid RAG step failed: %s", e)
            resp["answer"] = (
                sql_result["insights"][0]
                if sql_result and sql_result.get("insights")
                else "Hybrid query could not be fully completed."
            )

        return resp

    # ── Fallback (should never reach here) ────────────────────────────────────
    resp = _empty_response("chat")
    resp["answer"] = handle_chat(question)
    return resp
