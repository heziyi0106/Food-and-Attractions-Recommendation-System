import os
import sqlite3

now_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(now_dir)
db = os.path.join(parent_dir, 'db.sqlite3')

connect = sqlite3.connect(db)
cursor = connect.cursor()
cursor.execute("UPDATE Points SET todaypoint = 0 WHERE id > 0")
connect.commit()

cursor.close()
connect.close()

