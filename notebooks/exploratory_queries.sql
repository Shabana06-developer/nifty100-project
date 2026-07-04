-- ============================================================
-- exploratory_queries.sql
-- Nifty100 Data Foundation — Sprint 1, Day 7
-- 10 exploratory queries for sprint wrap-up and sanity review.
-- Run against nifty100.db (SQLite).
-- ============================================================


-- 1. Row counts across all 10 tables
-- Quick health check: confirms every table has data after the full load.
SELECT 'companies' AS table_name, COUNT(*) AS row_count FROM companies
UNION ALL SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL SELECT 'analysis', COUNT(*) FROM analysis
UNION ALL SELECT 'documents', COUNT(*) FROM documents
UNION ALL SELECT 'prosandcons', COUNT(*) FROM prosandcons
UNION ALL SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL SELECT 'market_cap', COUNT(*) FROM market_cap
UNION ALL SELECT 'stock_prices', COUNT(*) FROM stock_prices;


-- 2. Null counts on key financial fields in profitandloss
-- Surfaces how much missing data exists in the most-used table.
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS null_sales,
    SUM(CASE WHEN operating_profit IS NULL THEN 1 ELSE 0 END) AS null_operating_profit,
    SUM(CASE WHEN net_profit IS NULL THEN 1 ELSE 0 END) AS null_net_profit,
    SUM(CASE WHEN eps IS NULL THEN 1 ELSE 0 END) AS null_eps
FROM profitandloss;


-- 3. Year coverage per company (P&L)
-- How many distinct years of data each company has — flags thin coverage.
SELECT company_id, COUNT(DISTINCT year) AS years_covered,
       MIN(year) AS earliest_year, MAX(year) AS latest_year
FROM profitandloss
GROUP BY company_id
ORDER BY years_covered ASC;


-- 4. Companies with fewer than 5 years of P&L data
-- Cross-check against DQ-16 — should match validation_failures.csv.
SELECT company_id, COUNT(DISTINCT year) AS years_covered
FROM profitandloss
GROUP BY company_id
HAVING years_covered < 5;


-- 5. Top 10 companies by latest sales
-- Basic business-insight sanity check — do the big names show up as expected?
SELECT p.company_id, c.company_name, p.year, p.sales
FROM profitandloss p
JOIN companies c ON p.company_id = c.id
WHERE p.year = (SELECT MAX(year) FROM profitandloss p2 WHERE p2.company_id = p.company_id)
ORDER BY p.sales DESC
LIMIT 10;


-- 6. Company count and average ROE by sector
-- Confirms sectors table joins cleanly and gives a business-level summary.
SELECT s.broad_sector, COUNT(DISTINCT s.company_id) AS num_companies,
       ROUND(AVG(c.roe_percentage), 2) AS avg_roe_percentage
FROM sectors s
JOIN companies c ON s.company_id = c.id
GROUP BY s.broad_sector
ORDER BY num_companies DESC;


-- 7. Duplicate (company_id, year) check across time-series tables
-- Should return zero rows if Day 4/5 deduping held — cross-check against DQ-02.
SELECT 'profitandloss' AS tbl, company_id, year, COUNT(*) AS cnt
FROM profitandloss GROUP BY company_id, year HAVING cnt > 1
UNION ALL
SELECT 'balancesheet', company_id, year, COUNT(*)
FROM balancesheet GROUP BY company_id, year HAVING COUNT(*) > 1
UNION ALL
SELECT 'cashflow', company_id, year, COUNT(*)
FROM cashflow GROUP BY company_id, year HAVING COUNT(*) > 1;


-- 8. Highest and lowest net profit margin (latest year available per company)
-- Quick outlier scan — extreme margins are worth a manual glance.
SELECT company_id, year, sales, net_profit,
       ROUND((net_profit * 100.0 / NULLIF(sales, 0)), 2) AS net_margin_pct
FROM profitandloss
WHERE sales IS NOT NULL AND sales != 0
ORDER BY net_margin_pct DESC
LIMIT 5;


-- 9. Documents table coverage — how many companies have an annual report link
-- Checks the partial-coverage table actually spans a reasonable number of companies.
SELECT COUNT(DISTINCT company_id) AS companies_with_documents,
       COUNT(*) AS total_document_rows
FROM documents;


-- 10. Stock price date range and row count per company (sample check)
-- Confirms stock_prices loaded with sensible date coverage, not just row count.
SELECT company_id,
       COUNT(*) AS price_rows,
       MIN(date) AS earliest_date,
       MAX(date) AS latest_date
FROM stock_prices
GROUP BY company_id
ORDER BY price_rows ASC
LIMIT 10;