import importlib
import json
import threading
import time
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from moviecrew.mock import MockLLMClient
from moviecrew import projects
portal = importlib.import_module('moviecrew.portal.app')


def wait(client, sid):
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        data=client.get('/api/projects/'+sid).json()
        if data['status'] not in ('queued','running'): return data
        time.sleep(.01)
    pytest.fail('Planning did not finish')


@pytest.fixture
def setup(tmp_path,monkeypatch):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path/'projects'))
    calls=[]
    class Recorder(MockLLMClient):
        def complete_json(self,**kw):
            calls.append((kw['task'],json.loads(kw['user'])))
            return super().complete_json(**kw)
    monkeypatch.setattr(portal,'_build_llm',lambda backend:Recorder())
    client=TestClient(portal.app)
    return client,calls


def start(client):
    sid=client.post('/api/plan',json={'concept':'A climber tests a foothold','backend':'mock','review_director':True,'review_world':True}).json()['session_id']
    return sid,wait(client,sid)


def test_review_edit_restore_and_exact_writer_input(setup):
    client,calls=setup
    sid,data=start(client)
    assert data['status']=='director_review'
    assert [c[0] for c in calls]==['director']
    assert not data['project']['scenes']
    state=data['director_review'];original=deepcopy(state['draft'])
    draft=deepcopy(original);draft['title']='The broken foothold';draft['outline']=['Test the foothold','Fall and catch the rope']
    draft['characters']=[{'id':'climber','name':'Maya','role':'Solo climber','motivation':'Return home','description':'Red coat'}]
    r=client.put(f'/api/projects/{sid}/director',json={'revision':1,'draft':draft})
    assert r.status_code==200,r.text
    assert client.put(f'/api/projects/{sid}/director',json={'revision':1,'draft':original}).status_code==409
    restored=client.post(f'/api/projects/{sid}/director/restore',json={'revision':2,'restore_revision':1}).json()
    assert restored['draft']==original
    restored=client.post(f'/api/projects/{sid}/director/restore',json={'revision':3,'restore_revision':2}).json()
    assert restored['draft']==draft
    portal._sessions.pop(sid)
    data=client.get('/api/projects/'+sid).json()
    assert data['status']=='director_review' and data['director_review']['revision']==4
    assert client.post(f'/api/projects/{sid}/director/approve',json={'revision':4}).status_code==200
    data=wait(client,sid)
    assert data['status']=='awaiting_approval',data.get('error')
    assert [c[0] for c in calls]==['director','writer','designer']
    writer=next(v for k,v in calls if k=='writer')
    assert writer['title']==draft['title'] and writer['outline']==draft['outline']
    assert writer['provided_bible']['characters'][0]['name']=='Maya'
    assert 'Return home' in writer['provided_bible']['characters'][0]['description']
    assert data['project']['bible']['characters'][0]['name']=='Maya'
    assert client.post(f'/api/projects/{sid}/director/approve',json={'revision':4}).status_code==200
    assert [c[0] for c in calls].count('writer')==1
    old=deepcopy(data['project']);draft['title']='A different proposal'
    assert client.put(f'/api/projects/{sid}/director',json={'revision':4,'draft':draft}).status_code==200
    data=client.get('/api/projects/'+sid).json()
    assert data['project']==old and data['director_review']['needs_review']
    assert client.post(f'/api/projects/{sid}/director/approve',json={'revision':5}).status_code==409


def test_regenerate_receives_feedback_and_prevents_concurrent_edits(setup,monkeypatch):
    client,calls=setup;sid,data=start(client)
    entered=threading.Event();release=threading.Event()
    class Blocked(MockLLMClient):
        def complete_json(self,**kw):
            payload=json.loads(kw['user']);assert payload['feedback']=='Make the rescue hopeful'
            assert payload['current_draft']==data['director_review']['draft']
            entered.set();assert release.wait(3)
            return super().complete_json(**kw)
    monkeypatch.setattr(portal,'_build_llm',lambda _:Blocked())
    try:
        assert client.post(f'/api/projects/{sid}/director/regenerate',json={'revision':1,'feedback':'Make the rescue hopeful'}).status_code==200
        assert entered.wait(2)
        assert client.put(f'/api/projects/{sid}/director',json={'revision':1,'draft':data['director_review']['draft']}).status_code==409
        assert client.post(f'/api/projects/{sid}/director/approve',json={'revision':1}).status_code==409
        assert client.post(f'/api/projects/{sid}/director/regenerate',json={'revision':1}).status_code==409
    finally:release.set()
    data=wait(client,sid)
    assert data['director_review']['revision']==2 and data['status']=='director_review'
    assert len(data['director_review']['history'])==2


def test_failed_generation_retains_draft_and_retry(setup,monkeypatch):
    client,calls=setup;sid,data=start(client);original=data['director_review']['draft']
    class Fails:
        def complete_json(self,**kw):raise ValueError('Provider unavailable')
    monkeypatch.setattr(portal,'_build_llm',lambda _:Fails())
    client.post(f'/api/projects/{sid}/director/regenerate',json={'revision':1})
    data=wait(client,sid)
    assert data['status']=='failed' and data['director_review']['draft']==original
    monkeypatch.setattr(portal,'_build_llm',lambda _:MockLLMClient())
    client.post(f'/api/projects/{sid}/director/regenerate',json={'revision':1})
    assert wait(client,sid)['status']=='director_review'


def test_interrupted_generation_preserves_review_history(setup):
    client,calls=setup;sid,data=start(client)
    session=portal._sessions[sid]
    session.plan_progress.status='running';projects.save(session);portal._sessions.pop(sid)
    data=client.get('/api/projects/'+sid).json()
    assert data['status']=='failed' and data['director_review']['draft']
    assert data['director_review']['history']


def test_writer_failure_can_retry_approved_direction(setup,monkeypatch):
    client,calls=setup;sid,data=start(client)
    class Fails(MockLLMClient):
        def complete_json(self,**kw):
            if kw['task']=='writer':raise ValueError('Writer unavailable')
            return super().complete_json(**kw)
    monkeypatch.setattr(portal,'_build_llm',lambda _:Fails())
    client.post(f'/api/projects/{sid}/director/approve',json={'revision':1})
    assert wait(client,sid)['status']=='failed'
    monkeypatch.setattr(portal,'_build_llm',lambda _:MockLLMClient())
    assert client.post(f'/api/projects/{sid}/director/approve',json={'revision':1}).status_code==200
    assert wait(client,sid)['status']=='awaiting_approval'
