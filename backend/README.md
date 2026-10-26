# Accounts and profile API

This FastAPI backend adds registration, login, logout and authenticated profile
reads/writes and teammate matching to the existing SQLite project. It uses the
existing `accounts` and `profiles` tables and adds an `auth_sessions` table.
The web UI in `ui/` calls these APIs. Mutual-consent contact exchange remains
future work; use synthetic contact details for this course demonstration.

## Start locally

Use Python 3.10 or newer and run these commands from the repository root:

```bash
python -m venv .venv
```

Activate the environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or in macOS/Linux shells:

```bash
source .venv/bin/activate
```

Install and start:

```bash
python -m pip install -r requirements.txt
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for interactive API documentation. First call
register, then login. Copy the returned `access_token` into **Authorize** to try
the protected routes. `GET /health` returns `{"status":"ok"}`.

On first startup, a missing database is created from `matching/schema.sql`
without adding demo accounts. Existing accounts and profiles are preserved.

## Configuration

The app reads process environment variables; it does not automatically load
`.env` files.

| Variable | Default | Meaning |
|---|---|---|
| `DB_PATH` | `matching/ailt9019.db` in this repository | SQLite file used by the backend |
| `SESSION_TTL_SECONDS` | `3600` | Token lifetime, from 1 to 604800 seconds |
| `ALLOWED_ORIGINS` | `http://localhost:8001,http://127.0.0.1:8001` | Comma-separated frontend origins allowed by CORS |

For a frontend running at `http://localhost:5173`, set this before starting
Uvicorn in PowerShell:

```powershell
$env:ALLOWED_ORIGINS = "http://localhost:5173"
$env:DB_PATH = "C:\path\to\demo.db"
```

Or in a macOS/Linux shell:

```bash
export ALLOWED_ORIGINS=http://localhost:5173
export DB_PATH=/path/to/demo.db
```

Omit `DB_PATH` to share the default database with the existing matching CLI.
Use the actual frontend origin, including protocol and port: `localhost` and
`127.0.0.1` are different origins. Wildcard `*` origins are rejected. The API
uses explicit Bearer headers, not login cookies; cookie credentials are disabled.
For a deployed frontend/backend, serve the API over HTTPS.

## Request contract

Requests and responses use JSON except the empty successful logout response.
Protected routes require `Authorization: Bearer <access_token>`.

| Method and path | Input | Success |
|---|---|---|
| `POST /auth/register` | `username`, `password` | `201` with `{id, username}`; does not log in |
| `POST /auth/login` | `username`, `password` | `200` with `{access_token, token_type: "bearer", expires_in}` |
| `GET /auth/me` | Bearer token | `200` with `{id, username}` |
| `POST /auth/logout` | Bearer token | `204`, no response body; revokes that token |
| `GET /profiles/me` | Bearer token | `200` with the current user's profile |
| `PUT /profiles/me` | Bearer token and full editable profile | `200` with the saved profile |
| `POST /matches` | Bearer token; a saved profile is required | `200` with `picks`, `source`, `stats` and `filter_summary` |
| `GET /matches/me` | Bearer token | Alias for the current profile |

Registration/login usernames are trimmed and lowercased. They must contain
3-32 letters `a-z`, digits or underscores. Passwords must contain 8-128
characters. The backend saves Argon2 password hashes, never the submitted
password. Login tokens are opaque random values; only their SHA-256 digests
are stored in SQLite. Expired or logged-out tokens cannot access protected routes.
Accounts, saved profiles and unexpired sessions survive backend restarts when
the same database file is used.

The editable profile body is:

```json
{
  "display_name": "Demo Student",
  "contact_info": "demo@test.com",
  "city": "HK",
  "preferred_role": "Backend",
  "languages": ["Mandarin", "English"]
}
```

- `display_name`: required, 1-100 characters after trimming.
- `contact_info`: optional string up to 200 characters, or `null`.
- `city`: `HK` or `SH`.
- `preferred_role`: `Frontend`, `Backend`, `Database`, `Agentic Development` or `Other`.
- `languages`: a required list containing `Mandarin`, `Cantonese` and/or `English`.
  An empty list is accepted; repeated values are deduplicated.

`PUT` saves the complete editable profile, so send every required field on each
save. Omitting `contact_info` clears it to `null`. The response also contains
`account_id`, `in_team` and `updated_at`. Those are server-owned fields: do not
copy them back into the editable request. The backend uses the authenticated
account ID and preserves an existing `in_team` value.

Unknown input fields, including `account_id` and `in_team`, are rejected rather
than used to choose another account. There is no route for editing another
person's profile.

| Error | Meaning |
|---|---|
| `401` | Wrong login details, missing/invalid token, or expired/revoked session |
| `404` on `GET /profiles/me` | This account has not saved a profile yet |
| `409` on registration | Username already registered, including case variants |
| `422` | Invalid or extra input fields; details identify the affected fields |

Errors use `{"detail": ...}`. Validation errors omit submitted values so
passwords and contact details are not echoed back. Account/profile responses
are marked `Cache-Control: no-store`.

## Frontend example

The frontend sends requests; the backend checks identity and writes SQLite.
Hold the token in memory for this demo and send it on protected calls. A page
reload clears this example's token, requiring another login; the saved profile
remains in the database. Do not put the token into a URL.

```javascript
const API = "http://127.0.0.1:8000";
let token = null;

async function request(path, method = "GET", body) {
  const response = await fetch(`${API}${path}`, {
    method,
    headers: {
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data = response.status === 204 ? null : await response.json();
  if (!response.ok) {
    if (response.status === 401) token = null;
    throw new Error(JSON.stringify(data?.detail ?? data));
  }
  return data;
}

// Register once. Use a new synthetic username if this one already exists.
await request("/auth/register", "POST", {
  username: "demo_student",
  password: "DemoPassword123!",
});

const login = await request("/auth/login", "POST", {
  username: "demo_student",
  password: "DemoPassword123!",
});
token = login.access_token;

const account = await request("/auth/me");
const saved = await request("/profiles/me", "PUT", {
  display_name: "Demo Student",
  contact_info: "demo@test.com",
  city: "HK",
  preferred_role: "Backend",
  languages: ["Mandarin", "English"],
});
const profile = await request("/profiles/me");

await request("/auth/logout", "POST");
token = null;
```

Set `ALLOWED_ORIGINS` to the origin of the page running this code. The example
password is public demo data; it is not a credential for any seeded account.

## Existing fixtures and matching

To add the repository's 30 synthetic fixture profiles to a new demo database,
run this **before** starting the API:

```bash
python matching/seed.py
```

Fixture values such as `hash1` are placeholders, not valid login hashes. Register
a new test account through the API to obtain usable login credentials. Starting
the backend does not replace the fixture passwords or reset existing data.

The matching CLI can read profiles saved by this API when both use the same
database file. With the default database:

```bash
python matching/match.py demo_student
```

If you set `DB_PATH`, give both processes the same absolute path. Save a complete
profile before trying to match the new account. `seed.py` does not add fixtures
to an already-populated profile table. Its `--reset` option drops and recreates
the account/profile tables: use a separate disposable database for reset-based
experiments, not the file containing saved accounts and profiles.

## Tests

Both commands run from the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s backend/tests -v
```

The API tests use isolated temporary databases. They do not need an AI API key
or a running frontend. The application factory is also available for isolated
test/deployment configuration:

```python
from backend.app import create_app

app = create_app(
    db_path="/path/to/test.db",
    session_ttl_seconds=3600,
    allowed_origins=["http://localhost:5173"],
)
```
