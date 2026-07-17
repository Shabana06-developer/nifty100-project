"""
cagr.py
CAGR Engine — computes Compound Annual Growth Rate for Revenue, PAT (net profit),
and EPS across 3-year, 5-year, and 10-year windows.

Formula: CAGR = ((end_value / start_value) ** (1/n) - 1) * 100

Edge case handling (all 6, per Sprint 2 Day 10 spec):
  Positive -> Positive : compute normally
  Positive -> Negative : None, flag DECLINE_TO_LOSS
  Negative -> Positive : None, flag TURNAROUND
  Negative -> Negative : None, flag BOTH_NEGATIVE
  Zero base            : None, flag ZERO_BASE
  Insufficient years   : None, flag INSUFFICIENT

Every CAGR function returns a tuple: (cagr_value_or_None, flag_or_None)
so the caller can store both the value and the flag in separate DB columns
(e.g. revenue_cagr_5yr, revenue_cagr_5yr_flag).
"""


def compute_cagr(start_value, end_value, n_years):
    """
    Core CAGR calculation with full edge-case coverage.
    Returns (cagr_percent, flag). flag is None when the calculation succeeds.
    """
    if start_value is None or end_value is None or n_years is None or n_years <= 0:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    # Positive -> Positive (the only case where CAGR is mathematically meaningful)
    cagr = ((end_value / start_value) ** (1.0 / n_years) - 1) * 100
    return cagr, None


def _get_value_n_years_ago(series_by_year, target_year, n_years):
    """
    Helper: given a dict {year: value} (year as 'YYYY-MM' string) and a target
    end year, find the value from n_years before. Returns None if that year
    isn't present in the series (insufficient data).
    """
    try:
        end_yr = int(str(target_year)[:4])
    except (ValueError, TypeError):
        return None

    start_yr = end_yr - n_years
    for key in series_by_year:
        try:
            if int(str(key)[:4]) == start_yr:
                return series_by_year[key]
        except (ValueError, TypeError):
            continue
    return None


def revenue_cagr(series_by_year, latest_year, n_years):
    """
    Revenue CAGR for a given window (3, 5, or 10 years).
    series_by_year: dict of {year_str: sales_value} for one company.
    """
    if latest_year not in series_by_year:
        return None, "INSUFFICIENT"

    start_value = _get_value_n_years_ago(series_by_year, latest_year, n_years)
    if start_value is None:
        return None, "INSUFFICIENT"

    end_value = series_by_year[latest_year]
    return compute_cagr(start_value, end_value, n_years)


def pat_cagr(series_by_year, latest_year, n_years):
    """PAT (net profit) CAGR for a given window (3, 5, or 10 years)."""
    if latest_year not in series_by_year:
        return None, "INSUFFICIENT"

    start_value = _get_value_n_years_ago(series_by_year, latest_year, n_years)
    if start_value is None:
        return None, "INSUFFICIENT"

    end_value = series_by_year[latest_year]
    return compute_cagr(start_value, end_value, n_years)


def eps_cagr(series_by_year, latest_year, n_years):
    """EPS CAGR for a given window (3, 5, or 10 years)."""
    if latest_year not in series_by_year:
        return None, "INSUFFICIENT"

    start_value = _get_value_n_years_ago(series_by_year, latest_year, n_years)
    if start_value is None:
        return None, "INSUFFICIENT"

    end_value = series_by_year[latest_year]
    return compute_cagr(start_value, end_value, n_years)


def compute_all_cagr_windows(series_by_year, latest_year, windows=(3, 5, 10)):
    """
    Convenience wrapper: computes CAGR for all requested windows at once.
    Returns dict: {3: (value, flag), 5: (value, flag), 10: (value, flag)}
    Works for revenue, PAT, or EPS — pass whichever series_by_year you need.
    """
    return {n: revenue_cagr(series_by_year, latest_year, n) for n in windows}