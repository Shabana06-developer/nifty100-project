"""
normaliser.py
Functions that clean/standardize messy raw data values.
"""
import re
import pandas as pd

MONTH_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04",
    "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08",
    "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12",
    "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04",
    "JUNE": "06", "JULY": "07", "AUGUST": "08", "SEPTEMBER": "09",
    "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12",
}


def normalize_year(value) -> str:
    """
    Converts standard financial-year labels into 'YYYY-MM' format.
    Raises ValueError for anything that isn't a clean, standard fiscal year
    (e.g. stub/interim reporting periods like 'Mar 2016 9m', or malformed
    values like '2024.5'). TTM is a recognized special case (rolling window).
    """
    if value is None:
        raise ValueError("Year value cannot be None")

    text = str(value).strip().upper()

    if text == "TTM":
        return "TTM"

    # Already normalised: "2023-03"
    match_already = re.match(r"^(\d{4})-(\d{2})$", text)
    if match_already:
        return f"{match_already.group(1)}-{match_already.group(2)}"

    # "MAR-13" or "MAR-2013" (hyphen between month and year)
    match_hyphen = re.match(r"^([A-Z]+)-(\d{2,4})$", text)
    if match_hyphen:
        month_text, year_text = match_hyphen.groups()
        if month_text in MONTH_MAP:
            year_num = int(year_text)
            year_num = year_num + 2000 if year_num < 100 else year_num
            return f"{year_num}-{MONTH_MAP[month_text]}"

    # "MAR 2023" or "MARCH 2023" (space, 4-digit year)
    match_space4 = re.match(r"^([A-Z]+)\s+(\d{4})$", text)
    if match_space4:
        month_text, year_text = match_space4.groups()
        if month_text in MONTH_MAP:
            return f"{year_text}-{MONTH_MAP[month_text]}"

    # "MAR 23" (space, 2-digit year) — not seen in your data yet, but cheap to support
    match_space2 = re.match(r"^([A-Z]+)\s+(\d{2})$", text)
    if match_space2:
        month_text, year_text = match_space2.groups()
        if month_text in MONTH_MAP:
            year_num = int(year_text) + 2000
            return f"{year_num}-{MONTH_MAP[month_text]}"

    # "FY23" or "FY2023"
    match_fy = re.match(r"^FY\s*(\d{2,4})$", text)
    if match_fy:
        year_num = int(match_fy.group(1))
        year_num = year_num + 2000 if year_num < 100 else year_num
        return f"{year_num}-03"

    # Plain 4-digit year, e.g. "2013" -> assume March FY close
    match_year_only = re.match(r"^(\d{4})$", text)
    if match_year_only:
        return f"{match_year_only.group(1)}-03"

    # Anything else (e.g. "2024.5", "MAR 2016 9M", "MAR 2023 15") is a
    # stub/interim period or malformed value — cannot be safely standardised.
    raise ValueError(f"Could not parse year from: {value!r}")


def normalize_year_safe(value):
    """
    Wrapper around normalize_year() that never raises.
    Returns (normalized_value_or_None, raw_value_if_failed_or_None).
    """
    try:
        return normalize_year(value), None
    except ValueError:
        return None, str(value)


def normalize_year_column(df: pd.DataFrame, year_col: str = "year"):
    """
    Applies normalize_year() to an entire column safely.
    Returns (clean_df, rejected_df):
      - clean_df: rows whose year normalized successfully
      - rejected_df: original rows that failed, with a 'raw_year_value' column
    """
    df = df.copy()
    normalized_values = []
    raw_failed_values = []

    for value in df[year_col]:
        clean_value, failed_value = normalize_year_safe(value)
        normalized_values.append(clean_value)
        raw_failed_values.append(failed_value)

    df["_normalized_year"] = normalized_values
    df["_raw_year"] = raw_failed_values

    rejected = df[df["_normalized_year"].isna()].copy()
    rejected["raw_year_value"] = rejected["_raw_year"]
    rejected = rejected.drop(columns=["_normalized_year", "_raw_year"])

    clean = df[df["_normalized_year"].notna()].copy()
    clean[year_col] = clean["_normalized_year"]
    clean = clean.drop(columns=["_normalized_year", "_raw_year"])

    return clean, rejected


def normalize_ticker(value) -> str:
    """
    Standardizes stock ticker symbols / company_id values.
    Strips whitespace, uppercases. Preserves valid NSE characters like '&' and '-'.

    Examples:
        " tcs "        -> "TCS"
        "bajaj-auto"   -> "BAJAJ-AUTO"
        "m&m"          -> "M&M"
    """
    if value is None:
        raise ValueError("Ticker/company_id value cannot be None")

    text = str(value).strip().upper()
    if not (2 <= len(text) <= 12):
        raise ValueError(f"Ticker length out of range (2-12 chars): {text!r}")

    return text