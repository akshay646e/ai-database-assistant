"""
DB Loader for connecting to SQL databases and extracting schema
"""
from typing import Dict, Any

def get_connection(config: Dict[str, Any]):
    db_type = config["db_type"].lower()

    if db_type == "mysql":
        import mysql.connector
        return mysql.connector.connect(
            host=config["host"],
            port=int(config["port"]),
            user=config["username"],
            password=config["password"],
            database=config["database"],
            connect_timeout=10,
            autocommit=True,
        )

    elif db_type == "postgresql":
        import psycopg2
        return psycopg2.connect(
            host=config["host"],
            port=int(config["port"]),
            user=config["username"],
            password=config["password"],
            dbname=config["database"],
            connect_timeout=10,
        )

    elif db_type == "sqlite":
        import sqlite3
        # Connect to local file based on database name
        db_file = f"{config.get('database', 'local_uploads')}.db"
        conn = sqlite3.connect(db_file)
        # return rows as dicts for easier processing if needed, but we keep standard tuple behavior
        return conn

    else:
        raise ValueError(f"Unsupported DB type: '{db_type}'. Use 'mysql', 'postgresql', or 'sqlite'.")


def get_schema(conn, db_type: str) -> Dict[str, Any]:
    """Extract tables, columns, types, sample values, and row counts"""
    schema = {}
    cursor = conn.cursor()

    try:
        db_type = db_type.lower()

        if db_type == "mysql":
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                cursor.execute(f"DESCRIBE `{table}`")
                columns = [
                    {
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "key": row[3],
                        "default": row[4],
                    }
                    for row in cursor.fetchall()
                ]
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                count = cursor.fetchone()[0]
                schema[table] = {"columns": columns, "row_count": count}

        elif db_type == "postgresql":
            print(f"DEBUG: Fetching schema for PostgreSQL DB: {conn.get_dsn_parameters().get('dbname')} as user {conn.get_dsn_parameters().get('user')}")
            cursor.execute("""
                SELECT table_name, table_type FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            all_tables = cursor.fetchall()
            print(f"DEBUG: Found {len(all_tables)} total objects in 'public' schema: {all_tables}")
            
            # Keep both Base Tables and Views
            tables = [row[0] for row in all_tables if row[1] in ('BASE TABLE', 'VIEW')]

            for table in tables:
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """, (table,))
                columns = [
                    {
                        "name": row[0],
                        "type": row[1],
                        "nullable": row[2] == "YES",
                        "default": row[3],
                    }
                    for row in cursor.fetchall()
                ]
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                schema[table] = {"columns": columns, "row_count": count}

        elif db_type == "sqlite":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]

            for table in tables:
                cursor.execute(f"PRAGMA table_info(`{table}`)")
                # PRAGMA returns: cid, name, type, notnull, dflt_value, pk
                columns = [
                    {
                        "name": row[1],
                        "type": row[2],
                        "nullable": row[3] == 0,
                        "default": row[4],
                    }
                    for row in cursor.fetchall()
                ]
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                count = cursor.fetchone()[0]
                schema[table] = {"columns": columns, "row_count": count}

    finally:
        cursor.close()

    return schema
