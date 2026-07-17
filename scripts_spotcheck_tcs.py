import sqlite3

conn = sqlite3.connect("nifty100.db")

row = conn.execute(
    "SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year DESC LIMIT 1",
    ("TCS",)
).fetchone()

cols = [d[0] for d in conn.execute("SELECT * FROM financial_ratios LIMIT 1").description]

if row is None:
    print("No row found for TCS")
else:
    for col, val in zip(cols, row):
        print(f"{col}: {val}")

conn.close()