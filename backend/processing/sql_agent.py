import re
from typing import Dict, Any, Tuple, List
from core.llm import get_llm_model

def _schema_to_text(schema: Dict[str, Any], dialect: str) -> str:
    lines = []
    quote_char = '`' if dialect.lower() == "mysql" else '"'
    for table, info in schema.items():
        cols = ", ".join(f"{quote_char}{c['name']}{quote_char} {c['type']}" for c in info["columns"])
        lines.append(f"  Table {quote_char}{table}{quote_char} ({info['row_count']} rows): [{cols}]")
    return "\n".join(lines)


def natural_language_to_sql(question: str, schema: Dict[str, Any], db_type: str = "mysql") -> str:
    if not schema:
        raise ValueError("Database schema is empty. Please ensure tables exist in the database before querying.")

    model = get_llm_model()

    if db_type.lower() == "mysql":
        dialect = "MySQL"
    elif db_type.lower() == "sqlite":
        dialect = "SQLite"
    else:
        dialect = "PostgreSQL"
    
    schema_text = _schema_to_text(schema, dialect)

    prompt = f"""You are an expert {dialect} SQL query generator.

DATABASE SCHEMA:
{schema_text}

USER QUESTION: {question}

STRICT RULES:
1. Return ONLY the raw SQL query. Do NOT wrap it in ```sql ... ``` or any other markdown fence.
2. Use valid {dialect} syntax only
3. For MySQL, enclose table and column names in backticks (e.g., `my_table_name`)
4. For PostgreSQL, enclose table and column names in double quotes. Do NOT use literal "table_name", use actual tables
5. You MUST ONLY use the tables and columns provided in the DATABASE SCHEMA above. Do not hallucinate table names
6. Always use meaningful column aliases (e.g. COUNT(*) AS total_count)
7. Handle NULLs with COALESCE where appropriate
8. Use proper JOINs when multiple tables are needed

SQL QUERY (raw only):"""

    max_retries = 3
    base_delay = 2
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            sql = response.text.strip()

            # Strip any markdown artifacts
            sql = re.sub(r"```sql\s*", "", sql, flags=re.IGNORECASE)
            sql = re.sub(r"```\s*", "", sql)
            sql = sql.strip().rstrip(";").strip()

            return sql
        except Exception as e:
            if "429" in str(e) or "exhausted" in str(e).lower():
                if attempt < max_retries - 1:
                    import time
                    time.sleep(base_delay * (2 ** attempt))
                    continue
            raise e


def execute_query(conn, sql: str) -> Tuple[List[str], List[tuple]]:
    """Execute SQL, return (columns, rows)."""
    # Strip markdown code blocks before validation (e.g., ```sql\n ... \n```)
    cleaned = re.sub(r"^```[a-zA-Z]*\n", "", sql, flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.strip()
    upper = cleaned.upper()

    cursor = conn.cursor()
    try:
        cursor.execute(cleaned)

        if cursor.description is None:
            # Query did not return rows (e.g. UPDATE, INSERT, DELETE)
            conn.commit()
            return ["Rows Affected"], [(cursor.rowcount,)]

        description = cursor.description or []
        columns = [desc[0] for desc in description]
        rows = cursor.fetchall()

        # Serialize special types
        clean_rows = []
        for row in rows:
            clean_row = []
            for val in row:
                if val is None:
                    clean_row.append(None)
                elif hasattr(val, "isoformat"):   # datetime / date / time
                    clean_row.append(val.isoformat())
                elif isinstance(val, bytes):
                    clean_row.append(val.decode("utf-8", errors="replace"))
                elif isinstance(val, (int, float, str, bool)):
                    clean_row.append(val)
                else:
                    clean_row.append(str(val))
            clean_rows.append(tuple(clean_row))

        return columns, clean_rows

    except Exception as e:
        raise RuntimeError(f"SQL Error: {e}")
    finally:
        cursor.close()
