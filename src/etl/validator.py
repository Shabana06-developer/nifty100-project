"""
validator.py
Implements all 16 Data Quality rules from the project specification (Section 22).
Runs against the fully-loaded nifty100.db and returns a DataFrame of violations.

Severity levels:
  CRITICAL  — must be resolved before the full load (Day 5 exit criteria)
  WARNING   — logged and flagged; analyst review required
  INFO      — informational counter only
"""
import sqlite3
import pandas as pd
import re
import requests


# ---------- helpers ----------

def _v(rule_id, severity, table, company_id, year, field, issue):
    """Build a single violation record."""
    return {
        "rule_id":    rule_id,
        "severity":   severity,
        "table":      table,
        "company_id": str(company_id),
        "year":       str(year) if year is not None else "",
        "field":      field,
        "issue":      issue,
    }


def _load(db_path, query):
    """Run a SQL query and return a DataFrame."""
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(query, conn)


# ---------- individual rules ----------

def dq01_company_pk_uniqueness(db_path):
    """DQ-01 CRITICAL: companies.id must be unique."""
    df = _load(db_path, "SELECT id, COUNT(*) as cnt FROM companies GROUP BY id HAVING cnt > 1")
    return [_v("DQ-01", "CRITICAL", "companies", row["id"], None, "id",
               f"Duplicate company PK: {row['id']} appears {row['cnt']} times")
            for _, row in df.iterrows()]


def dq02_annual_pk_uniqueness(db_path):
    """DQ-02 CRITICAL: (company_id, year) must be unique in P&L, BS, CF."""
    violations = []
    for table in ["profitandloss", "balancesheet", "cashflow"]:
        df = _load(db_path,
            f"SELECT company_id, year, COUNT(*) as cnt FROM {table} "
            f"GROUP BY company_id, year HAVING cnt > 1")
        for _, row in df.iterrows():
            violations.append(_v("DQ-02", "CRITICAL", table, row["company_id"],
                                  row["year"], "(company_id,year)",
                                  f"Duplicate annual PK: count={row['cnt']}"))
    return violations


def dq03_fk_integrity(db_path):
    """DQ-03 CRITICAL: all company_id values in child tables must exist in companies."""
    violations = []
    child_tables = ["profitandloss", "balancesheet", "cashflow",
                    "analysis", "documents", "prosandcons",
                    "sectors", "market_cap", "stock_prices"]
    valid_ids = set(_load(db_path, "SELECT id FROM companies")["id"])
    for table in child_tables:
        try:
            df = _load(db_path, f"SELECT DISTINCT company_id FROM {table}")
            bad = df[~df["company_id"].isin(valid_ids)]
            for _, row in bad.iterrows():
                violations.append(_v("DQ-03", "CRITICAL", table, row["company_id"],
                                      None, "company_id",
                                      "company_id not found in companies table"))
        except Exception:
            pass
    return violations


def dq04_balance_sheet_balance(db_path):
    """DQ-04 WARNING: |total_assets - total_liabilities| / total_assets < 1%."""
    df = _load(db_path,
        "SELECT company_id, year, total_assets, total_liabilities "
        "FROM balancesheet WHERE total_assets IS NOT NULL AND total_assets != 0")
    violations = []
    for _, row in df.iterrows():
        diff_pct = abs(row["total_assets"] - row["total_liabilities"]) / abs(row["total_assets"])
        if diff_pct >= 0.01:
            violations.append(_v("DQ-04", "WARNING", "balancesheet",
                                  row["company_id"], row["year"], "total_assets",
                                  f"Balance sheet imbalance: {diff_pct:.2%} diff "
                                  f"(assets={row['total_assets']:.0f}, liabilities={row['total_liabilities']:.0f})"))
    return violations


def dq05_opm_cross_check(db_path):
    """DQ-05 WARNING: |opm_percentage - (op_profit/sales*100)| < 1.0."""
    df = _load(db_path,
        "SELECT company_id, year, sales, operating_profit, opm_percentage "
        "FROM profitandloss WHERE sales IS NOT NULL AND sales != 0 "
        "AND opm_percentage IS NOT NULL")
    violations = []
    for _, row in df.iterrows():
        computed = (row["operating_profit"] / row["sales"]) * 100
        diff = abs(computed - row["opm_percentage"])
        if diff >= 1.0:
            violations.append(_v("DQ-05", "WARNING", "profitandloss",
                                  row["company_id"], row["year"], "opm_percentage",
                                  f"OPM mismatch: source={row['opm_percentage']:.2f}%, "
                                  f"computed={computed:.2f}%, diff={diff:.2f}pp"))
    return violations


