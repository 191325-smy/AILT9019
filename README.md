# AILT9019 — Teammate Matcher

The matching engine for a course project: it turns a pool of profiles into a
**team**. Instead of ranking classmates one by one, it picks people who cover
different roles, so the result can start working together immediately.

This project has three parts:
- **`matching/`** - The matching logic layer (plain Python)
- **`backend/`** - FastAPI service for accounts, profiles, and matching
- **`ui/`** - Web frontend interface

Built for AILT9019 (AI Literacy II, HKU). Runs on SQLite, needs no server, and
works with **zero installs** for the CLI.

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/191325-smy/AILT9019.git
cd AILT9019
```

### 2. Seed the Database

```bash
cd matching
python seed.py              # builds ailt9019.db from schema.sql + seed.sql
cd ..
```

### 3. Start the Backend

**Windows:**
```bash
start-backend.bat
```

**Mac/Linux:**
```bash
chmod +x start-backend.sh
./start-backend.sh
```

Or manually:
```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: http://localhost:8000
API docs: http://localhost:8000/docs

### 4. Start the Frontend

**Windows:**
```bash
start-frontend.bat
```

**Mac/Linux:**
```bash
chmod +x start-frontend.sh
./start-frontend.sh
```

Or manually:
```bash
cd ui
python -m http.server 8001
```

Frontend will be at: http://localhost:8001

### 5. Use the Application

1. Open http://localhost:8001 in your browser
2. Register a new username with a password of at least 8 characters. Seeded accounts such as `alice_chen` have placeholder password hashes and cannot log in.
3. Complete your profile (city, role, languages)
4. Click "Run Matching Algorithm" to find teammates!

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
`source:` tells you whether the wording came from the model or from the
deterministic fallback.

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

## Using a real model

Out of the box nothing is called. To use DeepSeek:

```bash
python -m pip install -r backend/requirements-ai.txt
# Copy matching/.env.example to matching/.env only if .env does not exist.
# Fill DEEPSEEK_API_KEY locally; never commit or share the key.
python matching/check_model.py          # configuration only; no API call
python matching/check_model.py --live   # one real call with synthetic profiles
```

`matcher.py` reads `matching/.env` on import and defaults to
`deepseek:deepseek-flash` when a key is present. Restart the backend after
editing the file. The web UI's existing `/matches` request then invokes the
model and displays **AI Model** only when the model produced the result.

The model returns candidate IDs and reasons through structured tool output;
it has no external tools or agent loop. DeepSeek uses non-thinking mode to
support the forced tool choice, a 30-second timeout and no automatic retries.
Current model names and tool-choice requirements are documented by
[DeepSeek](https://api-docs.deepseek.com/api/create-chat-completion/).

If the key is missing, the packages are absent, or the request fails, the run
still completes with `source: fallback:<reason>` instead of a traceback.
The live check treats fallback as a failure rather than calling it AI success.

## Repo layout

```
.
── .gitignore
├── backend               FastAPI service (accounts, profiles, matching)
│   ├── app.py            Main API routes
│   ├── models.py         Request/response models
│   ├── store.py          Database operations
│   ├── security.py       Password hashing + tokens
│   ├── requirements.txt  Python dependencies
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
│   ├── sample_pool.json  JSON fixture data
│   └── requirements.txt  Model dependencies
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
| `source: fallback:ModuleNotFoundError` | key set but packages missing | `pip install -r requirements.txt` |
| `source: fallback:AuthenticationError` | bad or expired key | check `DEEPSEEK_API_KEY` in `.env` |
| `UNIQUE constraint failed` | `seed.sql` applied twice | `python3 seed.py --reset` |

`matching/SETUP.md` has the longer version, including how to read the raw tables.
