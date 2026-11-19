-- PostgreSQL schema for the shared AILT9019 database.
-- Apply once to an empty database before starting the backend:
--   psql "$DATABASE_URL" -f matching/schema.sql
--
-- The running backend only creates auth_sessions itself; accounts and profiles
-- must already exist, which is what this file provides.

CREATE TABLE IF NOT EXISTS accounts (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    account_id BIGINT PRIMARY KEY
        REFERENCES accounts(id) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    contact_info TEXT,
    city TEXT,
    preferred_role TEXT,
    languages TEXT,
    in_team SMALLINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    programme VARCHAR(40),
    open_roles TEXT,
    programming SMALLINT,
    github SMALLINT,
    debugging SMALLINT,
    web SMALLINT,
    ai_agent SMALLINT
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    token_hash TEXT PRIMARY KEY,
    account_id BIGINT NOT NULL
        REFERENCES accounts(id) ON DELETE CASCADE,
    expires_at BIGINT NOT NULL
);

CREATE INDEX IF NOT EXISTS auth_sessions_expiry
    ON auth_sessions(expires_at);

CREATE INDEX IF NOT EXISTS profiles_city_pool
    ON profiles(city, in_team);

-- Suggested demo fixtures: register through the UI or insert synthetic rows.
-- contact_info must stay synthetic; never commit real personal data.
