import importlib
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from moviecrew import projects
from moviecrew.crew import MovieCrew
from moviecrew.mock import MockLLMClient
from moviecrew.image import MockImageProvider
from moviecrew.studio import StudioSession, Stage
from moviecrew.render import FakeRenderClient
from moviecrew.portal import film_workflow as flow

portal = importlib.import_module('moviecrew.portal.app')

@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT', str(tmp_path / 'db'))
    fake = FakeRenderClient()
    monkeypatch.setattr(portal, '_render_client', lambda: (fake, None))
    for name in ('film-a', 'film-b'):
        s = StudioSession(name, Stage.SHOT_DEFS, MovieCrew(MockLLMClient()).make('A keeper.'), str(tmp_path/name), MockImageProvider(), backend='mock')
        s.produce()
        projects.save(s)
        portal._sessions[name] = s
    flow.init()
    yield TestClient(portal.app), fake, portal._sessions['film-a'], tmp_path
    portal._sessions.pop('film-a', None)
    portal._sessions.pop('film-b', None)


def request_for(s):
    return dict(request_id=str(uuid.uuid4()), shot_id=s.board[0].shot_id, frame_id=s.board[0].version_id,
                prompt='Gentle motion', model='fake/model', duration_s=1, aspect_ratio='16:9', resolution='480p')


def test_video_ownership_idempotency_and_estimate_no_submission(setup, monkeypatch):
    client, fake, s, _ = setup
    monkeypatch.setattr(flow, 'launch', lambda *args: None)
    req = request_for(s)
    assert client.post('/api/projects/film-a/video-estimate', json=req).status_code == 200
    assert not fake.submitted
    response = client.post('/api/projects/film-a/videos', json=req)
    assert response.status_code == 200
    assert client.post('/api/projects/film-a/videos', json=req).json()['id'] == response.json()['id']
    assert len(client.get('/api/projects/film-a/videos').json()['items']) == 1
    assert client.get('/api/projects/film-b/videos').json()['items'] == []
    assert client.get('/api/projects/film-b/film-media/'+req['request_id']).status_code == 404
    assert client.post('/api/projects/film-b/videos', json=req).status_code == 400
    assert client.put('/api/projects/film-b/cut', json={'clips':[{'video_id':req['request_id'],'end':1}]}).status_code == 404


def test_uncertain_submission_is_never_retried(setup, monkeypatch):
    _, fake, _, _ = setup
    item = dict(id=str(uuid.uuid4()),project='film-a',kind='video',status='submitting',backend='fake')
    flow.put(item)
    launches=[]
    monkeypatch.setattr(flow,'launch',lambda *args: launches.append(args))
    flow.recover()
    assert flow.get('film-a',item['id'])['status']=='uncertain'
    assert not launches and not fake.submitted


