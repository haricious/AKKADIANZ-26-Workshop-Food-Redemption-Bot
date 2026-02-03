import sqlite3

# List of valid student IDs (example)
STUDENT_IDS = [
    "SBM23ECE001",
    "SBM23ECE002",
    "SBM23ECE003",
    "SBM23ECE004"
]

conn = sqlite3.connect("food.db")
c = conn.cursor()

for sid in STUDENT_IDS:
    try:
        c.execute(
            "INSERT INTO users VALUES (?, NULL, NULL, NULL, 0, 0)",
            (sid,)
        )
    except:
        pass  # Ignore duplicates

conn.commit()
conn.close()

print("Database pre-filled successfully")
