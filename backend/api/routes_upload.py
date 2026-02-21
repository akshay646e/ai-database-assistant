from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
import json

from ingestion.db_loader import get_connection, get_schema
from ingestion.csv_loader import load_csv_excel
from ingestion.pdf_loader import load_pdf
from ingestion.docx_loader import load_docx
from utils.file_handler import sanitize_table_name

router = APIRouter()

class DBConfig(BaseModel):
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str

@router.post("/connect")
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

@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db_config_str: str = Form(..., alias="db_config")
):
    """Upload a file (CSV/Excel/PDF/Docx) and ingest into DB"""
    try:
        db_config = json.loads(db_config_str)
        filename = file.filename
        
        # Connect to DB
        conn = get_connection(db_config)
        
        if filename.endswith(('.csv', '.xlsx', '.xls')):
            result = load_csv_excel(file, db_config, conn)
            conn.close()
            return result
            
        elif filename.endswith(('.pdf', '.docx')):
            if filename.endswith('.pdf'):
                text_content = load_pdf(file)
            else:
                text_content = load_docx(file)
                
            cursor = conn.cursor()
            
            # Create table if not exists
            if db_config['db_type'] == 'mysql':
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS uploaded_documents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255),
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_text LONGTEXT
                );
                """
            elif db_config['db_type'] == 'sqlite':
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS uploaded_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename VARCHAR(255),
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_text TEXT
                );
                """
            else:
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS uploaded_documents (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255),
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    content_text TEXT
                );
                """
            
            cursor.execute(create_table_sql)
            
            # Insert document
            if db_config['db_type'] == 'sqlite':
                insert_sql = "INSERT INTO uploaded_documents (filename, content_text) VALUES (?, ?)"
            else:
                insert_sql = "INSERT INTO uploaded_documents (filename, content_text) VALUES (%s, %s)"
            cursor.execute(insert_sql, (filename, text_content))
            conn.commit()
            conn.close()
            
            return {"status": "success", "type": "unstructured", "table": "uploaded_documents", "length": len(text_content)}

        else:
            conn.close()
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV, Excel, PDF, or Docx.")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