@pytest.mark.skipif(not shutil.which('ffmpeg') or not shutil.which('ffprobe'), reason='ffmpeg required')
def test_offline_video_cut_export_and_reopen(setup, monkeypatch):
    client, _, s, _ = setup
    monkeypatch.setattr(flow,'launch',lambda *args: None)
    req=request_for(s)
    response=client.post('/api/projects/film-a/videos',json=req)
    assert response.status_code==200
    flow.work('film-a', req['request_id'])
    video=flow.get('film-a',req['request_id'])
    assert video['status']=='complete', video.get('error')
    assert video['offline']
    cut={'clips':[{'video_id':video['id'],'start':0,'end':.5,'mute':True},{'video_id':video['id'],'start':.2,'end':.8,'mute':False}], 'aspect_ratio':'9:16'}
    assert client.put('/api/projects/film-a/cut',json=cut).status_code==200
    bad={**cut,'clips':[{'video_id':video['id'],'start':1,'end':.5}]}
    assert client.put('/api/projects/film-a/cut',json=bad).status_code==400
    export=client.post('/api/projects/film-a/exports').json()
    flow.work('film-a',export['id'])
    completed=flow.get('film-a',export['id'])
    assert completed['status']=='complete',completed.get('error')
    duration,audio=flow.probe(completed['path'])
    assert .9 < duration < 1.4 and audio
    portal._sessions.pop('film-a')
    assert client.get('/api/projects/film-a/cut').json()==cut
    assert client.get('/api/projects/film-a/film-media/'+export['id']).status_code==200
    assert client.get('/api/projects/film-b/film-media/'+export['id']).status_code==404
    # A silent uploaded video also exports with a synthesized silent audio track.
    silent=Path(completed['path']).with_name('silent.mp4')
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',video['path'],'-an','-c:v','copy',str(silent)],check=True)
    uploaded=client.post('/api/projects/film-a/shots/'+s.board[0].shot_id+'/upload-video',content=silent.read_bytes())
    assert uploaded.status_code==200
    clip=uploaded.json()
    flow.work('film-a',clip['id'])
    assert flow.get('film-a',clip['id'])['status']=='complete'
    client.put('/api/projects/film-a/cut',json={'clips':[{'video_id':clip['id'],'end':.5}]})
    export2=client.post('/api/projects/film-a/exports').json()
    flow.work('film-a',export2['id'])
    assert flow.get('film-a',export2['id'])['status']=='complete'


def test_video_direction_persists_separately(setup):
    client, _, s, _=setup
    req=request_for(s)
    assert client.put('/api/projects/film-a/video-drafts',json=req).status_code==200
    assert client.get('/api/projects/film-a/video-drafts').json()[req['shot_id']]['prompt']=='Gentle motion'
    assert client.get('/api/projects/film-b/video-drafts').json()=={}
    assert s.draft_prompts.get(req['shot_id'])!='Gentle motion'


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='ffmpeg required')
def test_resume_known_provider_job_without_resubmitting(setup, monkeypatch):
    client, _, _, tmp = setup
    from moviecrew.render import RenderJob, JobStatus
    sample=tmp/'sample.mp4'
    flow.run_ffmpeg(['-f','lavfi','-i','color=c=blue:s=64x64:r=24','-t','0.25','-c:v','libx264','-pix_fmt','yuv420p',str(sample)])
    class Provider:
        name='test-provider'
        disconnected=True
        def submit(self, *args, **kwargs):
            raise AssertionError('Existing jobs must not be resubmitted')
        def poll(self, job_id):
            assert job_id=='existing-job'
            if self.disconnected:
                raise OSError('temporary connection failure')
            return RenderJob(job_id=job_id,shot_id='sc1-sh1',status=JobStatus.SUCCEEDED,video_url='https://example.test/video',raw={'status':'completed'})
        def fetch(self, job, out):
            shutil.copyfile(sample,out)
            return out
    provider=Provider()
    monkeypatch.setattr(portal,'_render_client',lambda:(provider,None))
    item={'id':str(uuid.uuid4()),'project':'film-a','kind':'video','status':'running','backend':'test-provider','provider_id':'existing-job','model':'test'}
    flow.put(item)
    flow.work('film-a',item['id'])
    assert flow.get('film-a',item['id'])['status']=='waiting'
    provider.disconnected=False
    flow.work('film-a',item['id'])
    assert flow.get('film-a',item['id'])['status']=='complete'
    assert client.get('/api/projects/film-a/film-media/'+item['id']).status_code==200
    assert client.get('/api/projects/film-b/film-media/'+item['id']).status_code==404


def test_unsupported_duration_rejected_before_submission(setup, monkeypatch):
    from dataclasses import replace
    client, fake, s, _ = setup
    caps = fake.capabilities()
    monkeypatch.setattr(fake, 'capabilities', lambda model=None: replace(caps, supported_durations=(5, 6)))
    response = client.post('/api/projects/film-a/videos', json=request_for(s))
    assert response.status_code == 400
    assert '5, 6 seconds' in response.json()['detail']
    assert not fake.submitted
