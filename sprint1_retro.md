# Sprint 1 Retrospective — Nifty100 Data Foundation

**Sprint dates:** Day 1–7
**Goal:** Build a fully loaded, validated 10-table SQLite database (`nifty100.db`) from 12 Excel source files covering 92 Nifty 100 companies.
**Status: Complete**

## What we shipped
- 12 source Excel files (7 core + 5 supplementary) loaded via src/etl/loader.py
- Year/ticker normalisation (src/etl/normaliser.py) handling Mar-23, Mar 2023, FY23, TTM exclusion, stub-period rejection
- 10-table SQLite schema (db/schema.sql) with PK/FK constraints, zero FK violations
- 16 DQ rules (src/etl/validator.py) -> output/validation_failures.csv
- 41 unit tests passing (tests/etl/)
- output/load_audit.csv - per-table row counts and rejections
- notebooks/exploratory_queries.sql - 10 queries
- Manual spot-check of 5 companies (TCS, HDFCBANK, RELIANCE, SUNPHARMA, TATASTEEL)

Final row counts: companies=92, profitandloss~1276, balancesheet~1312, cashflow~1187, stock_prices~5520

## What went well
- Caught wrong dataset (mutual fund CSVs) early on Day 3
- Normaliser edge-case handling (TTM, stub periods, multiple date formats) was robust on real load
- Test coverage caught the loader.py/validator.py content-swap bug immediately

## What was harder than expected
- loader.py got accidentally overwritten with validator.py content during Day 6 edits - had to reconstruct load_excel_file(), load_core_file(), load_supplementary_file(), load_all_raw_files() from spec
- 8 tickers not in 92-company universe excluded as FK orphans
- ADANIPORTS had 24 duplicate (company_id, year) rows - deduped, keep-last
- PowerShell venv activation dropping between terminal sessions caused false "pytest not recognized" alarms
- sqlite3 CLI not installed - exploratory queries run via Python wrapper instead

## Process improvements for Sprint 2
- Save all open files before running tests
- Double check active tab/filename before pasting large code blocks
- Strip debug prints after first successful run

## Exit criteria check
- SELECT COUNT(*) FROM companies = 92: PASS
- PRAGMA foreign_key_check -> 0 rows: PASS
- load_audit.csv zero CRITICAL rejections: PASS
- 41 unit tests pass: PASS
- Manual review of 5 companies: PASS

Sprint 1: Done.
