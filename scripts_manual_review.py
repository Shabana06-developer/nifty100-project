"""
scripts_manual_review.py
Manually spot-checks 5 random companies across all time-series tables.
"""
import sqlite3
import pandas as pd

DB_PATH = "nifty100.db"

# Pick 5 companies spread across sectors
SPOT_CHECK_COMPANIES = ["TCS", "HDFCBANK", "RELIANCE", "SUNPHARMA", "TATASTEEL"]

conn = sqlite3.connect(DB_PATH)

for ticker in SPOT_CHECK_COMPANIES:
    print(f"\n{'='*60}")
    print(f"COMPANY: {ticker}")
    print(f"{'='*60}")

    # Basic info
    co = pd.read_sql_query(f"SELECT company_name, face_value, roce_percentage, roe_percentage FROM companies WHERE id='{ticker}'", conn)
    print(co.to_string(index=False))

    # Year coverage
    for table in ["profitandloss", "balancesheet", "cashflow"]:
        years = pd.read_sql_query(f"SELECT year FROM {table} WHERE company_id='{ticker}' ORDER BY year", conn)
        print(f"  {table}: {len(years)} years ({years['year'].min()} → {years['year'].max()})")

    # Latest P&L
    pl = pd.read_sql_query(
        f"SELECT year, sales, operating_profit, opm_percentage, net_profit, eps "
        f"FROM profitandloss WHERE company_id='{ticker}' ORDER BY year DESC LIMIT 3", conn)
    print("\n  Latest P&L (last 3 years):")
    print(pl.to_string(index=False))

    # Latest Balance Sheet
    bs = pd.read_sql_query(
        f"SELECT year, total_assets, total_liabilities, borrowings "
        f"FROM balancesheet WHERE company_id='{ticker}' ORDER BY year DESC LIMIT 1", conn)
    print("\n  Latest Balance Sheet:")
    print(bs.to_string(index=False))

conn.close()

print("\n\nSpot-check complete. Review the above for any obviously wrong values:")
print("  - Are sales figures in the expected ballpark for each company?")
print("  - Are year ranges reasonable (2010/2011 to 2023/2024)?")
print("  - Any NaN values in critical fields?")