#!/bin/sh
set -eu
cd "$(dirname "$0")"
DEMO_PYTHON=python3
if [ -x .venv/bin/python ]; then DEMO_PYTHON=.venv/bin/python; fi
if ! "$DEMO_PYTHON" -c 'import fastapi, uvicorn, pwdlib, psycopg' 2>/dev/null; then
    "$DEMO_PYTHON" -m pip install -r requirements.txt
fi
exec "$DEMO_PYTHON" -m uvicorn backend.app:create_app --factory --host 127.0.0.1 --port 8000
