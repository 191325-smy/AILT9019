# Final offline evaluation

Baseline: `81886ac18511398f320b0e592828ea00c956d7cd`. Run: 2026-11-20T20:16:16+08:00.

**55 cases: 51 PASS, 4 FAIL, 0 ERROR.**

Existing backend cases use their original assertions. New cases record inputs, expectations and observed outputs below.
The sweep is ONE test case covering 60 profile queries (30 legacy + 30 enriched), each repeated twice. It is not 60 separately counted test cases.
Model-boundary cases use simulated provider output and the real application Pydantic schema. No live API or PostgreSQL service is tested by this command.
FAIL remains FAIL and makes the command exit 1; a working test runner does not mean the product passed.

| Case | Group | Result | Check |
|---|---|---|---|
| API-data_and_sessions_survive_app_restart | existing backend | PASS | data and sessions survive app restart |
| API-default_cors_accepts_the_recording_frontend | existing backend | PASS | default cors accepts the recording frontend |
| API-existing_seeded_database_is_preserved | existing backend | PASS | existing seeded database is preserved |
| API-expired_session_cannot_be_used | existing backend | PASS | expired session cannot be used |
| API-frontend_cors_preflight_uses_explicit_origin | existing backend | PASS | frontend cors preflight uses explicit origin |
| API-logout_revokes_only_the_current_session | existing backend | PASS | logout revokes only the current session |
| API-matches_can_disable_the_model_even_when_one_is_configured | existing backend | PASS | matches can disable the model even when one is configured |
| API-matches_handle_an_empty_eligible_pool | existing backend | PASS | matches handle an empty eligible pool |
| API-matches_require_login_and_a_saved_profile | existing backend | PASS | matches require login and a saved profile |
| API-matches_use_the_same_database_as_accounts_and_profiles | existing backend | PASS | matches use the same database as accounts and profiles |
| API-missing_and_invalid_credentials_cannot_read_or_write | existing backend | PASS | missing and invalid credentials cannot read or write |
| API-passwords_are_salted_hashes_and_not_returned | existing backend | PASS | passwords are salted hashes and not returned |
| API-private_responses_are_not_cacheable | existing backend | PASS | private responses are not cacheable |
| API-profile_accepts_matching_fields_and_validates_roles | existing backend | PASS | profile accepts matching fields and validates roles |
| API-profile_text_is_stored_literally_and_empty_preferences_are_allowed | existing backend | PASS | profile text is stored literally and empty preferences are allowed |
| API-profile_update_preserves_account_and_team_status | existing backend | PASS | profile update preserves account and team status |
| API-profile_validation_and_mass_assignment_rejection | existing backend | PASS | profile validation and mass assignment rejection |
| API-register_login_save_read_logout | existing backend | PASS | register login save read logout |
| API-saved_data_is_visible_to_existing_matching_reader | existing backend | PASS | saved data is visible to existing matching reader |
| API-session_database_does_not_store_the_bearer_token | existing backend | PASS | session database does not store the bearer token |
| API-tampered_token_is_rejected | existing backend | PASS | tampered token is rejected |
| API-username_and_password_validation | existing backend | PASS | username and password validation |
| API-username_case_normalization_and_duplicate_rejection | existing backend | PASS | username case normalization and duplicate rejection |
| API-users_only_read_and_modify_their_own_profiles | existing backend | PASS | users only read and modify their own profiles |
| API-wrong_password_and_unknown_account_have_same_error | existing backend | PASS | wrong password and unknown account have same error |
| C01 | CLI | PASS | JSON CLI works without dependencies or DB |
| C02 | CLI | PASS | Unknown JSON user is a readable error |
| K01 | cache simulation | PASS | Cache refresh after own profile save and logout |
| K02 | cache simulation | FAIL | Revocation across two cache instances |
| M01 | model boundary | PASS | Model toggle prevents provider invocation |
| M02 | model boundary | PASS | Provider timeout falls back |
| M03 | model boundary | PASS | Verified structured evidence and private payload |
| M04 | model boundary | PASS | Invalid and duplicate IDs removed |
| M05 | model boundary | PASS | All-invalid output falls back |
| M06 | model boundary | PASS | Oversized output capped |
| M07 | model boundary | FAIL | Short valid output supplies five |
| M08 | model boundary | PASS | Empty evidence produces nonblank verified sentences |
| M09 | model boundary | PASS | Invented role and absent skill claims are rejected |
| M10 | model boundary | PASS | Malformed response schema falls back |
| M11 | model boundary | FAIL | Only the five defined skills may be explained |
| P01 | API extension | PASS | All new preference values round-trip |
| P02 | API extension | PASS | New preference validation |
| P03 | API extension | PASS | Clearing open roles and skills is preserved |
| P04 | API extension | PASS | Empty-candidate browser-demo boundary |
| R01 | matching | PASS | Hard exclusions and soft language |
| R02 | matching | PASS | Empty and undersized pools |
| R03 | matching | PASS | Legacy and enriched 30-profile sweeps |
| R04 | matching | PASS | Open roles add useful coverage |
| R05 | matching | PASS | Known missing skill increases preference |
| R06 | matching | PASS | Language preference remains soft |
| R07 | matching | PASS | Duplicate roles may fill remaining slots |
| S01 | preferences | PASS | Declared weighted score on hand-calculated example |
| S02 | preferences | PASS | Rare programmes gain preference |
| S03 | preferences | PASS | Legacy attributes and null candidate skills |
| S04 | preferences | FAIL | Unknown student skills are neutral |

