"""Exercise authentication and profile writes through the actual FastAPI app.

Run from the repository root:
    python -m unittest discover -s backend/tests -v

All databases and registered users belong to temporary test directories. No
live API, existing account database, or model provider is used.
"""

import hashlib
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app import create_app
from matching import db as matching_db


ROOT = Path(__file__).resolve().parents[2]
PASSWORD = "DemoPassword123!"
PROFILE = {
    "display_name": "Demo Student",
    "contact_info": "demo@test.com",
    "city": "HK",
    "preferred_role": "Backend",
    "languages": ["English", "Mandarin"],
}


class BackendAPITests(unittest.TestCase):
    def setUp(self):
        # Kept under the checkout so restricted desktop runners can use it.
        temp_root = ROOT / ".test-tmp"
        temp_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="api-", dir=temp_root)
        self.addCleanup(self.temp.cleanup)
        self.db_path = Path(self.temp.name) / "test.db"
        self.client = self.open_client()

    def open_client(self, **kwargs):
        client = TestClient(create_app(db_path=self.db_path, **kwargs))
        client.__enter__()
        self.addCleanup(client.__exit__, None, None, None)
        return client

    def register(self, username="student_one", password=PASSWORD, client=None):
        response = (client or self.client).post(
            "/auth/register", json={"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def login(self, username="student_one", password=PASSWORD, client=None):
        response = (client or self.client).post(
            "/auth/login", json={"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["token_type"], "bearer")
        self.assertGreater(body["expires_in"], 0)
        self.assertGreaterEqual(len(body["access_token"]), 32)
        return body["access_token"]

    @staticmethod
    def headers(token):
        return {"Authorization": "Bearer " + token}

    def save(self, token, profile=None, client=None):
        response = (client or self.client).put(
            "/profiles/me", headers=self.headers(token),
            json=PROFILE if profile is None else profile,
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_register_login_save_read_logout(self):
        user = self.register()
        self.assertEqual(set(user), {"id", "username"})
        self.assertEqual(user["username"], "student_one")
        token = self.login()
        me = self.client.get("/auth/me", headers=self.headers(token))
        self.assertEqual(me.status_code, 200, me.text)
        self.assertEqual(me.json(), user)
        missing = self.client.get("/profiles/me", headers=self.headers(token))
        self.assertEqual(missing.status_code, 404)
        saved = self.save(token)
        self.assertEqual(saved["account_id"], user["id"])
        for field, value in PROFILE.items():
            self.assertEqual(saved[field], value)
        read = self.client.get("/profiles/me", headers=self.headers(token))
        self.assertEqual(read.status_code, 200, read.text)
        self.assertEqual(read.json(), saved)
        logged_out = self.client.post("/auth/logout", headers=self.headers(token))
        self.assertEqual(logged_out.status_code, 204)
        self.assertEqual(logged_out.content, b"")
        self.assertEqual(self.client.get("/auth/me", headers=self.headers(token)).status_code, 401)

    def test_username_case_normalization_and_duplicate_rejection(self):
        first = self.register("Demo_User")
        self.assertEqual(first["username"], "demo_user")
        duplicate = self.client.post(
            "/auth/register", json={"username": "DEMO_USER", "password": PASSWORD}
        )
        self.assertEqual(duplicate.status_code, 409, duplicate.text)
        token = self.login("DEMO_USER")
        self.assertEqual(
            self.client.get("/auth/me", headers=self.headers(token)).json()["id"], first["id"]
        )

    def test_username_and_password_validation(self):
        invalid = [
            {"username": "ab", "password": PASSWORD},
            {"username": "x" * 33, "password": PASSWORD},
            {"username": "invalid name", "password": PASSWORD},
            {"username": "';DROP_TABLE_accounts;--", "password": PASSWORD},
            {"username": "valid_name", "password": "A!2zQ"},
            {"username": "valid_name", "password": "x" * 129},
            {"username": "valid_name"},
        ]
        for index, payload in enumerate(invalid):
            with self.subTest(case=index):
                response = self.client.post("/auth/register", json=payload)
                self.assertEqual(response.status_code, 422, response.text)
                if "password" in payload:
                    self.assertNotIn(payload["password"], response.text)
        self.register("still_works")

    def test_passwords_are_salted_hashes_and_not_returned(self):
        first = self.register("student_one")
        second = self.register("student_two")
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            rows = conn.execute("SELECT password_hash FROM accounts ORDER BY id").fetchall()
        hashes = [row[0] for row in rows]
        self.assertEqual(len(hashes), 2)
        self.assertTrue(all(value != PASSWORD and len(value) > 32 for value in hashes))
        self.assertNotEqual(hashes[0], hashes[1], "Equal passwords need independently salted hashes.")
        self.assertNotIn(PASSWORD, json.dumps([first, second]))
        self.login("student_one")
        self.login("student_two")

    def test_wrong_password_and_unknown_account_have_same_error(self):
        self.register()
        bad_password = self.client.post(
            "/auth/login", json={"username": "student_one", "password": "WrongPassword123!"}
        )
        unknown = self.client.post(
            "/auth/login", json={"username": "unknown_student", "password": "WrongPassword123!"}
        )
        self.assertEqual(bad_password.status_code, 401)
        self.assertEqual(unknown.status_code, 401)
        self.assertEqual(bad_password.json(), unknown.json())
        self.assertNotIn(PASSWORD, bad_password.text)

    def test_missing_and_invalid_credentials_cannot_read_or_write(self):
        for headers in ({}, self.headers("not-a-real-session"), {"Authorization": "Basic fake"}):
            with self.subTest(headers=headers):
                for path in ("/auth/me", "/profiles/me"):
                    self.assertEqual(self.client.get(path, headers=headers).status_code, 401)
                self.assertEqual(
                    self.client.put("/profiles/me", headers=headers, json=PROFILE).status_code, 401
                )
                self.assertEqual(self.client.post("/auth/logout", headers=headers).status_code, 401)

    def test_tampered_token_is_rejected(self):
        self.register()
        token = self.login()
        tampered = ("A" if token[0] != "A" else "B") + token[1:]
        self.assertEqual(self.client.get("/auth/me", headers=self.headers(tampered)).status_code, 401)
        self.assertEqual(self.client.get("/auth/me", headers=self.headers(token)).status_code, 200)

    def test_session_database_does_not_store_the_bearer_token(self):
        self.register()
        token = self.login()
        expected_digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            rows = conn.execute("SELECT * FROM auth_sessions").fetchall()
        values = [str(value) for row in rows for value in row]
        self.assertNotIn(token, values)
        self.assertIn(expected_digest, values)

    def test_logout_revokes_only_the_current_session(self):
        self.register()
        first, second = self.login(), self.login()
        self.assertNotEqual(first, second)
        self.assertEqual(self.client.post("/auth/logout", headers=self.headers(first)).status_code, 204)
        self.assertEqual(self.client.get("/auth/me", headers=self.headers(first)).status_code, 401)
        self.assertEqual(self.client.get("/auth/me", headers=self.headers(second)).status_code, 200)

    def test_expired_session_cannot_be_used(self):
        self.register()
        token = self.login()
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute("UPDATE auth_sessions SET expires_at = 0")
            conn.commit()
        self.assertEqual(self.client.get("/auth/me", headers=self.headers(token)).status_code, 401)
        self.assertEqual(
            self.client.put("/profiles/me", headers=self.headers(token), json=PROFILE).status_code, 401
        )

    def test_users_only_read_and_modify_their_own_profiles(self):
        first = self.register("student_one")
        second = self.register("student_two")
        token_one, token_two = self.login("student_one"), self.login("student_two")
        one = self.save(token_one, dict(PROFILE, display_name="First Student"))
        two = self.save(token_two, dict(PROFILE, display_name="Second Student", city="SH"))
        self.assertEqual(one["account_id"], first["id"])
        self.assertEqual(two["account_id"], second["id"])
        spoof = self.client.put(
            "/profiles/me", headers=self.headers(token_one),
            json=dict(PROFILE, account_id=second["id"], display_name="Unauthorized overwrite"),
        )
        self.assertEqual(spoof.status_code, 422, spoof.text)
        for token, name in ((token_one, "First Student"), (token_two, "Second Student")):
            response = self.client.get("/profiles/me", headers=self.headers(token))
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["display_name"], name)

    def test_profile_update_preserves_account_and_team_status(self):
        user = self.register()
        token = self.login()
        self.save(token)
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.execute("UPDATE profiles SET in_team = 1 WHERE account_id = ?", (user["id"],))
            conn.commit()
        changed = dict(PROFILE, display_name="Updated Student", preferred_role="Database", languages=["Cantonese"])
        saved = self.save(token, changed)
        self.assertEqual(saved["account_id"], user["id"])
        self.assertEqual(saved["in_team"], 1)
        self.assertEqual(saved["preferred_role"], "Database")
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0], 1)

    def test_profile_validation_and_mass_assignment_rejection(self):
        self.register()
        token = self.login()
        invalid = [
            dict(PROFILE, city="Paris"),
            dict(PROFILE, preferred_role="Administrator"),
            dict(PROFILE, languages=["Klingon"]),
            dict(PROFILE, display_name=""),
            dict(PROFILE, account_id=123),
            dict(PROFILE, in_team=1),
            dict(PROFILE, password_hash="injected"),
        ]
        for index, payload in enumerate(invalid):
            with self.subTest(case=index):
                response = self.client.put("/profiles/me", headers=self.headers(token), json=payload)
                self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.client.get("/profiles/me", headers=self.headers(token)).status_code, 404)
        self.save(token)

    def test_saved_data_is_visible_to_existing_matching_reader(self):
        user = self.register()
        token = self.login()
        self.save(token)
        conn = sqlite3.connect(self.db_path)
        self.addCleanup(conn.close)
        conn.row_factory = sqlite3.Row
        loaded = matching_db.load_profile(conn, user["id"])
        self.assertEqual(loaded["account_id"], user["id"])
        for field, value in PROFILE.items():
            self.assertEqual(loaded[field], value)
        self.assertIsInstance(loaded["languages"], list)
        self.assertEqual(len(matching_db.load_pool(conn)), 1)

    def test_data_and_sessions_survive_app_restart(self):
        user = self.register()
        token = self.login()
        self.save(token)
        self.client.__exit__(None, None, None)
        restarted = self.open_client()
        me = restarted.get("/auth/me", headers=self.headers(token))
        self.assertEqual(me.status_code, 200, me.text)
        self.assertEqual(me.json()["id"], user["id"])
        saved = restarted.get("/profiles/me", headers=self.headers(token))
        self.assertEqual(saved.status_code, 200, saved.text)
        self.assertEqual(saved.json()["display_name"], PROFILE["display_name"])
        self.login(client=restarted)

    def test_existing_seeded_database_is_preserved(self):
        seeded_path = Path(self.temp.name) / "seeded.db"
        with closing(sqlite3.connect(seeded_path)) as conn, conn:
            conn.executescript((ROOT / "matching" / "schema.sql").read_text(encoding="utf-8"))
            conn.executescript((ROOT / "matching" / "seed.sql").read_text(encoding="utf-8"))
        client = TestClient(create_app(db_path=seeded_path))
        with client:
            with closing(sqlite3.connect(seeded_path)) as conn, conn:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0], 30)
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0], 30)
                self.assertEqual(
                    conn.execute("SELECT display_name FROM profiles WHERE account_id = 1").fetchone()[0],
                    "Alice Chen",
                )
            placeholder_login = client.post(
                "/auth/login", json={"username": "alice_chen", "password": "hash1notreal"}
            )
            self.assertEqual(placeholder_login.status_code, 401)
            created = self.register("new_student", client=client)
            self.assertGreater(created["id"], 30)
            token = self.login("new_student", client=client)
            self.save(token, client=client)
        with closing(sqlite3.connect(seeded_path)) as conn, conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0], 31)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0], 31)

    def test_private_responses_are_not_cacheable(self):
        registered = self.client.post(
            "/auth/register", json={"username": "student_one", "password": PASSWORD}
        )
        self.assertEqual(registered.headers.get("cache-control"), "no-store")
        token = self.login()
        self.save(token)
        for path in ("/auth/me", "/profiles/me"):
            response = self.client.get(path, headers=self.headers(token))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("cache-control"), "no-store")

    def test_profile_text_is_stored_literally_and_empty_preferences_are_allowed(self):
        self.register()
        token = self.login()
        text = "陈同学'); DROP TABLE profiles; --"
        values = dict(PROFILE, display_name=text, contact_info=None, languages=[])
        saved = self.save(token, values)
        self.assertEqual(saved["display_name"], text)
        self.assertIsNone(saved["contact_info"])
        self.assertEqual(saved["languages"], [])
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0], 1)

    def test_matches_use_the_same_database_as_accounts_and_profiles(self):
        # This database is passed to create_app, not matching.db's global path.
        # Seeding only this file catches accidental reads of a different DB.
        with closing(sqlite3.connect(self.db_path)) as conn, conn:
            conn.executescript((ROOT / "matching" / "seed.sql").read_text(encoding="utf-8"))
        user = self.register()
        token = self.login()
        self.save(token)
        with patch("backend.app.matcher.model_name", return_value=None):
            response = self.client.post("/matches", headers=self.headers(token))
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["stats"]["total_pool"], 31)
        self.assertEqual(len(data["picks"]), 5)
        self.assertTrue(data["source"].startswith("fallback:"))
        self.assertEqual(response.headers.get("cache-control"), "no-store")
        ids = [p["account_id"] for p in data["picks"]]
        self.assertEqual(len(set(ids)), 5)
        self.assertNotIn(user["id"], ids)
        with closing(sqlite3.connect(self.db_path)) as conn:
            for pick in data["picks"]:
                self.assertEqual(pick["city"], PROFILE["city"])
                self.assertTrue(pick["reason"].strip())
                self.assertEqual(conn.execute("SELECT in_team FROM profiles WHERE account_id = ?", (pick["account_id"],)).fetchone()[0], 0)

    def test_matches_require_login_and_a_saved_profile(self):
        self.assertEqual(self.client.post("/matches").status_code, 401)
        self.register()
        token = self.login()
        self.assertEqual(self.client.post("/matches", headers=self.headers(token)).status_code, 404)

    def test_matches_handle_an_empty_eligible_pool(self):
        self.register()
        token = self.login()
        self.save(token)
        response = self.client.post("/matches", headers=self.headers(token))
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["picks"], [])
        self.assertEqual(response.json()["stats"]["eligible"], 0)

    def test_default_cors_accepts_the_recording_frontend(self):
        response = self.client.options("/matches", headers={
            "Origin": "http://localhost:8001",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:8001")

    def test_frontend_cors_preflight_uses_explicit_origin(self):
        allowed = "http://localhost:5173"
        with TestClient(create_app(db_path=self.db_path, allowed_origins=[allowed])) as client:
            headers = {
                "Origin": allowed,
                "Access-Control-Request-Method": "PUT",
                "Access-Control-Request-Headers": "authorization,content-type",
            }
            accepted = client.options("/profiles/me", headers=headers)
            self.assertEqual(accepted.status_code, 200, accepted.text)
            self.assertEqual(accepted.headers.get("access-control-allow-origin"), allowed)
            headers["Origin"] = "http://untrusted.test"
            rejected = client.options("/profiles/me", headers=headers)
            self.assertEqual(rejected.status_code, 400)
            self.assertNotIn("access-control-allow-origin", rejected.headers)


if __name__ == "__main__":
    unittest.main()
