"""
loader.py
Functions that read raw source files into pandas DataFrames.
"""
import os
import pandas as pd


def load_excel_file(filepath: str) -> pd.DataFrame:
    """Reads a single Excel file into a DataFrame. Raises FileNotFoundError if missing."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_excel(filepath)


def load_all_raw_files(raw_dir: str) -> dict:
    """
    Loads every .xlsx file in raw_dir into a dict: {filename_without_ext: DataFrame}
    """
    if not os.path.isdir(raw_dir):
        raise FileNotFoundError(f"Directory not found: {raw_dir}")

    dataframes = {}
    for filename in os.listdir(raw_dir):
        if filename.endswith(".xlsx"):
            name = filename.replace(".xlsx", "")
            full_path = os.path.join(raw_dir, filename)
            dataframes[name] = load_excel_file(full_path)
    return dataframes