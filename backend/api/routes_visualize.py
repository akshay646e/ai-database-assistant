from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ingestion.db_loader import get_connection, get_schema

router = APIRouter()

class DBConfig(BaseModel):
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str

@router.post("/schema")
def get_db_schema(config: DBConfig):
    """Get database schema only"""
    try:
        conn = get_connection(config.model_dump())
        schema = get_schema(conn, config.db_type)
        conn.close()
        return {"schema": schema}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
