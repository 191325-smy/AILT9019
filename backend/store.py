"""Account and profile storage for SQLite and PostgreSQL."""

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

    def __init__(self, database):
        self.database = str(database)

        self.is_postgres = self.database.startswith(
            ("postgres://", "postgresql://")
        )

        if not self.is_postgres:
            self.path = Path(self.database).expanduser().resolve()

    @contextmanager
    def connection(self):
        """Open one connection per operation."""

        if self.is_postgres:
            import psycopg
            from psycopg.rows import dict_row

            with psycopg.connect(
                self.database,
                row_factory=dict_row,
            ) as conn:
                yield conn

        else:
            conn = sqlite3.connect(
                self.path,
                timeout=10,
            )

            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")

            try:
                with conn:
                    yield conn
            finally:
                conn.close()

    def _execute(self, conn, sql, params=()):
        """Use the correct SQL placeholder."""

        if self.is_postgres:
            sql = sql.replace("?", "%s")

        return conn.execute(sql, params)

    def initialise(self):
        """Create missing backend tables without deleting existing data."""

        if self.is_postgres:
            self._initialise_postgres()
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.connection() as conn:

            tables = {
                row["name"]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }

            existing = tables & {"accounts", "profiles"}

            if not existing:
                conn.executescript(
                    SCHEMA.read_text(encoding="utf-8")
                )

            elif existing != {"accounts", "profiles"}:
                raise RuntimeError(
                    "Database has an incomplete matching schema."
                )

            conn.executescript("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    token_hash TEXT PRIMARY KEY,
                    account_id INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    FOREIGN KEY (account_id)
                        REFERENCES accounts(id)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS auth_sessions_expiry
                ON auth_sessions(expires_at);
            """)

    def _initialise_postgres(self):
        """Create only the session table. Preserve existing accounts/profiles."""

        with self.connection() as conn:

            tables = conn.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name IN ('accounts', 'profiles')
            """).fetchall()

            existing = {row["table_name"] for row in tables}

            if existing != {"accounts", "profiles"}:
                raise RuntimeError(
                    "PostgreSQL must already contain both accounts "
                    "and profiles tables. Check the database schema."
                )

            conn.execute("""
                CREATE TABLE IF NOT EXISTS auth_sessions (
                    token_hash TEXT PRIMARY KEY,
                    account_id BIGINT NOT NULL
                        REFERENCES accounts(id)
                        ON DELETE CASCADE,
                    expires_at BIGINT NOT NULL
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS auth_sessions_expiry
                ON auth_sessions(expires_at)
            """)

    def create_account(self, username, password_hash):
        try:
            with self.connection() as conn:

                if self.is_postgres:
                    found = conn.execute(
                        """
                        SELECT id
                        FROM accounts
                        WHERE LOWER(username) = LOWER(%s)
                        """,
                        (username,),
                    ).fetchone()

                    if found:
                        raise DuplicateUsername

                    row = conn.execute(
                        """
                        INSERT INTO accounts (username, password_hash)
                        VALUES (%s, %s)
                        RETURNING id
                        """,
                        (username, password_hash),
                    ).fetchone()

                    return {
                        "id": row["id"],
                        "username": username,
                    }

                found = conn.execute(
                    """
                    SELECT id
                    FROM accounts
                    WHERE username = ? COLLATE NOCASE
                    """,
                    (username,),
                ).fetchone()

                if found:
                    raise DuplicateUsername

                cursor = conn.execute(
                    """
                    INSERT INTO accounts (username, password_hash)
                    VALUES (?, ?)
                    """,
                    (username, password_hash),
                )

                return {
                    "id": cursor.lastrowid,
                    "username": username,
                }

        except sqlite3.IntegrityError as exc:
            raise DuplicateUsername from exc

        except Exception as exc:
            if self.is_postgres:
                from psycopg.errors import UniqueViolation

                if isinstance(exc, UniqueViolation):
                    raise DuplicateUsername from exc

            raise

    def account_for_login(self, username):
        with self.connection() as conn:

            if self.is_postgres:
                row = conn.execute(
                    """
                    SELECT id, username, password_hash
                    FROM accounts
                    WHERE LOWER(username) = LOWER(%s)
                    """,
                    (username,),
                ).fetchone()

            else:
                row = conn.execute(
                    """
                    SELECT id, username, password_hash
                    FROM accounts
                    WHERE username = ? COLLATE NOCASE
                    """,
                    (username,),
                ).fetchone()

            return dict(row) if row else None

    def create_session(self, account_id, token, ttl):
        now = int(time.time())

        with self.connection() as conn:

            self._execute(
                conn,
                "DELETE FROM auth_sessions WHERE expires_at <= ?",
                (now,),
            )

            self._execute(
                conn,
                """
                INSERT INTO auth_sessions
                (token_hash, account_id, expires_at)
                VALUES (?, ?, ?)
                """,
                (
                    token_digest(token),
                    account_id,
                    now + ttl,
                ),
            )

    def session_account(self, token):
        with self.connection() as conn:

            row = self._execute(
                conn,
                """
                SELECT a.id, a.username
                FROM accounts AS a
                JOIN auth_sessions AS s
                  ON s.account_id = a.id
                WHERE s.token_hash = ?
                  AND s.expires_at > ?
                """,
                (
                    token_digest(token),
                    int(time.time()),
                ),
            ).fetchone()

            return dict(row) if row else None

    def revoke_session(self, token):
        with self.connection() as conn:

            self._execute(
                conn,
                "DELETE FROM auth_sessions WHERE token_hash = ?",
                (token_digest(token),),
            )

    def load_profile(self, account_id):
        with self.connection() as conn:

            row = self._execute(
                conn,
                """
                SELECT updated_at
                FROM profiles
                WHERE account_id = ?
                """,
                (account_id,),
            ).fetchone()

            if not row:
                return None

            profile = matching_db.load_profile(
                conn,
                account_id,
            )

            return {
                **profile,
                "updated_at": str(row["updated_at"]),
            }

    def save_profile(self, account_id, values):
        with self.connection() as conn:

            sql = """
                INSERT INTO profiles (
                    account_id,
                    display_name,
                    contact_info,
                    city,
                    preferred_role,
                    languages
                )
                VALUES (?, ?, ?, ?, ?, ?)

                ON CONFLICT(account_id)
                DO UPDATE SET
                    display_name = excluded.display_name,
                    contact_info = excluded.contact_info,
                    city = excluded.city,
                    preferred_role = excluded.preferred_role,
                    languages = excluded.languages,
                    updated_at = CURRENT_TIMESTAMP
            """

            self._execute(
                conn,
                sql,
                (
                    account_id,
                    values["display_name"],
                    values.get("contact_info"),
                    values["city"],
                    values["preferred_role"],
                    json.dumps(
                        values["languages"],
                        ensure_ascii=False,
                    ),
                ),
            )

            profile = matching_db.load_profile(
                conn,
                account_id,
            )

            updated = self._execute(
                conn,
                """
                SELECT updated_at
                FROM profiles
                WHERE account_id = ?
                """,
                (account_id,),
            ).fetchone()

            return {
                **profile,
                "updated_at": str(updated["updated_at"]),
            }
