"""
scripts_run_exploratory_queries.py
Runs the 10 exploratory queries from notebooks/exploratory_queries.sql
against nifty100.db and prints results.
"""
import sqlite3
import pandas as pd

DB_PATH = "nifty100.db"
SQL_FILE = "notebooks/exploratory_queries.sql"

with open(SQL_FILE, "r", encoding="utf-8") as f:
    sql_text = f.read()

# Split on semicolons, drop empty/comment-only statements

# Strip full-line comments first, then split on semicolons
lines_no_comments = [line for line in sql_text.splitlines() if not line.strip().startswith("--")]
cleaned_sql = "\n".join(lines_no_comments)
statements = [s.strip() for s in cleaned_sql.split(";") if s.strip()]
print(f"DEBUG: parsed {len(statements)} statements")

conn = sqlite3.connect(DB_PATH)

for i, stmt in enumerate(statements, start=1):
    # Skip pure comment blocks that survived splitting


    cleaned = stmt
    print(f"\n{'='*70}")
    print(f"QUERY {i}")
    print(f"{'='*70}")
    try:
        df = pd.read_sql_query(cleaned, conn)
        print(df.to_string(index=False))
    except Exception as e:
        print(f"ERROR: {e}")

conn.close()