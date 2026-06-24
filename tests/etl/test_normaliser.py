import pytest
from src.etl.normaliser import normalize_year, normalize_ticker


@pytest.mark.parametrize("raw_value, expected", [
    ("FY2020-21", 2020),
    ("2020-21", 2020),
    ("2021", 2021),
    (2021, 2021),
    ("FY2019-2020", 2019),
    ("2015-16", 2015),
    ("fy2018-19", 2018),
    (" 2020 ", 2020),
    ("FY 2022-23", 2022),
    (1999, 1999),
])
def test_normalize_year_valid(raw_value, expected):
    assert normalize_year(raw_value) == expected


@pytest.mark.parametrize("bad_value", [
    None,
    "not-a-year",
    "",
    "FYxx-yy",
])
def test_normalize_year_invalid(bad_value):
    with pytest.raises(ValueError):
        normalize_year(bad_value)


@pytest.mark.parametrize("raw_value, expected", [
    ("RELIANCE.NS", "RELIANCE"),
    (" tcs.bo ", "TCS"),
    ("INFY", "INFY"),
    ("infy.ns", "INFY"),
    ("HDFC.BO", "HDFC"),
    ("  wipro  ", "WIPRO"),
    ("TATAMOTORS.NS", "TATAMOTORS"),
    ("itc.bo", "ITC"),
    ("ICICIBANK", "ICICIBANK"),
    ("sbin.ns", "SBIN"),
])
def test_normalize_ticker_valid(raw_value, expected):
    assert normalize_ticker(raw_value) == expected


@pytest.mark.parametrize("bad_value", [None])
def test_normalize_ticker_invalid(bad_value):
    with pytest.raises(ValueError):
        normalize_ticker(bad_value)


@pytest.mark.parametrize("raw_value, expected", [
    ("FY2023-24", 2023),
    ("2024-25", 2024),
])
def test_normalize_year_extra_cases(raw_value, expected):
    assert normalize_year(raw_value) == expected