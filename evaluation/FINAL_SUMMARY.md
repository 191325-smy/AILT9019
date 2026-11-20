# Final evaluation summary

Application baseline: `81886ac18511398f320b0e592828ea00c956d7cd`. Offline run: 2026-11-20T20:16:16+08:00.

## Results

| Evidence | Result | Scope |
|---|---|---|
| Offline automated acceptance | 51/55 PASS; 4 FAIL; 0 ERROR | Includes 25 existing backend tests and 30 new acceptance cases |
| Fixture sweep | 60 profile queries, each repeated twice | 30 legacy + 30 enriched synthetic variants, counted as one automated case |
| Direct real-model checks | 6/6 successful | DeepSeek Flash, three synthetic profiles repeated twice |
| Automatic explanation fact audit | 30/30 without detected claim errors | Defined skill/role/programme assertions only; no human relevance/satisfaction rating |
| Browser scenarios | 7/7 PASS | Real UI/HTTP, temporary SQLite adapter; includes one additional real API call and empty-pool case |
| Clean environment | Install and pip check succeeded | Windows, Python 3.12.14; exact packages in requirements-tested.txt |

Six direct calls: median **2.554 s**, range **2.406–2.953 s**. This is a small client-side timing sample, not a service benchmark.

The six scripted calls plus one browser call are **seven observed real API invocations**, not seven additional test cases. Source labels were checked; fallback responses were not counted as live successes.

## Product failures

| Case | Finding | Evidence |
|---|---|---|
| K02 | Revocation across two cache instances | [Observed result and traceback](results/offline/REPORT.md#k02-revocation-across-two-cache-instances) |
| M07 | Short valid output supplies five | [Observed result and traceback](results/offline/REPORT.md#m07-short-valid-output-supplies-five) |
| M11 | Only the five defined skills may be explained | [Observed result and traceback](results/offline/REPORT.md#m11-only-the-five-defined-skills-may-be-explained) |
| S04 | Unknown student skills are neutral | [Observed result and traceback](results/offline/REPORT.md#s04-unknown-student-skills-are-neutral) |

Detailed causes and proposed fixes: [LIMITATIONS.md](LIMITATIONS.md). Failure labels remain ordinary FAIL results; the offline command correctly exits 1.

## Evidence links

- [All case inputs, expected and actual results](results/offline/REPORT.md)
- [Machine-readable results, source hashes and environment](results/offline/results.json)
- [Captured automated test run](results/offline/test-run.txt)
- [Real model results and descriptive comparison](results/live/REPORT.md)
- [Raw model results and timing](results/live/results.json)
- [Explanation audit and role/programme coverage comparison](results/live/factual-audit.json)
- [Browser scenarios](results/browser/results.json)
- [Real AI screenshot](results/browser/ai-results.png)
- [Empty-pool screenshot](results/browser/empty-pool.png)

## Limits on the conclusion

No shared PostgreSQL database, production deployment, multi-process PostgreSQL integration, real-student satisfaction or fairness study was tested. Cache cases enable production cache logic over isolated SQLite to reproduce the logic, not the database driver. Time-overlap preferences and mutual contact consent remain unimplemented. The team must review these results and name the actual human reviewers in its AI-use disclosure.

Reproduction note: after the initial transport failure, a separate fresh Git clone succeeded using HTTP/1.1. The final offline run was executed in that clone against the 35 verified baseline files, using the recorded dependency environment. Live/browser modes used identical verified application files in the preceding isolated checkout. No shared PostgreSQL deployment was exercised.
