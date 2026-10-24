"""Build ailt9019.db from schema.sql + seed.sql.

    python seed.py              # create the file if missing, seed only if empty
    python seed.py --reset      # drop both tables and rebuild from scratch

No server, no driver, no credentials. Re-running without --reset is safe: it
never duplicates rows and never deletes the database file.

The two .sql files are the team's fixtures, applied verbatim - if the schema
changes there, this script needs no edit.
"""

import os
import sqlite3
import sys

import db

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "schema.sql")
FIXTURES = os.path.join(HERE, "seed.sql")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def build(reset=False):
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        if reset:
            # Drop rather than unlink: the .db file is never deleted.
            conn.executescript("DROP TABLE IF EXISTS profiles; DROP TABLE IF EXISTS accounts;")

        tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}

        if "profiles" not in tables or "accounts" not in tables:
            conn.executescript(_read(SCHEMA))
            print(f"created tables from {os.path.basename(SCHEMA)}")

        count = conn.execute("SELECT COUNT(*) AS n FROM profiles").fetchone()["n"]
        if count == 0:
            conn.executescript(_read(FIXTURES))
            print(f"seeded rows from {os.path.basename(FIXTURES)}")
        elif not reset:
            print(f"already has {count} profiles - nothing to do (use --reset to rebuild)")

        total = conn.execute("SELECT COUNT(*) AS n FROM profiles").fetchone()["n"]
        pool = conn.execute(
            "SELECT COUNT(*) AS n FROM profiles WHERE COALESCE(in_team, 0) = 0"
        ).fetchone()["n"]
        print(f"{total} profiles ({pool} still in the pool) -> {db.DB_PATH}")
    finally:
        conn.close()


def main(argv):
    if not os.path.exists(SCHEMA) or not os.path.exists(FIXTURES):
        print("schema.sql and seed.sql must sit next to this script")
        return 1
    build(reset="--reset" in argv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
