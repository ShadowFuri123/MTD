import sqlite3

conn = sqlite3.connect('database.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS planes(
    id INT PRIMARY KEY,
    theme TEXT,
    description TEXT,
    mark BOOL,
    date TEXT);
    """)



conn.commit()