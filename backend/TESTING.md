# Backend verification

Verified on **25 October 2026**, using Python 3.12.14 on Windows, against the
existing matching baseline `b1c81c484b571e59b25583b28e9527b635f4fde2` plus this
backend addition. No original matching source or fixture files were changed.

## Automated API suite

```bash
python -m pip install -r backend/requirements-test.txt
python -m unittest discover -s backend/tests -v
```

Result: **19 tests passed; 0 failures; 0 errors.**

The suite checks:

- Register, log in, save/read a profile, and log out.
- Normalised usernames, duplicates and validation-error redaction.
- Independently salted password hashes and hashed session tokens.
- Wrong passwords, missing/tampered/expired tokens and session revocation.
- Separation of two users' data and rejection of client-supplied ownership or
  team-status fields.
- Profile updates that preserve the existing account and team status.
- Profile validation, literal Unicode/SQL-looking text and empty language lists.
- Data and unexpired sessions surviving an app restart.
- Preservation of the 30 seeded students and safe rejection of placeholder
  passwords; newly registered users coexist with those fixtures.
- Saved profiles remaining readable by `matching.db`.
- Private responses using `Cache-Control: no-store` and explicit-origin CORS.

The test databases are isolated under the ignored `.test-tmp/` directory and
their SQLite handles are closed before cleanup. No AI API is used.

## Real HTTP smoke check

A temporary single-worker Uvicorn service was started on `127.0.0.1` with a
disposable database. Actual HTTP requests verified `/health`, `/docs` and
`/openapi.json`, then registration, login, profile save/read, logout and rejection
of the logged-out token. The service was shut down and temporary data cleanup
completed successfully.

Result: **PASS**. This confirms local service operation; it does not claim that
a frontend has been connected or a public deployment has been tested.

## Tested direct dependencies

| Package | Version |
|---|---|
| FastAPI | 0.162.0 |
| Pydantic | 2.14.1 |
| Uvicorn | 0.54.0 |
| pwdlib with Argon2 | 0.3.1 |
| HTTPX (tests) | 0.28.1 |

The requirement files pin these tested direct versions. Backend setup and the
frontend request contract are in [README.md](README.md).
