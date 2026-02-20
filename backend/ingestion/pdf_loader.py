import io
import pypdf
from fastapi import UploadFile, HTTPException

def load_pdf(file: UploadFile) -> str:
    """Extracts text content from a PDF file."""
    try:
        content = file.file.read()
        text_content = ""
        reader = pypdf.PdfReader(io.BytesIO(content))
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
        return text_content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process PDF file: {e}")
