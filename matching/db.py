"""Thin DB layer for the AILT9019 matcher.

Everything SQL lives here and nowhere else, so the logic in match.py stays pure
and testable without a database.

Driver: psycopg against the shared PostgreSQL database. The URL comes from
DATABASE_URL (loaded from matching/.env). There is no local fallback: without
the variable the matcher fails loudly instead of reading a different database.
"""

import json
import os

JSON_COLUMNS = ("languages", "open_roles")
LIST_COLUMNS = ("languages",)

PROFILE_FIELDS = (
    "account_id, display_name, contact_info, city, preferred_role, "
    "languages, in_team, programme, open_roles, programming, github, "
    "debugging, web, ai_agent"
)


def get_conn():
    """Open the shared PostgreSQL database."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set - copy matching/.env.example to "
            "matching/.env and restart."
        )

    import psycopg
    from psycopg.rows import dict_row

    return psycopg.connect(
        database_url,
        row_factory=dict_row,
    )


def _placeholder(conn):
    """The backend tests use SQLite; the running app uses PostgreSQL."""
    module = type(conn).__module__
    return "%s" if module.startswith("psycopg") else "?"


def _decode(row):
    """Convert database rows into normal Python dictionaries."""
    if row is None:
        return None

    row = dict(row)

    for col in JSON_COLUMNS:
        value = row.get(col)

        if value is None:
            row[col] = [] if col in LIST_COLUMNS else None

        elif isinstance(value, (str, bytes)):
            row[col] = json.loads(value) if value else ([] if col in LIST_COLUMNS else None)

    return row


def load_profile(conn, account_id):
    mark = _placeholder(conn)
    row = conn.execute(
        f"""
        SELECT {PROFILE_FIELDS}
        FROM profiles
        WHERE account_id = {mark}
        """,
        (account_id,),
    ).fetchone()

    return _decode(row)


def load_profile_by_username(conn, username):
    fields = PROFILE_FIELDS.replace(", ", ", p.")
    mark = _placeholder(conn)

    row = conn.execute(
        f"""
        SELECT p.{fields}
        FROM profiles p
        JOIN accounts a ON a.id = p.account_id
        WHERE LOWER(a.username) = LOWER({mark})
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
