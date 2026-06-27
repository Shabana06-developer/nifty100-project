"""
db/loader.py
Creates the SQLite database from schema.sql and inserts cleaned DataFrames
into the correct tables.
"""
import os
import sqlite3
import pandas as pd


def create_database(db_path: str, schema_path: str = "db/schema.sql") -> None:
    """Creates (or re-creates) the database tables from schema.sql."""
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def insert_dataframe(db_path: str, table_name: str, df: pd.DataFrame, if_exists: str = "append") -> int:
    """
    Inserts a DataFrame into the given table.
    Returns the number of rows inserted.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)
        conn.commit()
    finally:
        conn.close()
    return len(df)


def check_foreign_keys(db_path: str) -> list:
    """
    Runs SQLite's built-in FK checker.
    Returns a list of violations (empty list = all good).
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.execute("PRAGMA foreign_key_check;")
        violations = cursor.fetchall()
    finally:
        conn.close()
    return violations


def get_table_row_count(db_path: str, table_name: str) -> int:
    """Returns the row count for a given table."""
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
    finally:
        conn.close()
    return count