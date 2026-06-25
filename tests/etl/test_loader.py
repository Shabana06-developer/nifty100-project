import pytest
import pandas as pd
from src.etl.loader import load_excel_file, load_core_file, load_supplementary_file, load_all_raw_files


def test_load_core_file_companies():
    df = load_core_file("companies")
    assert isinstance(df, pd.DataFrame)
    assert "id" in df.columns
    assert len(df) > 0


def test_load_core_file_missing_raises():
    with pytest.raises(FileNotFoundError):
        load_core_file("does_not_exist")


def test_load_supplementary_file_sectors():
    df = load_supplementary_file("sectors")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_load_all_raw_files_returns_dict():
    result = load_all_raw_files()
    assert isinstance(result, dict)
    assert "companies" in result
    assert "sectors" in result
    assert len(result) == 12


@pytest.mark.parametrize("table_name", [
    "companies", "profitandloss", "balancesheet", "cashflow",
    "analysis", "documents", "prosandcons"
])
def test_all_core_tables_load_successfully(table_name):
    df = load_core_file(table_name)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


@pytest.mark.parametrize("table_name", [
    "sectors", "stock_prices", "market_cap", "financial_ratios", "peer_groups"
])
def test_all_supplementary_tables_load_successfully(table_name):
    df = load_supplementary_file(table_name)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0