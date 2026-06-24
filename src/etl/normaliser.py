"""
normaliser.py
Functions that clean/standardize messy raw data values.
"""

def normalize_year(value) -> int:
    """
    Converts various year formats into a single integer (the starting year of the financial year).

    Examples:
        "FY2020-21" -> 2020
        "2020-21"   -> 2020
        "2021"      -> 2021
        2021 (int)  -> 2021
    """
    if value is None:
        raise ValueError("Year value cannot be None")

    text = str(value).strip().upper().replace("FY", "").strip()

    if "-" in text:
        # e.g. "2020-21" -> take the part before the dash
        text = text.split("-")[0].strip()

    try:
        return int(text)
    except ValueError:
        raise ValueError(f"Could not parse year from: {value!r}")


def normalize_ticker(value) -> str:
    """
    Standardizes stock ticker symbols.

    Examples:
        "RELIANCE.NS"  -> "RELIANCE"
        " tcs.bo "     -> "TCS"
        "INFY"         -> "INFY"
    """
    if value is None:
        raise ValueError("Ticker value cannot be None")

    text = str(value).strip().upper()

    for suffix in [".NS", ".BO"]:
        if text.endswith(suffix):
            text = text[: -len(suffix)]

    return text