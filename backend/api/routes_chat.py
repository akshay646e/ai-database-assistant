from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ingestion.db_loader import get_connection, get_schema
from processing.sql_agent import natural_language_to_sql, execute_query
from intelligence.metrics_engine import generate_metrics
from intelligence.insight_generator import generate_insights
from intelligence.suggestion_engine import generate_suggestions
from visualization.chart_generator import generate_chart_config

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
    """Full pipeline: NL → SQL → Execute → Metrics → Chart → Insights → Suggestions"""
    try:
        # Connect + get schema
        conn = get_connection(req.db_config.model_dump())
        schema = get_schema(conn, req.db_config.db_type)

        # NL → SQL via Gemini
        sql = req.sql_override or natural_language_to_sql(req.question, schema, req.db_config.db_type)

        # Execute SQL
        columns, rows = execute_query(conn, sql)
        conn.close()

        data = [dict(zip(columns, row)) for row in rows]

        # Generate all analytics
        metrics = generate_metrics(columns, data)
        chart = generate_chart_config(columns, data, req.question)
        insights = generate_insights(req.question, sql, data, metrics)
        suggestions = generate_suggestions(req.question, schema, data)

        return {
            "sql": sql,
            "columns": columns,
            "data": data[:500],
            "total_rows": len(data),
            "metrics": metrics,
            "chart": chart,
            "insights": insights,
            "suggestions": suggestions,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
