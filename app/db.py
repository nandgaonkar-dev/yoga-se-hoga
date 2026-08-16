import json
import sqlite3

from app.config import settings


def init_db():
    conn = sqlite3.connect(settings.db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experience_level TEXT NOT NULL,
            goal TEXT NOT NULL,
            injuries TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL REFERENCES user_profile(id),
            request_json TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def save_profile(experience_level: str, goal: str, injuries: str | None) -> int:
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.execute(
        "INSERT INTO user_profile (experience_level, goal, injuries) VALUES (?, ?, ?)",
        (experience_level, goal, injuries),
    )
    conn.commit()
    profile_id = cursor.lastrowid
    conn.close()
    return profile_id


def save_conversation(profile_id: int, request: dict, response: dict) -> int:
    conn = sqlite3.connect(settings.db_path)
    cursor = conn.execute(
        "INSERT INTO conversation_history (profile_id, request_json, response_json) VALUES (?, ?, ?)",
        (profile_id, json.dumps(request), json.dumps(response)),
    )
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    return conversation_id
