import sqlite3
import os

DB_PATH = os.path.join("instance", "dev.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

print("\n📦 USERS TABLE COLUMNS:\n")
for col in columns:
    print(f"- {col[1]}")

required = {"gmail_token", "calendar_token"}
found = {col[1] for col in columns}

missing = required - found

if missing:
    print("\n❌ MISSING COLUMNS:", missing)
else:
    print("\n✅ REQUIRED COLUMNS PRESENT")

conn.close()
