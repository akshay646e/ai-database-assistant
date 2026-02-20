def sanitize_table_name(filename: str) -> str:
    """Sanitize filename to be a valid SQL table name."""
    name = filename.split('.')[0]
    return "upload_" + "".join(c if c.isalnum() else "_" for c in name).lower()[:50]
