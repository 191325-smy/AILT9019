# Setup

The matching layer reads a PostgreSQL database. There is no local file:
`DATABASE_URL` in `matching/.env` is the only configuration, and the CLI stops
with a clear error if it is missing. The `accounts` and `profiles` tables must
already exist in that database.

```bash
cd ..                                        # repository root
cp matching/.env.example matching/.env       # then set DATABASE_URL
source .venv/bin/activate
python -m pip install -r requirements.txt    # psycopg for PostgreSQL
cd matching
python match.py alice_chen
```

Requires Python 3.9+.

## What each file is

| File | Role |
|---|---|
| `db.py` | the only file that writes SQL |
| `filters.py` | hard constraints + signals, pure functions |
| `matcher.py` | one model call, plus the deterministic fallback |
| `match.py` | CLI: load -> filter -> shortlist -> print |
| `sample_pool.json` | mirror of the fixtures for the no-DB path |
| `.env.example` | template for `.env` (the real one is git-ignored) |

## Try it

```bash
python match.py alice_chen  # HK, Frontend
python match.py peter_song  # SH, Frontend
python match.py alice_chen --verbose   # one line per dropped profile, plus who survived
```

`match.py` prints the pool counts, then the shortlist. By default the filter is
summarised by reason (`14 different cohort (SH), 3 already in a team, 1 that's
you`); `--verbose` replaces that summary with a per-profile list, which is what
you want when explaining the filter rather than reading the result. The
`source:` field on the shortlist says whether the picks came from the model or
from the deterministic fallback.

## Turning the model on

Out of the box nothing is called - the shortlist is ranked by rule and labelled
`source: fallback`. To use a real model, work from the repository root so the
shared environment from the README is used:

```bash
cd ..                                   # repository root
source .venv/bin/activate
python -m pip install -r requirements.txt
cp matching/.env.example matching/.env
```

Then open `matching/.env` and paste your key:

```
DEEPSEEK_API_KEY=sk-...
```

That's the whole configuration. `matcher.py` reads `matching/.env` on import, and
with the key present it defaults to `deepseek:deepseek-chat`. Override the model
in the same file if you want another provider:

```
MATCH_MODEL=openai:gpt-4o-mini   # needs langchain-openai installed
```

Real environment variables take precedence over `.env`, so CI can override
without editing the file.

One call, temperature 0, no agent, no tools. If the key is missing or the call
fails, it falls back instead of crashing and the `source:` field says why - e.g.
`fallback:ModuleNotFoundError` or `fallback:AuthenticationError`.

Keep `deepseek-chat` for this: `deepseek-reasoner` does not support the tool
calling that `with_structured_output` relies on.

**For anyone marking this:** `.env` is git-ignored and is never in the repo. A
fresh clone runs in fallback mode until they add their own key — which is
enough to see the whole pipeline work, just without the model's wording.

For a look at the raw data (the same database the API writes to):

```bash
export DATABASE_URL=$(sed -n 's/^DATABASE_URL=//p' .env)
psql "$DATABASE_URL" -c "SELECT display_name, city, preferred_role FROM profiles LIMIT 5;"
```

No database at all - read a JSON dump instead:

```bash
python match.py --from-json sample_pool.json alice_chen
```

## Hard rules in the matcher

Only two, both in `filters.py` so they're visible and testable:

1. same `city` (`HK` or `SH`) - separate cohorts
2. `in_team = 0` - people already placed are out of the pool

Languages are **not** filtered. They're passed to the model as a signal, so a
candidate whose role differs can still be suggested.

`in_team` is set directly in the database. The logic never flips it, so the same
input always yields the same pool and the same shortlist.

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
| `RuntimeError: DATABASE_URL is not set` | `matching/.env` missing | `cp matching/.env.example matching/.env` |
| `ModuleNotFoundError: psycopg` | driver not installed | `python -m pip install -r requirements.txt` from the repository root |
| `no account with username '...'` | wrong handle, or not in the shared DB | check the `accounts` table with `psql` |
| `JSONDecodeError` in `db._decode` | a row's `languages` isn't valid JSON | fix the row with `psql` |
| `psycopg.OperationalError` | wrong URL, credentials, or network | check `DATABASE_URL`; a paused Render database also refuses connections |

There is no reset flag. Dropping or recreating tables is a manual `psql`
operation; this repository ships no DDL or seed scripts. Otherwise the shared
database is edited directly with `psql`. Remember that every account and profile
row is shared by everyone running the app.

For the web UI, install the root `requirements.txt` into the shared
environment. Set `MATCH_MODEL=deepseek:deepseek-flash`
in `matching/.env` when using Flash, then restart the backend. Flash/V4
structured output uses non-thinking mode; the original model-selection,
prompt, parser and fallback remain in the existing `matcher.py`.
