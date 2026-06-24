import pandas as pd

df = pd.DataFrame({
    "company_id": [1, 2, 3],
    "company_name": ["Reliance Industries", "TCS", "Infosys"],
    "ticker": ["RELIANCE.NS", " tcs.bo ", "INFY"],
    "year": ["FY2020-21", "2021", "2019-20"]
})
df.to_excel("data/raw/sample_companies.xlsx", index=False)
print("Sample file created.")