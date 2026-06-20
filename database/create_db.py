import sqlite3

conn = sqlite3.connect("database/diabetes.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT

)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    age INTEGER,

    glucose REAL,

    probability REAL,

    prediction TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")
conn.commit()
conn.close()

print("Database created successfully!")