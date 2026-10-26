# Backend verification

Verified on **26 October 2026**, using Python 3.12.14 on Windows, against
integration baseline `0a5b0e3d0dc3765dbc1c6878b5d13ba64e997c97` plus these
startup and integration fixes. Fixtures are unchanged; the matching import
supports both package/API use and direct CLI use.

## Automated API suite

```bash
python -m pip install -r backend/requirements-test.txt
python -m unittest discover -s backend/tests -v
```

Result: **23 tests passed; 0 failures; 0 errors.**

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
- Matching uses the same configured database as accounts and profiles, returns
  five unique eligible same-city candidates with reasons, and excludes self.
- Matching rejects missing login/missing profile, handles an empty pool, and
  accepts CORS preflight from the default recording frontend.

The test databases are isolated under the ignored `.test-tmp/` directory and
their SQLite handles are closed before cleanup. No AI API is used.

## Real HTTP smoke check

A temporary single-worker Uvicorn service was started on `127.0.0.1` with a
disposable database. Actual HTTP requests verified `/health`, `/docs` and
`/openapi.json`, then registration, login, profile save/read, logout and rejection
of the logged-out token. The service was shut down and temporary data cleanup
completed successfully.

Result: **PASS**. Public deployment has not been tested.

## Browser workflow

Edge browser automation exercised the actual UI against local Uvicorn and HTTP
servers, using an isolated database seeded with the 30 synthetic classmates:

- Registration creates an account, signs in and saves the full profile.
- Dashboard reload fetches the saved profile from the backend.
- HK matching displays five candidates with reasons and the fallback label.
- Editing city to SH changes the saved data and returns five SH candidates.
- Logout revokes the server session; signing in again restores the edited data.

Result: **PASS**, with 17 actual API responses and zero page-script errors.
The browser check used deterministic fallback; it does not validate live-model
quality, time-overlap ranking or mutual-consent contact sharing. See
[the recording walkthrough](../RECORDING.md) for a manual reproduction.

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

## Real model verification

The existing matcher was also verified with the current DeepSeek Flash API
on 26 October 2026, using only synthetic profiles. The original call with
Flash fell back on a request error; disabling thinking for its structured
tool output allowed the API to return five candidates with non-empty reasons.
The webpage was previously verified to display AI Model for real replies.
This verifies connectivity, not recommendation quality. The auxiliary AI
checker, wrapper requirements and two SDK contract tests were removed as
unnecessary additions; the 23 backend regression tests remain.
