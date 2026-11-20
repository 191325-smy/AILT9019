# Browser reproduction and demo cases

The saved evidence uses the unchanged application/UI at baseline 81886ac with the existing test-only SQLite app-factory option. It is not a claim that shared PostgreSQL or the public deployment was tested. Screenshots and snapshots are under `results/browser/`.

## Start an isolated test run

Activate the project environment. Make sure ports 8000 and 8001 are available; do not stop someone else's service. In the first terminal, from the repository root:

```text
python -m uvicorn evaluation.demo_app:app --host 127.0.0.1 --port 8000
```

To include an actual model call, set `EVALUATION_KEY_FILE` to the absolute path of your existing private `.env` before starting this command. In PowerShell: `$env:EVALUATION_KEY_FILE = 'C:\private\matching.env'`; in a POSIX shell: `export EVALUATION_KEY_FILE=/private/matching.env`. The adapter selects only key/model, never the database URL. A fresh disposable database is created for every process start; no live application data is used.

In a second terminal:

```text
python -m http.server 8001 --bind 127.0.0.1 --directory ui
```

Open `http://localhost:8001/index.html`.

## Recorded scenarios

| ID | Steps | Expected / observed evidence |
|---|---|---|
| UI01 | Register `evaluation_browser` with synthetic name/email, HK, Frontend, Computer Science, English, open Database role, Programming and Web skills. | Saved dashboard contains the supplied programme, roles and skills. `profile.txt`, `profile.png`. |
| UI02 | Reload the dashboard. | Stored profile is fetched and rendered again. Checked during the recorded run; same profile evidence. |
| UI03 | Leave AI on and run matching once with the configured private model key. | Five HK candidates with reasons and AI Model label. `ai-results.txt`, `ai-results.png`. This is the additional real API call. |
| UI04 | Edit city to SH, save, turn AI off, run matching. | Five SH candidates with Deterministic (AI off) label. `sh-ai-off.txt`, `sh-ai-off.png`. |
| UI05 | Logout; attempt login with an intentionally wrong password. | Readable Invalid or expired login credentials error; no successful sign-in. |
| UI06 | Login with the test account's correct password. | Edited city and all new preferences restored. `relogin-profile.txt`. |
| UI07 | Logout and stop only this temporary backend. Start a new empty test backend as below; register the only student and run matching. | Zero eligible/recommended, No eligible candidates and No matches found; no provider call. `empty-pool.txt`, `empty-pool.png`. |

Use a synthetic password of at least eight characters. Seeded fixture accounts have placeholder hashes and cannot log in. Do not record a real password/key screen or browser storage. Stop the test services when finished.

## Empty-pool run for the final demo

After logging out and stopping this test backend, set `EVALUATION_EMPTY_POOL=1` and start the same `evaluation.demo_app:app` command. PowerShell: `$env:EVALUATION_EMPTY_POOL='1'`; POSIX: `export EVALUATION_EMPTY_POOL=1`.

Register `evaluation_boundary`, name `Boundary Student`, HK, Frontend, Applied AI and English. The database contains only this student. Click Run Matching Algorithm once. Show the total=1, eligible=0, recommended=0 and readable empty-result message continuously in the video. This is an expected boundary pass, distinct from the four failing product tests. Remove that environment flag before the next normal test run.

The browser scenarios were performed through a real browser; `results/browser/results.json` records their outcomes. This checklist is a reproducible manual workflow, not a claim that the Python offline runner drives a browser automatically.
