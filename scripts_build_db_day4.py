import os
import pandas as pd
from src.etl.loader import load_core_file
from src.etl.normaliser import normalize_ticker, normalize_year_column
from db.loader import create_database, insert_dataframe, check_foreign_keys, get_table_row_count

DB_PATH = "nifty100.db"
all_rejected = []  # collects rejected rows across all tables for parse_failures.csv

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

create_database(DB_PATH)
print("Database created from schema.sql")

# --- companies (no year column) ---
companies = load_core_file("companies")
companies["id"] = companies["id"].apply(normalize_ticker)
insert_dataframe(DB_PATH, "companies", companies)
print(f"Inserted companies: {get_table_row_count(DB_PATH, 'companies')} rows")


def load_clean_and_insert(table_name: str, valid_company_ids: set):
    df = load_core_file(table_name)

    # TTM is a rolling window, not a fiscal year — exclude before normalizing
    is_ttm = df["year"].astype(str).str.strip().str.upper() == "TTM"
    ttm_count = is_ttm.sum()
    df = df[~is_ttm].copy()

    df["company_id"] = df["company_id"].apply(normalize_ticker)
    clean_df, rejected_df = normalize_year_column(df, "year")

    if len(rejected_df) > 0:
        rejected_df["source_table"] = table_name
        all_rejected.append(rejected_df[["source_table", "company_id", "raw_year_value"]])

    # --- deduplicate on (company_id, year), keep last occurrence ---
    dupe_mask = clean_df.duplicated(subset=["company_id", "year"], keep=False)
    duplicate_count = dupe_mask.sum()
    if duplicate_count > 0:
        print(f"  Found {duplicate_count} duplicate (company_id, year) rows in {table_name}:")
        print(clean_df.loc[dupe_mask, ["company_id", "year"]].sort_values(["company_id", "year"]).to_string(index=False))
    clean_df = clean_df.drop_duplicates(subset=["company_id", "year"], keep="last")

    # --- NEW: filter out FK-orphan rows (company_id not in companies table) ---
    orphan_mask = ~clean_df["company_id"].isin(valid_company_ids)
    orphan_count = orphan_mask.sum()
    if orphan_count > 0:
        orphans = clean_df.loc[orphan_mask, ["company_id", "year"]].copy()
        orphans["source_table"] = table_name
        orphans["raw_year_value"] = "N/A (orphan FK - company not in 92-company universe)"
        all_rejected.append(orphans[["source_table", "company_id", "raw_year_value"]])
        print(f"  Excluded {orphan_count} orphan rows in {table_name} "
              f"(company_ids not in companies table: {sorted(clean_df.loc[orphan_mask, 'company_id'].unique())})")
    clean_df = clean_df[~orphan_mask].copy()
    # ---------------------------------------------------------------------------

    try:
        insert_dataframe(DB_PATH, table_name, clean_df)
    except Exception as e:
        print(f"\n!!! INSERT FAILED for table '{table_name}' !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e}")
        print(f"Underlying cause: {e.__cause__}")
        raise

    print(f"Inserted {table_name}: {get_table_row_count(DB_PATH, table_name)} rows "
          f"(excluded {ttm_count} TTM rows, rejected {len(rejected_df)} unparseable rows, "
          f"removed {duplicate_count} duplicate rows, excluded {orphan_count} orphan rows)")
    

    # --- Run the full load for all 3 time-series tables ---
valid_company_ids = set(companies["id"])

for table in ["profitandloss", "balancesheet", "cashflow"]:
    print(f">>> Starting table: {table}", flush=True)
    load_clean_and_insert(table, valid_company_ids)
    print(f">>> Finished table: {table}", flush=True)

# --- write rejected rows to output/parse_failures.csv ---
if all_rejected:
    combined = pd.concat(all_rejected, ignore_index=True)
    combined.to_csv("output/parse_failures.csv", index=False)
    print(f"\n{len(combined)} rows logged to output/parse_failures.csv")

# --- FK check ---
violations = check_foreign_keys(DB_PATH)
print(f"\nForeign key violations: {len(violations)}")
if violations:
    print(violations[:5])