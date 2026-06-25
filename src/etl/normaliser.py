"""
normaliser.py
Functions that clean/standardize messy raw data values.
"""
import re

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
    Converts various financial-year labels into 'YYYY-MM' format.

    Examples:
        "Mar-23"      -> "2023-03"
        "Mar 23"      -> "2023-03"
        "March-2023"  -> "2023-03"
        "2023"        -> "2023-03"   (assume March FY close if no month given)
        "FY23"        -> "2023-03"
        "Dec-22"      -> "2022-12"
        "2023-03"     -> "2023-03"   (already normalised, pass through)
    """
    if value is None:
        raise ValueError("Year value cannot be None")

    text = str(value).strip().upper().replace("-", " ")
    text = re.sub(r"\s+", " ", text)

    # Already normalised: "2023 03"
    match_already = re.match(r"^(\d{4})\s+(\d{2})$", text)
    if match_already:
        return f"{match_already.group(1)}-{match_already.group(2)}"

    text_no_fy = text.replace("FY", "").strip()

    # "MAR 23" or "MARCH 2023" pattern
    match_month_year = re.match(r"^([A-Z]+)\s*(\d{2,4})$", text_no_fy)
    if match_month_year:
        month_text, year_text = match_month_year.groups()
        if month_text in MONTH_MAP:
            year_num = int(year_text)
            year_num = year_num + 2000 if year_num < 100 else year_num
            return f"{year_num}-{MONTH_MAP[month_text]}"

    # Plain year only, e.g. "2023" or "23"
    match_year_only = re.match(r"^(\d{2,4})$", text_no_fy)
    if match_year_only:
        year_num = int(match_year_only.group(1))
        year_num = year_num + 2000 if year_num < 100 else year_num
        return f"{year_num}-03"  # assume March FY close

    raise ValueError(f"Could not parse year from: {value!r}")


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