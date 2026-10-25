"""SQLite writes compatible with matching/schema.sql and matching/db.py."""

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from matching import db as matching_db

from .security import token_digest


SCHEMA = Path(__file__).resolve().parents[1] / "matching" / "schema.sql"


class DuplicateUsername(Exception):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connection(self):
        # Each request opens its own connection in the thread handling it.
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def initialise(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            existing = tables & {"accounts", "profiles"}
            if not existing:
                conn.executescript(SCHEMA.read_text(encoding="utf-8"))
            elif existing != {"accounts", "profiles"}:
                raise RuntimeError("Database has an incomplete matching schema; use a complete database or a new DB_PATH.")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    token_hash TEXT PRIMARY KEY,
                    account_id INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS auth_sessions_expiry ON auth_sessions(expires_at);
            """)

    def create_account(self, username: str, password_hash: str):
        try:
            with self.connection() as conn:
                # The original table's uniqueness is case sensitive. Preserve
                # existing fixtures while treating web usernames consistently.
                if conn.execute("SELECT id FROM accounts WHERE username = ? COLLATE NOCASE", (username,)).fetchone():
                    raise DuplicateUsername
                cursor = conn.execute("INSERT INTO accounts (username, password_hash) VALUES (?, ?)", (username, password_hash))
                return {"id": cursor.lastrowid, "username": username}
        except sqlite3.IntegrityError as exc:
            raise DuplicateUsername from exc

    def account_for_login(self, username: str):
        with self.connection() as conn:
            row = conn.execute("SELECT id, username, password_hash FROM accounts WHERE username = ? COLLATE NOCASE", (username,)).fetchone()
            return dict(row) if row else None

    def create_session(self, account_id: int, token: str, ttl: int):
        now = int(time.time())
        with self.connection() as conn:
            conn.execute("DELETE FROM auth_sessions WHERE expires_at <= ?", (now,))
            conn.execute("INSERT INTO auth_sessions (token_hash, account_id, expires_at) VALUES (?, ?, ?)",
                         (token_digest(token), account_id, now + ttl))

    def session_account(self, token: str):
        with self.connection() as conn:
            row = conn.execute("""
                SELECT a.id, a.username FROM accounts AS a
                JOIN auth_sessions AS s ON s.account_id = a.id
                WHERE s.token_hash = ? AND s.expires_at > ?
            """, (token_digest(token), int(time.time()))).fetchone()
            return dict(row) if row else None

    def revoke_session(self, token: str):
        with self.connection() as conn:
            conn.execute("DELETE FROM auth_sessions WHERE token_hash = ?", (token_digest(token),))

    def load_profile(self, account_id: int):
        with self.connection() as conn:
            row = conn.execute("SELECT updated_at FROM profiles WHERE account_id = ?", (account_id,)).fetchone()
            if not row:
                return None
            return {**matching_db.load_profile(conn, account_id), "updated_at": row["updated_at"]}

    def save_profile(self, account_id: int, values: dict):
        with self.connection() as conn:
            conn.execute("""
                INSERT INTO profiles (account_id, display_name, contact_info, city, preferred_role, languages)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    display_name = excluded.display_name,
                    contact_info = excluded.contact_info,
                    city = excluded.city,
                    preferred_role = excluded.preferred_role,
                    languages = excluded.languages,
                    updated_at = CURRENT_TIMESTAMP
            """, (account_id, values["display_name"], values.get("contact_info"), values["city"],
                  values["preferred_role"], json.dumps(values["languages"], ensure_ascii=False)))
            profile = matching_db.load_profile(conn, account_id)
            updated = conn.execute("SELECT updated_at FROM profiles WHERE account_id = ?", (account_id,)).fetchone()
            return {**profile, "updated_at": updated["updated_at"]}
