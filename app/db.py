"""Thin DB layer for the AILT9019 matcher.

Everything SQL lives here and nowhere else, so the logic in match.py stays pure
and testable without a database.

Driver: sqlite3 - in the standard library, no install, no server. The database
is one file (`ailt9019.db`) sitting next to this module.

Override the location if you want it elsewhere:
    DB_PATH=/tmp/demo.db python match.py alice_chen
"""

import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(HERE, "ailt9019.db"))

JSON_COLUMNS = ("languages",)

# Every column the matcher or the result card needs. Keep this list in sync with
# the table: SELECT * would drag password_hash along if the tables are ever joined.
PROFILE_FIELDS = (
    "account_id, display_name, contact_info, city, preferred_role, "
    "languages, in_team"
)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _decode(row):
    """SQLite stores the JSON columns as text. Turn them into real lists."""
    if row is None:
        return None
    row = dict(row)
    for col in JSON_COLUMNS:
        value = row.get(col)
        if value is None:
            row[col] = []
        elif isinstance(value, (str, bytes)):
            row[col] = json.loads(value) if value else []
    return row


def load_profile(conn, account_id):
    row = conn.execute(
        f"SELECT {PROFILE_FIELDS} FROM profiles WHERE account_id = ?", (account_id,)
    ).fetchone()
    return _decode(row)


def load_profile_by_username(conn, username):
    row = conn.execute(
        f"SELECT p.{PROFILE_FIELDS.replace(', ', ', p.')} "
        "FROM profiles p JOIN accounts a ON a.id = p.account_id "
        "WHERE a.username = ?",
        (username,),
    ).fetchone()
    return _decode(row)


def load_pool(conn):
    """Every profile, unfiltered.

    Deliberately no WHERE clause: self-exclusion and `in_team` are rules, and
    rules live in filters.py where they are visible, testable, and apply the
    same way to the database path and the JSON path. Filtering here as well
    would create a second source of truth for the same decision.
    """
    rows = conn.execute(f"SELECT {PROFILE_FIELDS} FROM profiles").fetchall()
    return [_decode(r) for r in rows]
