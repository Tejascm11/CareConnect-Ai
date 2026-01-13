import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("chat_history.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_input TEXT,
        bot_response TEXT
    )
    """)
    conn.commit()
    return conn, cursor

def save_chat(cursor, conn, user_input, bot_response):
    cursor.execute(
        "INSERT INTO logs (timestamp, user_input, bot_response) VALUES (?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_input, bot_response)
    )
    conn.commit()
