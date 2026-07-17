"""
test_cagr.py
Unit tests for src/analytics/cagr.py — Day 10 (CAGR engine, all 6 edge cases)
"""
import pytest
from src.analytics.cagr import compute_cagr, revenue_cagr, pat_cagr, eps_cagr


# ---------------------------------------------------------------------
# Core compute_cagr — 6 edge cases + normal case (7 tests)
# ---------------------------------------------------------------------

def test_normal_cagr_positive_to_positive():
    cagr, flag = compute_cagr(start_value=100, end_value=200, n_years=5)
    # ((200/100)^(1/5) - 1) * 100 ≈ 14.87%
    assert cagr == pytest.approx(14.87, abs=0.01)
    assert flag is None


def test_decline_to_loss_flag():
    cagr, flag = compute_cagr(start_value=100, end_value=-50, n_years=5)
    assert cagr is None
    assert flag == "DECLINE_TO_LOSS"


def test_turnaround_flag():
    cagr, flag = compute_cagr(start_value=-100, end_value=50, n_years=5)
    assert cagr is None
    assert flag == "TURNAROUND"


def test_both_negative_flag():
    cagr, flag = compute_cagr(start_value=-100, end_value=-50, n_years=5)
    assert cagr is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base_flag():
    cagr, flag = compute_cagr(start_value=0, end_value=100, n_years=5)
    assert cagr is None
    assert flag == "ZERO_BASE"


def test_insufficient_data_missing_n_years():
    cagr, flag = compute_cagr(start_value=100, end_value=200, n_years=None)
    assert cagr is None
    assert flag == "INSUFFICIENT"


def test_insufficient_data_missing_values():
    cagr, flag = compute_cagr(start_value=None, end_value=200, n_years=5)
    assert cagr is None
    assert flag == "INSUFFICIENT"


# ---------------------------------------------------------------------
# revenue_cagr / pat_cagr / eps_cagr wired against a year-series (3 tests)
# ---------------------------------------------------------------------

def test_revenue_cagr_normal_case_with_series():
    series = {
        "2019-03": 1000,
        "2020-03": 1100,
        "2021-03": 1250,
        "2022-03": 1400,
        "2023-03": 2000,
    }
    cagr, flag = revenue_cagr(series, latest_year="2023-03", n_years=5)
    assert cagr is None  # start year 2018-03 not in series -> insufficient
    assert flag == "INSUFFICIENT"


def test_pat_cagr_insufficient_years_not_in_series():
    series = {
        "2021-03": 50,
        "2022-03": 60,
        "2023-03": 80,
    }
    cagr, flag = pat_cagr(series, latest_year="2023-03", n_years=5)
    assert cagr is None
    assert flag == "INSUFFICIENT"


def test_eps_cagr_normal_case_positive_growth():
    series = {
        "2018-03": 10,
        "2019-03": 12,
        "2020-03": 14,
        "2021-03": 16,
        "2022-03": 18,
        "2023-03": 20,
    }
    cagr, flag = eps_cagr(series, latest_year="2023-03", n_years=5)
    # ((20/10)^(1/5) - 1) * 100 ≈ 14.87%
    assert cagr == pytest.approx(14.87, abs=0.01)
    assert flag is None