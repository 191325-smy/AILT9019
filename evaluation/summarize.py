"""Generate report excerpts and a case catalogue from actual saved results."""
import csv
import importlib.metadata
import json
import re
import statistics
import sys
from pathlib import Path
from unittest.mock import patch
from common import HERE, ROOT, SKILLS, fixture, source_integrity
sys.path.insert(0,str(ROOT))
with patch('dotenv.load_dotenv',return_value=False):
    from matching import filters,matcher,scoring


def main():
    offline=json.loads((HERE/'results/offline/results.json').read_text(encoding='utf-8'))
    live=json.loads((HERE/'results/live/results.json').read_text(encoding='utf-8'))
    browser=json.loads((HERE/'results/browser/results.json').read_text(encoding='utf-8'))
    revision,hashes=source_integrity()
    if not (revision==offline['metadata']['revision']==live['metadata']['revision']==browser['revision']):
        raise RuntimeError('Evidence versions differ; rerun the stale mode before summarising')
    if not all(x['baseline_blob_matches'] for x in hashes):
        raise RuntimeError('Application source differs from the recorded baseline')
    labels={'programming':'programming','github':'GitHub','debugging':'debugging','web':'web development','ai_agent':'AI-agent'}
    audits=[];comparison=[];pool=fixture()
    for call in live['calls']:
        if not call.get('live_model'):continue
        me=next(p for p in pool if p['account_id']==call['student_id'])
        c,_,_=filters.candidates_for_model(me,pool)
        fallback,_=matcher.pick(me,c,use_model=False)
        def diversity(picks):
            return dict(roles=len(set([me['preferred_role'],*[r for p in picks for r in scoring.offered(p['profile'])]]) & set(scoring.CONCRETE_ROLES)),
                        programmes=len({me['programme'],*[p['profile']['programme'] for p in picks]}))
        comparison.append(dict(call=call['id'],ai=diversity(call['picks']),fallback=diversity(fallback),
                               identical_ids={p['profile']['account_id'] for p in call['picks']}=={p['profile']['account_id'] for p in fallback}))
        for pick in call['picks']:
            p=pick['profile'];text=pick['reason'];errors=[]
            for skill,label in labels.items():
                if re.search(r'\b'+re.escape(label)+r'\b',text,re.I) and p.get(skill)!=1:
                    errors.append('unsupported skill '+skill)
            for role in scoring.CONCRETE_ROLES:
                if re.search(r'can cover '+re.escape(role)+r'\b',text,re.I) and role not in scoring.offered(p):
                    errors.append('unsupported role '+role)
            if 'different programme' in text and (not p.get('programme') or p['programme']==me.get('programme')):
                errors.append('unsupported programme difference')
            audits.append(dict(call=call['id'],candidate_id=p['account_id'],reason=text,errors=errors,
                               check='Defined skill/role/programme claims against synthetic attributes; not a human quality rating'))
    audit=dict(explanations_checked=len(audits),without_detected_claim_errors=sum(not a['errors'] for a in audits),
               rows=audits,coverage_comparison=comparison,human_review='Pending team review; no human sign-off is invented')
    (HERE/'results/live/factual-audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    live_lines=['# Real model results','',f"Model: `{live['model']}`. Application: `{revision}`.",'',
                'These calls use the actual API and synthetic fixtures, not simulated provider output. Explanations are composed by the application from structured evidence returned by the model.','',
                '| Call | Status | Seconds | AI roles / programmes | Fallback roles / programmes |','|---|---|---:|---|---|']
    by_call={r['call']:r for r in comparison}
    for c in live['calls']:
        v=by_call.get(c['id'])
        if v:live_lines.append(f"| {c['id']} | {c['status']} | {c['elapsed_seconds']:.3f} | {v['ai']['roles']} / {v['ai']['programmes']} | {v['fallback']['roles']} / {v['fallback']['programmes']} |")
    live_lines+=['','Role coverage is the union of offered concrete roles (preferred + open roles), including the student. It does not solve one-person-one-role assignment. Programme coverage includes the student. The fallback is a comparison baseline, not labelled ground truth. In the two LIVE-07 samples the model covers two programmes while fallback covers three, so the data does not establish that the model always improves diversity.','',
                 f"Defined factual claims: {audit['without_detected_claim_errors']}/{audit['explanations_checked']} explanations without detected errors under the automated check. See factual-audit.json for every sentence and attribute check. This is not human sign-off or a general accuracy estimate."]
    for c in live['calls']:
        live_lines+=['',f"## {c['id']}",'',f"Status: {c['status']}; source: `{c.get('source','no reply')}`."]
        for p in c.get('picks',[]):live_lines.append(f"- ID {p['profile']['account_id']}: {p['reason']}")
    (HERE/'results/live/REPORT.md').write_text('\n'.join(live_lines)+'\n',encoding='utf-8')
    with (HERE/'TEST_CASES.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['ID','Group','Title','Input','Expected','Status','Observed','Test method'])
        for r in offline['cases']:w.writerow([r['id'],r['group'],r['title'],r['input'],r['expected'],r['status'],json.dumps(r['actual'],ensure_ascii=False),r['test']])
    # The lock must describe the environment that EXECUTED the tests, not the
    # environment someone later happens to use to format the report.
    versions={k:v for k,v in offline['metadata']['packages'].items() if k.lower() not in ('pip','setuptools')}
    (HERE/'requirements-tested.txt').write_text('# Exact packages in the clean Windows Python 3.12 evaluation environment.\n'+'\n'.join(f'{k}=={v}' for k,v in sorted(versions.items(),key=lambda x:x[0].lower()))+'\n',encoding='utf-8')
    summary=offline['summary'];times=[r['elapsed_seconds'] for r in live['calls'] if r.get('live_model')]
    if not times:
        raise RuntimeError('No successful real API timings; do not publish a success summary')
    bpass=sum(c['status']=='PASS' for c in browser['cases'])
    failures=[r for r in offline['cases'] if r['status']!='PASS']
    lines=['# Final evaluation summary','',f"Application baseline: `{revision}`. Offline run: {offline['metadata']['checked_at']}.",'',
           '## Results','', '| Evidence | Result | Scope |','|---|---|---|',
           f"| Offline automated acceptance | {summary['PASS']}/{summary['total']} PASS; {summary['FAIL']} FAIL; {summary['ERROR']} ERROR | Includes 25 existing backend tests and 30 new acceptance cases |",
           '| Fixture sweep | 60 profile queries, each repeated twice | 30 legacy + 30 enriched synthetic variants, counted as one automated case |',
           f"| Direct real-model checks | {live['summary']['PASS']}/{live['summary']['total']} successful | DeepSeek Flash, three synthetic profiles repeated twice |",
           f"| Automatic explanation fact audit | {audit['without_detected_claim_errors']}/{audit['explanations_checked']} without detected claim errors | Defined skill/role/programme assertions only; no human relevance/satisfaction rating |",
           f"| Browser scenarios | {bpass}/{len(browser['cases'])} PASS | Real UI/HTTP, temporary SQLite adapter; includes one additional real API call and empty-pool case |",
           '| Clean environment | Install and pip check succeeded | Windows, Python '+offline['metadata']['python']+'; exact packages in requirements-tested.txt |','',
           f"Six direct calls: median **{statistics.median(times):.3f} s**, range **{min(times):.3f}–{max(times):.3f} s**. This is a small client-side timing sample, not a service benchmark.",'',
           'The six scripted calls plus one browser call are **seven observed real API invocations**, not seven additional test cases. Source labels were checked; fallback responses were not counted as live successes.','',
           '## Product failures','', '| Case | Finding | Evidence |','|---|---|---|']
    for r in failures:lines.append(f"| {r['id']} | {r['title']} | [Observed result and traceback](results/offline/REPORT.md#{r['id'].lower()}-{r['title'].lower().replace(' ','-')}) |")
    lines+=['','Detailed causes and proposed fixes: [LIMITATIONS.md](LIMITATIONS.md). Failure labels remain ordinary FAIL results; the offline command correctly exits 1.','',
            '## Evidence links','', '- [All case inputs, expected and actual results](results/offline/REPORT.md)',
            '- [Machine-readable results, source hashes and environment](results/offline/results.json)',
            '- [Captured automated test run](results/offline/test-run.txt)',
            '- [Real model results and descriptive comparison](results/live/REPORT.md)',
            '- [Raw model results and timing](results/live/results.json)',
            '- [Explanation audit and role/programme coverage comparison](results/live/factual-audit.json)',
            '- [Browser scenarios](results/browser/results.json)',
            '- [Real AI screenshot](results/browser/ai-results.png)',
            '- [Empty-pool screenshot](results/browser/empty-pool.png)','',
            '## Limits on the conclusion','',
            'No shared PostgreSQL database, production deployment, multi-process PostgreSQL integration, real-student satisfaction or fairness study was tested. Cache cases enable production cache logic over isolated SQLite to reproduce the logic, not the database driver. Time-overlap preferences and mutual contact consent remain unimplemented. The team must review these results and name the actual human reviewers in its AI-use disclosure.','',
            'Reproduction note: after the initial transport failure, a separate fresh Git clone succeeded using HTTP/1.1. The final offline run was executed in that clone against the 35 verified baseline files, using the recorded dependency environment. Live/browser modes used identical verified application files in the preceding isolated checkout. No shared PostgreSQL deployment was exercised.']
    (HERE/'FINAL_SUMMARY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    passed_calls=live['summary']['PASS']
    excerpt=f'''# Suggested report text based on recorded evidence

Review and adapt this text; enter the actual team members responsible for checking it. These are measured results, not a claim of human sign-off.

## Section 3 Evaluation and test results

We evaluated application commit `{revision[:7]}` using synthetic student profiles. Success criteria were same-cohort eligibility, exclusion of self and already-placed students, five unique recommendations when available, nonblank factual explanations, saved-profile integrity, and safe handling of invalid input and model-service failures. We also tested the new programme, open-role and skill preferences. The offline suite comprised {summary['total']} cases, including 25 existing API cases and 30 additional acceptance cases: {summary['PASS']} passed, {summary['FAIL']} failed and {summary['ERROR']} encountered runner errors. One sweep case evaluated all 30 original profiles and 30 enriched variants, repeating each query twice; these 60 inputs are not counted as 60 extra test cases.

Of six direct DeepSeek Flash calls on three enriched synthetic profiles, {passed_calls} met the criteria for five unique eligible recommendations with nonblank reasons. The automatic audit found no detected unsupported defined claims in {audit['without_detected_claim_errors']}/{audit['explanations_checked']} returned explanations; this is not a human assessment of usefulness or student satisfaction. Median client-side latency was {statistics.median(times):.3f} seconds (range {min(times):.3f}–{max(times):.3f}). {bpass}/{len(browser['cases'])} browser scenarios passed, including registration, preference persistence, a separate live-AI run, city editing with AI disabled, authentication rejection, re-login, and an empty eligible pool. See evaluation/results/ for inputs, expected/observed outputs, logs, responses and screenshots.

## Section 4 Reproducibility, failure cases and limitations

Installation from the repository requirements and pip check succeeded in the recorded clean Windows Python {offline['metadata']['python']} environment. We then reran the same acceptance suite in a separate fresh Git clone, with identical totals, and recorded exact package versions in evaluation/requirements-tested.txt. All 35 application source files were checked against the immutable baseline. Live/browser checks used the same verified application files and the application's test-only SQLite injection with disposable synthetic data. Shared PostgreSQL and deployed-service operation remain unverified.

The suite exposed four failures: partial valid model output is not topped up to five; unknown student skills are treated as known gaps; an adversarial model response can use a non-skill numeric field as a skill; and logout in one cache instance is not immediately observed in another. The last issue was reproduced with two cache instances over a disposable SQLite transport and is conditional on multi-instance operation. Proposed improvements are validated-count fallback, explicit unknown-skill handling, a whitelist of allowed skill keys, and shared/revalidated session revocation, each followed by the same regression cases. Availability overlap and mutual consent remain scope limitations. The sample is synthetic and small, so these results establish observed behaviour rather than real-student matching quality.
'''
    (HERE/'REPORT_EXCERPT.md').write_text(excerpt,encoding='utf-8')
    print('Generated FINAL_SUMMARY.md, TEST_CASES.csv, REPORT_EXCERPT.md and factual-audit.json')


if __name__=='__main__':main()
