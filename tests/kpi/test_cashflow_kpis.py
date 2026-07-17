"""
test_cashflow_kpis.py
Unit tests for src/analytics/cashflow_kpis.py — Day 11
"""
import pytest
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


def test_free_cash_flow_normal_case():
    assert free_cash_flow(operating_activity=500, investing_activity=-200) == 300


def test_free_cash_flow_negative_allowed():
    assert free_cash_flow(operating_activity=100, investing_activity=-300) == -200


def test_cfo_quality_score_high_quality():
    avg, label = cfo_quality_score(cfo_values=[120, 130, 140], pat_values=[100, 100, 100])
    assert avg == pytest.approx(1.3)
    assert label == "High Quality"


def test_cfo_quality_score_accrual_risk():
    avg, label = cfo_quality_score(cfo_values=[30, 40, 20], pat_values=[100, 100, 100])
    assert avg == pytest.approx(0.3)
    assert label == "Accrual Risk"


def test_cfo_quality_score_pat_zero_returns_none():
    avg, label = cfo_quality_score(cfo_values=[100], pat_values=[0])
    assert avg is None
    assert label is None


def test_capex_intensity_asset_light():
    pct, label = capex_intensity(investing_activity=-20, sales=1000)
    assert pct == pytest.approx(2.0)
    assert label == "Asset Light"


def test_capex_intensity_capital_intensive():
    pct, label = capex_intensity(investing_activity=-150, sales=1000)
    assert pct == pytest.approx(15.0)
    assert label == "Capital Intensive"


def test_fcf_conversion_rate_zero_operating_profit_returns_none():
    assert fcf_conversion_rate(fcf=100, operating_profit=0) is None


def test_capital_allocation_reinvestor_pattern():
    cfo_s, cfi_s, cff_s, label = capital_allocation_pattern(cfo=500, cfi=-300, cff=-100, cfo_to_pat_ratio=0.8)
    assert (cfo_s, cfi_s, cff_s) == ("+", "-", "-")
    assert label == "Reinvestor"


def test_capital_allocation_shareholder_returns_pattern():
    cfo_s, cfi_s, cff_s, label = capital_allocation_pattern(cfo=500, cfi=-100, cff=-300, cfo_to_pat_ratio=1.5)
    assert (cfo_s, cfi_s, cff_s) == ("+", "-", "-")
    assert label == "Shareholder Returns"


def test_capital_allocation_distress_signal_pattern():
    cfo_s, cfi_s, cff_s, label = capital_allocation_pattern(cfo=-100, cfi=200, cff=150)
    assert (cfo_s, cfi_s, cff_s) == ("-", "+", "+")
    assert label == "Distress Signal"


def test_capital_allocation_pre_revenue_pattern():
    cfo_s, cfi_s, cff_s, label = capital_allocation_pattern(cfo=-50, cfi=-30, cff=-20)
    assert (cfo_s, cfi_s, cff_s) == ("-", "-", "-")
    assert label == "Pre-Revenue"