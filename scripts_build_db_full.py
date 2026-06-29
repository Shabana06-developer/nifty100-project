"""
scripts_build_db_full.py
Builds nifty100.db from scratch, loading all 12 source files into the
correct 10 SQLite tables. Generates output/load_audit.csv and
output/parse_failures.csv as a complete record of what happened to every row.
"""
import os
import time
import pandas as pd
from datetime import datetime

from src.etl.loader import load_core_file, load_supplementary_file
from src.etl.normaliser import normalize_ticker, normalize_year_column
from db.loader import create_database, insert_dataframe, check_foreign_keys, get_table_row_count

DB_PATH = "nifty100.db"
audit_records = []
all_rejected = []


def record_audit(table_name, rows_in, rows_out, rejected, runtime_s):
    audit_records.append({
        "table": table_name,
        "rows_in": rows_in,
        "rows_out": rows_out,
        "rejected": rejected,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "runtime_s": round(runtime_s, 3),
    })


def log_rejected(table_name, df, reason):
    if len(df) == 0:
        return
    out = df.copy()
    out["source_table"] = table_name
    out["reason"] = reason
    all_rejected.append(out)


# ---------------------------------------------------------------------------
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
create_database(DB_PATH)
print("Database created from schema.sql\n")

# ===== 1. companies (no FK, no year) =====
t0 = time.time()
companies = load_core_file("companies")
rows_in = len(companies)
companies["id"] = companies["id"].apply(normalize_ticker)
companies = companies.drop_duplicates(subset=["id"], keep="last")
insert_dataframe(DB_PATH, "companies", companies)
rows_out = get_table_row_count(DB_PATH, "companies")
record_audit("companies", rows_in, rows_out, rows_in - rows_out, time.time() - t0)
print(f"companies: {rows_out} rows")

valid_ids = set(companies["id"])


# ===== Generic helper for tables with (company_id, year) composite keys =====
def load_year_table(table_name, loader_func, **loader_kwargs):
    t0 = time.time()
    df = loader_func(table_name, **loader_kwargs)
    rows_in = len(df)

    is_ttm = df["year"].astype(str).str.strip().str.upper() == "TTM"
    df = df[~is_ttm].copy()

    df["company_id"] = df["company_id"].apply(normalize_ticker)
    clean_df, rejected_year_df = normalize_year_column(df, "year")
    log_rejected(table_name, rejected_year_df, "unparseable year (stub/interim period)")

    dupe_mask = clean_df.duplicated(subset=["company_id", "year"], keep=False)
    log_rejected(table_name, clean_df[dupe_mask], "duplicate (company_id, year) - kept last")
    clean_df = clean_df.drop_duplicates(subset=["company_id", "year"], keep="last")

    orphan_mask = ~clean_df["company_id"].isin(valid_ids)
    log_rejected(table_name, clean_df[orphan_mask], "company_id not in companies table")
    clean_df = clean_df[~orphan_mask].copy()

    insert_dataframe(DB_PATH, table_name, clean_df)
    rows_out = get_table_row_count(DB_PATH, table_name)
    record_audit(table_name, rows_in, rows_out, rows_in - rows_out, time.time() - t0)
    print(f"{table_name}: {rows_out} rows (rejected {rows_in - rows_out})")


# ===== 2-4. profitandloss, balancesheet, cashflow (already validated in Day 4) =====
for table in ["profitandloss", "balancesheet", "cashflow"]:
    load_year_table(table, load_core_file)


# ===== 5. analysis (no year, partial coverage expected) =====
t0 = time.time()
analysis = load_core_file("analysis")
rows_in = len(analysis)
analysis["company_id"] = analysis["company_id"].apply(normalize_ticker)
orphan_mask = ~analysis["company_id"].isin(valid_ids)
log_rejected("analysis", analysis[orphan_mask], "company_id not in companies table")
analysis = analysis[~orphan_mask].copy()
insert_dataframe(DB_PATH, "analysis", analysis)
rows_out = get_table_row_count(DB_PATH, "analysis")
record_audit("analysis", rows_in, rows_out, rows_in - rows_out, time.time() - t0)
print(f"analysis: {rows_out} rows (partial coverage expected per spec)")


# ===== 6. documents (Year -> report_year, Annual_Report -> annual_report) =====
t0 = time.time()
documents = load_core_file("documents")
rows_in = len(documents)
documents = documents.rename(columns={"Year": "report_year", "Annual_Report": "annual_report"})
documents["company_id"] = documents["company_id"].apply(normalize_ticker)
orphan_mask = ~documents["company_id"].isin(valid_ids)
log_rejected("documents", documents[orphan_mask], "company_id not in companies table")
documents = documents[~orphan_mask].copy()
insert_dataframe(DB_PATH, "documents", documents)
rows_out = get_table_row_count(DB_PATH, "documents")
record_audit("documents", rows_in, rows_out, rows_in - rows_out, time.time() - t0)
print(f"documents: {rows_out} rows (partial coverage expected per spec)")


