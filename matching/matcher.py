"""Model stage: one structured call that assembles a team.

Takes the already-filtered list from filters.py and asks a single model to rank
classmates by balanced complementarity, so the shortlist looks like a team
rather than five variations of the same person. The model does the weighing
itself and returns evidence (role, skill complements, programme flag), never
prose; the application composes the sentence from values it has verified, so a
reason cannot name a skill the candidate does not have.
Role diversity is an objective, not a constraint - duplicates are allowed when
they are the best people available.
One call, no agent, no tools, temperature 0.

The offline fallback is different: filters.py scores candidates with
scoring.py, so with no key the ranking is deterministic. Either way the model
never sees contact_info - contact is attached afterwards, only for the profiles
it actually picked.

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
    from .filters import MAX_MATCHES, diverse_picks, fact_sentence, fallback_reason
    from .scoring import SKILLS, score
else:
    from filters import MAX_MATCHES, diverse_picks, fact_sentence, fallback_reason
    from scoring import SKILLS, score


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
                "so the key was not read - run: python -m pip install -r "
                "requirements.txt from the repository root",
                file=sys.stderr,
            )
        return
    load_dotenv(env_path)


_load_env()

DEFAULT_MODEL = "deepseek:deepseek-chat"   # deepseek-reasoner has no tool calling

SKILL_LABELS = {
    "programming": "programming",
    "github": "GitHub",
    "debugging": "debugging",
    "web": "web development",
    "ai_agent": "AI-agent",
}

SYSTEM = (
    "You assemble a project team for a university course. 'You' is one student "
    "already on the team; 'candidates' are eligible classmates from the same "
    "city who are not yet in a team.\n\n"
    "Choose at most {limit} classmates, in priority order. The goal is balanced "
    "complementarity, not similarity: a strong team covers different roles and "
    "different skills. Weigh the candidates yourself - no score is precomputed.\n\n"
    "Judge with this rubric, roughly by weight:\n"
    "- role coverage (about 40%): a classmate who can fill a concrete role the "
    "team lacks (Frontend, Backend, Database, Agentic Development) is worth more "
    "than one who repeats a role. Count your own preferred_role as filled. "
    "open_roles lists every role a classmate is willing to fill, so someone whose "
    "preferred_role repeats can still add an uncovered role. 'Other' is a "
    "wildcard, ranked after the concrete roles.\n"
    "- skills (about 35%): five binary flags - programming, github, debugging, "
    "web, ai_agent - all equally weighted. A flag the candidate has and you lack "
    "is a complement. A flag you both have is not a penalty. Treat null as "
    "unknown and neutral.\n"
    "- flexibility (about 10%): extra uncovered roles in open_roles beyond the "
    "preferred one.\n"
    "- languages (about 5%): more shared languages is better.\n"
    "- programme (about 10%): a different programme adds diversity, and rarer "
    "programmes in this list count for more - avoid stacking several Computer "
    "Science classmates when other programmes are available.\n\n"
    "Treat the picks as a growing team: a role or programme already covered by "
    "'you' or by an earlier pick is no longer a gap, so later picks should look "
    "for what is still missing. Only call a skill a complement when the "
    "candidate has 1 and you have 0 - never present a skill you already have as "
    "something new.\n\n"
    "If nobody adds a new role, pick the strongest remaining classmates anyway - "
    "a duplicate is fine, and never return fewer than {limit} when {limit} are "
    "available. Avoid picking two people whose only contribution is the same "
    "role while an uncovered role remains.\n\n"
    "Use only account_id values present in the list; never invent one. For each "
    "pick return evidence, not prose: role - a role from that candidate's "
    "fills_roles that the team still lacks (empty string if none); skills - only "
    "skills where that candidate's skills map shows 1, preferring their "
    "complements because those are the ones you lack; repeating a skill you "
    "already have is allowed, naming a skill they lack never is; programme - "
    "true only when their programme differs from yours."
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
        role: str = Field(
            default="",
            description=(
                "a role from that candidate's fills_roles that the team still "
                "lacks; empty string when none"
            ),
        )
        skills: list[str] = Field(
            default_factory=list,
            description=(
                "skills where that candidate's skills map shows 1; prefer their "
                "complements, but a skill you already have is allowed; never a "
                "skill they lack"
            ),
        )
        programme: bool = Field(
            default=False,
            description="true only when their programme differs from yours",
        )

    class Shortlist(BaseModel):
        picks: list[Pick] = Field(
            description=(
                "teammates in priority order; prefer those covering a role the "
                "team lacks, but a repeated role is allowed when the list runs out"
            )
        )

    return Shortlist


def _facts(person):
    """Matching attributes shown to the model; contact_info stays private."""
    return {
        "programme": person.get("programme"),
        "preferred_role": person.get("preferred_role"),
        "open_roles": person.get("open_roles") or [],
        "skills": {k: person.get(k) for k in SKILLS},
        "languages": person.get("languages") or [],
    }


def _join_clauses(clauses):
    if len(clauses) == 1:
        return clauses[0]
    return ", ".join(clauses[:-1]) + " and " + clauses[-1]


def _fact_block(me, cand):
    """Deterministic evidence the model may quote; it never has to compute it."""
    s = score(me, cand)
    return {"fills_roles": s["fills_roles"], "complements": s["complements"]}


def _describe(me, cand, item, covered):
    """Compose a verified sentence; free text from the model is never trusted."""
    facts = _fact_block(me, cand)
    role = (item.role or "").strip()
    role_ok = role in facts["fills_roles"] and role.lower() not in covered

    skills = []
    for skill in item.skills:
        if cand.get(skill) == 1 and skill not in skills:
            skills.append(skill)

    programme_ok = bool(
        item.programme
        and me.get("programme")
        and cand.get("programme")
        and me["programme"] != cand["programme"]
    )

    clauses = []
    if role_ok:
        clauses.append(f"can cover {role}")
    if skills:
        clauses.append(
            "brings " + _join_clauses([SKILL_LABELS.get(s, s) for s in skills]) + " experience"
        )
    if programme_ok:
        clauses.append(f"comes from a different programme ({cand['programme']})")

    if not clauses:
        return f"{cand['display_name']} {fact_sentence(me, cand)}"
    return f"{cand['display_name']} {_join_clauses(clauses)}."


def _payload(me, candidates):
    """Attributes plus verified evidence; the application writes the sentence.

    Alphabetical order so the model never inherits the fallback's ranking.
    """
    return {
        "me": {
            "display_name": me["display_name"],
            "city": me.get("city"),
            **_facts(me),
        },
        "candidates": [
            {
                "account_id": cand["account_id"],
                "display_name": cand["display_name"],
                "city": cand.get("city"),
                "shared_languages": cand["signals"]["shared_languages"],
                "role_fit": cand["signals"]["role_fit"],
                **_facts(cand),
                **_fact_block(me, cand),
            }
            for cand in sorted(candidates, key=lambda c: c["display_name"])
        ],
    }


def _fallback(me, candidates, limit):
    """Same preference the model is asked for: new roles first, duplicates last."""
    picks = [
        {"profile": c, "reason": fallback_reason(me, c)}
        for c in diverse_picks(me, candidates, limit)
    ]
    return picks, "fallback"


def pick(me, candidates, limit=MAX_MATCHES, use_model=True):
    """Return (picks, source) where picks is [{profile, reason}] and source says why.

    source is "model" when the model answered, otherwise "fallback:<reason>".
    use_model=False forces the deterministic ranking even when a key is set.
    """
    if not candidates:
        return [], "empty"

    if not use_model:
        picks, why = _fallback(me, candidates, limit)
        return picks, f"{why}:model disabled"

    name = model_name()
    if name is None:
        picks, why = _fallback(me, candidates, limit)
        return picks, f"{why}:no DEEPSEEK_API_KEY or MATCH_MODEL"

    try:
        from langchain.chat_models import init_chat_model

        options = {}
        if name in ("deepseek:deepseek-flash", "deepseek:deepseek-v4-pro",
                    "deepseek:deepseek-v4-flash", "deepseek:deepseek-v4-flash-vision-exp"):
            # Flash/V4 rejects a forced structured-output tool in thinking mode.
            options["extra_body"] = {"thinking": {"type": "disabled"}}
        llm = init_chat_model(name, temperature=0, **options)
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
    covered = {(me.get("preferred_role") or "").strip().lower()}
    for item in result.picks:
        cand = by_id.get(item.account_id)
        if cand is None or item.account_id in seen:
            continue          # hallucinated or duplicated id - drop it
        seen.add(item.account_id)
        picks.append({"profile": cand, "reason": _describe(me, cand, item, covered)})
        for role in [cand.get("preferred_role"), *(cand.get("open_roles") or [])]:
            if role:
                covered.add(role.strip().lower())
        if len(picks) == limit:
            break

    if not picks:
        picks, _ = _fallback(me, candidates, limit)
        return picks, "fallback:no valid ids returned"
    return picks, name
