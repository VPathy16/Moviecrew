import importlib
import time
from fastapi.testclient import TestClient
from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
portal=importlib.import_module('moviecrew.portal.app')


def test_design_phase_calls_no_shot_agents():
    calls=[]
    class Recorder(MockLLMClient):
        def complete_json(self, **kwargs):
            calls.append(kwargs['task'])
            return super().complete_json(**kwargs)
    client=Recorder()
    draft=MovieCrew(client).make('A keeper.',stop_after_design=True)
    assert calls==['director','writer','designer']
    assert draft.scenes and all(not scene.shots for scene in draft.scenes)
    calls.clear()
    result=MovieCrew(client).make('',approved_project=draft,run_continuity=False)
    assert 'director' not in calls and 'writer' not in calls and 'designer' not in calls
    assert result.scenes[0].shots


def test_approval_gate_versions_and_restart(tmp_path,monkeypatch):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path/'projects'))
    monkeypatch.setattr(portal,'_build_llm',lambda backend:MockLLMClient())
    client=TestClient(portal.app)
    sid=client.post('/api/plan',json={'concept':'A keeper.','backend':'mock','review_world':True}).json()['session_id']
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        p=client.get('/api/projects/'+sid).json()
        if p['status'] not in ('queued','running'):break
        time.sleep(.01)
    assert p['status']=='awaiting_approval'
    assert all(not s['shots'] for s in p['project']['scenes'])
    assert client.post(f'/api/projects/{sid}/world/build-shots').status_code==409
    sheets=client.get(f'/api/projects/{sid}/world').json()['sheets']
    for sheet in sheets:
        response=client.post(f"/api/projects/{sid}/world/{sheet['key']}/approve",json={'version':sheet['version']})
        assert response.status_code==200
    first=sheets[0]
    edited=client.put(f"/api/projects/{sid}/world/{first['key']}",json={'version':1,'name':first['name'],'description':'Approved red coat','notes':{'Wardrobe':'Red coat'},'reference_ids':[]})
    assert edited.status_code==200
    assert client.post(f'/api/projects/{sid}/world/build-shots').status_code==409
    assert client.post(f"/api/projects/{sid}/world/{first['key']}/approve",json={'version':1}).status_code==409
    assert client.post(f"/api/projects/{sid}/world/{first['key']}/approve",json={'version':2}).status_code==200
    portal._sessions.pop(sid)
    assert client.get(f'/api/projects/{sid}/world').json()['ready']
    assert client.post(f'/api/projects/{sid}/world/build-shots').status_code==200
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        p=client.get('/api/projects/'+sid).json()
        if p['status']!='running':break
        time.sleep(.01)
    assert p['status']=='complete',p.get('error')
    assert p['project']['scenes'][0]['shots']
    assert 'Approved red coat' in p['project']['bible'][first['kind']][0]['description']
    assert client.post(f'/api/projects/{sid}/world/build-shots').status_code==409
    assert p['shot_sheet_versions']
    session=portal._sessions[sid]
    session.produce()
    media_before=list(session.versions)
    updated=client.put(f"/api/projects/{sid}/world/{first['key']}",json={'version':2,'name':first['name'],'description':'A blue coat','notes':{'Wardrobe':'Blue coat'},'reference_ids':[]})
    assert updated.status_code==200
    client.post(f"/api/projects/{sid}/world/{first['key']}/approve",json={'version':3})
    target=p['project']['scenes'][0]['shots'][0]['id']
    applied=client.post(f'/api/projects/{sid}/world/apply-to-shots',json={'shot_ids':[target]})
    assert applied.status_code==200
    assert 'Blue coat' in session.draft_prompts[target]
    assert session.versions==media_before
    portal._sessions.pop(sid,None)


def test_character_views_use_identity_and_preserve_versions(tmp_path, monkeypatch):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path/'projects'))
    monkeypatch.setattr(portal,'_build_llm',lambda backend:MockLLMClient())
    calls=[]
    class Images:
        def generate(self,prompt,key):
            calls[-1]['prompt']=prompt
            return b'\x89PNG\r\n\x1a\npreview'
    def provider(session,settings):
        calls.append({'refs':settings.reference_ids})
        return Images()
    monkeypatch.setattr(portal,'validate_image_settings',provider)
    client=TestClient(portal.app)
    sid=client.post('/api/plan',json={'concept':'A keeper.','backend':'mock','review_world':True}).json()['session_id']
    for _ in range(100):
        data=client.get('/api/projects/'+sid).json()
        if data['status']=='awaiting_approval': break
        time.sleep(.01)
    url=f'/api/projects/{sid}/world'
    sheet=next(s for s in client.get(url).json()['sheets'] if s['kind']=='characters')
    def generate(view):
        nonlocal sheet
        res=client.post(url+'/'+sheet['key']+'/generate-image',json={'version':sheet['version'],'view':view})
        assert res.status_code==200,res.text
        sheet=next(s for s in res.json()['sheets'] if s['key']==sheet['key'])
        return sheet['character_views'][view]
    face=generate('face')
    body=generate('full_body')
    assert calls[-1]['refs'][0]==face
    assert 'Head-to-toe' in calls[-1]['prompt']
    accessories=generate('accessories')
    costume=generate('costume')
    assert calls[-1]['refs'][:3]==[face,body,accessories]
    new_face=generate('face')
    assert face not in sheet['reference_ids']
    assert new_face in sheet['reference_ids']
    assert len(sheet['reference_ids'])==4
    assert any(face in version['reference_ids'] for version in sheet['history'])
    assert any(r['id']==face for r in portal._sessions[sid].image_references)
    portal._sessions.pop(sid)
    restored=next(s for s in client.get(url).json()['sheets'] if s['kind']=='characters')
    assert restored['character_views']['costume']==costume
    assert restored['character_views']['face']==new_face
    other=next(s for s in client.get(url).json()['sheets'] if s['kind']=='locations')
    assert client.post(url+'/'+other['key']+'/generate-image',json={'version':other['version'],'view':'face'}).status_code==400
    assert client.post(url+'/'+sheet['key']+'/generate-image',json={'version':sheet['version'],'view':'unknown'}).status_code==422
