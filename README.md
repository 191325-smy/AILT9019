# AILT9019 — Teammate Matcher

The matching engine for a course project: it turns a pool of profiles into a
**team**. Instead of ranking classmates one by one, it picks people who cover
different roles, so the result can start working together immediately.

This folder is the **logic layer only** — accounts, the signup form, the web UI
and the HTTP API are built separately. Everything here is plain Python with no
web framework, so it can be imported by the backend rather than run as a site.

Built for AILT9019 (AI Literacy II, HKU). Runs on SQLite, needs no server, and
works with **zero installs**.

```bash
git clone https://github.com/191325-smy/AILT9019.git
cd AILT9019/matching
python3 seed.py              # builds ailt9019.db from schema.sql + seed.sql
python3 match.py alice_chen   # prints the filtered pool and the shortlist
```

Requires Python 3.9+. There is nothing to `pip install` for the commands above.

## What you should see

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
cd matching
cp .env.example .env      # then paste your key after DEEPSEEK_API_KEY=
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 match.py alice_chen   # source: model
```

`matcher.py` reads `matching/.env` on import and defaults to `deepseek:deepseek-chat`
when a key is present. One call, temperature 0, no agent and no tools: the model
returns `account_id` values with a one-sentence reason, and any id not in the
candidate list is discarded.

Keep `deepseek-chat`. `deepseek-reasoner` does not support the tool calling that
`with_structured_output` relies on, so it would fall back on every call.

If the key is missing, the packages are absent, or the request fails, the run
still completes with `source: fallback:<reason>` instead of a traceback.

## Repo layout

```
.
├── .gitignore
└── matching              the logic layer (this folder)
    ├── SETUP.md          detailed setup, error table, reset instructions
    ├── schema.sql        two tables: accounts, profiles
    ├── seed.sql          30 synthetic profiles (15 HK, 15 SH)
    ├── seed.py           applies both .sql files to ailt9019.db
    ├── db.py             the only file that writes SQL
    ├── filters.py        hard constraints + signals (pure, no I/O)
    ├── matcher.py        model call + deterministic fallback
    ├── match.py          CLI: load -> filter -> shortlist -> print
    ├── sample_pool.json  mirror of seed.sql, for the no-database path
    ├── requirements.txt  only needed for the model stage
    └── .env.example      template; the real .env is git-ignored
```

The web frontend and the backend that serves it are separate work; they are not
in this folder. To reuse this logic from a backend, import it rather than shell
out:

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
- The interface is a CLI. There is no signup form or web UI in this repository.
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
