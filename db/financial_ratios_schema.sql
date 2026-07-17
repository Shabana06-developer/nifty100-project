-- financial_ratios table
-- Sprint 2, Day 12 — 14+ KPI columns per company-year
-- PK: (company_id, year), FK: company_id -> companies(id)

CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id              TEXT    NOT NULL,
    year                    TEXT    NOT NULL,

    -- Profitability
    net_profit_margin_pct        REAL,
    operating_profit_margin_pct  REAL,
    return_on_equity_pct         REAL,
    return_on_capital_employed_pct REAL,
    return_on_assets_pct         REAL,

    -- Leverage & Efficiency
    debt_to_equity          REAL,
    high_leverage_flag       INTEGER,   -- 0/1
    interest_coverage        REAL,
    icr_label                 TEXT,      -- e.g. 'Debt Free'
    icr_warning_flag          INTEGER,   -- 0/1
    net_debt_cr               REAL,
    asset_turnover             REAL,

    -- Cash Flow KPIs
    free_cash_flow_cr         REAL,
    cfo_quality_score          REAL,
    cfo_quality_label           TEXT,
    capex_cr                    REAL,
    capex_intensity_pct         REAL,
    capex_intensity_label        TEXT,
    fcf_conversion_rate_pct      REAL,
    cash_from_operations_cr      REAL,

    -- Capital Allocation
    cfo_sign                     TEXT,
    cfi_sign                     TEXT,
    cff_sign                     TEXT,
    capital_allocation_pattern    TEXT,

    -- Growth / CAGR
    revenue_cagr_3yr              REAL,
    revenue_cagr_3yr_flag          TEXT,
    revenue_cagr_5yr              REAL,
    revenue_cagr_5yr_flag          TEXT,
    revenue_cagr_10yr             REAL,
    revenue_cagr_10yr_flag         TEXT,
    pat_cagr_3yr                  REAL,
    pat_cagr_3yr_flag              TEXT,
    pat_cagr_5yr                  REAL,
    pat_cagr_5yr_flag               TEXT,
    pat_cagr_10yr                 REAL,
    pat_cagr_10yr_flag              TEXT,
    eps_cagr_3yr                  REAL,
    eps_cagr_3yr_flag               TEXT,
    eps_cagr_5yr                  REAL,
    eps_cagr_5yr_flag                TEXT,
    eps_cagr_10yr                 REAL,
    eps_cagr_10yr_flag               TEXT,

    -- Per-share / valuation-adjacent
    earnings_per_share            REAL,
    book_value_per_share          REAL,
    dividend_payout_ratio_pct     REAL,
    total_debt_cr                 REAL,

    -- Quality
    composite_quality_score       REAL,

    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);