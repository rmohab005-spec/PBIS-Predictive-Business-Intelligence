
import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "pbis_history.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                module TEXT NOT NULL,
                entity_name TEXT,
                probability REAL NOT NULL,
                risk_level TEXT NOT NULL,
                inputs TEXT NOT NULL,
                reasons TEXT,
                recommendations TEXT
            )
        """)
        conn.commit()


def save_prediction(module, entity_name, probability,
                    risk_level, inputs, reasons, recommendations):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO prediction_history (
                module, entity_name, probability, risk_level,
                inputs, reasons, recommendations
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            module,
            entity_name,
            float(probability),
            risk_level,
            json.dumps(inputs, ensure_ascii=False),
            json.dumps(reasons, ensure_ascii=False),
            json.dumps(recommendations, ensure_ascii=False)
        ))
        conn.commit()


def get_history(limit=100):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM prediction_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    return [dict(row) for row in rows]


initialize_database()
