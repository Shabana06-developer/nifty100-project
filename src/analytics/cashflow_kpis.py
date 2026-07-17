"""
cashflow_kpis.py
Cash Flow KPIs & Capital Allocation Classifier.

Uses: cashflow.operating_activity, cashflow.investing_activity,
      cashflow.financing_activity, profitandloss.net_profit (PAT),
      profitandloss.sales, profitandloss.operating_profit
"""


# ---------------------------------------------------------------------
# Free Cash Flow
# ---------------------------------------------------------------------

def free_cash_flow(operating_activity, investing_activity):
    """FCF = operating_activity + investing_activity. Negative FCF is allowed."""
    if operating_activity is None or investing_activity is None:
        return None
    return operating_activity + investing_activity


# ---------------------------------------------------------------------
# CFO Quality Score — CFO/PAT ratio averaged over 5 years
# ---------------------------------------------------------------------

def cfo_quality_score(cfo_values, pat_values):
    """
    CFO Quality Score = average(CFO / PAT) over the years provided.
    cfo_values, pat_values: lists of matching-length yearly values (same order).
    Classification: >1.0 = High Quality, 0.5-1.0 = Moderate, <0.5 = Accrual Risk.
    Returns (avg_ratio, label). Returns (None, None) if any PAT = 0 or lists empty/mismatched.
    """
    if not cfo_values or not pat_values or len(cfo_values) != len(pat_values):
        return None, None

    ratios = []
    for cfo, pat in zip(cfo_values, pat_values):
        if cfo is None or pat is None or pat == 0:
            return None, None
        ratios.append(cfo / pat)

    avg_ratio = sum(ratios) / len(ratios)

    if avg_ratio > 1.0:
        label = "High Quality"
    elif avg_ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return avg_ratio, label


# ---------------------------------------------------------------------
# CapEx Intensity
# ---------------------------------------------------------------------

def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity = abs(investing_activity) / sales * 100.
    Classification: <3% = Asset Light, 3-8% = Moderate, >8% = Capital Intensive.
    Returns (pct, label). None if sales = 0.
    """
    if investing_activity is None or sales is None or sales == 0:
        return None, None

    pct = abs(investing_activity) / sales * 100

    if pct < 3:
        label = "Asset Light"
    elif pct <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return pct, label


# ---------------------------------------------------------------------
# FCF Conversion Rate
# ---------------------------------------------------------------------

def fcf_conversion_rate(fcf, operating_profit):
    """FCF Conversion = FCF / operating_profit * 100. None if operating_profit = 0."""
    if fcf is None or operating_profit is None or operating_profit == 0:
        return None
    return (fcf / operating_profit) * 100


# ---------------------------------------------------------------------
# Capital Allocation 8-Pattern Classifier
# ---------------------------------------------------------------------

_PATTERN_LABELS = {
    ("+", "-", "-"): "Reinvestor",
    ("+", "-", "-", "high_cfo_pat"): "Shareholder Returns",  # special-cased below
    ("+", "+", "-"): "Liquidating Assets",
    ("-", "+", "+"): "Distress Signal",
    ("-", "-", "+"): "Growth Funded by Debt",
    ("+", "+", "+"): "Cash Accumulator",
    ("-", "-", "-"): "Pre-Revenue",
    ("+", "-", "+"): "Mixed",
}


def _sign(value):
    """Returns '+' , '-', or None."""
    if value is None:
        return None
    if value > 0:
        return "+"
    if value < 0:
        return "-"
    return "+"  # treat exactly zero as non-negative for classification purposes


def capital_allocation_pattern(cfo, cfi, cff, cfo_to_pat_ratio=None, high_cfo_pat_threshold=1.0):
    """
    Classifies capital allocation strategy based on sign of (CFO, CFI, CFF).
    Pattern labels:
      (+,-,-) = Reinvestor
      (+,-,-) with high CFO/PAT = Shareholder Returns
      (+,+,-) = Liquidating Assets
      (-,+,+) = Distress Signal
      (-,-,+) = Growth Funded by Debt
      (+,+,+) = Cash Accumulator
      (-,-,-) = Pre-Revenue
      (+,-,+) = Mixed
    Returns: (cfo_sign, cfi_sign, cff_sign, pattern_label)
    """
    cfo_s = _sign(cfo)
    cfi_s = _sign(cfi)
    cff_s = _sign(cff)

    if cfo_s is None or cfi_s is None or cff_s is None:
        return cfo_s, cfi_s, cff_s, None

    key = (cfo_s, cfi_s, cff_s)

    # Special case: (+,-,-) can be either Reinvestor or Shareholder Returns
    if key == ("+", "-", "-"):
        if cfo_to_pat_ratio is not None and cfo_to_pat_ratio > high_cfo_pat_threshold:
            return cfo_s, cfi_s, cff_s, "Shareholder Returns"
        return cfo_s, cfi_s, cff_s, "Reinvestor"

    label = _PATTERN_LABELS.get(key, "Mixed")
    return cfo_s, cfi_s, cff_s, label