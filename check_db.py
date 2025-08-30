#!/usr/bin/env python3
import sqlite3
import os

db_path = os.path.join('data', 'users.db')
print('DB exists:', os.path.exists(db_path))

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('Tables:', tables)
    
    # Check users
    try:
        cursor.execute("SELECT username, email, role FROM users;")
        users = cursor.fetchall()
        print('Users:', users)
    except Exception as e:
        print('Error reading users:', e)
    
    conn.close()
else:
    print('Database file does not exist')
