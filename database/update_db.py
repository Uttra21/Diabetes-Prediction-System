import sqlite3

conn = sqlite3.connect("database/diabetes.db")

cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE predictions
    ADD COLUMN user_id INTEGER
    """)

    print("user_id column added")

except Exception as e:
    print(e)

conn.commit()
conn.close()