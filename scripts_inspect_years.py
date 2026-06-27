from src.etl.loader import load_core_file

for table_name in ["profitandloss", "balancesheet", "cashflow"]:
    df = load_core_file(table_name)
    unique_years = sorted(df["year"].astype(str).unique())
    print(f"\n--- {table_name} ({len(unique_years)} unique year values) ---")
    for y in unique_years:
        print(repr(y))