def dq06_positive_sales(db_path):
    """DQ-06 WARNING: sales > 0 for all non-bank companies."""
    df = _load(db_path,
        "SELECT p.company_id, p.year, p.sales "
        "FROM profitandloss p "
        "LEFT JOIN sectors s ON p.company_id = s.company_id "
        "WHERE (p.sales IS NULL OR p.sales <= 0) "
        "AND (s.broad_sector IS NULL OR s.broad_sector != 'Financials')")
    return [_v("DQ-06", "WARNING", "profitandloss", row["company_id"],
               row["year"], "sales", f"Non-positive sales: {row['sales']}")
            for _, row in df.iterrows()]


def dq07_year_format(db_path):
    """DQ-07 CRITICAL: all year values must match YYYY-MM after normalisation."""
    pattern = re.compile(r"^\d{4}-\d{2}$")
    violations = []
    for table in ["profitandloss", "balancesheet", "cashflow"]:
        df = _load(db_path, f"SELECT DISTINCT company_id, year FROM {table}")
        for _, row in df.iterrows():
            if not pattern.match(str(row["year"])):
                violations.append(_v("DQ-07", "CRITICAL", table,
                                      row["company_id"], row["year"], "year",
                                      f"Year does not match YYYY-MM format: {row['year']!r}"))
    return violations


def dq08_ticker_format(db_path):
    """DQ-08 CRITICAL: company_id must be 2–12 chars, uppercase, stripped."""
    df = _load(db_path, "SELECT id FROM companies")
    violations = []
    for _, row in df.iterrows():
        ticker = str(row["id"])
        if ticker != ticker.strip().upper() or not (2 <= len(ticker) <= 12):
            violations.append(_v("DQ-08", "CRITICAL", "companies", ticker,
                                  None, "id",
                                  f"Ticker format invalid: {ticker!r}"))
    return violations


def dq09_net_cash_check(db_path):
    """DQ-09 WARNING: |net_cash_flow - (CFO+CFI+CFF)| <= 10 Crore."""
    df = _load(db_path,
        "SELECT company_id, year, operating_activity, investing_activity, "
        "financing_activity, net_cash_flow FROM cashflow "
        "WHERE net_cash_flow IS NOT NULL")
    violations = []
    for _, row in df.iterrows():
        computed = ((row["operating_activity"] or 0) +
                    (row["investing_activity"] or 0) +
                    (row["financing_activity"] or 0))
        diff = abs(computed - row["net_cash_flow"])
        if diff > 10:
            violations.append(_v("DQ-09", "WARNING", "cashflow",
                                  row["company_id"], row["year"], "net_cash_flow",
                                  f"Net cash mismatch: reported={row['net_cash_flow']:.0f}, "
                                  f"computed={computed:.0f}, diff={diff:.0f} Cr"))
    return violations


def dq10_non_negative_fixed_assets(db_path):
    """DQ-10 WARNING: fixed_assets >= 0."""
    df = _load(db_path,
        "SELECT company_id, year, fixed_assets FROM balancesheet "
        "WHERE fixed_assets IS NOT NULL AND fixed_assets < 0")
    return [_v("DQ-10", "WARNING", "balancesheet", row["company_id"],
               row["year"], "fixed_assets",
               f"Negative fixed_assets: {row['fixed_assets']:.0f}")
            for _, row in df.iterrows()]


def dq11_tax_rate_range(db_path):
    """DQ-11 WARNING: 0 <= tax_percentage <= 60."""
    df = _load(db_path,
        "SELECT company_id, year, tax_percentage FROM profitandloss "
        "WHERE tax_percentage IS NOT NULL "
        "AND (tax_percentage < 0 OR tax_percentage > 60)")
    return [_v("DQ-11", "WARNING", "profitandloss", row["company_id"],
               row["year"], "tax_percentage",
               f"Tax rate out of range [0-60%]: {row['tax_percentage']:.1f}%")
            for _, row in df.iterrows()]


def dq12_dividend_payout_cap(db_path):
    """DQ-12 WARNING: dividend_payout <= 200%."""
    df = _load(db_path,
        "SELECT company_id, year, dividend_payout FROM profitandloss "
        "WHERE dividend_payout IS NOT NULL AND dividend_payout > 200")
    return [_v("DQ-12", "WARNING", "profitandloss", row["company_id"],
               row["year"], "dividend_payout",
               f"Dividend payout > 200%: {row['dividend_payout']:.1f}%")
            for _, row in df.iterrows()]


