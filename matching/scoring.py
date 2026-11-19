"""Deterministic fit score used by the offline fallback (no model configured).

Hard constraints (same city, not already in a team, not yourself) stay in
filters.hard_filter(); this module only ranks the survivors. The model path
does its own weighing from raw attributes (see matcher.py); when no key is
available, filters.py ranks with this formula instead.

The weights below are the single source of truth for the fallback and are
quoted in the prompt as guidance, so both paths describe the same rubric.

    total = 0.40*role + 0.35*skills + 0.10*flexibility + 0.05*languages
            + 0.10*programme

The programme term rewards diversity and rarity: a different programme counts,
but a programme that half the eligible list shares earns little, so a handful
of Computer Science classmates do not sweep the shortlist. Same programme = 0.

Value formats come from the database:
    programme       'AI and Data Science' | 'Applied AI' | 'Computer Science' | 'Others'
    open_roles      JSON array of the same role values as preferred_role
    skill flags     0 | 1 (NULL/absent = unknown, treated as neutral)
"""

SKILLS = ("programming", "github", "debugging", "web", "ai_agent")
CONCRETE_ROLES = ("Frontend", "Backend", "Database", "Agentic Development")
WILDCARD_ROLE = "Other"

WEIGHTS = {
    "role": 0.40,
    "skills": 0.35,
    "flexibility": 0.10,
    "languages": 0.05,
    "programme": 0.10,
}


def offered(cand):
    """Roles a candidate can fill: preferred first, then open_roles, deduplicated."""
    roles = []
    for role in [cand.get("preferred_role"), *(cand.get("open_roles") or [])]:
        if role and role not in roles:
            roles.append(role)
    return roles


def score(me, cand, programme_share=None):
    """0..1 fit score plus its weighted breakdown, relative to `me` only.

    `programme_share` maps programme -> share of the eligible list. Rarer
    programmes score higher; without the map (or with an unknown programme)
    any difference counts fully.
    """
    covered = {me.get("preferred_role")} if me.get("preferred_role") else set()
    gaps = [r for r in CONCRETE_ROLES if r not in covered]
    offered_roles = offered(cand)
    fills = [r for r in offered_roles if r in gaps]

    role = 1.0 if fills else (0.5 if WILDCARD_ROLE in offered_roles and gaps else 0.0)

    complements = [k for k in SKILLS if cand.get(k) == 1 and me.get(k) != 1]
    skills = len(complements) / len(SKILLS)

    # Breadth beyond the preferred role: spare roles the team could still use.
    extras = [
        r for r in offered_roles
        if r in gaps and r != cand.get("preferred_role")
    ]
    flexibility = len(extras) / len(gaps) if gaps else 0.0

    mine = set(me.get("languages") or [])
    langs = len(mine & set(cand.get("languages") or [])) / len(mine) if mine else 0.0

    programme = 0.0
    if (
        me.get("programme")
        and cand.get("programme")
        and me["programme"] != cand["programme"]
    ):
        if programme_share is None:
            programme = 1.0
        else:
            programme = max(0.0, 1.0 - programme_share.get(cand["programme"], 0.0))

    return {
        "total": round(
            WEIGHTS["role"] * role
            + WEIGHTS["skills"] * skills
            + WEIGHTS["flexibility"] * flexibility
            + WEIGHTS["languages"] * langs
            + WEIGHTS["programme"] * programme,
            3,
        ),
        "role": round(WEIGHTS["role"] * role, 3),
        "skills": round(WEIGHTS["skills"] * skills, 3),
        "flexibility": round(WEIGHTS["flexibility"] * flexibility, 3),
        "languages": round(WEIGHTS["languages"] * langs, 3),
        "programme": round(WEIGHTS["programme"] * programme, 3),
        "complements": complements,
        "fills_roles": fills,
    }
