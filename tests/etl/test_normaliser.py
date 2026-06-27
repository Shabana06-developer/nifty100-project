import pandas as pd
import pytest
from src.etl.normaliser import (
    normalize_year, normalize_year_safe, normalize_year_column, normalize_ticker
)


@pytest.mark.parametrize("raw_value, expected", [
    ("Mar-23", "2023-03"),
    ("Dec 2012", "2012-12"),
    ("Mar 2024", "2024-03"),
    ("2013", "2013-03"),
    ("FY23", "2023-03"),
    ("2023-03", "2023-03"),
    ("TTM", "TTM"),
    ("ttm", "TTM"),
    ("Jun-13", "2013-06"),
    ("Sep 2011", "2011-09"),
])
def test_normalize_year_valid(raw_value, expected):
    assert normalize_year(raw_value) == expected


@pytest.mark.parametrize("bad_value", [
    None,
    "garbage",
    "",
    "2024.5",          # malformed
    "Mar 2016 9m",     # stub/interim period
    "Mar 2023 15",     # stub/interim period
])
def test_normalize_year_invalid(bad_value):
    with pytest.raises(ValueError):
        normalize_year(bad_value)


def test_normalize_year_safe_returns_none_on_failure():
    clean, raw = normalize_year_safe("Mar 2023 15")
    assert clean is None
    assert raw == "Mar 2023 15"


def test_normalize_year_safe_returns_value_on_success():
    clean, raw = normalize_year_safe("Mar-23")
    assert clean == "2023-03"
    assert raw is None


def test_normalize_year_column_splits_correctly():
    df = pd.DataFrame({
        "company_id": ["TCS", "INFY", "WIPRO"],
        "year": ["Mar-23", "Mar 2016 9m", "2024.5"],
    })
    clean, rejected = normalize_year_column(df)
    assert len(clean) == 1
    assert len(rejected) == 2
    assert clean.iloc[0]["year"] == "2023-03"
    assert "raw_year_value" in rejected.columns


@pytest.mark.parametrize("raw_value, expected", [
    ("TCS", "TCS"),
    ("tcs", "TCS"),
    ("bajaj-auto", "BAJAJ-AUTO"),
    ("m&m", "M&M"),
])
def test_normalize_ticker_valid(raw_value, expected):
    assert normalize_ticker(raw_value) == expected


@pytest.mark.parametrize("bad_value", [None, "A"])
def test_normalize_ticker_invalid(bad_value):
    with pytest.raises(ValueError):
        normalize_ticker(bad_value)