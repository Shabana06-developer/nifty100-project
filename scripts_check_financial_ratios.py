import sqlite3

conn = sqlite3.connect("nifty100.db")

print("FINANCIAL_RATIOS columns:")
cols = list(conn.execute("PRAGMA table_info(financial_ratios)"))
for r in cols:
    print(" ", r[1], "-", r[2])
print("TOTAL COLUMNS:", len(cols))

print()
print("CREATE TABLE statement:")
row = conn.execute(
    "SELECT sql FROM sqlite_master WHERE name = 'financial_ratios'"
).fetchone()
print(row[0] if row else "TABLE DOES NOT EXIST")

conn.close()