# ===== 7. prosandcons (no year, partial coverage expected) =====
t0 = time.time()
prosandcons = load_core_file("prosandcons")
rows_in = len(prosandcons)
prosandcons["company_id"] = prosandcons["company_id"].apply(normalize_ticker)
orphan_mask = ~prosandcons["company_id"].isin(valid_ids)
log_rejected("prosandcons", prosandcons[orphan_mask], "company_id not in companies table")
prosandcons = prosandcons[~orphan_mask].copy()
insert_dataframe(DB_PATH, "prosandcons", prosandcons)
rows_out = get_table_row_count(DB_PATH, "prosandcons")
record_audit("prosandcons", rows_in, rows_out, rows_in - rows_out, time.time() - t0)
print(f"prosandcons: {rows_out} rows (partial coverage expected per spec)")


# ===== 8. sectors (no year, should cover all 92) =====
t0 = time.time()
sectors = load_supplementary_file("sectors")
rows_in = len(sectors)
sectors["company_id"] = sectors["company_id"].apply(normalize_ticker)
sectors = sectors.drop_duplicates(subset=["company_id"], keep="last")
orphan_mask = ~sectors["company_id"].isin(valid_ids)
log_rejected("sectors", sectors[orphan_mask], "company_id not in companies table")
sectors = sectors[~orphan_mask].copy()

# Keep only columns that exist in our schema (drop stray extras like 'id')
expected_cols = ["company_id", "broad_sector", "sub_sector", "index_weight_pct", "market_cap_category"]
sectors = sectors[[c for c in expected_cols if c in sectors.columns]]

insert_dataframe(DB_PATH, "sectors", sectors)
rows_out = get_table_row_count(DB_PATH, "sectors")
record_audit("sectors", rows_in, rows_out, rows_in - rows_out, time.time() - t0)
print(f"sectors: {rows_out} rows")





# ===== 9. market_cap (plain calendar year, no FY parsing needed) =====
t0 = time.time()
market_cap = load_supplementary_file("market_cap")
rows_in = len(market_cap)
market_cap["company_id"] = market_cap["company_id"].apply(normalize_ticker)
market_cap = market_cap.drop_duplicates(subset=["company_id", "year"], keep="last")
orphan_mask = ~market_cap["company_id"].isin(valid_ids)
log_rejected("market_cap", market_cap[orphan_mask], "company_id not in companies table")
market_cap = market_cap[~orphan_mask].copy()

expected_cols = ["company_id", "year", "market_cap_crore", "enterprise_value_crore",
                  "pe_ratio", "pb_ratio", "ev_ebitda", "dividend_yield_pct"]
market_cap = market_cap[[c for c in expected_cols if c in market_cap.columns]]

insert_dataframe(DB_PATH, "market_cap", market_cap)
rows_out = get_table_row_count(DB_PATH, "market_cap")
record_audit("market_cap", rows_in, rows_out, rows_in - rows_out, time.time() - t0)
print(f"market_cap: {rows_out} rows")


# ===== 10. stock_prices (company_id, date composite key) =====
t0 = time.time()
stock_prices = load_supplementary_file("stock_prices")
rows_in = len(stock_prices)
stock_prices["company_id"] = stock_prices["company_id"].apply(normalize_ticker)
stock_prices = stock_prices.drop_duplicates(subset=["company_id", "date"], keep="last")
orphan_mask = ~stock_prices["company_id"].isin(valid_ids)
log_rejected("stock_prices", stock_prices[orphan_mask], "company_id not in companies table")
stock_prices = stock_prices[~orphan_mask].copy()

expected_cols = ["company_id", "date", "open_price", "high_price", "low_price",
                  "close_price", "volume", "adjusted_close"]
stock_prices = stock_prices[[c for c in expected_cols if c in stock_prices.columns]]

insert_dataframe(DB_PATH, "stock_prices", stock_prices)
rows_out = get_table_row_count(DB_PATH, "stock_prices")
record_audit("stock_prices", rows_in, rows_out, rows_in - rows_out, time.time() - t0)
print(f"stock_prices: {rows_out} rows")


# ===== Write load_audit.csv =====
audit_df = pd.DataFrame(audit_records)
audit_df.to_csv("output/load_audit.csv", index=False)
print(f"\nload_audit.csv written with {len(audit_df)} table records")

# ===== Write parse_failures.csv (rejected rows across all tables) =====
if all_rejected:
    combined = pd.concat(all_rejected, ignore_index=True)
    combined.to_csv("output/parse_failures.csv", index=False)
    print(f"{len(combined)} total rejected rows logged to output/parse_failures.csv")

# ===== Final FK integrity check =====
violations = check_foreign_keys(DB_PATH)
print(f"\nForeign key violations: {len(violations)}")
if violations:
    print(violations[:5])

print("\n--- Final table row counts ---")
for t in ["companies", "profitandloss", "balancesheet", "cashflow", "analysis",
          "documents", "prosandcons", "sectors", "market_cap", "stock_prices"]:
    print(f"  {t}: {get_table_row_count(DB_PATH, t)}")