# Final test cases and evaluation pack

This pack evaluates application baseline **81886ac18511398f320b0e592828ea00c956d7cd**. It supplies case inputs, expectations, actual results, failure evidence, real-model responses, browser screenshots and a report excerpt. It adds files only under `evaluation/`; it does not change the team's runtime code or repair the documented defects.

Start with [FINAL_SUMMARY.md](FINAL_SUMMARY.md), [TEST_CASES.csv](TEST_CASES.csv), [the detailed results](results/offline/REPORT.md), and [LIMITATIONS.md](LIMITATIONS.md). Suggested report text is in [REPORT_EXCERPT.md](REPORT_EXCERPT.md). Real and simulated results are explicitly separated.

## Reproduce the automated evaluation

Clone the published repository and run from its root. The publication commit includes this evaluation directory; SOURCE.json identifies the application baseline. The runner verifies the baseline application files, so an evaluation-only publication commit remains reproducible:

```text
git clone https://github.com/191325-smy/AILT9019.git
cd AILT9019
python -m venv .venv
```

Activate `.venv` (`.venv\Scripts\Activate.ps1` in Windows PowerShell, or `source .venv/bin/activate` in a POSIX shell), then:

```text
python -m pip install -r requirements.txt
python -m pip check
python evaluation/run_evaluation.py
```

For the exact clean Windows Python 3.12 package versions recorded in this pack, install `evaluation/requirements-tested.txt` instead of the floating root requirements. This lock describes the tested Windows environment; it is not a guarantee for other operating systems.

Expected result for this baseline: **55 cases, 51 PASS, 4 FAIL, 0 ERROR; exit code 1**. Exit 1 is the correct signal for documented product failures, not an installation problem. Exit 2 means a runner/source-integrity error. Do not change expectations to manufacture an all-green run. The existing backend tests are run once as part of the 55 and are not counted a second time.

Offline mode overrides inherited model/database configuration, suppresses `.env` loading, uses the existing disposable SQLite test branch and simulates model transport. It validates simulated responses with the real Pydantic schema; it does not test provider SDK behaviour or a PostgreSQL service. No configured shared database is used.

`SOURCE.json` identifies the immutable GitHub blobs. The runner checks application-file hashes before and after execution and records Python/package versions and evaluation-file hashes. For a new application revision, deliberately update the source manifest and rerun; do not present these results as evidence for changed source. Path information is replaced with placeholders in captured test output.

## Repeat the real-model sample

Use a private `.env` file containing only your locally configured API key/model. Do not send it to anyone or include it in this pack.

```text
python evaluation/run_evaluation.py --live --key-file /absolute/private/path/to/.env
```

This makes **six actual calls**, three synthetic profiles twice each, using the existing `matching.matcher.pick`. It reads only DEEPSEEK_API_KEY and MATCH_MODEL from the supplied file and never contacts its DATABASE_URL. Each call has a 75-second outer evaluation deadline. Missing keys produce a runner error; fallback replies are failures for live-connectivity acceptance. Six successes do not prove general matching quality, fairness, or real-student satisfaction.

Then regenerate the summary:

```text
python evaluation/summarize.py
```

This reads existing offline/live/browser evidence; it does not create new API calls. The explanation audit checks defined factual claims mechanically. A team member still needs to inspect the reasons and record their actual human verification in the final report.

## Data and scope

- `matching/sample_pool.json`: unchanged original 30 synthetic profiles.
- `fixtures/enriched_profiles.json`: the same synthetic identities/cities/roles/team flags, with explicitly generated evaluation attributes. For ID `i`, programme cycles through the four API programmes; open roles are preferred role plus the concrete role at `i % 4`; skill `j` is 1 when `(i+j) % 3 == 0`, otherwise 0. These additions are test inputs, not collected student facts.
- The 60-query sweep is **one case**, covering original and enriched profiles; repeated deterministic runs are not additional independent samples.
- Small/empty pools and preference-isolation cases use additional labelled synthetic data in `test_cases.py`.
- Role/programme coverage comparisons are descriptive; the fallback is a baseline, not labelled ground truth or an optimality oracle. Role duplicates and no shared language remain allowed.
- Four ordinary failures are preserved. Time overlap, mutual consent, production PostgreSQL and student-level quality/fairness are disclosed limitations, not claimed passing features.
- Dependency installation was verified in a newly created Windows Python 3.12 environment. The final offline evaluation was rerun in a separate fresh Git clone, using that recorded environment; all 35 baseline application files were verified against GitHub blob hashes. Live/browser checks used identical verified source in the preceding isolated checkout. Shared PostgreSQL is not part of this reproduction.

## Browser evidence and recording

See [BROWSER_CHECKLIST.md](BROWSER_CHECKLIST.md) for the real UI workflow, model toggle, negative login, and empty-pool case. `demo_app.py` is a test-only adapter using the existing app factory and SQLite test support; it never changes production code. The recorded browser verification includes one additional successful real-model request, so total observed API invocations are six direct plus one browser call.

## Course requirements covered

- Report Sections 3–4 / A2: success criteria, methods, concrete results, expected versus observed failures, limitations and improvements.
- B1: successful and boundary/failure behaviour plus invalid-input handling.
- B2: source identity, exact tested environment, install/run/test instructions and reproducibility evidence, with missing production/PostgreSQL verification stated.
- C1/C2: a genuine run, concise evaluation evidence and a real boundary case for the webpage/demo.

The rubric does not prescribe a test count or a particular folder layout. Report body is still limited to five pages; put detailed logs in repository/appendix and keep the principal results and failure discussion in the body. Source requirements: [rubric](https://moodle.hku.hk/mod/resource/view.php?id=4356067), [report template](https://moodle.hku.hk/mod/resource/view.php?id=4355806), [final announcement](https://edstem.org/au/courses/40809/discussion/3719878).
