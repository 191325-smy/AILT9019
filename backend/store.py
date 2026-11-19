"""Account and profile storage for PostgreSQL.

The SQLite branch below exists only for the test suite, which injects a
throwaway file through create_app(db_path=...). The running app always uses
the shared PostgreSQL database from DATABASE_URL.
"""

import json
import sqlite3
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from matching import db as matching_db

from .security import token_digest


PROFILE_CACHE_SECONDS = 30


# Test-only SQLite definitions. The running app uses PostgreSQL, whose tables are
# created outside this codebase; these constants let the test suite spin up a
# throwaway database without any SQL files on disk.
SQLITE_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE profiles (
    account_id INTEGER PRIMARY KEY,
    display_name TEXT NOT NULL,
    contact_info TEXT,
    city TEXT,
    preferred_role TEXT,
    languages TEXT,
    in_team INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    programme TEXT,
    open_roles TEXT,
    programming INTEGER,
    github INTEGER,
    debugging INTEGER,
    web INTEGER,
    ai_agent INTEGER,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
"""


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

        self._pool = None
        # SQLite is the test backend; tests must see direct writes immediately.
        self._cache_enabled = self.is_postgres
        self._cache_lock = threading.Lock()
        self._sessions = {}
        self._profiles = {}

    def open(self):
        """Warm the PostgreSQL pool once for the lifetime of the app."""

        if not self.is_postgres or self._pool is not None:
            return

        from psycopg.rows import dict_row
        from psycopg_pool import ConnectionPool

        pool = ConnectionPool(
            self.database,
            min_size=1,
            max_size=4,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        pool.open(wait=True, timeout=30)
        self._pool = pool

    def close(self):
        """Release pooled connections and in-process caches."""

        pool, self._pool = self._pool, None
        if pool is not None:
            pool.close()

        with self._cache_lock:
            self._sessions.clear()
            self._profiles.clear()

    @contextmanager
    def connection(self):
        """Borrow a pooled PostgreSQL connection, or a short SQLite one."""

        if self.is_postgres:
            if self._pool is None:
                self.open()

            with self._pool.connection() as conn:
                with conn:
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
                conn.executescript(SQLITE_SCHEMA)

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

    def _remember_session(self, token, account, expires_at):
        """Keep the authenticated account in memory until its DB session ends."""

        now = time.time()
        if not self._cache_enabled or expires_at <= now:
            return

        with self._cache_lock:
            if len(self._sessions) > 256:
                self._sessions = {
                    key: value
                    for key, value in self._sessions.items()
                    if value[1] > now
                }
            self._sessions[token_digest(token)] = (dict(account), expires_at)

    def create_session(self, account, token, ttl):
        now = int(time.time())

        if isinstance(account, dict):
            account_id = account["id"]
            username = account.get("username")
        else:
            account_id = account
            username = None

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

        if username is not None:
            self._remember_session(
                token,
                {"id": account_id, "username": username},
                now + ttl,
            )

    def session_account(self, token):
        now = time.time()
        digest = token_digest(token)

        if self._cache_enabled:
            with self._cache_lock:
                cached = self._sessions.get(digest)
                if cached is not None:
                    account, expires_at = cached
                    if expires_at > now:
                        return dict(account)
                    self._sessions.pop(digest, None)

        with self.connection() as conn:

            row = self._execute(
                conn,
                """
                SELECT a.id, a.username, s.expires_at
                FROM accounts AS a
                JOIN auth_sessions AS s
                  ON s.account_id = a.id
                WHERE s.token_hash = ?
                  AND s.expires_at > ?
                """,
                (
                    digest,
                    int(now),
                ),
            ).fetchone()

            if not row:
                return None

            account = {"id": row["id"], "username": row["username"]}
            self._remember_session(token, account, int(row["expires_at"]))
            return account

    def revoke_session(self, token):
        with self.connection() as conn:

            self._execute(
                conn,
                "DELETE FROM auth_sessions WHERE token_hash = ?",
                (token_digest(token),),
            )

        with self._cache_lock:
            self._sessions.pop(token_digest(token), None)

    def load_profile(self, account_id):
        now = time.time()
        if self._cache_enabled:
            with self._cache_lock:
                cached = self._profiles.get(account_id)
                if cached is not None:
                    profile, expires_at = cached
                    if expires_at > now:
                        return dict(profile)
                    self._profiles.pop(account_id, None)

        with self.connection() as conn:

            row = self._execute(
                conn,
                f"""
                SELECT {matching_db.PROFILE_FIELDS}, updated_at
                FROM profiles
                WHERE account_id = ?
                """,
                (account_id,),
            ).fetchone()

            if not row:
                return None

            profile = matching_db.decode_profile(row)
            profile["updated_at"] = str(profile["updated_at"])

            with self._cache_lock:
                if self._cache_enabled:
                    self._profiles[account_id] = (
                        profile,
                        time.time() + PROFILE_CACHE_SECONDS,
                    )

            return dict(profile)

    def save_profile(self, account_id, values):
        with self.connection() as conn:

            sql = """
                INSERT INTO profiles (
                    account_id,
                    display_name,
                    contact_info,
                    city,
                    preferred_role,
                    languages,
                    programme,
                    open_roles,
                    programming,
                    github,
                    debugging,
                    web,
                    ai_agent
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(account_id)
                DO UPDATE SET
                    display_name = excluded.display_name,
                    contact_info = excluded.contact_info,
                    city = excluded.city,
                    preferred_role = excluded.preferred_role,
                    languages = excluded.languages,
                    programme = COALESCE(excluded.programme, profiles.programme),
                    open_roles = COALESCE(excluded.open_roles, profiles.open_roles),
                    programming = COALESCE(excluded.programming, profiles.programming),
                    github = COALESCE(excluded.github, profiles.github),
                    debugging = COALESCE(excluded.debugging, profiles.debugging),
                    web = COALESCE(excluded.web, profiles.web),
                    ai_agent = COALESCE(excluded.ai_agent, profiles.ai_agent),
                    updated_at = CURRENT_TIMESTAMP
            """

            open_roles = values.get("open_roles")

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
                    values.get("programme"),
                    json.dumps(open_roles, ensure_ascii=False) if open_roles is not None else None,
                    values.get("programming"),
                    values.get("github"),
                    values.get("debugging"),
                    values.get("web"),
                    values.get("ai_agent"),
                ),
            )

            row = self._execute(
                conn,
                f"""
                SELECT {matching_db.PROFILE_FIELDS}, updated_at
                FROM profiles
                WHERE account_id = ?
                """,
                (account_id,),
            ).fetchone()

            result = matching_db.decode_profile(row)
            result["updated_at"] = str(result["updated_at"])

        with self._cache_lock:
            if self._cache_enabled:
                self._profiles[account_id] = (
                    result,
                    time.time() + PROFILE_CACHE_SECONDS,
                )

        return dict(result)
