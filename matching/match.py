"""CLI for the AILT9019 matcher: load -> filter -> shortlist -> print.

The work lives in two modules, this file only glues them together:
    filters.py   hard constraints + signals, pure and deterministic
    matcher.py   one model call, with a deterministic fallback

Run it:
    python match.py alice_chen                         # against ailt9019.db
    python match.py --from-json pool.json alice_chen   # against a JSON dump
    python match.py alice_chen --verbose               # one line per dropped/surviving profile

Without --verbose the filter is summarised by reason ("15 different cohort (SH),
2 already in a team, 1 that's you"); with it, every profile is listed by name.
"""

import json
import sys
from collections import Counter

from filters import MAX_MATCHES, candidates_for_model
import matcher


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    for row in rows:
        for col in ("languages",):
            if isinstance(row.get(col), str):
                row[col] = json.loads(row[col]) if row[col] else []
    return rows


def _print_shortlist(me, picks, total, source):
    print(f"\nshortlist: {len(picks)} of {total}   (source: {source})")
    for i, p in enumerate(picks, 1):
        c = p["profile"]
        print(f"  {i}. {c['display_name']:<14} {c['preferred_role'] or '-':<20} {c.get('contact_info') or '-'}")
        print(f"     reason: {p['reason']}")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1

    verbose = "--verbose" in argv
    argv = [a for a in argv if a != "--verbose"]

    if argv[1] == "--from-json":
        if len(argv) < 4:
            print("usage: python match.py --from-json pool.json <username>")
            return 1
        path, username = argv[2], argv[3]
        rows = _load_json(path)
        me = next(
            (r for r in rows
             if r.get("username") == username or r.get("display_name") == username),
            None,
        )
        if me is None:
            print(f"no profile named {username!r} in {path}")
            return 1
        pool = rows          # no pre-filtering here either - filters.py owns the rules
    else:
        import db  # imported lazily so the JSON path needs no database file

        username = argv[1]
        conn = db.get_conn()
        try:
            me = db.load_profile_by_username(conn, username)
            if me is None:
                print(f"no account with username {username!r} - run `python seed.py` first")
                return 1
            pool = db.load_pool(conn)
        finally:
            conn.close()

    candidates, dropped, _ = candidates_for_model(me, pool)

    print(f"\nme: {me['display_name']} ({me['city']}, {me['preferred_role']})")
    print(f"pool: {len(candidates) + len(dropped)}   "
          f"kept: {len(candidates)}   dropped: {len(dropped)}")

    if verbose and candidates:
        print("\nkept: " + ", ".join(c["display_name"] for c in candidates))

    if dropped:
        if verbose:
            print("\ndropped")
            for c, why in dropped:
                print(f"  - {c['display_name']:<14} {why}")
        else:
            counts = Counter(why for _, why in dropped)
            print("  dropped: " + ", ".join(
                f"{n} {why}" for why, n in counts.most_common()
            ))

    if not candidates:
        print("\nno one fits - suggest widening the preferences")
        return 0

    picks, source = matcher.pick(me, candidates, MAX_MATCHES)
    _print_shortlist(me, picks, len(candidates), source)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
