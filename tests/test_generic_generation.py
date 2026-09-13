import importlib
import time
from copy import deepcopy
from fastapi.testclient import TestClient
from moviecrew.mock import MockLLMClient
portal=importlib.import_module('moviecrew.portal.app')


def test_missing_provider_does_not_create_demo(monkeypatch,tmp_path):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path))
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.delenv('ANTHROPIC_API_KEY',raising=False)
    client=TestClient(portal.app)
    before=set(portal._sessions)
    result=client.post('/api/plan',json={'concept':'A robot exploring a moon'})
    assert result.status_code==400 and 'Demo example' in result.text
    assert set(portal._sessions)==before
    assert portal._default_backend()==''
    monkeypatch.setenv('ANTHROPIC_API_KEY','test-placeholder')
    assert portal._default_backend()=='anthropic'
    monkeypatch.setenv('OPENROUTER_API_KEY','test-placeholder')
    assert portal._default_backend()=='openrouter'


def test_reference_overflow_never_reaches_provider(monkeypatch,tmp_path):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path))
    monkeypatch.setattr(portal,'_build_llm',lambda _:MockLLMClient())
    client=TestClient(portal.app)
    sid=client.post('/api/plan',json={'concept':'A creature','backend':'mock','review_world':True}).json()['session_id']
    for _ in range(100):
        if client.get('/api/projects/'+sid).json()['status']=='awaiting_approval':break
        time.sleep(.01)
    session=portal._sessions[sid];sheet=next(iter(session.world_sheets.values()))
    sheet['reference_ids']=['a','b','c','d','e'];snapshot=deepcopy(sheet)
    def unexpected(*args):raise AssertionError('Provider must not be called')
    monkeypatch.setattr(portal,'validate_image_settings',unexpected)
    response=client.post(f"/api/projects/{sid}/world/{sheet['key']}/generate-image",json={'version':sheet['version']})
    assert response.status_code==400 and 'No references were dropped' in response.text
    assert sheet==snapshot and not session.image_lock.locked()


def test_nonhuman_character_prompt_preserves_subject(monkeypatch,tmp_path):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path))
    monkeypatch.setattr(portal,'_build_llm',lambda _:MockLLMClient())
    client=TestClient(portal.app)
    sid=client.post('/api/plan',json={'concept':'An octopus','backend':'mock','review_world':True}).json()['session_id']
    for _ in range(100):
        if client.get('/api/projects/'+sid).json()['status']=='awaiting_approval':break
        time.sleep(.01)
    session=portal._sessions[sid];sheet=next(s for s in session.world_sheets.values() if s['kind']=='characters')
    sheet.update(name='Octopus',description='An octopus with eight arms and no clothing',notes={})
    calls=[]
    from moviecrew.image import MockImageProvider
    class Capture:
        def generate(self,prompt,key):calls.append(prompt);return MockImageProvider._BYTES
    monkeypatch.setattr(portal,'validate_image_settings',lambda *args:Capture())
    response=client.post(f"/api/projects/{sid}/world/{sheet['key']}/generate-image",json={'version':sheet['version'],'view':'full_body'})
    assert response.status_code==200,response.text
    assert 'octopus with eight arms' in calls[0]
    assert 'simple neutral everyday clothing' not in calls[0]
    assert 'Use clothing or coverings only when specified' in calls[0]


def test_designer_profiles_survive_and_drafting_preserves_edits(monkeypatch, tmp_path):
    from moviecrew.crew import MovieCrew
    from moviecrew.portal.world import initialize_sheets
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path))
    class Designer(MockLLMClient):
        def complete_json(self, *, task, system, user):
            result = super().complete_json(task=task, system=system, user=user)
            if task == 'designer':
                assert 'sheet_notes' in system
                result['sheet_notes'] = {'characters:'+result['characters'][0]['id']: {'Appearance': 'Eight copper arms'}}
            return result
    project = MovieCrew(Designer()).make('A mechanical creature', stop_after_design=True)
    assert next(iter(project.to_dict()['sheet_notes'].values()))['Appearance'] == 'Eight copper arms'
    monkeypatch.setattr(portal, '_build_llm', lambda _: MockLLMClient())
    client = TestClient(portal.app)
    sid = client.post('/api/plan', json={'concept':'A creature', 'backend':'mock', 'review_world':True}).json()['session_id']
    for _ in range(100):
        if client.get('/api/projects/'+sid).json()['status'] == 'awaiting_approval': break
        time.sleep(.01)
    session = portal._sessions[sid]
    session.project = project
    session.world_sheets = {}
    initialize_sheets(session)
    sheet = next(s for s in session.world_sheets.values() if s['kind']=='characters')
    assert sheet['notes']['Appearance'] == 'Eight copper arms'
    class Profile:
        def complete_json(self, **kwargs):
            return {'Appearance':'Overwrite', 'Personality':'Curious', 'invalid':'Ignored'}
    monkeypatch.setattr(portal, '_default_backend', lambda:'openrouter')
    monkeypatch.setattr(portal, '_build_llm', lambda _:Profile())
    url = f"/api/projects/{sid}/world/{sheet['key']}/draft-details"
    result = client.post(url, json={'version':1})
    assert result.status_code == 200, result.text
    assert result.json()['notes'] == {'Appearance':'Eight copper arms','Personality':'Curious'}
    assert result.json()['version'] == 2
    assert client.post(url, json={'version':1}).status_code == 409
