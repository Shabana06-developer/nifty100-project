"""
scripts_run_validation.py
Runs all 16 DQ rules against nifty100.db and writes output/validation_failures.csv.
"""
from src.etl.validator import run_all_validations


DB_PATH = "nifty100.db"
OUTPUT = "output/validation_failures.csv"

print("Running 16 DQ rules against nifty100.db...\n")
results = run_all_validations(DB_PATH, check_live_urls=False)

if results.empty:
    print("\nAll 16 DQ rules passed. No violations.")
else:
    critical = results[results["severity"] == "CRITICAL"]
    warnings  = results[results["severity"] == "WARNING"]
    info      = results[results["severity"] == "INFO"]

    print(f"\nSummary:")
    print(f"  CRITICAL : {len(critical)}")
    print(f"  WARNING  : {len(warnings)}")
    print(f"  INFO     : {len(info)}")
    print(f"  TOTAL    : {len(results)}")

    results.to_csv(OUTPUT, index=False)
    print(f"\nvalidation_failures.csv written to {OUTPUT}")

    if not critical.empty:
        print("\n--- CRITICAL violations (must fix before Day 7) ---")
        print(critical[["rule_id","table","company_id","year","issue"]].to_string(index=False))