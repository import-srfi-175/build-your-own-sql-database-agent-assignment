# SQL Library Agent (SQLite + Gemini)

## Purpose
Interactive ReAct-style SQL agent for a sample library database (`library.db`). The agent inspects schema, answers questions via tools, and formats results as rich tables.

## Setup
```bash
cd /Users/yashkambli/Desktop/SQL-Agent-main
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
echo "GEMINI_API=your_api_key_here" > .env
python3 Setup_dummy_db.py   # creates library.db
```

## Run
```bash
source .venv/bin/activate
python3 main.py
# type queries; 'exit' or 'quit' to leave
```

## Tools (arguments → returns)
- `list_tables()` → `[table_name, ...]`
- `describe_table(table_name: str)` → `"Table '<name>' has N rows. Columns: col1 (type), ..."`
- `query_database(query: str)` → `{"columns": [...], "rows": [...]}` (SELECT-only, auto-LIMIT 100)

## Example Trace (abridged)
```
THOUGHT: Identify tables first.
ACTION: list_tables({})
OBSERVATION: authors, books, members, loans
THOUGHT: Describe books.
ACTION: describe_table({"table_name":"books"})
OBSERVATION: Table 'books' has 7 rows. Columns: book_id (INTEGER), title (TEXT), author_id (INTEGER), genre (TEXT), published_year (INTEGER), price (NUMERIC(10, 2))
THOUGHT: Compute avg price.
ACTION: query_database({"query":"SELECT genre, ROUND(AVG(price),2) AS avg_price FROM books GROUP BY genre"})
OBSERVATION:
genre           avg_price
--------------- ---------
Fantasy         9.99
Fiction         12.87
Magical Realism 12.75
Science Fiction 12.38
FINAL ANSWER: Listed tables, described books schema, and returned average price per genre.
```

## Notes
- Database is read-only from the agent’s perspective; only SELECT allowed.
- Update sample data by editing `Setup_dummy_db.py` and rerunning it.

