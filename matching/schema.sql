-- AILT9019 teammate matcher - demo schema (SQLite)
-- Source of truth is this file; seed.py applies it and then seed.sql.
--
--   python seed.py              # creates ailt9019.db if missing, seeds if empty
--   python seed.py --reset      # drops and rebuilds both tables
--
-- Two tables. Match results are NOT stored: a shortlist is computed and rendered
-- once, so there is nothing to persist or keep in sync.

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
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);
