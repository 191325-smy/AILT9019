"""Evaluation fixtures and assertions; no alternative matching implementation."""
import contextlib
import copy
import hashlib
import json
import os
import sqlite3
import sys
import types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "evaluation"
SKILLS = ("programming", "github", "debugging", "web", "ai_agent")
PROGRAMMES = ("AI and Data Science", "Applied AI", "Computer Science", "Others")
ROLES = ("Frontend", "Backend", "Database", "Agentic Development")
SAFE_DATABASE = "postgresql://evaluation:unused@127.0.0.1:1/evaluation"


def case(code, title, inputs, expected, group="matching", gap=None):
    def decorate(method):
        method.case_spec = dict(id=code, title=title, input=inputs,
                                expected=expected, group=group, gap=gap)
        return method
    return decorate


def profile(i, name=None, **values):
    row = dict(account_id=i, display_name=name or f"Synthetic {i}",
               username=f"synthetic_{i}", contact_info=f"synthetic_{i}@test.com",
               city="HK", preferred_role="Backend", languages=["English"],
               in_team=0, programme="Applied AI", open_roles=["Backend"],
               **{s: 0 for s in SKILLS})
    row.update(values)
    if "preferred_role" in values and "open_roles" not in values:
        row["open_roles"] = [row["preferred_role"]]
    return row


def fixture(enriched=True):
    path = HERE / "fixtures" / "enriched_profiles.json" if enriched else ROOT / "matching" / "sample_pool.json"
    return copy.deepcopy(json.loads(path.read_text(encoding="utf-8")))


def validate_picks(me, candidates, picks, expected_count=None):
    """Check public acceptance rules independently of the ranking formula."""
    allowed = {c["account_id"] for c in candidates}
    ids = [p["profile"]["account_id"] for p in picks]
    def require(condition, message):
        if not condition:
            raise AssertionError(message)
    require(len(ids) == len(set(ids)), "Duplicate recommendations")
    require(set(ids) <= allowed, "Recommendation outside the eligible pool")
    expected_count = min(5, len(candidates)) if expected_count is None else expected_count
    require(len(picks) == expected_count, f"Expected {expected_count} candidates; got {len(picks)}")
    for item in picks:
        p = item["profile"]
        require(p["account_id"] != me["account_id"], "Self recommended")
        require(p["city"] == me["city"], "Wrong cohort")
        require(not p.get("in_team"), "Placed candidate recommended")
        require(bool(item["reason"].strip()), "Blank explanation")


@contextlib.contextmanager
def provider(matcher, items=None, error=None, malformed=None):
    """Fake transport; use the application's REAL Pydantic response schema."""
    captured = {}

    class Model:
        def with_structured_output(self, schema):
            self.schema = schema
            captured["schema"] = schema.__name__
            return self

        def invoke(self, messages):
            captured["messages"] = messages
            if error:
                raise error
            return self.schema.model_validate(malformed if malformed is not None else {"picks": items})

    def init(name, **options):
        captured.update(model=name, options=options)
        return Model()

    parent = types.ModuleType("langchain")
    chat = types.ModuleType("langchain.chat_models")
    chat.init_chat_model = init
    parent.chat_models = chat
    with patch.object(matcher, "model_name", return_value="evaluation:simulated"), \
         patch.dict(sys.modules, {"langchain": parent, "langchain.chat_models": chat}):
        yield captured


def seed_connection(conn, rows):
    """Insert disposable fixtures into the existing test-only SQLite schema."""
    for p in rows:
        conn.execute("INSERT INTO accounts(id,username,password_hash) VALUES (?,?,?)",
                     (p["account_id"], p.get("username", f"fixture_{p['account_id']}"), "not-a-real-hash"))
        columns = ["account_id", "display_name", "contact_info", "city", "preferred_role",
                   "languages", "in_team", "programme", "open_roles", *SKILLS]
        values = [json.dumps(p.get(k)) if k in ("languages", "open_roles") and p.get(k) is not None
                  else p.get(k) for k in columns]
        conn.execute("INSERT INTO profiles (" + ",".join(columns) + ") VALUES (" + ",".join("?" for _ in columns) + ")", values)


def source_integrity():
    manifest = json.loads((HERE / "SOURCE.json").read_text(encoding="utf-8"))
    # Detect added runtime modules as well as changed/deleted baseline files.
    expected = {item["path"] for item in manifest["files"]}
    suffixes = {".py", ".json", ".sql", ".html", ".css", ".js", ".md"}
    unexpected = []
    for directory in ("backend", "matching", "ui"):
        for path in (ROOT / directory).rglob("*"):
            relative = path.relative_to(ROOT).as_posix()
            if (path.is_file() and "__pycache__" not in path.parts
                    and path.suffix in suffixes and relative not in expected):
                unexpected.append(relative)
    if unexpected:
        raise RuntimeError("Application files outside baseline: " + ", ".join(sorted(unexpected)))
    rows = []
    for item in manifest["files"]:
        raw = (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        # Git blobs in the immutable baseline use LF.
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        rows.append(dict(path=item["path"], sha256=hashlib.sha256(raw).hexdigest(),
                         baseline_blob_matches=blob == item["git_blob_sha"]))
    return manifest["revision"], rows
