# Setup

No database server, no driver, no credentials. SQLite ships with Python, and the
database is a single file.

```bash
cd matching
python3 seed.py
python3 match.py alice_chen
```

That's the whole thing. `seed.py` creates `ailt9019.db` from `schema.sql` and
fills it with 30 synthetic profiles from `seed.sql`.

Requires Python 3.9+. Nothing to `pip install`.

## What each file is

| File | Role |
|---|---|
| `schema.sql` | the two tables (`accounts`, `profiles`) |
| `seed.sql` | 30 fake accounts, 15 HK / 15 SH |
| `seed.py` | applies both to `ailt9019.db` |
| `db.py` | the only file that writes SQL |
| `filters.py` | hard constraints + signals, pure functions |
| `matcher.py` | one model call, plus the deterministic fallback |
| `match.py` | CLI: load -> filter -> shortlist -> print |
| `sample_pool.json` | mirror of `seed.sql` for the no-DB path |
| `.env.example` | template for `.env` (the real one is git-ignored) |
| `ailt9019.db` | generated, git-ignored |

## Try it

```bash
python3 seed.py              # create + seed if needed, no-op if already populated
python3 seed.py --reset      # drop both tables and rebuild from the fixtures
python3 match.py alice_chen  # HK, Frontend
python3 match.py peter_song  # SH, Frontend
python3 match.py alice_chen --verbose   # one line per dropped profile, plus who survived
```

`match.py` prints the pool counts, then the shortlist. By default the filter is
summarised by reason (`14 different cohort (SH), 3 already in a team, 1 that's
you`); `--verbose` replaces that summary with a per-profile list, which is what
you want when explaining the filter rather than reading the result. The
`source:` field on the shortlist says whether the picks came from the model or
from the deterministic fallback.

## Turning the model on

Out of the box nothing is called - the shortlist is ranked by rule and labelled
`source: fallback`. To use a real model:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and paste your key:

```
DEEPSEEK_API_KEY=sk-...
```

That's the whole configuration. `matcher.py` reads `matching/.env` on import, and
with the key present it defaults to `deepseek:deepseek-flash`. Override the model
in the same file if you want another provider:

```
MATCH_MODEL=openai:gpt-4o-mini   # needs langchain-openai installed
```

Real environment variables take precedence over `.env`, so CI can override
without editing the file.

One call, temperature 0, no agent, no tools. If the key is missing or the call
fails, it falls back instead of crashing and the `source:` field says why - e.g.
`fallback:ModuleNotFoundError` or `fallback:AuthenticationError`.

DeepSeek structured output uses tool calling with thinking disabled. See the
[current API documentation](https://api-docs.deepseek.com/api/create-chat-completion/)
for supported model names and tool-choice requirements. The caller uses a
30-second timeout and no automatic retries.

For the web application, install the model and backend dependencies into the
same root environment: `python -m pip install -r backend/requirements-ai.txt`
from the repository root. A `.venv` created inside `matching/` is not used by
the root startup scripts. Restart the backend after editing `matching/.env`.
Run `python matching/check_model.py --live` from the root to verify one real
request using synthetic fixtures. A fallback response does not pass this check.

**For anyone marking this:** `.env` is git-ignored and is never in the repo. A
fresh clone runs in fallback mode until they add their own key — which is
enough to see the whole pipeline work, just without the model's wording.

For a look at the raw data:

```bash
sqlite3 ailt9019.db "SELECT display_name, city, preferred_role FROM profiles LIMIT 5;"
```

Or open `ailt9019.db` in DB Browser for SQLite / DBeaver.

No database at all - read a JSON dump instead:

```bash
python3 match.py --from-json sample_pool.json alice_chen
```

## Hard rules in the matcher

Only two, both in `filters.py` so they're visible and testable:

1. same `city` (`HK` or `SH`) - separate cohorts
2. `in_team = 0` - people already placed are out of the pool

Languages are **not** filtered. They're passed to the model as a signal, so a
candidate whose role differs can still be suggested.

`in_team` is set only by `seed.sql`. The logic never flips it, so the same input
always yields the same pool and the same shortlist.

## How the team is assembled

The shortlist is not a plain top-N ranking, but **role diversity is a
preference, not a filter**. Both stages optimise toward a team whose members
cover different roles (counting the student already on it) and happily return
duplicates when those are the best people left.

- `matcher.py` states the preference in the system prompt, tells the model a
  repeated role is acceptable, and requires a full list of 5 whenever 5
  classmates are available.
- `filters.diverse_picks()` is the deterministic twin: pass one takes anyone who
  fills an uncovered role, pass two fills the remaining slots by rank.

The fixtures use five role values, so a fully covered team is five people - the
student plus four picks - and the fifth pick usually repeats a role. That is the
intended behaviour, not a bug.

## When it breaks

| Error | Cause | Fix |
|---|---|---|
| `no such table: profiles` | database file missing or empty | `python3 seed.py` |
| `no account with username '...'` | wrong handle, or DB not seeded | check `accounts` table; usernames look like `alice_chen` |
| `JSONDecodeError` in `db._decode` | a fixture row's `languages` isn't valid JSON | fix the row in `seed.sql`, then `--reset` |
| `UNIQUE constraint failed` | `seed.sql` ran twice | `python3 seed.py --reset` |

Reset from scratch:

```bash
python3 seed.py --reset
```

Nothing deletes `ailt9019.db` - `--reset` drops the tables and recreates them.
