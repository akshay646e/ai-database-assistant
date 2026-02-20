import io
import docx
from fastapi import UploadFile, HTTPException

def load_docx(file: UploadFile) -> str:
    """Extracts text content from a DOCX file."""
    try:
        content = file.file.read()
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process DOCX file: {e}")
