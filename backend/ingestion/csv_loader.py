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
        
        # Drop completely empty rows and columns
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        
        # Sanitize column names: Handle Unnamed, replace non-alphanumeric, truncate to 60 chars
        import re
        new_columns = []
        seen = set()
        for i, col in enumerate(df.columns):
            col_str = str(col)
            if col_str.startswith('Unnamed:'):
                new_col = f"col_{i}"
            else:
                new_col = "".join(c if c.isalnum() else "_" for c in col_str)
                new_col = re.sub(r'_+', '_', new_col).strip('_').lower()
                new_col = new_col[:60] # MySQL limit is 64
                if not new_col:
                    new_col = f"col_{i}"
            
            # Prevent duplicate column names
            base_col = new_col
            counter = 1
            while new_col in seen:
                suffix = f"_{counter}"
                new_col = base_col[:60 - len(suffix)] + suffix
                counter += 1
            seen.add(new_col)
            new_columns.append(new_col)
            
        df.columns = new_columns
        
        # To make it cleaner for the frontend, we can fill missing values
        # For object (string) columns, use '' instead of NaN to avoid literal "null" everywhere
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('')
            else:
                # For numeric columns, NaNs remain as NULL
                pass
                
        table_name = sanitize_table_name(filename)
        
        engine_url = get_db_url(db_config)
        engine = create_engine(engine_url)
        
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        return {"status": "success", "type": "structured", "table": table_name, "rows": len(df)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process structured file: {e}")
