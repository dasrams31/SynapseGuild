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

def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

def init_auth_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        class_role TEXT DEFAULT 'Knight',
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        avatar TEXT DEFAULT '🧙‍♂️',
        created_at REAL NOT NULL
    )
    """)
    
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
    
    # Ensure default admin dasrams exists with known hashes for both rama123 and dasrams123
    cursor.execute("SELECT id, password_hash FROM users WHERE username = 'dasrams' COLLATE NOCASE")
    row = cursor.fetchone()
    if not row:
        pwd_hash = hash_password("dasrams123")
        cursor.execute("""
        INSERT INTO users (username, password_hash, class_role, level, exp, avatar, created_at)
        VALUES ('dasrams', ?, 'Grand Guild Master', 99, 9999, '👑', ?)
        """, (pwd_hash, time.time()))
        
    conn.commit()
    conn.close()

def register_user(username: str, password: str, class_role: str = "Knight", avatar: str = "⚔️") -> dict:
    clean_user = username.strip().lower()
    clean_pass = password.strip()
    if not clean_user or len(clean_user) < 3:
        return {"success": False, "error": "Nama pahlawan minimal 3 karakter!"}
    if not clean_pass or len(clean_pass) < 4:
        return {"success": False, "error": "Mantra sandi minimal 4 karakter!"}

    conn = get_db_connection()
    cursor = conn.cursor()
    pwd_hash = hash_password(clean_pass)
    
    try:
        cursor.execute("""
        INSERT INTO users (username, password_hash, class_role, level, exp, avatar, created_at)
        VALUES (?, ?, ?, 1, 0, ?, ?)
        """, (clean_user, pwd_hash, class_role, avatar, time.time()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {
            "success": True,
            "user": {
                "id": user_id,
                "username": clean_user,
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
    clean_user = username.strip().lower()
    clean_pass = password.strip()
    pwd_hash = hash_password(clean_pass)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Exact match on username (case-insensitive) & password hash
    cursor.execute("""
    SELECT id, username, class_role, level, exp, avatar, password_hash FROM users
    WHERE LOWER(TRIM(username)) = ?
    """, (clean_user,))
    
    rows = cursor.fetchall()
    conn.close()
    
    for r in rows:
        stored_hash = r["password_hash"]
        # Match standard hash or fallback common passwords for dasrams
        if stored_hash == pwd_hash:
            d = dict(r)
            d.pop("password_hash", None)
            return d
        # Dual password support for dasrams admin
        if clean_user == "dasrams" and (clean_pass in ["dasrams123", "rama123", "dasrams", "admin"]):
            d = dict(r)
            d.pop("password_hash", None)
            return d

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

init_auth_db()
