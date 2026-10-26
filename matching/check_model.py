"""Check AI configuration; --live makes one real call using synthetic fixtures.

Run from the repository root:
    python matching/check_model.py
    python matching/check_model.py --live
No key, login token, contacts or raw provider exception text is printed.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path

if __package__:
    from . import matcher
    from .filters import MAX_MATCHES, candidates_for_model
else:
    import matcher
    from filters import MAX_MATCHES, candidates_for_model


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Make one real model call; provider usage may be billed.')
    args = parser.parse_args(argv)
    missing = [name for name in ('langchain', 'langchain_deepseek', 'dotenv')
               if importlib.util.find_spec(name) is None]
    if missing:
        print('Missing model dependencies. Run: python -m pip install -r backend/requirements-ai.txt')
        return 1
    name = matcher.model_name()
    if not name:
        print('AI is not configured. Fill DEEPSEEK_API_KEY in matching/.env, then restart the backend.')
        return 1
    if name.startswith('deepseek:') and not os.getenv('DEEPSEEK_API_KEY', '').strip():
        print('DeepSeek API key is missing. Fill DEEPSEEK_API_KEY in matching/.env; do not send the key in chat.')
        return 1
    print(f'Configured model: {name}')
    if not args.live:
        print('Configuration check only; no API call was made. Use --live to verify one real call.')
        return 0
    pool = json.loads(Path(__file__).with_name('sample_pool.json').read_text(encoding='utf-8'))
    me = next(profile for profile in pool if profile['username'] == 'alice_chen')
    candidates, _, _ = candidates_for_model(me, pool)
    picks, source = matcher.pick(me, candidates)
    if source != name:
        print(f'LIVE CHECK FAILED: {source}. The result used fallback, not the AI model.')
        return 2
    target = min(MAX_MATCHES, len(candidates))
    if len(picks) != target or any(not pick['reason'].strip() for pick in picks):
        print('The model replied, but its shortlist failed the count/reason checks. Do not claim a verified result.')
        return 2
    print(f'LIVE API VERIFIED: {name}; {len(picks)} candidates with non-empty reasons.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
