import sqlite3
import pandas as pd
from datetime import date

DB_PATH = "fitness_data.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Weight table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight (
                date TEXT PRIMARY KEY,
                weight REAL
            )
        ''')
        # Calories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calories (
                date TEXT,
                calories INTEGER,
                PRIMARY KEY (date)
            )
        ''')
        # Workouts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                exercise TEXT,
                duration INTEGER,
                intensity TEXT
            )
        ''')
        # Water table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water (
                date TEXT,
                amount INTEGER,
                PRIMARY KEY (date)
            )
        ''')
        # Settings table (for Goal Weight)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        conn.commit()

def log_weight(weight):
    today = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO weight (date, weight) VALUES (?, ?)", (today, weight))

def get_weight_history():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM weight ORDER BY date ASC", conn)

def log_calories(calories):
    today = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO calories (date, calories) VALUES (?, ?)", (today, calories))

def get_calorie_history():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM calories ORDER BY date ASC", conn)

def log_workout(exercise, duration, intensity):
    today = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO workouts (date, exercise, duration, intensity) VALUES (?, ?, ?, ?)", 
                     (today, exercise, duration, intensity))

def get_workout_history():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM workouts ORDER BY date DESC", conn)

def log_water(amount):
    today = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        # Increment water intake for the day
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM water WHERE date = ?", (today,))
        row = cursor.fetchone()
        if row:
            new_amount = row[0] + amount
            conn.execute("UPDATE water SET amount = ? WHERE date = ?", (new_amount, today))
        else:
            conn.execute("INSERT INTO water (date, amount) VALUES (?, ?)", (today, amount))

def get_water_history():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM water ORDER BY date DESC", conn)

def set_setting(key, value):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

def get_setting(key, default=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