## API-data_and_sessions_survive_app_restart data and sessions survive app restart

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_data_and_sessions_survive_app_restart`.

Input: Existing backend fixture/profile and HTTP calls in test_data_and_sessions_survive_app_restart

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-default_cors_accepts_the_recording_frontend default cors accepts the recording frontend

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_default_cors_accepts_the_recording_frontend`.

Input: Existing backend fixture/profile and HTTP calls in test_default_cors_accepts_the_recording_frontend

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-existing_seeded_database_is_preserved existing seeded database is preserved

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_existing_seeded_database_is_preserved`.

Input: Existing backend fixture/profile and HTTP calls in test_existing_seeded_database_is_preserved

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-expired_session_cannot_be_used expired session cannot be used

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_expired_session_cannot_be_used`.

Input: Existing backend fixture/profile and HTTP calls in test_expired_session_cannot_be_used

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-frontend_cors_preflight_uses_explicit_origin frontend cors preflight uses explicit origin

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_frontend_cors_preflight_uses_explicit_origin`.

Input: Existing backend fixture/profile and HTTP calls in test_frontend_cors_preflight_uses_explicit_origin

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-logout_revokes_only_the_current_session logout revokes only the current session

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_logout_revokes_only_the_current_session`.

Input: Existing backend fixture/profile and HTTP calls in test_logout_revokes_only_the_current_session

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-matches_can_disable_the_model_even_when_one_is_configured matches can disable the model even when one is configured

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_matches_can_disable_the_model_even_when_one_is_configured`.

Input: Existing backend fixture/profile and HTTP calls in test_matches_can_disable_the_model_even_when_one_is_configured

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-matches_handle_an_empty_eligible_pool matches handle an empty eligible pool

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_matches_handle_an_empty_eligible_pool`.

Input: Existing backend fixture/profile and HTTP calls in test_matches_handle_an_empty_eligible_pool

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-matches_require_login_and_a_saved_profile matches require login and a saved profile

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_matches_require_login_and_a_saved_profile`.

Input: Existing backend fixture/profile and HTTP calls in test_matches_require_login_and_a_saved_profile

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-matches_use_the_same_database_as_accounts_and_profiles matches use the same database as accounts and profiles

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_matches_use_the_same_database_as_accounts_and_profiles`.

Input: Existing backend fixture/profile and HTTP calls in test_matches_use_the_same_database_as_accounts_and_profiles

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-missing_and_invalid_credentials_cannot_read_or_write missing and invalid credentials cannot read or write

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_missing_and_invalid_credentials_cannot_read_or_write`.

Input: Existing backend fixture/profile and HTTP calls in test_missing_and_invalid_credentials_cannot_read_or_write

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-passwords_are_salted_hashes_and_not_returned passwords are salted hashes and not returned

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_passwords_are_salted_hashes_and_not_returned`.

Input: Existing backend fixture/profile and HTTP calls in test_passwords_are_salted_hashes_and_not_returned

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-private_responses_are_not_cacheable private responses are not cacheable

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_private_responses_are_not_cacheable`.

Input: Existing backend fixture/profile and HTTP calls in test_private_responses_are_not_cacheable

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-profile_accepts_matching_fields_and_validates_roles profile accepts matching fields and validates roles

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_profile_accepts_matching_fields_and_validates_roles`.

Input: Existing backend fixture/profile and HTTP calls in test_profile_accepts_matching_fields_and_validates_roles

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-profile_text_is_stored_literally_and_empty_preferences_are_allowed profile text is stored literally and empty preferences are allowed

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_profile_text_is_stored_literally_and_empty_preferences_are_allowed`.

Input: Existing backend fixture/profile and HTTP calls in test_profile_text_is_stored_literally_and_empty_preferences_are_allowed

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-profile_update_preserves_account_and_team_status profile update preserves account and team status

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_profile_update_preserves_account_and_team_status`.

Input: Existing backend fixture/profile and HTTP calls in test_profile_update_preserves_account_and_team_status

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-profile_validation_and_mass_assignment_rejection profile validation and mass assignment rejection

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_profile_validation_and_mass_assignment_rejection`.

Input: Existing backend fixture/profile and HTTP calls in test_profile_validation_and_mass_assignment_rejection

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-register_login_save_read_logout register login save read logout

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_register_login_save_read_logout`.

Input: Existing backend fixture/profile and HTTP calls in test_register_login_save_read_logout

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-saved_data_is_visible_to_existing_matching_reader saved data is visible to existing matching reader

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_saved_data_is_visible_to_existing_matching_reader`.

Input: Existing backend fixture/profile and HTTP calls in test_saved_data_is_visible_to_existing_matching_reader

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-session_database_does_not_store_the_bearer_token session database does not store the bearer token

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_session_database_does_not_store_the_bearer_token`.

