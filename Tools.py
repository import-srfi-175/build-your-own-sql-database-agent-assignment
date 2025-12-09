import sqlite3

ROW_LIMIT = 100


def list_tables(cursor: sqlite3.Cursor):
    table_lookup_query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(table_lookup_query)
    return [table_name[0] for table_name in cursor.fetchall()]


def describe_table(cursor: sqlite3.Cursor, table_name: str):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    available_tables = [row[0] for row in cursor.fetchall()]
    if table_name not in available_tables:
        return f"Error: Table '{table_name}' not found. Use list_tables() to check available tables."

    cursor.execute(f"PRAGMA table_info({table_name});")
    column_metadata = cursor.fetchall()
    column_descriptions = [f"{column[1]} ({column[2]})" for column in column_metadata]

    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]

    return f"Table '{table_name}' has {row_count} rows. Columns: {', '.join(column_descriptions)}"


def query_database(cursor: sqlite3.Cursor, query: str):
    if not query.strip().lower().startswith("select"):
        return "Error: Only SELECT queries are allowed."

    enforced_query = query.strip()
    if "limit" not in enforced_query.lower():
        enforced_query = enforced_query.rstrip(";") + f" LIMIT {ROW_LIMIT};"

    try:
        cursor.execute(enforced_query)
        rows = cursor.fetchall()
        if not rows:
            return "Query executed successfully but returned no results."
        cols = [description[0] for description in cursor.description]
        return {"columns": cols, "rows": rows}
    except sqlite3.Error as e:
        return f"SQL Error: {e}"


list_tables_tool = {
    "name": "list_tables",
    "description": "Lists all tables in the connected SQLite database.",
    "parameters": {"type": "object", "properties": {}}
}

describe_table_tool = {
    "name": "describe_table",
    "description": "Describes a table’s schema and row count.",
    "parameters": {
        "type": "object",
        "properties": {
            "table_name": {
                "type": "string",
                "description": "The name of the table to describe."
            }
        },
        "required": ["table_name"]
    }
}

query_database_tool = {
    "name": "query_database",
    "description": "Executes a read-only SELECT query (limited to 100 rows).",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The SELECT query to execute."
            }
        },
        "required": ["query"]
    }
}

# === TOOL LIST + REGISTRY ===
ALL_TOOLS = [
    {
        "function_declarations": [
            list_tables_tool,
            describe_table_tool,
            query_database_tool
        ]
    }
]

TOOL_REGISTRY = {
    "list_tables": list_tables,
    "describe_table": describe_table,
    "query_database": query_database,
}
