from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from modules.db_connection import get_connection, get_schema
from modules.nl_to_sql import natural_language_to_sql
from modules.sql_executor import execute_query
from modules.metrics_generator import generate_metrics
from modules.visualization import generate_chart_config
from modules.insight_generator import generate_insights
from modules.suggestion_generator import generate_suggestions

app = FastAPI(title="BAAP AI - Database Analytics", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ──────────────────────────────────────────────
class DBConfig(BaseModel):
    db_type: str        # "mysql" or "postgresql"
    host: str
    port: int
    username: str
    password: str
    database: str

class QueryRequest(BaseModel):
    db_config: DBConfig
    question: str
    sql_override: Optional[str] = None

# ── Routes ──────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "BAAP AI Backend is running ✓"}


@app.post("/api/connect")
def connect_database(config: DBConfig):
    """Test DB connection and return schema"""
    try:
        conn = get_connection(config.model_dump())
        schema = get_schema(conn, config.db_type)
        conn.close()
        return {
            "status": "connected",
            "database": config.database,
            "db_type": config.db_type,
            "schema": schema,
            "table_count": len(schema)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/query")
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


@app.post("/api/schema")
def get_db_schema(config: DBConfig):
    """Get database schema only"""
    try:
        conn = get_connection(config.model_dump())
        schema = get_schema(conn, config.db_type)
        conn.close()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
