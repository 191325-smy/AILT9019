# AILT9019 — Teammate Matcher

The matching engine for a course project: it turns a pool of profiles into a
**team**. Instead of ranking classmates one by one, it picks people who cover
different roles, so the result can start working together immediately.

This project has three parts:
- **`matching/`** - The matching logic layer (plain Python)
- **`backend/`** - FastAPI service for accounts, profiles, and matching
- **`ui/`** - Web frontend interface

Built for AILT9019 (AI Literacy II, HKU). Runs on SQLite, needs no server, and
works with **zero installs** for the CLI. This is an AI application, so adding a
DeepSeek API key is recommended; without one, matching still returns a ranked
shortlist from the deterministic fallback.

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/191325-smy/AILT9019.git
cd AILT9019
```

### 2. Install Dependencies

The repository root has one `requirements.txt` covering all three parts: the
matching model stage, the FastAPI backend and the backend tests.

```bash
python3 -m venv .venv            # Windows: python -m venv .venv
source .venv/bin/activate        # Windows cmd: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

On Windows PowerShell the activate line is `.venv\Scripts\Activate.ps1`.

The CLI, seeder and filter logic still run on the standard library alone; these
packages are needed for the model call, the API and its tests.

### 3. Seed the Database

```bash
python matching/seed.py     # builds matching/ailt9019.db from schema.sql + seed.sql
```

Re-running is safe: it only seeds an empty database. `start-backend.sh` does
this for you when `matching/ailt9019.db` is missing.

### 4. Start the Backend

**Windows:**
```bash
start-backend.bat
```

**Mac/Linux:**
```bash
chmod +x start-backend.sh
./start-backend.sh
```

Or manually, from the repository root:
```bash
source .venv/bin/activate
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Backend will be at: http://localhost:8000
API docs: http://localhost:8000/docs

### 5. Start the Frontend

**Windows:**
```bash
start-frontend.bat
```

**Mac/Linux:**
```bash
chmod +x start-frontend.sh
./start-frontend.sh
```

Or manually, from the repository root:
```bash
python -m http.server 8001 --directory ui
```

Frontend will be at: http://localhost:8001

### 6. Use the Application

1. Open http://localhost:8001 in your browser
2. Register a new username with a password of at least 8 characters. Seeded accounts such as `alice_chen` have placeholder password hashes and cannot log in.
3. Complete your profile (city, role, languages)
4. Click "Run Matching Algorithm" to find teammates!

Matching runs without any setup, but this is an AI application: add a DeepSeek
API key for the intended experience. Put it in `matching/.env`:

```bash
cp matching/.env.example matching/.env     # then set DEEPSEEK_API_KEY=sk-...
```

The backend reads that file at startup, so restart it after editing. Setup
details and model selection are in
[Using the DeepSeek API](#using-the-deepseek-api-recommended).

## CLI Usage (without web UI)

You can also use the matching engine directly from command line:

```bash
cd matching
python seed.py              # builds ailt9019.db from schema.sql + seed.sql
python match.py alice_chen  # prints the filtered pool and the shortlist
```

Requires Python 3.9+. There is nothing to `pip install` for the CLI.

## API Endpoints

### Authentication
- `POST /auth/register` - Register new account
- `POST /auth/login` - Login (returns token)
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout

### Profiles
- `GET /profiles/me` - Get your profile
- `PUT /profiles/me` - Update your profile

### Matching
- `POST /matches` - Run matching algorithm
- `GET /matches/me` - Get your profile (alias)

`POST /matches` calls the DeepSeek API when `DEEPSEEK_API_KEY` is set in
`matching/.env`; without it the response comes from the deterministic fallback.
See [Using the DeepSeek API](#using-the-deepseek-api-recommended).

Account, profile and matching routes require `Authorization: Bearer <token>`,
except registration and login. Health and API documentation are public.

For a complete browser walkthrough and recording steps, see
[RECORDING.md](RECORDING.md). Verification results are in
[backend/TESTING.md](backend/TESTING.md).

## What you should see (CLI)

```
me: Alice Chen (HK, Frontend)
pool: 30   kept: 12   dropped: 18
  dropped: 14 different cohort (SH), 3 already in a team, 1 that's you

