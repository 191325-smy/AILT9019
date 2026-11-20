"""Run final acceptance checks and produce auditable evidence.

python evaluation/run_evaluation.py
python evaluation/run_evaluation.py --live --key-file /private/path/to/.env

Offline exits 1 on any real FAIL, 2 on runner/integrity errors. Live mode makes
six actual requests via the existing matcher; no database service is used.
"""
import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import socket
import subprocess
import sys
import time
import traceback
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from common import SAFE_DATABASE, fixture, source_integrity, validate_picks


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def metadata():
    revision, files = source_integrity()
    if not all(f['baseline_blob_matches'] for f in files):
        raise RuntimeError('Baseline source changed. Update SOURCE.json deliberately for a new revision before evaluating it.')
    packages = {d.metadata['Name']: d.version for d in importlib.metadata.distributions() if d.metadata['Name']}
    scripts = {str(p.relative_to(HERE)).replace('\\','/'): hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
               for p in HERE.rglob('*') if p.is_file() and ('results' not in p.relative_to(HERE).parts)
               and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
    return dict(revision=revision, checked_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
                python=platform.python_version(), platform=platform.system(), source=files,
                evaluation_hashes=scripts, packages=packages,
                source_acquisition=json.loads((HERE/'SOURCE.json').read_text(encoding='utf-8')).get('acquisition','Verified GitHub source'))


def clean(value):
    if isinstance(value,str): return value.replace(str(ROOT),'<REPO>').replace(str(Path.home()),'<USER>')
    if isinstance(value,list): return [clean(v) for v in value]
    if isinstance(value,dict): return {k:clean(v) for k,v in value.items()}
    return value


class EvidenceResult(unittest.TextTestResult):
    def __init__(self,*a,**k):
        super().__init__(*a,**k);self.records=[]

    def startTest(self,test):
        super().startTest(test);self.current_status=None;self.current_failure=None;self.started=time.monotonic()

    def addSuccess(self,test):
        self.current_status='PASS';super().addSuccess(test)

    def addFailure(self,test,err):
        self.current_status='FAIL';self.current_failure=self._exc_info_to_string(err,test);super().addFailure(test,err)

    def addError(self,test,err):
        self.current_status='ERROR';self.current_failure=self._exc_info_to_string(err,test);super().addError(test,err)

    def addSubTest(self,test,subtest,err):
        if err is not None:
            self.current_status='FAIL' if issubclass(err[0],test.failureException) else 'ERROR'
            self.current_failure=self._exc_info_to_string(err,test)
        super().addSubTest(test,subtest,err)

    def stopTest(self,test):
        method=getattr(test,test._testMethodName)
        spec=getattr(method,'case_spec',None)
        if spec is None:
            spec=dict(id='API-'+test._testMethodName.removeprefix('test_'),
                      title=test._testMethodName.removeprefix('test_').replace('_',' '),
                      input='Existing backend fixture/profile and HTTP calls in '+test._testMethodName,
                      expected='Assertions in the existing backend test must pass; see backend/tests/test_api.py.',
                      group='existing backend',gap=None)
        row=dict(spec,status=self.current_status or 'ERROR',duration_seconds=round(time.monotonic()-self.started,3),
                 test=test.id(),actual=getattr(test,'actual',{'assertions':'passed' if self.current_status=='PASS' else 'see failure evidence'}),
                 failure=self.current_failure)
        self.records.append(clean(row));super().stopTest(test)


def offline(output):
    # Override potentially inherited service credentials before importing the app.
    os.environ.update(DATABASE_URL=SAFE_DATABASE,DEEPSEEK_API_KEY='',MATCH_MODEL='')
    from dotenv import load_dotenv
    with patch('dotenv.load_dotenv',return_value=False):
        import test_cases
        from backend.tests import test_api
    meta=metadata();console=io.StringIO()
    original_connect=socket.socket.connect
    def local_only(sock,address):
        if isinstance(address,tuple) and address[0] not in ('127.0.0.1','localhost','::1'):
            raise AssertionError('Offline tests attempted an external network connection')
        return original_connect(sock,address)
    suite=unittest.TestSuite()
    for cls in (test_api.BackendAPITests,test_cases.MatchingCases,test_cases.APICases):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
    with patch.object(socket.socket,'connect',local_only):
        result=unittest.TextTestRunner(stream=console,verbosity=2,resultclass=EvidenceResult).run(suite)
    after=metadata()
    if meta['source']!=after['source']:raise RuntimeError('Application source changed during evaluation')
    counts={s:sum(r['status']==s for r in result.records) for s in ('PASS','FAIL','ERROR')}
    data=dict(metadata=meta,mode='offline',live_api_tested=False,
              storage='Disposable SQLite; cache logic simulated over SQLite, not PostgreSQL integration',
              summary=dict(total=len(result.records),**counts),cases=sorted(result.records,key=lambda r:r['id']))
    write_json(output/'results.json',data)
    (output/'test-run.txt').write_text(clean(console.getvalue()),encoding='utf-8')
    lines=['# Final offline evaluation','',f"Baseline: `{meta['revision']}`. Run: {meta['checked_at']}.",'',
           f"**{len(result.records)} cases: {counts['PASS']} PASS, {counts['FAIL']} FAIL, {counts['ERROR']} ERROR.**",'',
           'Existing backend cases use their original assertions. New cases record inputs, expectations and observed outputs below.',
           'The sweep is ONE test case covering 60 profile queries (30 legacy + 30 enriched), each repeated twice. It is not 60 separately counted test cases.',
           'Model-boundary cases use simulated provider output and the real application Pydantic schema. No live API or PostgreSQL service is tested by this command.',
           'FAIL remains FAIL and makes the command exit 1; a working test runner does not mean the product passed.', '',
           '| Case | Group | Result | Check |','|---|---|---|---|']
    for r in data['cases']:lines.append(f"| {r['id']} | {r['group']} | {r['status']} | {r['title']} |")
    for r in data['cases']:
        lines+=['',f"## {r['id']} {r['title']}",'',f"Result: **{r['status']}**. Test: `{r['test']}`.",'',
                'Input: '+r['input'],'','Expected: '+r['expected'],'','Observed:','','```json',json.dumps(r['actual'],indent=2,ensure_ascii=False),'```']
        if r['failure']:lines+=['','Failure evidence:','','```text',r['failure'].strip(),'```']
    (output/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    groups={}
    for r in data['cases']:
        g=groups.setdefault(r['group'],dict(total=0,PASS=0,FAIL=0,ERROR=0));g['total']+=1;g[r['status']]+=1
    write_json(output/'summary.json',dict(summary=data['summary'],groups=groups))
    print(json.dumps(data['summary']))
    for r in data['cases']:
        if r['status']!='PASS':print(r['status'],r['id'],r['title'])
    print('Evidence:',output/'REPORT.md')
    return 0 if result.wasSuccessful() else 1


def live_one(input_path):
    # Parent supplies only the requested API key/model, never a DATABASE_URL.
    os.environ['DATABASE_URL']=SAFE_DATABASE
    os.environ['LANGCHAIN_TRACING_V2']='false'
    os.environ['LANGSMITH_TRACING']='false'
    with patch('dotenv.load_dotenv',return_value=False):
        from matching import matcher,filters
    data=json.loads(Path(input_path).read_text(encoding='utf-8'))
    me=data['me'];pool=data['pool'];candidates,_,_=filters.candidates_for_model(me,pool)
    before=time.monotonic();picks,source=matcher.pick(me,candidates)
    elapsed=round(time.monotonic()-before,3)
    errors=[]
    try:validate_picks(me,candidates,picks)
    except AssertionError as e:errors.append(str(e))
    real=not (source.startswith('fallback') or source=='empty')
    if not real:errors.append('Provider did not produce a successful live-model response')
    # Save synthetic profiles/results for independent factual review, not secrets.
    print(json.dumps(dict(source=source,live_model=real,elapsed_seconds=elapsed,eligible=len(candidates),
                          picks=picks,acceptance_errors=errors,status='PASS' if not errors else 'FAIL'),ensure_ascii=False))


def live(output,key_file):
    from dotenv import dotenv_values
    config=dotenv_values(key_file) if key_file else {}
    key=config.get('DEEPSEEK_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
    model=config.get('MATCH_MODEL') or os.getenv('MATCH_MODEL') or 'deepseek:deepseek-chat'
    if not key:raise RuntimeError('No local API key configured; no requests made')
    meta=metadata();rows=fixture();selected=[rows[0],rows[6],rows[15]];records=[]
    # An allow-list prevents inherited DB passwords, proxies and tracing tokens
    # from being sent into the model-check subprocess.
    env={k:v for k,v in os.environ.items() if k.upper() in {'PATH','SYSTEMROOT','WINDIR','TEMP','TMP','LANG'}}
    env.update(DEEPSEEK_API_KEY=key,MATCH_MODEL=model,DATABASE_URL=SAFE_DATABASE,
               LANGCHAIN_TRACING_V2='false',LANGSMITH_TRACING='false',PYTHONIOENCODING='utf-8')
    for me in selected:
        for repeat in (1,2):
            code=f"LIVE-{me['account_id']:02d}-{repeat}";p=output/'inputs'/(code+'.json')
            write_json(p,dict(me=me,pool=rows))
            try:
                r=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--live-one',str(p)],env=env,
                                 capture_output=True,text=True,encoding='utf-8',timeout=75)
                if r.returncode:observed=dict(status='ERROR',error='child exit '+str(r.returncode))
                else:observed=json.loads(r.stdout)
            except subprocess.TimeoutExpired:observed=dict(status='ERROR',error='75-second evaluation deadline exceeded')
            observed.update(id=code,student_id=me['account_id'],repeat=repeat)
            records.append(observed);write_json(output/(code+'.json'),observed)
            print(code,observed['status'],observed.get('source','no response'),flush=True)
    summary={s:sum(r['status']==s for r in records) for s in ('PASS','FAIL','ERROR')}
    data=dict(metadata=meta,model=model,mode='real API',summary=dict(total=len(records),**summary),calls=records,
              qualification='Six calls on three synthetic profiles; connectivity/structural checks, not a real-student suitability or fairness study. Semantic review is recorded separately.')
    write_json(output/'results.json',data)
    return 0 if summary['PASS']==len(records) else 1


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path)
    p.add_argument('--live',action='store_true')
    p.add_argument('--key-file',type=Path)
    p.add_argument('--live-one',type=Path,help=argparse.SUPPRESS)
    a=p.parse_args()
    if a.live_one:live_one(a.live_one);return 0
    out=(a.output or HERE/'results'/('live' if a.live else 'offline')).resolve();out.mkdir(parents=True,exist_ok=True)
    return live(out,a.key_file) if a.live else offline(out)


if __name__=='__main__':
    try:code=main()
    except Exception as exc:
        print('Evaluation runner error:',type(exc).__name__,str(exc),file=sys.stderr);code=2
    sys.exit(code)
