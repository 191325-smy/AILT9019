"""Hard constraints + fallback ranking. Pure functions: no database, no network, no model.

This is the deterministic half of the matcher. Everything here can be called
from a test with plain dicts, and it always returns the same answer for the
same input. Hard constraints are city, not-already-in-a-team and not-yourself;
the ranking of survivors uses scoring.py, the same formula the prompt describes,
so the no-key shortlist reflects the new profile attributes too.

    from filters import candidates_for_model
    candidates, dropped, _ = candidates_for_model(me, pool)

Value formats come straight from the database:
    city            'HK' | 'SH'
    preferred_role  'Frontend' | 'Backend' | 'Database' | 'Agentic Development' | 'Other'
    open_roles      JSON array of the same role values
    programme       'AI and Data Science' | 'Applied AI' | 'Computer Science' | 'Others'
    skill flags     0 | 1 (NULL = unknown)
    languages       ["Mandarin", "English", "Cantonese"]
"""

from collections import Counter

if __package__:
    from . import scoring
else:
    import scoring


MAX_MATCHES = 5
CITY_MUST_MATCH = True          # the one hard grouping rule left, on purpose
EXCLUDE_PLACED = True           # in_team = 1 means already on a team


def _role(value):
    return (value or "").strip().lower()


# --------------------------------------------------------------------------- #
# stage 2 - hard constraints
# --------------------------------------------------------------------------- #
def hard_filter(me, pool):
    """Split the pool into eligible and dropped, keeping a reason for each drop.

    Returns (kept, dropped) where dropped is [(profile, reason)].
    """
    kept, dropped = [], []

    for cand in pool:
        if cand["account_id"] == me["account_id"]:
            dropped.append((cand, "that's you"))
            continue

        if EXCLUDE_PLACED and cand.get("in_team"):
            dropped.append((cand, "already in a team"))
            continue

        if CITY_MUST_MATCH and (cand.get("city") or "") != (me.get("city") or ""):
            dropped.append((cand, f"different cohort ({cand.get('city') or 'unknown'})"))
            continue

        kept.append(cand)

    return kept, dropped


# --------------------------------------------------------------------------- #
# stage 3 - signals (facts for the model, and a deterministic order for fallback)
# --------------------------------------------------------------------------- #
def add_signals(me, cand, programme_share=None):
    shared_langs = sorted(set(me.get("languages") or []) & set(cand.get("languages") or []))

    enriched = dict(cand)
    enriched["signals"] = {
        "shared_languages": shared_langs,
        "role_fit": "complement" if _role(cand.get("preferred_role")) != _role(me.get("preferred_role")) else "same",
        "score": scoring.score(me, cand, programme_share),
    }
    return enriched


def rank_key(me, cand):
    """Fallback ordering: fit score, then shared languages, then name.

    Only the no-key path uses this. The model receives candidates in
    alphabetical order and does its own weighing.
    """
    s = cand["signals"]
    return (-s["score"]["total"], -len(s["shared_languages"]), cand["display_name"])


def _sentence(clauses):
    """Join clauses into one readable fragment: A, B and C."""
    if len(clauses) == 1:
        return clauses[0]
    return ", ".join(clauses[:-1]) + " and " + clauses[-1]


def fact_sentence(me, cand):
    """Evidence-only sentence, no score; safe to reuse when a model reason fails."""
    s = cand["signals"]["score"]
    clauses = []

    if s["fills_roles"]:
        clauses.append("can cover " + " and ".join(s["fills_roles"]))
    if s["complements"]:
        clauses.append("adds " + " and ".join(s["complements"]))
    if (
        cand.get("programme")
        and me.get("programme")
        and cand["programme"] != me["programme"]
    ):
        clauses.append(f"studies {cand['programme']} rather than your {me['programme']}")
    if cand["signals"]["shared_languages"]:
        clauses.append("shares " + " and ".join(cand["signals"]["shared_languages"]))

    if not clauses:
        return "offers no role, skill, programme or language gain."
    return _sentence(clauses) + "."


def fallback_reason(me, cand):
    """One readable sentence citing the same evidence the model is asked to name.

    No numeric score: the deterministic ranking is an implementation detail.
    """
    sentence = fact_sentence(me, cand)
    return sentence[:1].upper() + sentence[1:]


def diverse_picks(me, candidates, limit=MAX_MATCHES):
    """Up to `limit` candidates: fill missing roles first, then best score.

    Diversity is an objective here, not a constraint: five Backends are still a
    legal answer if they are the best people left. So it runs in two passes.

    1. walk the score order and take anyone who can fill a concrete role the
       team does not have yet (`open_roles` counts; `me` counts as filled);
    2. fill the remaining seats by score - duplicates allowed, because a
       duplicate is better than a shortlist that leaves seats empty. Team-level
       programme spread comes from the rarity term in scoring.py plus the
       prompt instruction, not from a hard ordering rule here.

    Always returns min(limit, len(candidates)) people. This mirrors the prompt,
    which asks the model for the same preference rather than a filter.
    """
    ordered = sorted(candidates, key=lambda c: rank_key(me, c))

    picked, taken = [], set()
    covered = {_role(me.get("preferred_role"))}
    for cand in ordered:
        if len(picked) == limit:
            return picked
        fills = [
            r for r in scoring.offered(cand)
            if r in scoring.CONCRETE_ROLES and _role(r) not in covered
        ]
        if not fills:
            continue
        picked.append(cand)
        taken.add(cand["account_id"])
        covered.update(_role(r) for r in fills)

    for cand in ordered:
        if len(picked) == limit:
            break
        if cand["account_id"] not in taken:
            picked.append(cand)
    return picked


def candidates_for_model(me, pool):
    """Stage 2 + 3 in one call, ready to serialise into the prompt.

    Returns (candidates, dropped, excluded_count).
    """
    kept, dropped = hard_filter(me, pool)
    # Programme rarity is relative to this request's eligible list.
    counts = Counter(c.get("programme") for c in kept if c.get("programme"))
    share = {p: n / len(kept) for p, n in counts.items()} if kept else {}
    # Alphabetical on purpose: the model must weigh candidates itself instead
    # of inheriting the fallback's score order. diverse_picks re-sorts.
    enriched = sorted(
        (add_signals(me, c, share) for c in kept),
        key=lambda c: c["display_name"],
    )
    return enriched, dropped, len(dropped)