shortlist: 5 of 12   (source: fallback:no DEEPSEEK_API_KEY or MATCH_MODEL)
  1. David Zhao     Agentic Development  david@test.com
     reason: Agentic Development pairs with your frontend; can talk in English, Mandarin.
  2. Grace Wu       Backend              grace@test.com
     reason: Backend pairs with your frontend; can talk in English, Mandarin.
  3. Henry Xu       Database             henry@test.com
     reason: Database pairs with your frontend; can talk in English.
  4. Emma Sun       Other                emma@test.com
     reason: Other pairs with your frontend; can talk in Mandarin.
  5. Bob Liu        Backend              bob@test.com
     reason: Backend pairs with your frontend; can talk in English.
```

Pick 5 repeats `Backend` on purpose — see [How matching works](#how-matching-works).
This sample is the no-key output; with a key the same run prints
`source: deepseek:deepseek-chat` (or whichever model `MATCH_MODEL` selects) and
the reasons come from the model.

Other profiles worth trying:

| Command | Shows |
|---|---|
| `python3 match.py grace_wu` | the same rules mirrored: Alice becomes *your* top pick |
| `python3 match.py peter_song` | cohort isolation — Peter is SH, no HK profiles appear |
| `python3 match.py alice_chen --verbose` | one line per dropped profile instead of a summary |
| `python3 match.py --from-json sample_pool.json alice_chen` | the same result with no database at all |

## How matching works

Three stages, each in its own file:

```
profiles ──▶ 1. hard filter ──▶ 2. signals ──▶ 3. shortlist
              filters.py          filters.py       matcher.py
