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
This initial browser check used deterministic fallback. See
[the recording walkthrough](../RECORDING.md) for a manual reproduction.

## Real AI integration

On 26 October 2026, the local ignored configuration was used for two successful
real DeepSeek API calls with synthetic profiles: one CLI verification and one
browser matching request. Both returned source `deepseek:deepseek-flash`, five
candidates and non-empty reasons. The browser displayed **AI Model**, returned
same-city picks, and had zero page-script errors; the matching interaction took
approximately 2.5 seconds. Normal account data was preserved by using a separate
test database for the browser check. No key or user token is included here.

Two additional model tests pass using the real DeepSeek SDK and structured
parser against mock HTTP: supported non-thinking tool requests parse correctly,
and HTTP 401 is labelled as fallback without an automatic retry. Run them with:

```bash
python -m pip install -r backend/requirements-ai.txt
python -m unittest discover -s matching/tests -v
```

The combined result is **23 backend tests plus 2 model HTTP contract tests
passed**. A successful live smoke call proves connectivity and basic parsing;
it does not establish recommendation quality across many cases. Time-overlap
ranking, mutual-consent contact sharing and previously documented model-output
edge cases remain outside this verification.

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
