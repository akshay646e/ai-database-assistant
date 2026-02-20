import pandas as pd
import io
from fastapi import UploadFile, HTTPException
from sqlalchemy import create_engine
from config import get_db_url
from utils.file_handler import sanitize_table_name

def load_csv_excel(file: UploadFile, db_config: dict, conn) -> dict:
    """Loads CSV or Excel data into a new SQL table."""
    filename = file.filename
    content = file.file.read()
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Sanitize column names
        df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
        table_name = sanitize_table_name(filename)
        
        engine_url = get_db_url(db_config)
        engine = create_engine(engine_url)
        
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        return {"status": "success", "type": "structured", "table": table_name, "rows": len(df)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process structured file: {e}")