```

**1. Hard filter (`filters.hard_filter`).** Two rules, nothing else:

- same `city` (`HK` or `SH`) — two separate cohorts
- `in_team = 0` — anyone already placed is out

Each drop keeps a reason, which is why `--verbose` can explain every exclusion.

**2. Signals (`filters.add_signals`).** For each survivor: which languages are
shared with you, and whether their role complements yours.

**3. Shortlist (`matcher.pick`).** One structured call to the model, or a
deterministic fallback when no key is configured. Either way the goal is a team,
not a ranking: prefer classmates who fill a role the team does not have yet
(your own role counts as filled), then fill the remaining slots with the best of
the rest.

Role diversity is an **objective, not a constraint**. With five role values in
the fixtures, a student plus four picks covers everything available, so the fifth
pick necessarily repeats a role. That is the intended behaviour — duplicates are
allowed, they just rank last.

The model never sees `contact_info`. Contact details are attached after the picks
are chosen, so they only appear for people who actually made the shortlist.

## Using the DeepSeek API (recommended)

Adding a key is recommended: this is an AI application, and with a key DeepSeek
writes the shortlist and a reason for every pick. Without one, matching still
works - the shortlist is ranked by rule and every result says `fallback`. The
install from step 2 already includes the model packages.

**1. Get a key.** Create one at <https://platform.deepseek.com/api_keys>; it
looks like `sk-...`.

**2. Create the env file**, from the repository root with the environment from
step 2:

```bash
cp matching/.env.example matching/.env
```

**3. Paste the key**, and the model for the current Flash API, into
`matching/.env`, so the file looks like this:

```
# matching/.env
DEEPSEEK_API_KEY=sk-...
MATCH_MODEL=deepseek:deepseek-flash
```

Without `MATCH_MODEL` the matcher uses `deepseek:deepseek-chat`, so that line is
optional; the original default is unchanged. `matching/.env` is git-ignored, so
the key is never committed. An exported variable wins over the file if you would
rather not store it: `DEEPSEEK_API_KEY=sk-... ./start-backend.sh`.

**4. Restart the backend** so it re-reads the file - `matcher.py` loads
`matching/.env` once at import:

```bash
# Ctrl+C in the backend window, then
./start-backend.sh
```

Then match from the UI, or from the CLI to see the raw result:

```bash
python matching/match.py alice_chen      # source: deepseek:deepseek-flash
```

The results page shows **AI Model** when the call succeeded and
**Deterministic Fallback** when it did not; the CLI prints the reason in the
`source:` field. No separate model service or check command is needed.

One call, temperature 0, no agent and no tools: the model returns `account_id`
values with a one-sentence reason, and any id outside the candidate list is
discarded. Flash and the V4 models reject a forced structured-output tool in
thinking mode, so `matcher.py` disables thinking for those ids.
`deepseek-reasoner` remains unsupported because it has no tool calling at all.
To use another provider, set `MATCH_MODEL` in the same file, for example
`MATCH_MODEL=openai:gpt-4o-mini` (needs `langchain-openai` installed).

If the key is missing, the packages are absent, or the request fails, the run
still completes with `source: fallback:<reason>` instead of a traceback.

## Repo layout

```
.
── .gitignore
├── requirements.txt      One environment: matching + API + tests
├── backend               FastAPI service (accounts, profiles, matching)
│   ├── app.py            Main API routes
│   ├── models.py         Request/response models
│   ├── store.py          Database operations
│   ├── security.py       Password hashing + tokens
│   └── tests/            API tests
├── matching              The matching logic layer
│   ├── SETUP.md          Detailed setup instructions
│   ├── schema.sql        Database schema
│   ├── seed.sql          30 synthetic profiles
│   ├── seed.py           Database seeder
│   ├── db.py             Database readers
│   ├── filters.py        Hard constraints + signals
│   ├── matcher.py        Model call + fallback
│   ├── match.py          CLI interface
│   └── sample_pool.json  JSON fixture data
── ui                    Web frontend
│   ├── index.html        Login page
│   ├── register.html     Registration page
│   ├── dashboard.html    Main dashboard
│   ├── results.html      Match results
│   ├── edit-profile.html Profile editor
│   ├── css/style.css     Styling
│   ├── js/app.js         Frontend logic
│   └── data/mock-data.json  Demo data
├── start-backend.sh      Backend startup script (Mac/Linux)
├── start-backend.bat     Backend startup script (Windows)
├── start-frontend.sh     Frontend startup script (Mac/Linux)
└── start-frontend.bat    Frontend startup script (Windows)
```

The accounts/profile and matching APIs are in `backend/`, connected to the web UI.
Mutual-consent contact sharing and time-overlap preferences remain future work.
From the `matching/` directory,
the existing logic can be reused directly:

```python
import db, matcher
from filters import candidates_for_model

conn = db.get_conn()
me = db.load_profile_by_username(conn, "alice_chen")
candidates, dropped, pool = candidates_for_model(me, db.load_pool(conn))
picks, source = matcher.pick(me, candidates)
```

`matcher.pick()` returns `[{"profile": {...}, "reason": "..."}]` plus the
`source` string, so an API layer can serialise it directly.

`ailt9019.db` is generated and git-ignored — `python3 seed.py` recreates it in
under a second. `python3 seed.py --reset` rebuilds it after a schema change.

## Data and scope

This is a course demo, not a product:

- All 30 profiles are **synthetic**. Names, emails and preferences in `seed.sql`
  are invented; `contact_info` values are placeholders like `david@test.com`.
- SQLite is a single file, chosen so the workflow is reproducible offline.
- The project has a CLI (`matching/match.py`), a FastAPI backend (`backend/`),
  and a web UI (`ui/`). All three can be used independently or together.
- `in_team` is set only by `seed.sql`; the logic never flips it, so the same
  input always produces the same pool.

## When it breaks

| Symptom | Cause | Fix |
|---|---|---|
| `no such table: profiles` | no database file | `python3 seed.py` |
| `no account with username '...'` | typo, or database not seeded | usernames look like `alice_chen` |
| `source: fallback:ModuleNotFoundError` | key set but packages missing | `pip install -r requirements.txt` from the repository root |
| `source: fallback:AuthenticationError` | bad or expired key | check `DEEPSEEK_API_KEY` in `matching/.env` |
| `UNIQUE constraint failed` | `seed.sql` applied twice | `python3 seed.py --reset` |

`matching/SETUP.md` has the longer version, including how to read the raw tables.
