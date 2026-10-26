"""Model stage: one structured call that assembles a team.

Takes the already-filtered list from filters.py and asks a single model to pick
classmates who *tend* to cover different roles, so the shortlist looks like a
team rather than five variations of the same person. Role diversity is an
objective, not a constraint - duplicates are allowed when they are the best
people available.
One call, no agent, no tools, temperature 0.

The model only ever sees account_id, display_name, preferred_role, city and
the signals. It never sees contact_info - contact is attached afterwards, only
for the profiles it actually picked.

Configure in `app/.env` (git-ignored, copy from `.env.example`):
    DEEPSEEK_API_KEY=sk-...             # picked up automatically
    MATCH_MODEL=deepseek:deepseek-chat  # optional, this is the default

Real environment variables win over .env, so CI can still override them.

Any provider init_chat_model understands works (`openai:gpt-4o-mini`,
`anthropic:claude-...`, `google_genai:gemini-...`), but each needs its own
langchain-* provider package installed.

With no key set, or no langchain installed, or any API failure, this falls back
to the deterministic ranking in filters.py. The CLI therefore works out of the
box with zero installs.
"""

import json
import os
import sys
from pathlib import Path

if __package__:
    from .filters import MAX_MATCHES, diverse_picks, fallback_reason
else:
    from filters import MAX_MATCHES, diverse_picks, fallback_reason


def _load_env():
    """Read app/.env so a key survives a new terminal.

    no-op when python-dotenv isn't installed, and it never overrides a variable
    that is already set - so a real env var still wins.
    """
    env_path = Path(__file__).with_name(".env")
    try:
        from dotenv import load_dotenv
    except ImportError:
        if env_path.exists():
            print(
                f"warning: {env_path.name} exists but python-dotenv is not installed, "
                "so the key was not read - run: pip install -r requirements.txt",
                file=sys.stderr,
            )
        return
    load_dotenv(env_path)


_load_env()

DEFAULT_MODEL = "deepseek:deepseek-chat"   # deepseek-reasoner has no tool calling

SYSTEM = (
    "You assemble a project team for a university course. "
    "You are given one student ('you') who is already on the team, and a list of "
    "eligible classmates. Choose at most {limit} classmates.\n\n"
    "Prefer a team whose members cover different roles - that produces the "
    "strongest team, but it is a preference, not a rule:\n"
    "1. A classmate who fills a role the team does not yet have is worth more "
    "than one who repeats a role. My role counts as already filled. Concrete "
    "roles first: Frontend, Backend, Database, Agentic Development; treat "
    "'Other' as a wildcard that ranks after those.\n"
    "2. If nobody left adds a new role, pick the strongest remaining classmates "
    "anyway. A duplicate role is completely acceptable - never return a shorter "
    "list than {limit} when {limit} classmates are available.\n"
    "3. Among classmates bringing the same role, prefer the one who shares more "
    "languages with me.\n\n"
    "Use only account_id values present in the list - never invent one. "
    "Order the picks so the ones that most improve the team come first. For each "
    "pick, write one sentence naming the role it fills and why the team is "
    "stronger with it, using only the attributes you were given. Be concrete, "
    "no filler."
)


def model_name():
    """Resolve the model id. None means 'run deterministically'."""
    explicit = os.getenv("MATCH_MODEL")
    if explicit:
        return explicit
    if os.getenv("DEEPSEEK_API_KEY"):
        return DEFAULT_MODEL
    return None


def available():
    return model_name() is not None


def _schema():
    """Defined lazily so pydantic is only imported when a model is configured."""
    from pydantic import BaseModel, Field

    class Pick(BaseModel):
        account_id: int = Field(description="account_id copied from the candidate list")
        reason: str = Field(description="one sentence, at most 25 words, naming the role filled")

    class Shortlist(BaseModel):
        picks: list[Pick] = Field(
            description=(
                "teammates in priority order; prefer those covering a role the "
                "team lacks, but a repeated role is allowed when the list runs out"
            )
        )

    return Shortlist


def _payload(me, candidates):
    """The only fields the model gets to see."""
    return {
        "me": {
            "display_name": me["display_name"],
            "city": me.get("city"),
            "preferred_role": me.get("preferred_role"),
            "languages": me.get("languages") or [],
        },
        "candidates": [
            {
                "account_id": c["account_id"],
                "display_name": c["display_name"],
                "preferred_role": c.get("preferred_role"),
                "city": c.get("city"),
                "shared_languages": c["signals"]["shared_languages"],
                "role_fit": c["signals"]["role_fit"],
            }
            for c in candidates
        ],
    }


def _fallback(me, candidates, limit):
    """Same preference the model is asked for: new roles first, duplicates last."""
    picks = [
        {"profile": c, "reason": fallback_reason(me, c)}
        for c in diverse_picks(me, candidates, limit)
    ]
    return picks, "fallback"


def pick(me, candidates, limit=MAX_MATCHES):
    """Return (picks, source) where picks is [{profile, reason}] and source says why.

    source is "model" when the model answered, otherwise "fallback:<reason>".
    """
    if not candidates:
        return [], "empty"

    name = model_name()
    if name is None:
        picks, why = _fallback(me, candidates, limit)
        return picks, f"{why}:no DEEPSEEK_API_KEY or MATCH_MODEL"

    try:
        from langchain.chat_models import init_chat_model

        llm = init_chat_model(name, temperature=0)
        structured = llm.with_structured_output(_schema())

        messages = [
            ("system", SYSTEM.format(limit=limit)),
            ("human", json.dumps(_payload(me, candidates), ensure_ascii=False, indent=2)),
        ]
        result = structured.invoke(messages)
    except Exception as exc:  # missing key, no network, bad model name, schema drift
        picks, _ = _fallback(me, candidates, limit)
        return picks, f"fallback:{type(exc).__name__}"

    by_id = {c["account_id"]: c for c in candidates}
    picks, seen = [], set()
    for item in result.picks:
        cand = by_id.get(item.account_id)
        if cand is None or item.account_id in seen:
            continue          # hallucinated or duplicated id - drop it
        seen.add(item.account_id)
        picks.append({"profile": cand, "reason": item.reason.strip()})
        if len(picks) == limit:
            break

    if not picks:
        picks, _ = _fallback(me, candidates, limit)
        return picks, "fallback:no valid ids returned"
    return picks, name
