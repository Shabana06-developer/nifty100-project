"""
ratios.py
Financial Ratio Engine — Profitability, Leverage & Efficiency ratios.

All functions take raw values (floats or None) and return either:
  - a float ratio, or
  - None when the calculation is undefined (e.g. zero denominator),
    per the Sprint 2 spec.

Schema note: profitandloss has no direct EBIT column.
EBIT is derived as: profit_before_tax + interest
"""


# ---------------------------------------------------------------------
# Day 8 — Profitability Ratios
# ---------------------------------------------------------------------

def net_profit_margin(net_profit, sales):
    """Net Profit Margin = net_profit / sales * 100. None if sales = 0."""
    if sales is None or sales == 0 or net_profit is None:
        return None
    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales, opm_percentage=None, tolerance=1.0):
    """
    Operating Profit Margin = operating_profit / sales * 100.
    Cross-checks against the source opm_percentage field; logs (via return flag)
    if the difference exceeds `tolerance` percentage points.

    Returns: (computed_opm, mismatch_flag: bool)
    """
    if sales is None or sales == 0 or operating_profit is None:
        return None, False

    computed = (operating_profit / sales) * 100
    mismatch = False
    if opm_percentage is not None:
        if abs(computed - opm_percentage) > tolerance:
            mismatch = True
    return computed, mismatch


def return_on_equity(net_profit, equity_capital, reserves):
    """ROE = net_profit / (equity_capital + reserves) * 100. None if base <= 0."""
    if net_profit is None or equity_capital is None or reserves is None:
        return None
    base = equity_capital + reserves
    if base <= 0:
        return None
    return (net_profit / base) * 100


def return_on_capital_employed(ebit, equity_capital, reserves, borrowings,
                                is_financials_sector=False):
    """
    ROCE = EBIT / (equity + reserves + borrowings) * 100.
    For companies in the Financials broad_sector, callers should use a
    sector-relative benchmark rather than this absolute threshold
    (handled by the caller / validator, not this function).
    """
    if ebit is None or equity_capital is None or reserves is None or borrowings is None:
        return None
    capital_employed = equity_capital + reserves + borrowings
    if capital_employed <= 0:
        return None
    return (ebit / capital_employed) * 100


def return_on_assets(net_profit, total_assets):
    """ROA = net_profit / total_assets * 100. None if total_assets = 0."""
    if net_profit is None or total_assets is None or total_assets == 0:
        return None
    return (net_profit / total_assets) * 100


def compute_ebit(profit_before_tax, interest):
    """EBIT = profit_before_tax + interest (schema has no direct EBIT column)."""
    if profit_before_tax is None or interest is None:
        return None
    return profit_before_tax + interest


# ---------------------------------------------------------------------
# Day 9 — Leverage & Efficiency Ratios
# ---------------------------------------------------------------------

def debt_to_equity(borrowings, equity_capital, reserves, is_financials_sector=False,
                    high_leverage_threshold=5.0):
    """
    D/E = borrowings / (equity_capital + reserves).
    Returns 0 (not None) if borrowings = 0.
    Returns: (de_ratio, high_leverage_flag: bool)
    high_leverage_flag is suppressed (always False) for Financials sector companies.
    """
    if borrowings is None or equity_capital is None or reserves is None:
        return None, False

    if borrowings == 0:
        return 0.0, False

    base = equity_capital + reserves
    if base <= 0:
        return None, False

    de = borrowings / base
    high_leverage_flag = (de > high_leverage_threshold) and not is_financials_sector
    return de, high_leverage_flag


def interest_coverage_ratio(operating_profit, other_income, interest,
                             warning_threshold=1.5):
    """
    ICR = (operating_profit + other_income) / interest.
    If interest = 0 (debt-free company): return (None, "Debt Free", False).
    Returns: (icr_value, icr_label, warning_flag)
    """
    if operating_profit is None or interest is None:
        return None, None, False

    other_income = other_income or 0

    if interest == 0:
        return None, "Debt Free", False

    icr = (operating_profit + other_income) / interest
    warning_flag = icr < warning_threshold
    return icr, None, warning_flag


def net_debt(borrowings, investments):
    """Net Debt = borrowings - investments (investments used as liquid asset proxy)."""
    if borrowings is None or investments is None:
        return None
    return borrowings - investments


def asset_turnover(sales, total_assets):
    """Asset Turnover = sales / total_assets. None if total_assets = 0."""
    if sales is None or total_assets is None or total_assets == 0:
        return None
    return sales / total_assets