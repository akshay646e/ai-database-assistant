"""
Module 3: SQL Executor — safe SELECT-only execution
"""
import re
from typing import Tuple, List


FORBIDDEN = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER",
             "TRUNCATE", "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"]


def execute_query(conn, sql: str) -> Tuple[List[str], List[tuple]]:
    """Execute SQL, return (columns, rows). Only SELECT allowed."""
    cleaned = sql.strip()
    upper = cleaned.upper()

    # Safety check
    for kw in FORBIDDEN:
        if re.search(rf"\b{kw}\b", upper):
            raise ValueError(
                f"Security: '{kw}' is not allowed. Only SELECT queries are permitted."
            )

    if not upper.startswith("SELECT") and not upper.startswith("WITH"):
        raise ValueError("Only SELECT or WITH (CTE) queries are allowed.")

    cursor = conn.cursor()
    try:
        cursor.execute(cleaned)
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
