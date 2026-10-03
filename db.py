import sqlite3
from datetime import datetime

DB_FILE = "elderly_app.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recipients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        interval_hours INTEGER DEFAULT 2
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient_id INTEGER,
        timestamp TEXT,
        FOREIGN KEY(recipient_id) REFERENCES recipients(id)
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient_id INTEGER,
        recipient_name TEXT,
        message TEXT,
        timestamp TEXT,
        FOREIGN KEY(recipient_id) REFERENCES recipients(id)
    )
    """)
    
    conn.commit()
    conn.close()

def add_recipient(name, email, interval_hours):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO recipients (name,email,interval_hours) VALUES (?,?,?)",
                (name,email,interval_hours))
    conn.commit()
    conn.close()

def delete_recipient(email):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM recipients WHERE email=?", (email,))
    conn.commit()
    conn.close()

def get_recipients():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, interval_hours FROM recipients")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_recipient_by_email(email):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, interval_hours FROM recipients WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    return row

def save_checkin(recipient_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO checkins (recipient_id, timestamp) VALUES (?,?)", (recipient_id, ts))
    conn.commit()
    conn.close()
    return ts

def get_last_checkin(recipient_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT timestamp FROM checkins WHERE recipient_id=? ORDER BY id DESC LIMIT 1", (recipient_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def add_alert(recipient_id, message):
    recipient = get_recipient_by_id(recipient_id)
    if not recipient:
        return
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO alerts (recipient_id, recipient_name, message, timestamp) VALUES (?,?,?,?)",
                (recipient_id, recipient[1], message, ts))
    conn.commit()
    conn.close()

def get_alerts():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, recipient_name, message, timestamp FROM alerts ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_recipient_by_id(recipient_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, interval_hours FROM recipients WHERE id=?", (recipient_id,))
    row = cur.fetchone()
    conn.close()
    return row
