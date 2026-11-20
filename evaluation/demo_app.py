"""Test-only Uvicorn entry point: real app/UI, disposable synthetic SQLite.

python -m uvicorn evaluation.demo_app:app --host 127.0.0.1 --port 8000
Optional EVALUATION_KEY_FILE selects only API key/model from a private file.
No production database is loaded, contacted or modified by this adapter.
"""
import atexit
import os
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from common import SAFE_DATABASE, fixture, seed_connection

os.environ['DATABASE_URL']=SAFE_DATABASE
os.environ['DEEPSEEK_API_KEY']=''
os.environ['MATCH_MODEL']=''
if os.environ.get('EVALUATION_KEY_FILE'):
    from dotenv import dotenv_values
    values=dotenv_values(os.environ['EVALUATION_KEY_FILE'])
    for key in ('DEEPSEEK_API_KEY','MATCH_MODEL'):
        if values.get(key):os.environ[key]=values[key]
with patch('dotenv.load_dotenv',return_value=False):
    from backend.app import create_app
from backend.store import Store

work=tempfile.TemporaryDirectory(prefix='ailt-browser-evaluation-')
atexit.register(work.cleanup)
database=Path(work.name)/'demo.db'
store=Store(database);store.initialise()
if os.environ.get('EVALUATION_EMPTY_POOL')!='1':
    with closing(sqlite3.connect(database)) as conn, conn:
        seed_connection(conn,fixture())
app=create_app(db_path=database)
