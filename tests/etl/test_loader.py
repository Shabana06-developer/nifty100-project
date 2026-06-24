import pytest
import pandas as pd
from src.etl.loader import load_excel_file, load_all_raw_files


def test_load_excel_file_success():
    df = load_excel_file("data/raw/sample_companies.xlsx")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 3
    assert "company_name" in df.columns


def test_load_excel_file_missing_raises():
    with pytest.raises(FileNotFoundError):
        load_excel_file("data/raw/does_not_exist.xlsx")


def test_load_all_raw_files_returns_dict():
    result = load_all_raw_files("data/raw")
    assert isinstance(result, dict)
    assert "sample_companies" in result


def test_load_all_raw_files_missing_dir_raises():
    with pytest.raises(FileNotFoundError):
        load_all_raw_files("data/does_not_exist")


@pytest.mark.parametrize("column", ["company_id", "company_name", "ticker", "year"])
def test_sample_file_has_expected_columns(column):
    df = load_excel_file("data/raw/sample_companies.xlsx")
    assert column in df.columns