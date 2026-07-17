"""
scripts_build_financial_ratios.py
Sprint 2, Day 12 — Populates the financial_ratios table for all 92 companies
across all available years, using src/analytics/ratios.py, cagr.py, and
cashflow_kpis.py.

Run with: python scripts_build_financial_ratios.py
"""
import sqlite3
import pandas as pd

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
from src.analytics.cagr import compute_cagr
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

DB_PATH = "nifty100.db"


def year_to_int(year_str):
    """Extract the leading YYYY as int from 'YYYY-MM' strings."""
    try:
        return int(str(year_str)[:4])
    except (ValueError, TypeError):
        return None


def build_cagr_for_all_windows(series_by_year, latest_year_int, prefix, results_row):
    """
    Computes 3/5/10-yr CAGR for a given series (revenue, pat, or eps) and writes
    value + flag into results_row under keys like f"{prefix}_cagr_5yr".
    series_by_year: dict {year_int: value}
    """
    for window in (3, 5, 10):
        start_yr = latest_year_int - window
        start_val = series_by_year.get(start_yr)
        end_val = series_by_year.get(latest_year_int)
        cagr, flag = compute_cagr(start_val, end_val, window)
        results_row[f"{prefix}_cagr_{window}yr"] = cagr
        results_row[f"{prefix}_cagr_{window}yr_flag"] = flag


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    companies = pd.read_sql_query("SELECT id, book_value FROM companies", conn)
    sectors = pd.read_sql_query("SELECT company_id, broad_sector FROM sectors", conn)
    pnl = pd.read_sql_query(
        "SELECT company_id, year, sales, operating_profit, opm_percentage, "
        "other_income, interest, profit_before_tax, net_profit, eps, "
        "dividend_payout FROM profitandloss", conn)
    bs = pd.read_sql_query(
        "SELECT company_id, year, equity_capital, reserves, borrowings, "
        "investments, total_assets FROM balancesheet", conn)
    cf = pd.read_sql_query(
        "SELECT company_id, year, operating_activity, investing_activity, "
        "financing_activity FROM cashflow", conn)

    financials_set = set(sectors[sectors["broad_sector"] == "Financials"]["company_id"])
    book_value_map = dict(zip(companies["id"], companies["book_value"]))

    rows_to_insert = []
    skipped = 0

    for company_id in companies["id"]:
        is_financials = company_id in financials_set

        pnl_c = pnl[pnl["company_id"] == company_id].copy()
        bs_c = bs[bs["company_id"] == company_id].copy()
        cf_c = cf[cf["company_id"] == company_id].copy()

        if pnl_c.empty:
            skipped += 1
            continue

        # Build year -> value series for CAGR (sales, net_profit, eps)
        sales_series = {}
        pat_series = {}
        eps_series = {}
        for _, r in pnl_c.iterrows():
            yr_int = year_to_int(r["year"])
            if yr_int is None:
                continue
            sales_series[yr_int] = r["sales"]
            pat_series[yr_int] = r["net_profit"]
            eps_series[yr_int] = r["eps"]

        # CFO/PAT list for cfo_quality_score (needs 5 years, matched by year)
        merged = pnl_c.merge(bs_c, on=["company_id", "year"], how="left") \
                       .merge(cf_c, on=["company_id", "year"], how="left")

        for _, r in merged.iterrows():
            year = r["year"]
            yr_int = year_to_int(year)
            row = {"company_id": company_id, "year": year}

            sales = r.get("sales")
            operating_profit = r.get("operating_profit")
            opm_percentage = r.get("opm_percentage")
            other_income = r.get("other_income")
            interest = r.get("interest")
            profit_before_tax = r.get("profit_before_tax")
            net_profit = r.get("net_profit")
            eps = r.get("eps")
            dividend_payout = r.get("dividend_payout")

            equity_capital = r.get("equity_capital")
            reserves = r.get("reserves")
            borrowings = r.get("borrowings")
            investments = r.get("investments")
            total_assets = r.get("total_assets")

            operating_activity = r.get("operating_activity")
            investing_activity = r.get("investing_activity")
            financing_activity = r.get("financing_activity")

            # --- Profitability ---
            row["net_profit_margin_pct"] = net_profit_margin(net_profit, sales)
            opm_computed, opm_mismatch = operating_profit_margin(
                operating_profit, sales, opm_percentage)
            row["operating_profit_margin_pct"] = opm_computed
            row["return_on_equity_pct"] = return_on_equity(net_profit, equity_capital, reserves)
            ebit = compute_ebit(profit_before_tax, interest)
            row["return_on_capital_employed_pct"] = return_on_capital_employed(
                ebit, equity_capital, reserves, borrowings, is_financials)
            row["return_on_assets_pct"] = return_on_assets(net_profit, total_assets)

            # --- Leverage & Efficiency ---
            de, high_leverage = debt_to_equity(
                borrowings, equity_capital, reserves, is_financials)
            row["debt_to_equity"] = de
            row["high_leverage_flag"] = int(high_leverage) if high_leverage is not None else None
            icr, icr_label, icr_warn = interest_coverage_ratio(operating_profit, other_income, interest)
            row["interest_coverage"] = icr
            row["icr_label"] = icr_label
            row["icr_warning_flag"] = int(icr_warn) if icr_warn is not None else None
            row["net_debt_cr"] = net_debt(borrowings, investments)
            row["asset_turnover"] = asset_turnover(sales, total_assets)

            # --- Cash Flow KPIs ---
            fcf = free_cash_flow(operating_activity, investing_activity)
            row["free_cash_flow_cr"] = fcf
            row["capex_cr"] = investing_activity
            capex_pct, capex_label = capex_intensity(investing_activity, sales)
            row["capex_intensity_pct"] = capex_pct
            row["capex_intensity_label"] = capex_label
            row["fcf_conversion_rate_pct"] = fcf_conversion_rate(fcf, operating_profit)
            row["cash_from_operations_cr"] = operating_activity

            # cfo_quality_score needs a 5-year window ending at this year
            if yr_int is not None:
                cfo_vals, pat_vals = [], []
                for offset in range(5):
                    yr_lookup = yr_int - offset
                    cf_row = cf_c[cf_c["year"].astype(str).str.startswith(str(yr_lookup))]
                    pnl_row = pnl_c[pnl_c["year"].astype(str).str.startswith(str(yr_lookup))]
                    if not cf_row.empty and not pnl_row.empty:
                        cfo_vals.append(cf_row.iloc[0]["operating_activity"])
                        pat_vals.append(pnl_row.iloc[0]["net_profit"])
                if len(cfo_vals) == 5:
                    from src.analytics.cashflow_kpis import cfo_quality_score
                    avg_ratio, label = cfo_quality_score(cfo_vals, pat_vals)
                else:
                    avg_ratio, label = None, None
            else:
                avg_ratio, label = None, None
            row["cfo_quality_score"] = avg_ratio
            row["cfo_quality_label"] = label

            # --- Capital Allocation ---
            cfo_to_pat = None
            if operating_activity is not None and net_profit not in (None, 0):
                cfo_to_pat = operating_activity / net_profit
            cfo_s, cfi_s, cff_s, pattern = capital_allocation_pattern(
                operating_activity, investing_activity, financing_activity, cfo_to_pat)
            row["cfo_sign"] = cfo_s
            row["cfi_sign"] = cfi_s
            row["cff_sign"] = cff_s
            row["capital_allocation_pattern"] = pattern

            # --- Growth / CAGR ---
            if yr_int is not None:
                build_cagr_for_all_windows(sales_series, yr_int, "revenue", row)
                build_cagr_for_all_windows(pat_series, yr_int, "pat", row)
                build_cagr_for_all_windows(eps_series, yr_int, "eps", row)
            else:
                for prefix in ("revenue", "pat", "eps"):
                    for window in (3, 5, 10):
                        row[f"{prefix}_cagr_{window}yr"] = None
                        row[f"{prefix}_cagr_{window}yr_flag"] = "INSUFFICIENT"

            # --- Per-share / valuation-adjacent ---
            row["earnings_per_share"] = eps
            row["book_value_per_share"] = book_value_map.get(company_id)
            row["dividend_payout_ratio_pct"] = dividend_payout
            row["total_debt_cr"] = borrowings

            # --- Composite quality score (simple average of normalized signals) ---
            quality_components = [v for v in [
                row["return_on_equity_pct"],
                row["cfo_quality_score"] * 50 if row["cfo_quality_score"] is not None else None,
                (100 - row["debt_to_equity"] * 10) if row["debt_to_equity"] is not None else None,
            ] if v is not None]
            row["composite_quality_score"] = (
                sum(quality_components) / len(quality_components) if quality_components else None
            )

            rows_to_insert.append(row)

    # --- Insert into DB ---
    if not rows_to_insert:
        print("No rows to insert.")
        return

    columns = list(rows_to_insert[0].keys())
    placeholders = ", ".join(["?"] * len(columns))
    col_names = ", ".join(columns)
    sql = f"INSERT OR REPLACE INTO financial_ratios ({col_names}) VALUES ({placeholders})"

    values = [tuple(row.get(c) for c in columns) for row in rows_to_insert]

    cur = conn.cursor()
    cur.executemany(sql, values)
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    print(f"Inserted/updated {len(rows_to_insert)} rows.")
    print(f"Companies skipped (no P&L data): {skipped}")
    print(f"Total rows now in financial_ratios: {total}")

    conn.close()


if __name__ == "__main__":
    main()