# Observed failures and limits

These findings apply to application commit `81886ac18511398f320b0e592828ea00c956d7cd`. The application files are unchanged. Re-run the named case after any fix and retain before/after evidence.

| Case | Observed failure | Cause and proposed next step |
|---|---|---|
| M07 | Six eligible candidates; after dropping duplicate/invalid IDs, one recommendation remains instead of five. | `matching/matcher.py` falls back only when no valid IDs remain. Fall back or top up using unique eligible candidates when the validated count is short. |
| S04 | `programming=None` for the student and 1 for the candidate is counted as a known complementary skill. | `scoring.py` uses `me.get(k) != 1`, treating unknown like known zero despite the prompt/docs saying unknown is neutral. Agree unknown semantics, apply them consistently to scoring/evidence and rerun the isolated test. |
| M11 | A simulated model asks for skill `account_id`; candidate ID 1 causes the explanation to say `account_id experience`. | `_describe` checks `cand.get(skill) == 1` without requiring membership in the five allowed skills. Whitelist SKILLS before looking up values. This is adversarial synthetic output, not an observed live-model error frequency. |
| K02 | Two cache instances remember a session; revoking in one does not immediately invalidate the other's cached session. | Cached entries are trusted until expiry without shared invalidation. Use shared revocation/revalidation, or explicitly restrict deployment to one process and document the remaining cache assumption. The case enables cache logic over temporary SQLite; no multi-worker PostgreSQL deployment was tested. |

The previous blank-reason failure is no longer reproduced: the current application constructs a nonblank sentence from verified structured evidence even when the model supplies empty evidence. This pass does not imply arbitrary model-supplied skill keys are safe; M11 demonstrates the remaining boundary.

## Unverified or outside the implemented scope

- PostgreSQL driver/pool integration, required deployed table schemas, migrations and public Render deployment have not been exercised. SQLite API tests are not a replacement for production integration tests.
- No live shared accounts/profiles were read or modified. A private model key was used only for explicitly labelled real-model calls over synthetic data; it is absent from the evidence files.
- Time-overlap preferences and mutual-consent contact release are unimplemented. The fixture uses synthetic contact addresses; results must not be described as having a consent gate.
- Six direct live calls plus one browser call are a small connectivity/behaviour sample. The explanation audit checks defined factual claims, not human usefulness, fairness, recommendation optimality or student satisfaction.
- Original versus enriched fixtures share identities and are not independent student populations. The deterministic repeat check proves repeatability on those inputs, not general reliability.
- The programme/role coverage comparison reports descriptive diversity; it does not define a single correct ranking or prove the model is better than fallback.
- Team members must review the evidence and identify actual human verifiers and contributions. Generated report text must not be presented as already approved by the team.
