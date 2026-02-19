"""
Module 2: Natural Language → SQL using Google Gemini
"""
import os
import re
import google.generativeai as genai
from typing import Dict, Any


def _schema_to_text(schema: Dict[str, Any]) -> str:
    lines = []
    for table, info in schema.items():
        cols = ", ".join(f"{c['name']} {c['type']}" for c in info["columns"])
        lines.append(f"  Table `{table}` ({info['row_count']} rows): [{cols}]")
    return "\n".join(lines)


def natural_language_to_sql(question: str, schema: Dict[str, Any], db_type: str = "mysql") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env file")

    genai.configure(api_key=api_key)
    model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)

    dialect = "MySQL" if db_type.lower() == "mysql" else "PostgreSQL"
    schema_text = _schema_to_text(schema)

    prompt = f"""You are an expert {dialect} SQL query generator.

DATABASE SCHEMA:
{schema_text}

USER QUESTION: {question}

STRICT RULES:
1. Return ONLY the raw SQL query — no markdown, no backticks, no explanation
2. Use valid {dialect} syntax only
3. For MySQL use backticks for table/column names: `table_name`
4. For PostgreSQL use double quotes: "table_name"
5. If the question asks for "all" or could return many rows, add LIMIT 1000
6. Always use meaningful column aliases (e.g. COUNT(*) AS total_count)
7. Handle NULLs with COALESCE where appropriate
8. Use proper JOINs when multiple tables are needed

SQL QUERY (raw only):"""

    response = model.generate_content(prompt)
    sql = response.text.strip()

    # Strip any markdown artifacts
    sql = re.sub(r"```sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"```\s*", "", sql)
    sql = sql.strip().rstrip(";").strip()

    return sql
