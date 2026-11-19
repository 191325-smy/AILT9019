"""Insert the 30 synthetic demo profiles into the configured PostgreSQL database.

Idempotent: accounts and profiles that already exist are left untouched, so it
is safe to run against the shared database.

Run from the repository root:
    python matching/seed.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).with_name(".env"))
except ImportError:
    pass

from matching.db import get_conn  # noqa: E402

PROGRAMMES = ["AI and Data Science", "Applied AI", "Computer Science", "Others"]
ROLES = ["Frontend", "Backend", "Database", "Agentic Development"]
SKILL_PATTERNS = [
    (1, 1, 0, 1, 0),
    (1, 0, 1, 1, 0),
    (0, 1, 0, 1, 1),
    (1, 1, 1, 0, 0),
    (0, 0, 1, 1, 1),
]

# username, display name, contact, city, preferred role, languages, in_team
FIXTURES = [
    ("alice_chen", "Alice Chen", "alice@test.com", "HK", "Frontend", ["Mandarin", "English"], 0),
    ("bob_liu", "Bob Liu", "bob@test.com", "HK", "Backend", ["English"], 0),
    ("carol_wang", "Carol Wang", "carol@test.com", "HK", "Database", ["Cantonese"], 1),
    ("david_zhao", "David Zhao", "david@test.com", "HK", "Agentic Development", ["Mandarin", "English"], 0),
    ("emma_sun", "Emma Sun", "emma@test.com", "HK", "Other", ["Mandarin"], 0),
    ("frank_zhou", "Frank Zhou", "frank@test.com", "HK", "Frontend", ["English", "Cantonese"], 0),
    ("grace_wu", "Grace Wu", "grace@test.com", "HK", "Backend", ["Mandarin", "English"], 0),
    ("henry_xu", "Henry Xu", "henry@test.com", "HK", "Database", ["English"], 0),
    ("ivy_huang", "Ivy Huang", "ivy@test.com", "HK", "Agentic Development", ["Mandarin"], 1),
    ("jack_lin", "Jack Lin", "jack@test.com", "HK", "Other", ["Cantonese"], 0),
    ("karen_he", "Karen He", "karen@test.com", "HK", "Frontend", ["Mandarin", "English"], 0),
    ("leo_gao", "Leo Gao", "leo@test.com", "HK", "Backend", ["English"], 0),
    ("mia_luo", "Mia Luo", "mia@test.com", "HK", "Database", ["Mandarin", "Cantonese"], 0),
    ("nathan_zheng", "Nathan Zheng", "nathan@test.com", "HK", "Agentic Development", ["English"], 0),
    ("olivia_liang", "Olivia Liang", "olivia@test.com", "HK", "Other", ["Mandarin"], 0),
    ("peter_song", "Peter Song", "peter@test.com", "SH", "Frontend", ["Mandarin", "English"], 0),
    ("queenie_tang", "Queenie Tang", "queenie@test.com", "SH", "Backend", ["English"], 0),
    ("ryan_feng", "Ryan Feng", "ryan@test.com", "SH", "Database", ["Mandarin"], 0),
    ("sophia_cao", "Sophia Cao", "sophia@test.com", "SH", "Agentic Development", ["Mandarin", "English"], 0),
    ("tom_yao", "Tom Yao", "tom@test.com", "SH", "Other", ["Cantonese"], 1),
    ("uma_pan", "Uma Pan", "uma@test.com", "SH", "Frontend", ["English"], 0),
    ("victor_qin", "Victor Qin", "victor@test.com", "SH", "Backend", ["Mandarin", "English"], 0),
    ("wendy_jiang", "Wendy Jiang", "wendy@test.com", "SH", "Database", ["Mandarin"], 0),
    ("xander_guo", "Xander Guo", "xander@test.com", "SH", "Agentic Development", ["English", "Mandarin"], 0),
    ("yuki_han", "Yuki Han", "yuki@test.com", "SH", "Other", ["Cantonese"], 0),
    ("zoe_shi", "Zoe Shi", "zoe@test.com", "SH", "Frontend", ["English"], 0),
    ("aaron_deng", "Aaron Deng", "aaron@test.com", "SH", "Backend", ["Mandarin"], 0),
    ("bella_ma", "Bella Ma", "bella@test.com", "SH", "Database", ["English", "Mandarin"], 0),
    ("cody_lei", "Cody Lei", "cody@test.com", "SH", "Agentic Development", ["Mandarin"], 0),
    ("diana_fan", "Diana Fan", "diana@test.com", "SH", "Other", ["English", "Cantonese"], 0),
]


def _open_roles(index, preferred):
    if preferred in ROLES:
        return [preferred, ROLES[(index + 1) % len(ROLES)]]
    return [preferred]


def seed():
    import json

    inserted = 0
    with get_conn() as conn:
        for index, (username, name, contact, city, role, languages, in_team) in enumerate(FIXTURES):
            conn.execute(
                """
                INSERT INTO accounts (username, password_hash)
                VALUES (%s, %s)
                ON CONFLICT (username) DO NOTHING
                """,
                (username, f"placeholder-{index + 1}"),
            )
            account_id = conn.execute(
                "SELECT id FROM accounts WHERE username = %s",
                (username,),
            ).fetchone()["id"]

            cursor = conn.execute(
                """
                INSERT INTO profiles (
                    account_id, display_name, contact_info, city, preferred_role,
                    languages, in_team, programme, open_roles,
                    programming, github, debugging, web, ai_agent
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (account_id) DO NOTHING
                """,
                (
                    account_id,
                    name,
                    contact,
                    city,
                    role,
                    json.dumps(languages),
                    in_team,
                    PROGRAMMES[index % len(PROGRAMMES)],
                    json.dumps(_open_roles(index, role)),
                    *SKILL_PATTERNS[index % len(SKILL_PATTERNS)],
                ),
            )
            inserted += cursor.rowcount

    print(f"seed complete: {inserted} new profiles, {len(FIXTURES) - inserted} already present")


if __name__ == "__main__":
    seed()
