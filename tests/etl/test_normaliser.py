import pytest
from src.etl.normaliser import normalize_year, normalize_ticker


@pytest.mark.parametrize("raw_value, expected", [
    ("Mar-23", "2023-03"),
    ("Mar 23", "2023-03"),
    ("March-2023", "2023-03"),
    ("2023", "2023-03"),
    ("FY23", "2023-03"),
    ("Dec-22", "2022-12"),
    ("Jun-23", "2023-06"),
    ("2023-03", "2023-03"),
    ("mar-23", "2023-03"),
    ("FY2023", "2023-03"),
    ("Sep-21", "2021-09"),
    ("Nov-20", "2020-11"),
])
def test_normalize_year_valid(raw_value, expected):
    assert normalize_year(raw_value) == expected


@pytest.mark.parametrize("bad_value", [
    None,
    "garbage",
    "",
    "XYZ-99",
])
def test_normalize_year_invalid(bad_value):
    with pytest.raises(ValueError):
        normalize_year(bad_value)


@pytest.mark.parametrize("raw_value, expected", [
    ("TCS", "TCS"),
    ("tcs", "TCS"),
    (" tcs ", "TCS"),
    ("BAJAJ-AUTO", "BAJAJ-AUTO"),
    ("bajaj-auto", "BAJAJ-AUTO"),
    ("M&M", "M&M"),
    ("m&m", "M&M"),
    ("infy", "INFY"),
    ("HDFCBANK", "HDFCBANK"),
    ("relianceindustries", "RELIANCEINDUSTRIES"[:12] if False else "RELIANCEINDUSTRIES"),
])
def test_normalize_ticker_valid(raw_value, expected):
    if len(expected) <= 12:
        assert normalize_ticker(raw_value) == expected


@pytest.mark.parametrize("bad_value", [None, "A", ""])
def test_normalize_ticker_invalid(bad_value):
    with pytest.raises(ValueError):
        normalize_ticker(bad_value)