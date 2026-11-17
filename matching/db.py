"""Thin DB layer for the AILT9019 matcher.

Everything SQL lives here and nowhere else, so the logic in match.py stays pure
and testable without a database.

Driver: sqlite3 - in the standard library, no install, no server. The database
is one file (`ailt9019.db`) sitting next to this module.

Override the location if you want it elsewhere:
    DB_PATH=/tmp/demo.db python match.py alice_chen
"""

"""Database readers for SQLite and PostgreSQL."""

import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(HERE, "ailt9019.db"))

JSON_COLUMNS = ("languages",)

PROFILE_FIELDS = (
    "account_id, display_name, contact_info, city, preferred_role, "
    "languages, in_team"
)


def get_conn():
    """Open the configured database."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(
            database_url,
            row_factory=dict_row,
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _placeholder(conn):
    """Return the parameter placeholder for the active database."""
    if conn.__class__.__module__.startswith("psycopg"):
        return "%s"
    return "?"


def _decode(row):
    """Convert database rows into normal Python dictionaries."""
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
    placeholder = _placeholder(conn)

    row = conn.execute(
        f"""
        SELECT {PROFILE_FIELDS}
        FROM profiles
        WHERE account_id = {placeholder}
        """,
        (account_id,),
    ).fetchone()

    return _decode(row)


def load_profile_by_username(conn, username):
    placeholder = _placeholder(conn)

    fields = PROFILE_FIELDS.replace(", ", ", p.")

    row = conn.execute(
        f"""
        SELECT p.{fields}
        FROM profiles p
        JOIN accounts a ON a.id = p.account_id
        WHERE LOWER(a.username) = LOWER({placeholder})
        """,
        (username,),
    ).fetchone()

    return _decode(row)


def load_pool(conn):
    """Load all profiles. Filtering remains in filters.py."""

    rows = conn.execute(
        f"SELECT {PROFILE_FIELDS} FROM profiles"
    ).fetchall()

    return [_decode(row) for row in rows]
