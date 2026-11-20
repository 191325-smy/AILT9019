"""Final acceptance checks for the application baseline in SOURCE.json."""
import copy
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from common import (HERE, ROOT, SAFE_DATABASE, SKILLS, case, fixture, profile,
                    provider, seed_connection, validate_picks)
from matching import filters, matcher, scoring
from backend.models import ProfileWrite
from backend.store import Store
from backend.app import create_app
from fastapi.testclient import TestClient


class MatchingCases(unittest.TestCase):
    def setUp(self):
        self.actual = {}
        self.me = profile(100, "Evaluation Student", preferred_role="Frontend",
                          programme="AI and Data Science", languages=["English", "Mandarin"])
        self.pool = fixture()
        self.addCleanup(patch.stopall)
        patch.object(matcher, "model_name", return_value=None).start()

    def run_match(self, pool=None, me=None, **options):
        me = self.me if me is None else me
        candidates, dropped, _ = filters.candidates_for_model(me, self.pool if pool is None else pool)
        picks, source = matcher.pick(me, candidates, **options)
        self.actual = dict(eligible=len(candidates), ids=[p["profile"]["account_id"] for p in picks],
                           source=source, reasons=[p["reason"] for p in picks])
        return candidates, dropped, picks, source

    @case("R01", "Hard exclusions and soft language", "Self, SH, placed HK and Cantonese-only HK candidate.", "Only the unplaced other HK candidate remains; lack of shared language does not exclude.")
    def test_hard_filters(self):
        c,d,p,_=self.run_match([self.me,profile(1,city="SH"),profile(2,in_team=1),profile(3,languages=["Cantonese"])])
        self.actual["drops"]=[why for _,why in d]
        self.assertEqual([x["account_id"] for x in c],[3]);validate_picks(self.me,c,p)
        self.assertEqual(len(d),3);self.assertTrue(all(why for _,why in d))

    @case("R02", "Empty and undersized pools", "Separate pools of 0, 1, 2, 4 and 5 eligible people.", "Return exactly min(5, eligible), with no invented people.")
    def test_pool_sizes(self):
        self.actual={}
        for size in (0,1,2,4,5):
            c,_,_=filters.candidates_for_model(self.me,[profile(i) for i in range(1,size+1)])
            p,s=matcher.pick(self.me,c);validate_picks(self.me,c,p)
            self.actual[str(size)]={"count":len(p),"source":s}
        self.assertEqual(self.actual['0']['source'],'empty')

    @case("R03", "Legacy and enriched 30-profile sweeps", "Each of 30 legacy profiles and 30 enriched variants, twice.", "All 60 queries satisfy count, eligibility, uniqueness and explanation invariants; deterministic repeats agree.")
    def test_all_profiles(self):
        observations=[];self.actual={"queries":observations}
        for enriched in (False,True):
            rows=fixture(enriched)
            for me in rows:
                c,_,_=filters.candidates_for_model(me,rows)
                p,s=matcher.pick(me,c);q,_=matcher.pick(me,c)
                observations.append(dict(dataset="enriched" if enriched else "legacy",student_id=me['account_id'],eligible=len(c),ids=[i['profile']['account_id'] for i in p]))
                validate_picks(me,c,p);self.assertEqual(p,q)

    @case("R04", "Open roles add useful coverage", "Frontend-preferred candidate also offers Database; other candidates repeat Frontend.", "Flexible candidate is retained and recommended before identical Frontend-only candidates.")
    def test_open_roles(self):
        rows=[profile(1,"Zulu",preferred_role="Frontend",open_roles=["Frontend","Database"]),profile(2,"Alpha",preferred_role="Frontend")]
        c,_,p,_=self.run_match(rows);validate_picks(self.me,c,p)
        self.assertEqual(p[0]['profile']['account_id'],1)
        self.assertIn('Database',p[0]['reason'])

    @case("R05", "Known missing skill increases preference", "Two otherwise equal Backend candidates; only Zulu has programming=1, student has programming=0.", "Zulu precedes Alpha; explanation can cite programming.")
    def test_skill_preference(self):
        _,_,p,_=self.run_match([profile(1,"Alpha"),profile(2,"Zulu",programming=1)])
        self.assertEqual(p[0]['profile']['account_id'],2);self.assertIn('programming',p[0]['reason'])

    @case("R06", "Language preference remains soft", "Identical candidates, one shares two languages and one shares none.", "Both retained; shared-language candidate preferred on an otherwise equal tie.")
    def test_language_preference(self):
        _,_,p,_=self.run_match([profile(1,"Alpha",languages=["Cantonese"]),profile(2,"Zulu",languages=["English","Mandarin"])])
        self.assertEqual([i['profile']['account_id'] for i in p],[2,1])

    @case("R07", "Duplicate roles may fill remaining slots", "Six eligible Backend-only candidates.", "Five distinct candidates returned; role diversity is not a hard exclusion.")
    def test_duplicate_roles_allowed(self):
        c,_,p,_=self.run_match([profile(i) for i in range(1,7)]);validate_picks(self.me,c,p)
        self.assertEqual({i['profile']['preferred_role'] for i in p},{'Backend'})

    @case("S01", "Declared weighted score on hand-calculated example", "Backend+Database, one missing skill, one shared language; different programme has share .25.", "role=.400, skills=.070, flexibility=.033, languages=.025, programme=.075; total=.603.",group="preferences")
    def test_weighted_example(self):
        cand=profile(1,open_roles=['Backend','Database'],programming=1)
        result=scoring.score(self.me,cand,{'Applied AI':.25});self.actual=result
        self.assertEqual({k:result[k] for k in ['role','skills','flexibility','languages','programme','total']},dict(role=.4,skills=.07,flexibility=.033,languages=.025,programme=.075,total=.603))

    @case("S02", "Rare programmes gain preference", "Same eligible role and skills, candidates from a common versus rare different programme.", "Rarer different programme has higher programme contribution, same-programme contribution is zero.",group="preferences")
    def test_programme_rarity(self):
        common=scoring.score(self.me,profile(1,programme='Computer Science'),{'Computer Science':.8,'Applied AI':.2})
        rare=scoring.score(self.me,profile(2,programme='Applied AI'),{'Computer Science':.8,'Applied AI':.2})
        same=scoring.score(self.me,profile(3,programme=self.me['programme']))
        self.actual=dict(common=common['programme'],rare=rare['programme'],same=same['programme'])
        self.assertGreater(rare['programme'],common['programme']);self.assertEqual(same['programme'],0)

    @case("S03", "Legacy attributes and null candidate skills", "Legacy profiles lack programme/open_roles/skills; another candidate has null skill flags.", "Matching remains usable; no candidate skill is invented from null values.",group="preferences")
    def test_legacy_and_null_candidate(self):
        cand=profile(1,**{s:None for s in SKILLS});r=scoring.score(self.me,cand);self.actual=r
        self.assertEqual(r['complements'],[])
        c,_,p,_=self.run_match(fixture(False));validate_picks(self.me,c,p)

    @case("S04", "Unknown student skills are neutral", "Student programming=None (unknown); candidate programming=1.", "An unknown student skill is not reported as a known missing-skill complement, as stated by the prompt/docs.",group="preferences",gap="G02")
    def test_unknown_student_skill(self):
        me=dict(self.me,programming=None);r=scoring.score(me,profile(1,programming=1));self.actual=r
        self.assertNotIn('programming',r['complements'],'Unknown skill is treated as an established lack.')

    @case("M01", "Model toggle prevents provider invocation", "Configure a model but call pick(use_model=False).", "No provider resolution; five deterministic picks with disabled label.",group="model boundary")
    def test_model_disabled(self):
        with patch.object(matcher,'model_name',side_effect=AssertionError('provider must not be resolved')):
            c,_,p,s=self.run_match(use_model=False)
        validate_picks(self.me,c,p);self.assertEqual(s,'fallback:model disabled')

    @case("M02", "Provider timeout falls back", "Simulated provider raises TimeoutError.", "Five eligible nonblank results; fallback source and no crash.",group="model boundary")
    def test_timeout(self):
        with provider(matcher,error=TimeoutError('evaluation timeout')):
            c,_,p,s=self.run_match()
        validate_picks(self.me,c,p);self.assertEqual(s,'fallback:TimeoutError')

    @case("M03", "Verified structured evidence and private payload", "Simulated response names an eligible role/skill/programme; inspect actual model payload.", "Reason cites valid facts; real schema used; payload excludes contacts, hashes and fallback score.",group="model boundary")
    def test_payload_and_evidence(self):
        rows=[profile(i,programming=1) for i in range(1,7)]
        items=[dict(account_id=i,role='Backend',skills=['programming'],programme=True) for i in range(1,6)]
        with provider(matcher,items=items) as call:
            c,_,p,s=self.run_match(rows)
        validate_picks(self.me,c,p);payload=json.loads(call['messages'][1][1])
        self.actual.update(payload=payload,schema=call['schema'])
        self.assertEqual(s,'evaluation:simulated');self.assertIn('programming',p[0]['reason'])
        for person in [payload['me'],*payload['candidates']]:
            for field in ('contact_info','password_hash','score','token'):
                self.assertNotIn(field,person)
        self.assertNotIn('@test.com',json.dumps(payload))

    @case("M04", "Invalid and duplicate IDs removed", "Simulated unknown ID, repeated valid ID and five distinct valid IDs.", "Return five unique eligible IDs only.",group="model boundary")
    def test_invalid_duplicate(self):
        rows=[profile(i) for i in range(1,7)]
        with provider(matcher,items=[dict(account_id=i) for i in [999999,1,1,2,3,4,5]]):
            c,_,p,_=self.run_match(rows)
        validate_picks(self.me,c,p)

    @case("M05", "All-invalid output falls back", "Model returns only an out-of-pool ID.", "Five deterministic picks and an explicit fallback source.",group="model boundary")
    def test_all_invalid(self):
        with provider(matcher,items=[dict(account_id=999999)]):c,_,p,s=self.run_match()
        validate_picks(self.me,c,p);self.assertEqual(s,'fallback:no valid ids returned')

    @case("M06", "Oversized output capped", "Model returns six eligible people.", "At most five recommendations.",group="model boundary")
    def test_too_many(self):
        with provider(matcher,items=[dict(account_id=i) for i in range(1,7)]):
            c,_,p,_=self.run_match([profile(i) for i in range(1,7)])
        validate_picks(self.me,c,p)

    @case("M07", "Short valid output supplies five", "Six eligible people; model returns ID 1 twice and invalid ID 999999.", "Five unique eligible recommendations after validation/fallback.",group="model boundary",gap="G01")
    def test_short_output(self):
        with provider(matcher,items=[dict(account_id=i) for i in [1,1,999999]]):
            c,_,p,_=self.run_match([profile(i) for i in range(1,7)])
        validate_picks(self.me,c,p)

    @case("M08", "Empty evidence produces nonblank verified sentences", "Five valid IDs, blank roles and empty skills/programme flags.", "Application produces five nonblank reasons from verified profile facts.",group="model boundary")
    def test_empty_evidence(self):
        with provider(matcher,items=[dict(account_id=i,role='  ',skills=[],programme=False) for i in range(1,6)]):
            c,_,p,_=self.run_match([profile(i) for i in range(1,7)])
        validate_picks(self.me,c,p)

    @case("M09", "Invented role and absent skill claims are rejected", "Model claims Database, AI-agent skills and a different programme for same-programme Backend candidates with skills=0.", "Reasons do not repeat the invented facts and remain nonblank.",group="model boundary")
    def test_hallucinated_evidence(self):
        rows=[profile(i,programme=self.me['programme']) for i in range(1,7)]
        with provider(matcher,items=[dict(account_id=i,role='Database',skills=['ai_agent'],programme=True) for i in range(1,6)]):
            c,_,p,_=self.run_match(rows)
        validate_picks(self.me,c,p)
        for item in p:
            for invented in ('Database','AI-agent','different programme'):self.assertNotIn(invented,item['reason'])

    @case("M10", "Malformed response schema falls back", "Structured output has a noninteger account_id.", "Real Pydantic validation rejects it; matching falls back safely.",group="model boundary")
    def test_invalid_schema(self):
        with provider(matcher,malformed={'picks':[{'account_id':'not-an-id'}]}):c,_,p,s=self.run_match()
        validate_picks(self.me,c,p);self.assertEqual(s,'fallback:ValidationError')

    @case("M11", "Only the five defined skills may be explained", "Candidate ID is 1; model names account_id as a skill.", "An ID field must not become a skill claim in the explanation.",group="model boundary",gap="G03")
    def test_unsupported_skill(self):
        with provider(matcher,items=[dict(account_id=i,skills=['account_id']) for i in range(1,6)]):
            c,_,p,_=self.run_match([profile(i) for i in range(1,7)])
        validate_picks(self.me,c,p);self.assertNotIn('account_id',p[0]['reason'])

    @case("C01", "JSON CLI works without dependencies or DB", "Run enriched fixture through match.py --from-json with -S and no key.", "Readable five-result fallback with no database or traceback.",group="CLI")
    def test_json_cli(self):
        env={k:v for k,v in os.environ.items() if k.upper() in {'PATH','SYSTEMROOT','WINDIR','TEMP','TMP'}}
        env.update(DEEPSEEK_API_KEY='',MATCH_MODEL='',DATABASE_URL='',PYTHONIOENCODING='utf-8')
        r=subprocess.run([sys.executable,'-S',str(ROOT/'matching/match.py'),'--from-json',str(HERE/'fixtures/enriched_profiles.json'),'alice_chen'],env=env,capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.actual=dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
        self.assertEqual(r.returncode,0);self.assertIn('shortlist: 5 of',r.stdout);self.assertEqual(r.stdout.count('reason:'),5)

    @case("C02", "Unknown JSON user is a readable error", "JSON CLI with no_such_student.", "Exit 1 with a readable error, no traceback.",group="CLI")
    def test_unknown_json_user(self):
        env=dict(os.environ,DEEPSEEK_API_KEY='',MATCH_MODEL='',DATABASE_URL='')
        r=subprocess.run([sys.executable,'-S',str(ROOT/'matching/match.py'),'--from-json',str(HERE/'fixtures/enriched_profiles.json'),'no_such_student'],env=env,capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.actual=dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr)
        self.assertEqual(r.returncode,1);self.assertIn('no profile named',r.stdout);self.assertNotIn('Traceback',r.stderr)


class APICases(unittest.TestCase):
    def setUp(self):
        self.actual={}
        self.temp=tempfile.TemporaryDirectory(prefix='evaluation-api-')
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'test.db'
        self.client=TestClient(create_app(db_path=self.path))
        self.client.__enter__();self.addCleanup(self.client.__exit__,None,None,None)
        self.values={k:v for k,v in profile(100).items() if k not in ('account_id','username','in_team')}

    def auth(self):
        password='Evaluation123!'
        self.client.post('/auth/register',json=dict(username='evaluation_user',password=password)).raise_for_status()
        token=self.client.post('/auth/login',json=dict(username='evaluation_user',password=password)).json()['access_token']
        return {'Authorization':'Bearer '+token}

    @case("P01", "All new preference values round-trip", "Save programme, flexible roles and all five skill flags, then read and match.", "Values persist exactly and saved preferences reach the existing matcher payload.",group="API extension")
    def test_fields_reach_matcher(self):
        h=self.auth();v=dict(self.values,programme='Computer Science',open_roles=['Backend','Database'],programming=1,github=0,debugging=1,web=0,ai_agent=1)
        r=self.client.put('/profiles/me',headers=h,json=v);self.assertEqual(r.status_code,200)
        with closing(sqlite3.connect(self.path)) as c, c:
            seed_connection(c,[profile(i) for i in range(2,8)])
        captured={}
        original=matcher.pick
        def capture(me,candidates,**options):
            captured.update(me=me)
            return original(me,candidates,use_model=False)
        with patch('backend.app.matcher.pick',side_effect=capture):r=self.client.post('/matches',headers=h,json={'use_model':False})
        self.actual=dict(saved_preferences={k:captured['me'][k] for k in ['programme','open_roles',*SKILLS]},count=len(r.json()['picks']))
        self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['picks']),5)
        for k in ['programme','open_roles',*SKILLS]:self.assertEqual(captured['me'][k],v[k])

    @case("P02", "New preference validation", "Invalid programme, out-of-range/bool skill flags and open_roles missing preferred_role.", "422 for each invalid input; valid profile can still be saved afterwards.",group="API extension")
    def test_new_validation(self):
        h=self.auth();bad=[dict(self.values,programme='Invented'),dict(self.values,programming=True),dict(self.values,web=2),dict(self.values,open_roles=['Database'])]
        statuses=[self.client.put('/profiles/me',headers=h,json=v).status_code for v in bad]
        self.actual={'invalid_statuses':statuses};self.assertEqual(statuses,[422]*4)
        self.assertEqual(self.client.put('/profiles/me',headers=h,json=self.values).status_code,200)

    @case("P03", "Clearing open roles and skills is preserved", "Save flexible roles and skills, then save open_roles=[] and programming=0.", "Explicit zero and empty list persist; omitted optional fields preserve prior values.",group="API extension")
    def test_clear_preferences(self):
        h=self.auth();self.client.put('/profiles/me',headers=h,json=dict(self.values,open_roles=['Backend','Database'],programming=1))
        r=self.client.put('/profiles/me',headers=h,json=dict(self.values,open_roles=[],programming=0))
        self.actual={k:r.json()[k] for k in ['open_roles','programming']};self.assertEqual(self.actual,dict(open_roles=[],programming=0))

    @case("P04", "Empty-candidate browser-demo boundary", "Register and save the only profile in a disposable database, then POST /matches.", "200 with no eligible candidates, empty picks and source=empty.",group="API extension")
    def test_empty_demo_case(self):
        h=self.auth();self.client.put('/profiles/me',headers=h,json=self.values)
        r=self.client.post('/matches',headers=h);self.actual=r.json()
        self.assertEqual(r.status_code,200);self.assertEqual(r.json()['source'],'empty');self.assertEqual(r.json()['picks'],[])

    @case("K01", "Cache refresh after own profile save and logout", "Enable production cache logic over a disposable SQLite transport; save/update and revoke a session.", "Own update is immediately visible and own logout invalidates the cached session.",group="cache simulation")
    def test_cache_refresh(self):
        s=self.client.app.state.store;s._cache_enabled=True
        h=self.auth();self.client.put('/profiles/me',headers=h,json=self.values)
        self.client.get('/profiles/me',headers=h)
        r=self.client.put('/profiles/me',headers=h,json=dict(self.values,display_name='Changed'))
        read=self.client.get('/profiles/me',headers=h)
        self.client.post('/auth/logout',headers=h);rejected=self.client.get('/auth/me',headers=h)
        self.actual=dict(name=read.json()['display_name'],logged_out_status=rejected.status_code)
        self.assertEqual(self.actual,dict(name='Changed',logged_out_status=401))

    @case("K02", "Revocation across two cache instances", "Two Store instances share a test DB and cache one token; first revokes it.", "Second instance should reject the revoked session rather than use its stale cache.",group="cache simulation",gap="G04")
    def test_multi_instance_revoke(self):
        s=self.client.app.state.store;s._cache_enabled=True
        h=self.auth();token=h['Authorization'].split(' ',1)[1]
        second=Store(self.path);second._cache_enabled=True
        self.assertIsNotNone(second.session_account(token));s.revoke_session(token)
        stale=second.session_account(token)
        self.actual=dict(other_instance_still_accepts=stale is not None)
        self.assertIsNone(stale,'Another process/instance retains the token until cached expiry.')
