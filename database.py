import sqlite3
import os

DB_PATH = 'scores.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_index INTEGER,
            player_name TEXT,
            moves INTEGER,
            time_seconds INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_score(level_index, player_name, moves, time_seconds):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scores (level_index, player_name, moves, time_seconds)
        VALUES (?, ?, ?, ?)
    ''', (level_index, player_name, moves, time_seconds))
    conn.commit()
    conn.close()

def get_top_scores(level_index, limit=5):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Order first by lowest moves, then lowest time
    cursor.execute('''
        SELECT player_name, moves, time_seconds, date
        FROM scores
        WHERE level_index = ?
        ORDER BY moves ASC, time_seconds ASC
        LIMIT ?
    ''', (level_index, limit))
    results = cursor.fetchall()
    conn.close()
    return results

def get_max_unlocked_level():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(level_index) FROM scores')
    res = cursor.fetchone()
    conn.close()
    if res and res[0] is not None:
        return res[0] + 1
    return 0