Input: Existing backend fixture/profile and HTTP calls in test_session_database_does_not_store_the_bearer_token

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-tampered_token_is_rejected tampered token is rejected

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_tampered_token_is_rejected`.

Input: Existing backend fixture/profile and HTTP calls in test_tampered_token_is_rejected

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-username_and_password_validation username and password validation

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_username_and_password_validation`.

Input: Existing backend fixture/profile and HTTP calls in test_username_and_password_validation

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-username_case_normalization_and_duplicate_rejection username case normalization and duplicate rejection

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_username_case_normalization_and_duplicate_rejection`.

Input: Existing backend fixture/profile and HTTP calls in test_username_case_normalization_and_duplicate_rejection

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-users_only_read_and_modify_their_own_profiles users only read and modify their own profiles

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_users_only_read_and_modify_their_own_profiles`.

Input: Existing backend fixture/profile and HTTP calls in test_users_only_read_and_modify_their_own_profiles

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## API-wrong_password_and_unknown_account_have_same_error wrong password and unknown account have same error

Result: **PASS**. Test: `backend.tests.test_api.BackendAPITests.test_wrong_password_and_unknown_account_have_same_error`.

Input: Existing backend fixture/profile and HTTP calls in test_wrong_password_and_unknown_account_have_same_error

Expected: Assertions in the existing backend test must pass; see backend/tests/test_api.py.

Observed:

```json
{
  "assertions": "passed"
}
```

## C01 JSON CLI works without dependencies or DB

Result: **PASS**. Test: `test_cases.MatchingCases.test_json_cli`.

Input: Run enriched fixture through match.py --from-json with -S and no key.

Expected: Readable five-result fallback with no database or traceback.

Observed:

```json
{
  "exit_code": 0,
  "stdout": "\nme: Alice Chen (HK, Frontend)\npool: 30   kept: 12   dropped: 18\n  dropped: 14 different cohort (SH), 3 already in a team, 1 that's you\n\nshortlist: 5 of 12   (source: fallback:no DEEPSEEK_API_KEY or MATCH_MODEL)\n  1. Karen He       Frontend             karen@test.com\n     reason: Can cover Agentic Development, adds github and ai_agent, studies Computer Science rather than your AI and Data Science and shares English and Mandarin.\n  2. Bob Liu        Backend              bob@test.com\n     reason: Can cover Backend and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English.\n  3. Olivia Liang   Other                olivia@test.com\n     reason: Can cover Agentic Development, adds programming and web, studies Computer Science rather than your AI and Data Science and shares Mandarin.\n  4. Frank Zhou     Frontend             frank@test.com\n     reason: Can cover Database, adds programming and web, studies Applied AI rather than your AI and Data Science and shares English.\n  5. Nathan Zheng   Agentic Development  nathan@test.com\n     reason: Can cover Agentic Development and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English.\n",
  "stderr": ""
}
```

## C02 Unknown JSON user is a readable error

Result: **PASS**. Test: `test_cases.MatchingCases.test_unknown_json_user`.

Input: JSON CLI with no_such_student.

Expected: Exit 1 with a readable error, no traceback.

Observed:

```json
{
  "exit_code": 1,
  "stdout": "no profile named 'no_such_student' in <REPO>\\evaluation\\fixtures\\enriched_profiles.json\n",
  "stderr": ""
}
```

## K01 Cache refresh after own profile save and logout

Result: **PASS**. Test: `test_cases.APICases.test_cache_refresh`.

Input: Enable production cache logic over a disposable SQLite transport; save/update and revoke a session.

Expected: Own update is immediately visible and own logout invalidates the cached session.

Observed:

```json
{
  "name": "Changed",
  "logged_out_status": 401
}
```

## K02 Revocation across two cache instances

Result: **FAIL**. Test: `test_cases.APICases.test_multi_instance_revoke`.

Input: Two Store instances share a test DB and cache one token; first revokes it.

Expected: Second instance should reject the revoked session rather than use its stale cache.

Observed:

```json
{
  "other_instance_still_accepts": true
}
```

Failure evidence:

```text
Traceback (most recent call last):
  File "<REPO>\evaluation\test_cases.py", line 276, in test_multi_instance_revoke
    self.assertIsNone(stale,'Another process/instance retains the token until cached expiry.')
AssertionError: {'id': 1, 'username': 'evaluation_user'} is not None : Another process/instance retains the token until cached expiry.
```

## M01 Model toggle prevents provider invocation

Result: **PASS**. Test: `test_cases.MatchingCases.test_model_disabled`.

Input: Configure a model but call pick(use_model=False).

Expected: No provider resolution; five deterministic picks with disabled label.

Observed:

