import sqlite3

conn = sqlite3.connect("database/diabetes.db")

cursor = conn.cursor()

cursor.execute("PRAGMA table_info(predictions)")

for row in cursor.fetchall():
    print(row)

conn.close()