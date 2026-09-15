from pathlib import Path

from moviecrew import projects
from moviecrew.crew import MovieCrew
from moviecrew.image import MockImageProvider
from moviecrew.mock import MockLLMClient
from moviecrew.studio import StudioSession, Stage


def test_restart_keeps_versions_drafts_and_selection(tmp_path, monkeypatch):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path / 'db'))
    session = StudioSession('persistent', Stage.SHOT_DEFS,
        MovieCrew(MockLLMClient()).make('A lighthouse keeper.'), str(tmp_path / 'media'), MockImageProvider())
    session.produce()
    original = session.board[0]
    original_bytes = Path(original.image_path).read_bytes()
    session.revise(shot_id=original.shot_id, prompt='A new image prompt')
    session.draft_prompts[original.shot_id] = 'Unsumbitted draft'
    projects.save(session)
    restored = projects.load('persistent', MockImageProvider())
    assert restored.project == session.project
    assert restored.board == session.board
    assert restored.versions == session.versions
    assert restored.draft_prompts == session.draft_prompts
    assert restored.board[0].image_path != original.image_path
    assert Path(original.image_path).read_bytes() == original_bytes
    assert projects.listing()[0]['id'] == 'persistent'
    assert projects.listing()[0]['cover_version_id'] == session.board[0].version_id


def test_project_library_api_exposes_thumbnail_url(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from moviecrew.portal.app import app, _sessions
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path / 'db'))
    with_image = StudioSession('with-image', Stage.SHOT_DEFS,
        MovieCrew(MockLLMClient()).make('A lighthouse keeper.'), str(tmp_path / 'media'), MockImageProvider())
    with_image.produce()
    projects.save(with_image)
    without_image = StudioSession('without-image', Stage.SHOT_DEFS,
        MovieCrew(MockLLMClient()).make('A lighthouse keeper.'), str(tmp_path / 'media2'), MockImageProvider())
    projects.save(without_image)
    _sessions.clear()
    client = TestClient(app)
    listing = {p['id']: p for p in client.get('/api/projects').json()['projects']}
    assert listing['with-image']['thumbnail_url'] == f"/api/projects/with-image/versions/{with_image.board[0].version_id}/image"
    assert client.get(listing['with-image']['thumbnail_url']).status_code == 200
    assert listing['without-image']['thumbnail_url'] is None


def test_interrupted_plan_retains_partial_project(tmp_path, monkeypatch):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path))
    session = StudioSession('interrupted', Stage.SHOT_DEFS,
        MovieCrew(MockLLMClient()).make('A keeper.'), str(tmp_path), MockImageProvider())
    session.plan_progress.status = 'running'
    projects.save(session)
    restored = projects.load('interrupted', MockImageProvider())
    assert restored.plan_progress.status == 'failed'
    assert restored.project.scenes == session.project.scenes
    assert 'restart' in restored.plan_progress.error


def test_api_select_rename_duplicate_and_missing_version(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from moviecrew.portal.app import app, _sessions
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path / 'db'))
    session = StudioSession('api-project', Stage.SHOT_DEFS,
        MovieCrew(MockLLMClient()).make('A lighthouse keeper.'), str(tmp_path / 'media'), MockImageProvider())
    session.produce()
    original = session.board[0]
    session.revise(shot_id=original.shot_id, prompt='Edited image')
    projects.save(session)
    _sessions.pop(session.session_id, None)
    client = TestClient(app)
    assert client.get('/api/projects/api-project').status_code == 200
    response = client.patch('/api/projects/api-project', json={'shot_id':original.shot_id, 'version_id':original.version_id, 'prompt':'Saved draft', 'title':'Renamed film'})
    assert response.status_code == 200
    assert response.json()['project']['title'] == 'Renamed film'
    assert next(f for f in response.json()['frames'] if f['shot_id']==original.shot_id)['version_id'] == original.version_id
    assert client.patch('/api/projects/api-project', json={'shot_id':original.shot_id,'version_id':'missing'}).status_code == 404
    duplicate = client.post('/api/projects/api-project/duplicate').json()['id']
    assert client.get('/api/projects/'+duplicate).json()['project']['title'] == 'Renamed film (copy)'
    _sessions.pop(session.session_id, None)
    restored = client.get('/api/projects/api-project').json()
    assert restored['draft_prompts'][original.shot_id] == 'Saved draft'
    assert client.get('/api/projects/api-project/versions/'+original.version_id+'/image').status_code == 200


def test_crew_review_survives_reopen(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from moviecrew.portal.app import app, _sessions
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path / 'db'))
    session = StudioSession('crew-review', Stage.SHOT_DEFS,
        MovieCrew(MockLLMClient()).make('A lighthouse keeper.', run_continuity=False),
        str(tmp_path / 'media'), MockImageProvider(), backend='mock')
    session.base_flags = list(session.project.render_plan.flags)
    projects.save(session)
    _sessions[session.session_id] = session
    client = TestClient(app)
    response = client.post('/api/session/crew-review/continuity')
    assert response.status_code == 200
    assert response.json()['continuity_status'] == 'complete'
    _sessions.pop(session.session_id)
    reopened = client.get('/api/projects/crew-review').json()
    assert reopened['continuity_status'] == 'complete'
    assert reopened['project']['render_plan']['flags'] == response.json()['flags']
    assert reopened['plan_progress']['status'] == 'complete'
    _sessions.pop(session.session_id, None)
