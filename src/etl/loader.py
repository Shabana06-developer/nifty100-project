"""
loader.py
Functions that read raw source files into pandas DataFrames.
Core files (7): use header=1 (row 0 is metadata, row 1 is real header).
Supplementary files (5): use header=0.
"""
import os
import pandas as pd

CORE_FILES = ["companies", "profitandloss", "balancesheet", "cashflow",
              "analysis", "documents", "prosandcons"]
SUPPLEMENTARY_FILES = ["sectors", "stock_prices", "market_cap",
                        "financial_ratios", "peer_groups"]


def load_excel_file(filepath: str, header_row: int = 0) -> pd.DataFrame:
    """Reads a single Excel file into a DataFrame. Raises FileNotFoundError if missing."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_excel(filepath, header=header_row)


def load_core_file(name: str, raw_dir: str = "data/raw") -> pd.DataFrame:
    """Loads one core file by name (no extension), using header=1."""
    path = os.path.join(raw_dir, f"{name}.xlsx")
    return load_excel_file(path, header_row=1)


def load_supplementary_file(name: str, supporting_dir: str = "data/supporting") -> pd.DataFrame:
    """Loads one supplementary file by name (no extension), using header=0."""
    path = os.path.join(supporting_dir, f"{name}.xlsx")
    return load_excel_file(path, header_row=0)


def load_all_raw_files(raw_dir: str = "data/raw", supporting_dir: str = "data/supporting") -> dict:
    """Loads all 12 source files into a dict: {table_name: DataFrame}."""
    dataframes = {}
    for name in CORE_FILES:
        dataframes[name] = load_core_file(name, raw_dir)
    for name in SUPPLEMENTARY_FILES:
        dataframes[name] = load_supplementary_file(name, supporting_dir)
    return dataframes