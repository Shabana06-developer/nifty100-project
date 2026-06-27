-- schema.sql
-- Nifty100 Financial Intelligence Platform — Sprint 1 Database Schema
-- 10 tables. FK constraints enforced. Run with PRAGMA foreign_keys = ON.

PRAGMA foreign_keys = ON;

-- ========== 1. companies (master reference table) ==========
CREATE TABLE IF NOT EXISTS companies (
    id                 TEXT PRIMARY KEY,         -- NSE ticker, e.g. 'TCS'
    company_logo       TEXT,
    company_name       TEXT NOT NULL,
    chart_link         TEXT,
    about_company      TEXT,
    website            TEXT,
    nse_profile        TEXT,
    bse_profile        TEXT,
    face_value         REAL,
    book_value         REAL,
    roce_percentage    REAL,
    roe_percentage     REAL
);

-- ========== 2. profitandloss ==========
CREATE TABLE IF NOT EXISTS profitandloss (
    id                  INTEGER,
    company_id          TEXT NOT NULL,
    year                 TEXT NOT NULL,           -- format 'YYYY-MM'
    sales                REAL,
    expenses             REAL,
    operating_profit     REAL,
    opm_percentage       REAL,
    other_income         REAL,
    interest             REAL,
    depreciation         REAL,
    profit_before_tax    REAL,
    tax_percentage       REAL,
    net_profit           REAL,
    eps                  REAL,
    dividend_payout      REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 3. balancesheet ==========
CREATE TABLE IF NOT EXISTS balancesheet (
    id                  INTEGER,
    company_id          TEXT NOT NULL,
    year                 TEXT NOT NULL,
    equity_capital       REAL,
    reserves             REAL,
    borrowings           REAL,
    other_liabilities    REAL,
    total_liabilities    REAL,
    fixed_assets         REAL,
    cwip                 REAL,
    investments          REAL,
    other_asset          REAL,
    total_assets         REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 4. cashflow ==========
CREATE TABLE IF NOT EXISTS cashflow (
    id                   INTEGER,
    company_id           TEXT NOT NULL,
    year                  TEXT NOT NULL,
    operating_activity     REAL,
    investing_activity     REAL,
    financing_activity     REAL,
    net_cash_flow          REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 5. analysis (partial coverage, ~8 companies) ==========
CREATE TABLE IF NOT EXISTS analysis (
    id                          INTEGER PRIMARY KEY,
    company_id                  TEXT NOT NULL,
    compounded_sales_growth      TEXT,
    compounded_profit_growth     TEXT,
    stock_price_cagr             TEXT,
    roe                          TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 6. documents (annual report links) ==========
CREATE TABLE IF NOT EXISTS documents (
    id                INTEGER PRIMARY KEY,
    company_id        TEXT NOT NULL,
    report_year        INTEGER NOT NULL,     -- source column is 'Year', renamed for SQL safety
    annual_report       TEXT,                -- source column is 'Annual_Report'
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 7. prosandcons (partial coverage, ~8 companies) ==========
CREATE TABLE IF NOT EXISTS prosandcons (
    id            INTEGER PRIMARY KEY,
    company_id     TEXT NOT NULL,
    pros           TEXT,
    cons           TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 8. sectors ==========
CREATE TABLE IF NOT EXISTS sectors (
    company_id            TEXT PRIMARY KEY,
    broad_sector           TEXT NOT NULL,
    sub_sector             TEXT,
    index_weight_pct       REAL,
    market_cap_category    TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 9. market_cap ==========
CREATE TABLE IF NOT EXISTS market_cap (
    company_id              TEXT NOT NULL,
    year                      INTEGER NOT NULL,
    market_cap_crore          REAL,
    enterprise_value_crore    REAL,
    pe_ratio                  REAL,
    pb_ratio                  REAL,
    ev_ebitda                 REAL,
    dividend_yield_pct        REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- ========== 10. stock_prices ==========
CREATE TABLE IF NOT EXISTS stock_prices (
    company_id      TEXT NOT NULL,
    date              TEXT NOT NULL,        -- 'YYYY-MM-DD'
    open_price         REAL,
    high_price         REAL,
    low_price          REAL,
    close_price        REAL,
    volume             INTEGER,
    adjusted_close     REAL,
    PRIMARY KEY (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);