```json
{
  "eligible": 13,
  "ids": [
    11,
    2,
    15,
    6,
    14
  ],
  "source": "fallback:model disabled",
  "reasons": [
    "Can cover Agentic Development, adds github and ai_agent, studies Computer Science rather than your AI and Data Science and shares English and Mandarin.",
    "Can cover Backend and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development, adds programming and web, studies Computer Science rather than your AI and Data Science and shares Mandarin.",
    "Can cover Database, adds programming and web, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## M02 Provider timeout falls back

Result: **PASS**. Test: `test_cases.MatchingCases.test_timeout`.

Input: Simulated provider raises TimeoutError.

Expected: Five eligible nonblank results; fallback source and no crash.

Observed:

```json
{
  "eligible": 13,
  "ids": [
    11,
    2,
    15,
    6,
    14
  ],
  "source": "fallback:TimeoutError",
  "reasons": [
    "Can cover Agentic Development, adds github and ai_agent, studies Computer Science rather than your AI and Data Science and shares English and Mandarin.",
    "Can cover Backend and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development, adds programming and web, studies Computer Science rather than your AI and Data Science and shares Mandarin.",
    "Can cover Database, adds programming and web, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## M03 Verified structured evidence and private payload

Result: **PASS**. Test: `test_cases.MatchingCases.test_payload_and_evidence`.

Input: Simulated response names an eligible role/skill/programme; inspect actual model payload.

Expected: Reason cites valid facts; real schema used; payload excludes contacts, hashes and fallback score.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "source": "evaluation:simulated",
  "reasons": [
    "Synthetic 1 can cover Backend, brings programming experience and comes from a different programme (Applied AI).",
    "Synthetic 2 brings programming experience and comes from a different programme (Applied AI).",
    "Synthetic 3 brings programming experience and comes from a different programme (Applied AI).",
    "Synthetic 4 brings programming experience and comes from a different programme (Applied AI).",
    "Synthetic 5 brings programming experience and comes from a different programme (Applied AI)."
  ],
  "payload": {
    "me": {
      "display_name": "Evaluation Student",
      "city": "HK",
      "programme": "AI and Data Science",
      "preferred_role": "Frontend",
      "open_roles": [
        "Frontend"
      ],
      "skills": {
        "programming": 0,
        "github": 0,
        "debugging": 0,
        "web": 0,
        "ai_agent": 0
      },
      "languages": [
        "English",
        "Mandarin"
      ]
    },
    "candidates": [
      {
        "account_id": 1,
        "display_name": "Synthetic 1",
        "city": "HK",
        "shared_languages": [
          "English"
        ],
        "role_fit": "complement",
        "programme": "Applied AI",
        "preferred_role": "Backend",
        "open_roles": [
          "Backend"
        ],
        "skills": {
          "programming": 1,
          "github": 0,
          "debugging": 0,
          "web": 0,
          "ai_agent": 0
        },
        "languages": [
          "English"
        ],
        "fills_roles": [
          "Backend"
        ],
        "complements": [
          "programming"
        ]
      },
      {
        "account_id": 2,
        "display_name": "Synthetic 2",
        "city": "HK",
        "shared_languages": [
          "English"
        ],
        "role_fit": "complement",
        "programme": "Applied AI",
        "preferred_role": "Backend",
        "open_roles": [
          "Backend"
        ],
        "skills": {
          "programming": 1,
          "github": 0,
          "debugging": 0,
          "web": 0,
          "ai_agent": 0
        },
        "languages": [
          "English"
        ],
        "fills_roles": [
          "Backend"
        ],
        "complements": [
          "programming"
        ]
      },
      {
        "account_id": 3,
        "display_name": "Synthetic 3",
        "city": "HK",
        "shared_languages": [
          "English"
        ],
        "role_fit": "complement",
        "programme": "Applied AI",
        "preferred_role": "Backend",
        "open_roles": [
          "Backend"
        ],
        "skills": {
          "programming": 1,
          "github": 0,
          "debugging": 0,
          "web": 0,
          "ai_agent": 0
        },
        "languages": [
          "English"
        ],
        "fills_roles": [
          "Backend"
        ],
        "complements": [
          "programming"
        ]
      },
      {
        "account_id": 4,
        "display_name": "Synthetic 4",
        "city": "HK",
        "shared_languages": [
          "English"
        ],
        "role_fit": "complement",
        "programme": "Applied AI",
        "preferred_role": "Backend",
        "open_roles": [
          "Backend"
        ],
        "skills": {
          "programming": 1,
          "github": 0,
          "debugging": 0,
          "web": 0,
          "ai_agent": 0
        },
        "languages": [
          "English"
        ],
        "fills_roles": [
          "Backend"
        ],
        "complements": [
          "programming"
        ]
      },
      {
        "account_id": 5,
        "display_name": "Synthetic 5",
        "city": "HK",
        "shared_languages": [
          "English"
        ],
        "role_fit": "complement",
        "programme": "Applied AI",
        "preferred_role": "Backend",
        "open_roles": [
          "Backend"
        ],
        "skills": {
          "programming": 1,
          "github": 0,
          "debugging": 0,
          "web": 0,
          "ai_agent": 0
        },
        "languages": [
          "English"
        ],
        "fills_roles": [
          "Backend"
        ],
        "complements": [
          "programming"
        ]
      },
      {
        "account_id": 6,
        "display_name": "Synthetic 6",
        "city": "HK",
        "shared_languages": [
          "English"
        ],
        "role_fit": "complement",
        "programme": "Applied AI",
        "preferred_role": "Backend",
        "open_roles": [
          "Backend"
        ],
        "skills": {
          "programming": 1,
          "github": 0,
          "debugging": 0,
          "web": 0,
          "ai_agent": 0
        },
        "languages": [
          "English"
        ],
        "fills_roles": [
          "Backend"
        ],
        "complements": [
          "programming"
        ]
      }
    ]
  },
  "schema": "Shortlist"
}
```

## M04 Invalid and duplicate IDs removed

Result: **PASS**. Test: `test_cases.MatchingCases.test_invalid_duplicate`.

Input: Simulated unknown ID, repeated valid ID and five distinct valid IDs.

Expected: Return five unique eligible IDs only.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "source": "evaluation:simulated",
  "reasons": [
    "Synthetic 1 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 2 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 3 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 4 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 5 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## M05 All-invalid output falls back

Result: **PASS**. Test: `test_cases.MatchingCases.test_all_invalid`.

Input: Model returns only an out-of-pool ID.

Expected: Five deterministic picks and an explicit fallback source.

Observed:

```json
{
  "eligible": 13,
  "ids": [
    11,
    2,
    15,
    6,
    14
  ],
  "source": "fallback:no valid ids returned",
  "reasons": [
    "Can cover Agentic Development, adds github and ai_agent, studies Computer Science rather than your AI and Data Science and shares English and Mandarin.",
    "Can cover Backend and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development, adds programming and web, studies Computer Science rather than your AI and Data Science and shares Mandarin.",
    "Can cover Database, adds programming and web, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## M06 Oversized output capped

Result: **PASS**. Test: `test_cases.MatchingCases.test_too_many`.

Input: Model returns six eligible people.

Expected: At most five recommendations.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "source": "evaluation:simulated",
  "reasons": [
    "Synthetic 1 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 2 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 3 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 4 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 5 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## M07 Short valid output supplies five

Result: **FAIL**. Test: `test_cases.MatchingCases.test_short_output`.

Input: Six eligible people; model returns ID 1 twice and invalid ID 999999.

Expected: Five unique eligible recommendations after validation/fallback.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1
  ],
  "source": "evaluation:simulated",
  "reasons": [
    "Synthetic 1 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

Failure evidence:

```text
Traceback (most recent call last):
  File "<REPO>\evaluation\test_cases.py", line 162, in test_short_output
    validate_picks(self.me,c,p)
  File "<REPO>\evaluation\common.py", line 56, in validate_picks
    require(len(picks) == expected_count, f"Expected {expected_count} candidates; got {len(picks)}")
  File "<REPO>\evaluation\common.py", line 52, in require
    raise AssertionError(message)
AssertionError: Expected 5 candidates; got 1
```

## M08 Empty evidence produces nonblank verified sentences

Result: **PASS**. Test: `test_cases.MatchingCases.test_empty_evidence`.

Input: Five valid IDs, blank roles and empty skills/programme flags.

Expected: Application produces five nonblank reasons from verified profile facts.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "source": "evaluation:simulated",
  "reasons": [
    "Synthetic 1 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 2 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 3 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 4 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 5 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## M09 Invented role and absent skill claims are rejected

Result: **PASS**. Test: `test_cases.MatchingCases.test_hallucinated_evidence`.

Input: Model claims Database, AI-agent skills and a different programme for same-programme Backend candidates with skills=0.

Expected: Reasons do not repeat the invented facts and remain nonblank.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "source": "evaluation:simulated",
  "reasons": [
    "Synthetic 1 can cover Backend and shares English.",
    "Synthetic 2 can cover Backend and shares English.",
    "Synthetic 3 can cover Backend and shares English.",
    "Synthetic 4 can cover Backend and shares English.",
    "Synthetic 5 can cover Backend and shares English."
  ]
}
```

## M10 Malformed response schema falls back

Result: **PASS**. Test: `test_cases.MatchingCases.test_invalid_schema`.

Input: Structured output has a noninteger account_id.

Expected: Real Pydantic validation rejects it; matching falls back safely.

Observed:

```json
{
  "eligible": 13,
  "ids": [
    11,
    2,
    15,
    6,
    14
  ],
  "source": "fallback:ValidationError",
  "reasons": [
    "Can cover Agentic Development, adds github and ai_agent, studies Computer Science rather than your AI and Data Science and shares English and Mandarin.",
    "Can cover Backend and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development, adds programming and web, studies Computer Science rather than your AI and Data Science and shares Mandarin.",
    "Can cover Database, adds programming and web, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Agentic Development and Database, adds github and ai_agent, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## M11 Only the five defined skills may be explained

Result: **FAIL**. Test: `test_cases.MatchingCases.test_unsupported_skill`.

Input: Candidate ID is 1; model names account_id as a skill.

Expected: An ID field must not become a skill claim in the explanation.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "source": "evaluation:simulated",
  "reasons": [
    "Synthetic 1 brings account_id experience.",
    "Synthetic 2 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 3 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 4 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Synthetic 5 can cover Backend, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

Failure evidence:

```text
Traceback (most recent call last):
  File "<REPO>\evaluation\test_cases.py", line 188, in test_unsupported_skill
    validate_picks(self.me,c,p);self.assertNotIn('account_id',p[0]['reason'])
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'account_id' unexpectedly found in 'Synthetic 1 brings account_id experience.'
```

## P01 All new preference values round-trip

Result: **PASS**. Test: `test_cases.APICases.test_fields_reach_matcher`.

Input: Save programme, flexible roles and all five skill flags, then read and match.

Expected: Values persist exactly and saved preferences reach the existing matcher payload.

Observed:

```json
{
  "saved_preferences": {
    "programme": "Computer Science",
    "open_roles": [
      "Backend",
      "Database"
    ],
    "programming": 1,
    "github": 0,
    "debugging": 1,
    "web": 0,
    "ai_agent": 1
  },
  "count": 5
}
```

## P02 New preference validation

Result: **PASS**. Test: `test_cases.APICases.test_new_validation`.

Input: Invalid programme, out-of-range/bool skill flags and open_roles missing preferred_role.

Expected: 422 for each invalid input; valid profile can still be saved afterwards.

Observed:

```json
{
  "invalid_statuses": [
    422,
    422,
    422,
    422
  ]
}
```

## P03 Clearing open roles and skills is preserved

Result: **PASS**. Test: `test_cases.APICases.test_clear_preferences`.

Input: Save flexible roles and skills, then save open_roles=[] and programming=0.

Expected: Explicit zero and empty list persist; omitted optional fields preserve prior values.

Observed:

```json
{
  "open_roles": [],
  "programming": 0
}
```

## P04 Empty-candidate browser-demo boundary

Result: **PASS**. Test: `test_cases.APICases.test_empty_demo_case`.

Input: Register and save the only profile in a disposable database, then POST /matches.

Expected: 200 with no eligible candidates, empty picks and source=empty.

Observed:

```json
{
  "picks": [],
  "source": "empty",
  "stats": {
    "total_pool": 1,
    "eligible": 0,
    "filtered_out": 1
  },
  "filter_summary": {
    "that's you": 1
  }
}
```

## R01 Hard exclusions and soft language

Result: **PASS**. Test: `test_cases.MatchingCases.test_hard_filters`.

Input: Self, SH, placed HK and Cantonese-only HK candidate.

Expected: Only the unplaced other HK candidate remains; lack of shared language does not exclude.

Observed:

```json
{
  "eligible": 1,
  "ids": [
    3
  ],
  "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL",
  "reasons": [
    "Can cover Backend and studies Applied AI rather than your AI and Data Science."
  ],
  "drops": [
    "that's you",
    "different cohort (SH)",
    "already in a team"
  ]
}
```

## R02 Empty and undersized pools

Result: **PASS**. Test: `test_cases.MatchingCases.test_pool_sizes`.

Input: Separate pools of 0, 1, 2, 4 and 5 eligible people.

Expected: Return exactly min(5, eligible), with no invented people.

Observed:

```json
{
  "0": {
    "count": 0,
    "source": "empty"
  },
  "1": {
    "count": 1,
    "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL"
  },
  "2": {
    "count": 2,
    "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL"
  },
  "4": {
    "count": 4,
    "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL"
  },
  "5": {
    "count": 5,
    "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL"
  }
}
```

## R03 Legacy and enriched 30-profile sweeps

Result: **PASS**. Test: `test_cases.MatchingCases.test_all_profiles`.

Input: Each of 30 legacy profiles and 30 enriched variants, twice.

Expected: All 60 queries satisfy count, eligibility, uniqueness and explanation invariants; deterministic repeats agree.

Observed:

```json
{
  "queries": [
    {
      "dataset": "legacy",
      "student_id": 1,
      "eligible": 12,
      "ids": [
        4,
        7,
        8,
        2,
        12
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 2,
      "eligible": 12,
      "ids": [
        1,
        4,
        8,
        6,
        11
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 3,
      "eligible": 13,
      "ids": [
        6,
        2,
        4,
        1,
        7
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 4,
      "eligible": 12,
      "ids": [
        1,
        7,
        8,
        11,
        2
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 5,
      "eligible": 12,
      "ids": [
        1,
        4,
        7,
        13,
        11
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 6,
      "eligible": 12,
      "ids": [
        2,
        4,
        8,
        7,
        12
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 7,
      "eligible": 12,
      "ids": [
        1,
        4,
        8,
        11,
        6
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 8,
      "eligible": 12,
      "ids": [
        1,
        2,
        4,
        6,
        7
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 9,
      "eligible": 13,
      "ids": [
        1,
        7,
        13,
        11,
        2
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 10,
      "eligible": 12,
      "ids": [
        6,
        13,
        2,
        4,
        1
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 11,
      "eligible": 12,
      "ids": [
        4,
        7,
        8,
        2,
        12
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 12,
      "eligible": 12,
      "ids": [
        1,
        4,
        8,
        6,
        11
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 13,
      "eligible": 12,
      "ids": [
        1,
        4,
        7,
        6,
        11
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 14,
      "eligible": 12,
      "ids": [
        1,
        2,
        8,
        6,
        7
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 15,
      "eligible": 12,
      "ids": [
        1,
        4,
        7,
        13,
        11
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 16,
      "eligible": 13,
      "ids": [
        28,
        19,
        22,
        24,
        27
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 17,
      "eligible": 13,
      "ids": [
        28,
        16,
        19,
        21,
        24
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 18,
      "eligible": 13,
      "ids": [
        27,
        29,
        16,
        19,
        22
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 19,
      "eligible": 13,
      "ids": [
        28,
        16,
        22,
        27,
        17
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 20,
      "eligible": 14,
      "ids": [
        27,
        28,
        29,
        16,
        17
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 21,
      "eligible": 13,
      "ids": [
        28,
        17,
        19,
        22,
        24
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 22,
      "eligible": 13,
      "ids": [
        28,
        16,
        19,
        24,
        29
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 23,
      "eligible": 13,
      "ids": [
        27,
        29,
        16,
        19,
        22
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 24,
      "eligible": 13,
      "ids": [
        28,
        16,
        22,
        27,
        17
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 25,
      "eligible": 13,
      "ids": [
        27,
        28,
        29,
        16,
        17
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 26,
      "eligible": 13,
      "ids": [
        28,
        17,
        19,
        22,
        24
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 27,
      "eligible": 13,
      "ids": [
        28,
        29,
        16,
        18,
        19
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 28,
      "eligible": 13,
      "ids": [
        16,
        19,
        22,
        24,
        27
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 29,
      "eligible": 13,
      "ids": [
        27,
        28,
        16,
        18,
        22
      ]
    },
    {
      "dataset": "legacy",
      "student_id": 30,
      "eligible": 13,
      "ids": [
        28,
        16,
        17,
        19,
        21
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 1,
      "eligible": 12,
      "ids": [
        11,
        2,
        15,
        6,
        14
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 2,
      "eligible": 12,
      "ids": [
        12,
        15,
        6,
        4,
        7
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 3,
      "eligible": 13,
      "ids": [
        5,
        8,
        14,
        13,
        2
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 4,
      "eligible": 12,
      "ids": [
        5,
        11,
        2,
        6,
        14
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 5,
      "eligible": 12,
      "ids": [
        15,
        12,
        6,
        4,
        7
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 6,
      "eligible": 12,
      "ids": [
        11,
        5,
        8,
        1,
        7
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 7,
      "eligible": 12,
      "ids": [
        8,
        14,
        12,
        2,
        6
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 8,
      "eligible": 12,
      "ids": [
        6,
        15,
        1,
        7,
        12
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 9,
      "eligible": 13,
      "ids": [
        11,
        8,
        2,
        14,
        4
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 10,
      "eligible": 12,
      "ids": [
        5,
        8,
        11,
        12,
        15
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 11,
      "eligible": 12,
      "ids": [
        6,
        12,
        15,
        1,
        13
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 12,
      "eligible": 12,
      "ids": [
        11,
        2,
        14,
        7,
        8
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 13,
      "eligible": 12,
      "ids": [
        11,
        12,
        15,
        8,
        6
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 14,
      "eligible": 12,
      "ids": [
        12,
        6,
        1,
        4,
        7
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 15,
      "eligible": 12,
      "ids": [
        5,
        8,
        14,
        2,
        1
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 16,
      "eligible": 13,
      "ids": [
        27,
        23,
        29,
        30,
        21
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 17,
      "eligible": 13,
      "ids": [
        24,
        30,
        27,
        28,
        22
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 18,
      "eligible": 13,
      "ids": [
        23,
        29,
        28,
        17,
        16
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 19,
      "eligible": 13,
      "ids": [
        24,
        29,
        30,
        21,
        26
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 20,
      "eligible": 14,
      "ids": [
        30,
        27,
        21,
        25,
        18
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 21,
      "eligible": 13,
      "ids": [
        26,
        23,
        22,
        28,
        19
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 22,
      "eligible": 13,
      "ids": [
        24,
        23,
        27,
        29,
        21
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 23,
      "eligible": 13,
      "ids": [
        24,
        21,
        28,
        27,
        16
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 24,
      "eligible": 13,
      "ids": [
        29,
        26,
        23,
        17,
        22
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 25,
      "eligible": 13,
      "ids": [
        30,
        27,
        24,
        23,
        26
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 26,
      "eligible": 13,
      "ids": [
        21,
        24,
        30,
        27,
        28
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 27,
      "eligible": 13,
      "ids": [
        29,
        26,
        28,
        22,
        23
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 28,
      "eligible": 13,
      "ids": [
        27,
        21,
        23,
        29,
        17
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 29,
      "eligible": 13,
      "ids": [
        24,
        27,
        18,
        30,
        28
      ]
    },
    {
      "dataset": "enriched",
      "student_id": 30,
      "eligible": 13,
      "ids": [
        23,
        17,
        28,
        29,
        26
      ]
    }
  ]
}
```

## R04 Open roles add useful coverage

Result: **PASS**. Test: `test_cases.MatchingCases.test_open_roles`.

Input: Frontend-preferred candidate also offers Database; other candidates repeat Frontend.

Expected: Flexible candidate is retained and recommended before identical Frontend-only candidates.

Observed:

```json
{
  "eligible": 2,
  "ids": [
    1,
    2
  ],
  "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL",
  "reasons": [
    "Can cover Database, studies Applied AI rather than your AI and Data Science and shares English.",
    "Studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## R05 Known missing skill increases preference

Result: **PASS**. Test: `test_cases.MatchingCases.test_skill_preference`.

Input: Two otherwise equal Backend candidates; only Zulu has programming=1, student has programming=0.

Expected: Zulu precedes Alpha; explanation can cite programming.

Observed:

```json
{
  "eligible": 2,
  "ids": [
    2,
    1
  ],
  "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL",
  "reasons": [
    "Can cover Backend, adds programming, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Backend, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## R06 Language preference remains soft

Result: **PASS**. Test: `test_cases.MatchingCases.test_language_preference`.

Input: Identical candidates, one shares two languages and one shares none.

Expected: Both retained; shared-language candidate preferred on an otherwise equal tie.

Observed:

```json
{
  "eligible": 2,
  "ids": [
    2,
    1
  ],
  "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL",
  "reasons": [
    "Can cover Backend, studies Applied AI rather than your AI and Data Science and shares English and Mandarin.",
    "Can cover Backend and studies Applied AI rather than your AI and Data Science."
  ]
}
```

## R07 Duplicate roles may fill remaining slots

Result: **PASS**. Test: `test_cases.MatchingCases.test_duplicate_roles_allowed`.

Input: Six eligible Backend-only candidates.

Expected: Five distinct candidates returned; role diversity is not a hard exclusion.

Observed:

```json
{
  "eligible": 6,
  "ids": [
    1,
    2,
    3,
    4,
    5
  ],
  "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL",
  "reasons": [
    "Can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Backend, studies Applied AI rather than your AI and Data Science and shares English.",
    "Can cover Backend, studies Applied AI rather than your AI and Data Science and shares English."
  ]
}
```

## S01 Declared weighted score on hand-calculated example

Result: **PASS**. Test: `test_cases.MatchingCases.test_weighted_example`.

Input: Backend+Database, one missing skill, one shared language; different programme has share .25.

Expected: role=.400, skills=.070, flexibility=.033, languages=.025, programme=.075; total=.603.

Observed:

```json
{
  "total": 0.603,
  "role": 0.4,
  "skills": 0.07,
  "flexibility": 0.033,
  "languages": 0.025,
  "programme": 0.075,
  "complements": [
    "programming"
  ],
  "fills_roles": [
    "Backend",
    "Database"
  ]
}
```

## S02 Rare programmes gain preference

Result: **PASS**. Test: `test_cases.MatchingCases.test_programme_rarity`.

Input: Same eligible role and skills, candidates from a common versus rare different programme.

Expected: Rarer different programme has higher programme contribution, same-programme contribution is zero.

Observed:

```json
{
  "common": 0.02,
  "rare": 0.08,
  "same": 0.0
}
```

## S03 Legacy attributes and null candidate skills

Result: **PASS**. Test: `test_cases.MatchingCases.test_legacy_and_null_candidate`.

Input: Legacy profiles lack programme/open_roles/skills; another candidate has null skill flags.

Expected: Matching remains usable; no candidate skill is invented from null values.

Observed:

```json
{
  "eligible": 13,
  "ids": [
    4,
    7,
    8,
    2,
    12
  ],
  "source": "fallback:no DEEPSEEK_API_KEY or MATCH_MODEL",
  "reasons": [
    "Can cover Agentic Development and shares English and Mandarin.",
    "Can cover Backend and shares English and Mandarin.",
    "Can cover Database and shares English.",
    "Can cover Backend and shares English.",
    "Can cover Backend and shares English."
  ]
}
```

## S04 Unknown student skills are neutral

Result: **FAIL**. Test: `test_cases.MatchingCases.test_unknown_student_skill`.

Input: Student programming=None (unknown); candidate programming=1.

Expected: An unknown student skill is not reported as a known missing-skill complement, as stated by the prompt/docs.

Observed:

```json
{
  "total": 0.595,
  "role": 0.4,
  "skills": 0.07,
  "flexibility": 0.0,
  "languages": 0.025,
  "programme": 0.1,
  "complements": [
    "programming"
  ],
  "fills_roles": [
    "Backend"
  ]
}
```

Failure evidence:

```text
Traceback (most recent call last):
  File "<REPO>\evaluation\test_cases.py", line 112, in test_unknown_student_skill
    self.assertNotIn('programming',r['complements'],'Unknown skill is treated as an established lack.')
AssertionError: 'programming' unexpectedly found in ['programming'] : Unknown skill is treated as an established lack.
```
