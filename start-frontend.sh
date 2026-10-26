#!/bin/sh
set -eu
cd "$(dirname "$0")"
DEMO_PYTHON=python3
if [ -x .venv/bin/python ]; then DEMO_PYTHON=.venv/bin/python; fi
echo 'Open http://localhost:8001/index.html'
exec "$DEMO_PYTHON" -m http.server 8001 --bind 127.0.0.1 --directory ui