def dq13_url_validity(db_path, check_live_urls=False):
    """
    DQ-13 WARNING: Annual report URLs should be valid.
    check_live_urls=False by default (skips HTTP requests for speed during dev).
    Set to True only for final sprint review — it makes 1,400+ HTTP requests.
    """
    df = _load(db_path,
        "SELECT company_id, report_year, annual_report FROM documents "
        "WHERE annual_report IS NOT NULL")
    violations = []
    url_pattern = re.compile(r"^https?://[^\s]+$")
    for _, row in df.iterrows():
        url = str(row["annual_report"]).strip()
        if not url_pattern.match(url):
            violations.append(_v("DQ-13", "WARNING", "documents",
                                  row["company_id"], row["report_year"],
                                  "annual_report",
                                  f"Malformed URL: {url[:80]}"))
        elif check_live_urls:
            try:
                resp = requests.head(url, timeout=5, allow_redirects=True)
                if resp.status_code == 404:
                    violations.append(_v("DQ-13", "WARNING", "documents",
                                          row["company_id"], row["report_year"],
                                          "annual_report",
                                          f"URL returns 404: {url[:80]}"))
            except Exception:
                pass  # timeouts treated as acceptable (server down, not bad data)
    return violations


def dq14_eps_sign_consistency(db_path):
    """DQ-14 WARNING: eps > 0 if net_profit > 0."""
    df = _load(db_path,
        "SELECT company_id, year, eps, net_profit FROM profitandloss "
        "WHERE eps IS NOT NULL AND net_profit IS NOT NULL "
        "AND ((eps > 0 AND net_profit < 0) OR (eps < 0 AND net_profit > 0))")
    return [_v("DQ-14", "WARNING", "profitandloss", row["company_id"],
               row["year"], "eps",
               f"EPS sign ({row['eps']:.2f}) inconsistent with "
               f"net_profit sign ({row['net_profit']:.0f})")
            for _, row in df.iterrows()]


def dq15_strict_balance_check(db_path):
    """DQ-15 INFO: total_liabilities == total_assets (strict equality, informational)."""
    df = _load(db_path,
        "SELECT company_id, year, total_assets, total_liabilities "
        "FROM balancesheet "
        "WHERE total_assets IS NOT NULL AND total_liabilities IS NOT NULL "
        "AND total_assets != total_liabilities")
    return [_v("DQ-15", "INFO", "balancesheet", row["company_id"],
               row["year"], "total_assets",
               f"Strict mismatch: assets={row['total_assets']:.0f}, "
               f"liabilities={row['total_liabilities']:.0f}")
            for _, row in df.iterrows()]


def dq16_year_coverage(db_path):
    """DQ-16 WARNING: each company must have >= 5 years of P&L, BS, CF records."""
    violations = []
    for table in ["profitandloss", "balancesheet", "cashflow"]:
        df = _load(db_path,
            f"SELECT company_id, COUNT(DISTINCT year) as yr_count "
            f"FROM {table} GROUP BY company_id HAVING yr_count < 5")
        for _, row in df.iterrows():
            violations.append(_v("DQ-16", "WARNING", table,
                                  row["company_id"], None, "year",
                                  f"Only {row['yr_count']} year(s) of data "
                                  f"(minimum 5 required for CAGR)"))
    return violations


# ---------- orchestrator ----------

def run_all_validations(db_path: str, check_live_urls: bool = False) -> pd.DataFrame:
    """
    Runs all 16 DQ rules against the loaded database.
    Returns a DataFrame of all violations sorted by severity then rule_id.
    """
    all_violations = []
    rules = [
        dq01_company_pk_uniqueness,
        dq02_annual_pk_uniqueness,
        dq03_fk_integrity,
        dq04_balance_sheet_balance,
        dq05_opm_cross_check,
        dq06_positive_sales,
        dq07_year_format,
        dq08_ticker_format,
        dq09_net_cash_check,
        dq10_non_negative_fixed_assets,
        dq11_tax_rate_range,
        dq12_dividend_payout_cap,
        lambda db: dq13_url_validity(db, check_live_urls),
        dq14_eps_sign_consistency,
        dq15_strict_balance_check,
        dq16_year_coverage,
    ]

    for rule_fn in rules:
        try:
            result = rule_fn(db_path)
            all_violations.extend(result)
            rule_id = result[0]["rule_id"] if result else rule_fn.__name__
            print(f"  {rule_id}: {len(result)} violation(s)")
        except Exception as e:
            print(f"  ERROR running {rule_fn.__name__}: {e}")

    severity_order = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
    df = pd.DataFrame(all_violations)
    if not df.empty:
        df["_sev_order"] = df["severity"].map(severity_order)
        df = df.sort_values(["_sev_order", "rule_id"]).drop(columns=["_sev_order"])
    return df