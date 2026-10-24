"""Hard constraints + signals. Pure functions: no database, no network, no model.

This is the deterministic half of the matcher. Everything here can be called
from a test with plain dicts, and it always returns the same answer for the
same input.

    from filters import candidates_for_model
    candidates, dropped, _ = candidates_for_model(me, pool)

Value formats come straight from the fixtures:
    city            'HK' | 'SH'
    preferred_role  'Frontend' | 'Backend' | 'Database' | 'Agentic Development' | 'Other'
    languages       ["Mandarin", "English", "Cantonese"]
"""

MAX_MATCHES = 5
CITY_MUST_MATCH = True          # the one hard grouping rule left, on purpose
EXCLUDE_PLACED = True           # in_team = 1 means already on a team
WILDCARD_ROLE = "other"         # counts as a role, but ranked after real ones


def _role(value):
    return (value or "").strip().lower()


def _label(value):
    """Display form: keep the fixture's own capitalisation ("Agentic Development")."""
    return (value or "").strip()


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
def add_signals(me, cand):
    shared_langs = sorted(set(me.get("languages") or []) & set(cand.get("languages") or []))

    enriched = dict(cand)
    enriched["signals"] = {
        "shared_languages": shared_langs,
        "role_fit": "complement" if _role(cand.get("preferred_role")) != _role(me.get("preferred_role")) else "same",
    }
    return enriched


def rank_key(cand):
    """Deterministic ordering: complementary role, then overlap in languages.

    Used for the offline fallback and to give the model a stable candidate order.
    """
    s = cand["signals"]
    return (
        s["role_fit"] != "complement",
        -len(s["shared_languages"]),
        cand["display_name"],
    )


def fallback_reason(me, cand):
    """One sentence built from the signals, used when the model is unavailable."""
    s = cand["signals"]
    bits = []

    if s["role_fit"] == "complement":
        bits.append(
            f"{_label(cand.get('preferred_role'))} pairs with your "
            f"{_role(me.get('preferred_role'))}"
        )
    if s["shared_languages"]:
        bits.append("can talk in " + ", ".join(s["shared_languages"]))

    if not bits:
        return "Same cohort and role, no shared language listed."
    text = "; ".join(bits)
    return text[:1].upper() + text[1:] + "."


def diverse_picks(me, candidates, limit=MAX_MATCHES):
    """Up to `limit` candidates, leaning toward role coverage without requiring it.

    Diversity is an objective here, not a constraint: five Backends are still a
    legal answer if they are the best people left. So it runs in two passes.

    1. walk the rank order and take anyone who fills a role the team does not
       have yet (`me` counts as filled);
    2. if that runs out before `limit`, fill the remaining slots from whoever is
       left by rank - duplicates allowed, because a duplicate is better than a
       shortlist that leaves seats empty.

    Always returns min(limit, len(candidates)) people. This is the deterministic
    twin of the prompt, which asks the model for the same preference rather than
    a filter.
    """
    ordered = sorted(
        candidates,
        key=lambda c: (_role(c.get("preferred_role")) == WILDCARD_ROLE, rank_key(c)),
    )

    picked, covered = [], {_role(me.get("preferred_role"))}
    for cand in ordered:
        role = _role(cand.get("preferred_role"))
        if not role or role in covered:
            continue
        picked.append(cand)
        covered.add(role)
        if len(picked) == limit:
            return picked

    taken = {c["account_id"] for c in picked}
    for cand in ordered:
        if len(picked) == limit:
            break
        if cand["account_id"] in taken:
            continue
        picked.append(cand)
    return picked


def candidates_for_model(me, pool):
    """Stage 2 + 3 in one call, ready to serialise into the prompt.

    Returns (candidates, dropped, excluded_count).
    """
    kept, dropped = hard_filter(me, pool)
    enriched = sorted((add_signals(me, c) for c in kept), key=rank_key)
    return enriched, dropped, len(dropped)
