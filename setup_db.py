import sqlite3

conn = sqlite3.connect("food.db")
c = conn.cursor()

c.execute("""
CREATE TABLE users (
    reg_id TEXT PRIMARY KEY,
    tg_id INTEGER,
    code_day1 TEXT UNIQUE,
    code_day2 TEXT UNIQUE,
    day1 INTEGER,
    day2 INTEGER
)
""")

conn.commit()
conn.close()

print("Database ready")
