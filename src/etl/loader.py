"""
loader.py
Loads raw Excel source files for the Nifty100 project.

Core files (data/raw/, header=1): companies, profitandloss, balancesheet,
    cashflow, analysis, documents, prosandcons
Supplementary files (data/supporting/, header=0): sectors, stock_prices,
    market_cap, financial_ratios, peer_groups
"""
import os
import pandas as pd

RAW_DIR = "data/raw"
SUPPORTING_DIR = "data/supporting"

CORE_FILES = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
}

SUPPLEMENTARY_FILES = {
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
    "market_cap": "market_cap.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
    "peer_groups": "peer_groups.xlsx",
}


def load_excel_file(filepath: str, header: int = 0) -> pd.DataFrame:
    """Load a single Excel file. Raises FileNotFoundError if missing."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_excel(filepath, header=header)


def load_core_file(table_name: str) -> pd.DataFrame:
    """Load a core file (header=1) by logical table name."""
    if table_name not in CORE_FILES:
        raise FileNotFoundError(f"Unknown core table: {table_name}")
    filepath = os.path.join(RAW_DIR, CORE_FILES[table_name])
    return load_excel_file(filepath, header=1)


def load_supplementary_file(table_name: str) -> pd.DataFrame:
    """Load a supplementary file (header=0) by logical table name."""
    if table_name not in SUPPLEMENTARY_FILES:
        raise FileNotFoundError(f"Unknown supplementary table: {table_name}")
    filepath = os.path.join(SUPPORTING_DIR, SUPPLEMENTARY_FILES[table_name])
    return load_excel_file(filepath, header=0)


def load_all_raw_files() -> dict:
    """Load all 12 core + supplementary files into a dict of DataFrames."""
    result = {}
    for name in CORE_FILES:
        result[name] = load_core_file(name)
    for name in SUPPLEMENTARY_FILES:
        result[name] = load_supplementary_file(name)
    return result