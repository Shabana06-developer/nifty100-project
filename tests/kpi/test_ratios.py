"""
test_ratios.py
Unit tests for src/analytics/ratios.py — Day 8 (profitability) + Day 9 (leverage/efficiency)
"""
import pytest
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    compute_ebit,
    debt_to_equity,
    interest_coverage_ratio,
    net_debt,
    asset_turnover,
)


# ---------------------------------------------------------------------
# Day 8 — Profitability Ratios (8 tests)
# ---------------------------------------------------------------------

def test_net_profit_margin_normal_case():
    assert net_profit_margin(net_profit=100, sales=1000) == pytest.approx(10.0)


def test_net_profit_margin_zero_sales_returns_none():
    assert net_profit_margin(net_profit=100, sales=0) is None


def test_operating_profit_margin_normal_case_no_mismatch():
    computed, mismatch = operating_profit_margin(operating_profit=130, sales=1000, opm_percentage=13.0)
    assert computed == pytest.approx(13.0)
    assert mismatch is False


def test_operating_profit_margin_mismatch_flagged():
    # computed = 13.0%, source says 20.0% -> diff > 1.0pp tolerance -> flagged
    computed, mismatch = operating_profit_margin(operating_profit=130, sales=1000, opm_percentage=20.0)
    assert computed == pytest.approx(13.0)
    assert mismatch is True


def test_return_on_equity_normal_case():
    roe = return_on_equity(net_profit=100, equity_capital=50, reserves=450)
    assert roe == pytest.approx(20.0)


def test_return_on_equity_negative_equity_returns_none():
    roe = return_on_equity(net_profit=100, equity_capital=50, reserves=-500)
    assert roe is None


def test_return_on_assets_zero_denominator_returns_none():
    assert return_on_assets(net_profit=100, total_assets=0) is None


def test_compute_ebit_and_roce_normal_case():
    ebit = compute_ebit(profit_before_tax=200, interest=50)
    assert ebit == 250
    roce = return_on_capital_employed(ebit=ebit, equity_capital=100, reserves=400, borrowings=500)
    assert roce == pytest.approx(25.0)


# ---------------------------------------------------------------------
# Day 9 — Leverage & Efficiency Ratios (8 tests)
# ---------------------------------------------------------------------

def test_debt_to_equity_debt_free_returns_zero_not_none():
    de, flag = debt_to_equity(borrowings=0, equity_capital=100, reserves=400)
    assert de == 0.0
    assert flag is False


def test_debt_to_equity_high_leverage_flag_set():
    de, flag = debt_to_equity(borrowings=600, equity_capital=50, reserves=50, is_financials_sector=False)
    assert de == pytest.approx(6.0)
    assert flag is True


def test_debt_to_equity_high_leverage_suppressed_for_financials():
    de, flag = debt_to_equity(borrowings=600, equity_capital=50, reserves=50, is_financials_sector=True)
    assert de == pytest.approx(6.0)
    assert flag is False


def test_interest_coverage_ratio_interest_zero_returns_debt_free_label():
    icr, label, warn = interest_coverage_ratio(operating_profit=100, other_income=10, interest=0)
    assert icr is None
    assert label == "Debt Free"
    assert warn is False


def test_interest_coverage_ratio_normal_case():
    icr, label, warn = interest_coverage_ratio(operating_profit=150, other_income=10, interest=40)
    assert icr == pytest.approx(4.0)
    assert label is None
    assert warn is False


def test_interest_coverage_ratio_warning_flag_below_threshold():
    icr, label, warn = interest_coverage_ratio(operating_profit=50, other_income=5, interest=40)
    assert icr == pytest.approx(1.375)
    assert warn is True


def test_net_debt_normal_case():
    assert net_debt(borrowings=500, investments=200) == 300


def test_asset_turnover_zero_denominator_returns_none():
    assert asset_turnover(sales=1000, total_assets=0) is None