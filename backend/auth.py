import sqlite3
import hashlib
import os
import time
import json
from typing import Optional, Dict, Any, List

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "guild_users.db"))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_auth_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users Table (Guild Adventurers)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        class_role TEXT DEFAULT 'Apprentice',
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        avatar TEXT DEFAULT '🧙‍♂️',
        created_at REAL NOT NULL
    )
    """)
    
    # 2. User Quests & Chat History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_quests (
        quest_id TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        title TEXT NOT NULL,
        prompt TEXT NOT NULL,
        language TEXT DEFAULT 'python',
        preset TEXT DEFAULT 'classic',
        score INTEGER DEFAULT 0,
        status TEXT DEFAULT 'in_progress',
        created_at REAL NOT NULL,
        finished_at REAL,
        artifacts_json TEXT DEFAULT '{}',
        review_summary TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    # Create Default Guild Master Rama Admin if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'dasrams'")
    if not cursor.fetchone():
        pwd_hash = hashlib.sha256("rama123".encode("utf-8")).hexdigest()
        cursor.execute("""
        INSERT INTO users (username, password_hash, class_role, level, exp, avatar, created_at)
        VALUES ('dasrams', ?, 'Grand Guild Master', 99, 9999, '👑', ?)
        """, (pwd_hash, time.time()))
        
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(username: str, password: str, class_role: str = "Knight", avatar: str = "⚔️") -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    
    try:
        cursor.execute("""
        INSERT INTO users (username, password_hash, class_role, level, exp, avatar, created_at)
        VALUES (?, ?, ?, 1, 0, ?, ?)
        """, (username.strip().lower(), pwd_hash, class_role, avatar, time.time()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {
            "success": True,
            "user": {
                "id": user_id,
                "username": username.strip().lower(),
                "class_role": class_role,
                "level": 1,
                "exp": 0,
                "avatar": avatar
            }
        }
    except sqlite3.IntegrityError:
        conn.close()
        return {"success": False, "error": "Nama pahlawan (username) sudah terdaftar di prasasti Guild!"}
    except Exception as e:
        conn.close()
        return {"success": False, "error": str(e)}

def authenticate_user(username: str, password: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    
    cursor.execute("""
    SELECT id, username, class_role, level, exp, avatar FROM users
    WHERE username = ? AND password_hash = ?
    """, (username.strip().lower(), pwd_hash))
    
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def save_user_quest(user_id: int, username: str, quest_id: str, title: str, prompt: str, language: str, preset: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO user_quests (quest_id, user_id, username, title, prompt, language, preset, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'in_progress', ?)
    """, (quest_id, user_id, username, title, prompt, language, preset, time.time()))
    conn.commit()
    conn.close()

def update_user_quest_finished(quest_id: str, status: str, score: int, artifacts: list, review: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE user_quests
    SET status = ?, score = ?, artifacts_json = ?, review_summary = ?, finished_at = ?
    WHERE quest_id = ?
    """, (status, score, json.dumps(artifacts), review, time.time(), quest_id))
    
    # Give +100 EXP to the user if completed
    if status == "completed":
        cursor.execute("SELECT user_id FROM user_quests WHERE quest_id = ?", (quest_id,))
        row = cursor.fetchone()
        if row:
            uid = row["user_id"]
            cursor.execute("UPDATE users SET exp = exp + 100 WHERE id = ?", (uid,))
            cursor.execute("UPDATE users SET level = 1 + (exp / 100) WHERE id = ?", (uid,))
            
    conn.commit()
    conn.close()

def get_user_quest_history(user_id: int) -> List[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT quest_id, title, prompt, language, preset, score, status, created_at, finished_at, artifacts_json, review_summary
    FROM user_quests
    WHERE user_id = ?
    ORDER BY created_at DESC
    LIMIT 30
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["artifacts"] = json.loads(d.get("artifacts_json") or "[]")
        result.append(d)
    return result

# Initialize Auth DB automatically
init_auth_db()
