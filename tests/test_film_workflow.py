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
    listed=client.get('/api/projects/film-a/videos').json()['items']
    assert listed[0]['width'] and listed[0]['height']
    cut={'clips':[{'video_id':video['id'],'start':0,'end':.5,'mute':True},{'video_id':video['id'],'start':.2,'end':.8,'mute':False}], 'aspect_ratio':'9:16'}
    assert client.put('/api/projects/film-a/cut',json=cut).status_code==200
    bad={**cut,'clips':[{'video_id':video['id'],'start':1,'end':.5}]}
    assert client.put('/api/projects/film-a/cut',json=bad).status_code==400
    export=client.post('/api/projects/film-a/exports').json()
    flow.work('film-a',export['id'])
    completed=flow.get('film-a',export['id'])
    assert completed['status']=='complete',completed.get('error')
    duration,audio,width,height=flow.probe(completed['path'])
    assert .9 < duration < 1.4 and audio
    assert width and height
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


def test_character_mode_uses_only_owned_references_without_frame_anchors(setup, monkeypatch):
    from types import SimpleNamespace
    from moviecrew.render_openrouter import OpenRouterRenderClient
    client, _, s, tmp = setup
    calls=[]
    def transport(method, url, headers, body):
        if url.endswith('/videos/models'):
            return {'data':[{'id':'minimax/hailuo-3','supported_durations':[5],
                             'supported_resolutions':['480p'],'supported_aspect_ratios':['16:9'],
                             'supported_frame_images':['first_frame','last_frame']}]}
        calls.append(body)
        return {'error':'deliberate test rejection', 'status':'failed'}
    provider=OpenRouterRenderClient(transport=transport)
    monkeypatch.setattr(portal,'_render_client',lambda:(provider,None))
    monkeypatch.setattr(flow,'launch',lambda *args:None)
    path=tmp/'character.png'
    path.write_bytes(MockImageProvider._BYTES)
    s.image_references=[{'id':'face','path':str(path),'name':'Face'}]
    req={**request_for(s),'model':'minimax/hailuo-3','duration_s':5,
         'frame_id':'','reference_mode':'character','reference_ids':['face']}
    assert client.post('/api/projects/film-a/video-estimate',json=req).status_code==200
    assert not calls
    for update in ({'reference_ids':['foreign']},{'reference_ids':[]},{'frame_id':s.board[0].version_id}):
        assert client.post('/api/projects/film-a/videos',json={**req,**update}).status_code==400
    result=client.post('/api/projects/film-a/videos',json=req)
    assert result.status_code==200
    assert 'reference_paths' not in result.json()
    uploaded=[]
    class Store:
        serves_public_urls=True
        name='test'
        def put_reference(self,path,key):
            uploaded.append(path)
            return SimpleNamespace(url='https://example.test/character.png')
    monkeypatch.setattr(portal,'_asset_store',lambda:Store())
    flow.work('film-a',req['request_id'])
    assert uploaded==[str(path)]
    assert len(calls)==1
    assert 'frame_images' not in calls[0]
    assert calls[0]['input_references']==[{'type':'image_url','image_url':{'url':'https://example.test/character.png'}}]


def test_canvas_modes_and_sizes_roundtrip(setup, monkeypatch):
    client, _, _, _ = setup
    payload={'clips':[], 'aspect_ratio':'9:16','fit':'cover','resolution':'4K'}
    assert client.put('/api/projects/film-a/cut',json=payload).json()==payload
    assert client.get('/api/projects/film-a/cut').json()==payload
    assert client.put('/api/projects/film-a/cut',json={**payload,'fit':'stretch'}).status_code==422
    assert client.put('/api/projects/film-a/cut',json={**payload,'resolution':'8K'}).status_code==422
    assert client.put('/api/projects/film-a/cut',json={**payload,'resolution':'1440p'}).status_code==200
    assert 'crop=1280:720' in flow.canvas_filter(1280,720,'cover')
    assert 'color=black' in flow.canvas_filter(1280,720,'contain')


@pytest.mark.skipif(not shutil.which('ffmpeg'), reason='ffmpeg required')
def test_enhancement_ownership_payload_resume_and_original_audio(setup, monkeypatch):
    from moviecrew.portal import film_enhance as enhance
    from types import SimpleNamespace
    client, _, s, tmp=setup
    monkeypatch.setattr(flow,'launch',lambda *args:None)
    monkeypatch.setenv('FAL_KEY','test-key-not-real')
    source=tmp/'portrait.mp4'
    flow.run_ffmpeg(['-f','lavfi','-i','color=c=red:s=90x160:r=24','-f','lavfi','-i','sine=frequency=400:sample_rate=48000','-t','0.5','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(source)])
    original=dict(id=str(uuid.uuid4()),project='film-a',kind='video',status='complete',shot_id=s.board[0].shot_id,path=str(source),duration_s=.5)
    flow.put(original)
    class Store:
        serves_public_urls=True
        name='test'
        def put_reference(self,path,key):return SimpleNamespace(url='https://v3.fal.media/source.mp4')
    monkeypatch.setattr(portal,'_asset_store',lambda:Store())
    calls=[]
    def queue(url,body=None):
        calls.append((url,body))
        if body:return {'request_id':'remote-1','status_url':'https://queue.fal.run/status','response_url':'https://queue.fal.run/result'}
        if url.endswith('status'):return {'status':'COMPLETED'}
        return {'video':{'url':'https://v3.fal.media/output.mp4'}}
    monkeypatch.setattr(enhance,'queue_request',queue)
    monkeypatch.setattr(enhance,'download',lambda url,path:shutil.copyfile(source,path))
    monkeypatch.setenv('OPENROUTER_API_KEY','test-key-not-real')
    from moviecrew.render_openrouter import OpenRouterRenderClient
    from moviecrew.render import RenderJob, JobStatus
    def flux_call(self, method, path, body=None):
        calls.append((path,body))
        return {'id':'flux-1'}
    monkeypatch.setattr(OpenRouterRenderClient,'_call',flux_call)
    monkeypatch.setattr(OpenRouterRenderClient,'poll',lambda self,job_id:RenderJob(job_id=job_id,shot_id='',status=JobStatus.SUCCEEDED))
    monkeypatch.setattr(OpenRouterRenderClient,'fetch',lambda self,job,path:shutil.copyfile(source,path))
    req={'request_id':str(uuid.uuid4()),'video_id':original['id'],'operation':'upscale','start':0,'end':.5,'factor':2}
    assert client.post('/api/projects/film-b/enhancements',json=req).status_code==404
    res=client.post('/api/projects/film-a/enhancements',json=req)
    assert res.status_code==200
    assert client.post('/api/projects/film-a/enhancements',json=req).json()['id']==req['request_id']
    assert not calls
    flow.work('film-a',req['request_id'])
    done=flow.get('film-a',req['request_id'])
    assert done['status']=='complete',done.get('error')
    assert calls[0][1]=={'model':'black-forest-labs/flux-video-upscale','upscale_factor':2,'creativity':0,'input_references':[{'type':'video_url','video_url':{'url':'https://v3.fal.media/source.mp4'}}]}
    assert client.post('/api/projects/film-a/enhancements',json={**req,'request_id':str(uuid.uuid4()),'factor':4}).status_code==422
    assert flow.probe(done['path'])[1]
    assert flow.get('film-a',original['id'])==original
    assert 'fal_status_url' not in flow.public(done)
    # Resume only polls the original provider job.
    done.update(status='waiting');flow.put(done);calls.clear();flow.work('film-a',done['id'])
    assert not any(body for _,body in calls)
    # Expand sends a video (not an image-generation prompt); centre is composited back.
    req.update(request_id=str(uuid.uuid4()),operation='expand',aspect_ratio='16:9',preserve_center=True)
    client.post('/api/projects/film-a/enhancements',json=req);calls.clear();flow.work('film-a',req['request_id'])
    expanded=flow.get('film-a',req['request_id'])
    assert expanded['status']=='complete',expanded.get('error')
    assert calls[0][1]['aspect_ratio']=='16:9'
    assert '/reframe' in calls[0][0]
    assert flow.probe(expanded['path'])[1]
    import json
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',expanded['path']]))
    v=next(x for x in info['streams'] if x['codec_type']=='video')
    assert (v['width'],v['height'])==(1280,720)
    # A boundary image is owned by this film and usable as a starting frame.
    frame=client.post('/api/projects/film-a/editor-frame',json={'shot_id':s.board[0].shot_id,'video_id':original['id'],'time_s':.25})
    assert frame.status_code==200
    assert any(v.version_id==frame.json()['frame_id'] for v in s.versions)
    assert client.post('/api/projects/film-b/editor-frame',json={'shot_id':s.board[0].shot_id,'video_id':original['id'],'time_s':.25}).status_code==404


def test_enhance_missing_key_and_unknown_submission(setup, monkeypatch):
    from moviecrew.portal import film_enhance as enhance
    client,_,_,tmp=setup
    monkeypatch.delenv('FAL_KEY',raising=False)
    assert client.get('/api/projects/film-a/enhancement-options').json()['configured'] is False
    monkeypatch.setenv('FAL_KEY','test')
    monkeypatch.setattr(enhance,'queue_request',lambda *args: (_ for _ in ()).throw(AssertionError('must not resubmit')))
    # The common recovery path marks an interrupted enhancement submission uncertain.
    job=dict(id=str(uuid.uuid4()),project='film-a',kind='video',backend='fal-enhance',status='submitting')
    flow.put(job);monkeypatch.setattr(flow,'launch',lambda *args:None);flow.recover()
    assert flow.get('film-a',job['id'])['status']=='uncertain'


@pytest.mark.skipif(not shutil.which('ffmpeg') or not shutil.which('ffprobe'), reason='ffmpeg required')
def test_extensions_use_trimmed_boundaries_and_correct_anchor_positions(setup, monkeypatch):
    import json
    from types import SimpleNamespace
    from moviecrew.render_openrouter import OpenRouterRenderClient
    client, _, s, tmp=setup
    monkeypatch.setattr(flow,'launch',lambda *args:None)
    path=tmp/'48fps.mp4'
    flow.run_ffmpeg(['-f','lavfi','-i','testsrc2=s=96x96:r=48','-t','1','-c:v','libx264','-pix_fmt','yuv420p',str(path)])
    source=dict(id=str(uuid.uuid4()),project='film-a',kind='video',status='complete',shot_id=s.board[0].shot_id,path=str(path),duration_s=1)
    flow.put(source)
    calls=[]
    def transport(method,url,headers,body):
        if url.endswith('/videos/models'):
            return {'data':[{'id':name,'supported_durations':[5],'supported_resolutions':['480p'],
                             'supported_aspect_ratios':['16:9'],'supported_frame_images':positions}
                            for name,positions in [('start-only',['first_frame']),('both',['first_frame','last_frame'])]]}
        calls.append(body)
        return {'status':'failed','error':'deliberate test stop'}
    provider=OpenRouterRenderClient(transport=transport)
    monkeypatch.setattr(portal,'_render_client',lambda:(provider,None))
    class Store:
        serves_public_urls=True
        name='test'
        def put_reference(self,path,key):return SimpleNamespace(url='https://example.test/boundary.png')
    monkeypatch.setattr(portal,'_asset_store',lambda:Store())
    models=client.get('/api/projects/film-a/video-models').json()['models']
    assert models[0]['frame_positions']==['first_frame']
    for direction,position in [('before','last_frame'),('after','first_frame')]:
        trim={'video_id':source['id'],'start':.2,'end':.4,'direction':direction}
        result=client.post('/api/projects/film-a/extension-boundary',json=trim)
        assert result.status_code==200,result.text
        boundary=result.json()
        assert boundary['anchor_position']==position
        assert not calls  # Boundary preparation must never start paid work.
        frame=next(v for v in s.versions if v.version_id==boundary['frame_id'])
        if direction=='after':
            assert .39 < frame.settings['boundary_time_s'] < .4  # Last 48fps frame, not end - 1/24.
        req={**request_for(s),'model':'both','duration_s':5,'frame_id':boundary['frame_id'],'anchor_position':position}
        if direction=='before':
            assert client.post('/api/projects/film-a/videos',json={**req,'model':'start-only'}).status_code==400
            assert client.post('/api/projects/film-a/videos',json={**req,'anchor_position':'first_frame'}).status_code==400
        created=client.post('/api/projects/film-a/videos',json=req)
        assert created.status_code==200,created.text
        assert created.json()['extension']==trim
        assert client.post('/api/projects/film-a/videos',json=req).json()['id']==req['request_id']
        flow.work('film-a',req['request_id'])
        assert len(calls)==1
        assert calls[0]['frame_images']==[{'type':'image_url','image_url':{'url':'https://example.test/boundary.png'},'frame_type':position}]
        calls.clear()
    assert client.post('/api/projects/film-b/extension-boundary',json=trim).status_code==404
    assert client.post('/api/projects/film-a/extension-boundary',json={**trim,'end':2}).status_code==400


def test_text_only_video_has_no_image_inputs(setup, monkeypatch):
    client, fake, s, _ = setup
    monkeypatch.setattr(fake, 'name', 'test-live')
    monkeypatch.setattr(flow, 'launch', lambda *args: None)
    req = {**request_for(s), 'reference_mode':'text', 'frame_id':'', 'reference_ids':[]}
    _, frame, spec = flow.prepare('film-a', flow.VideoRequest(**req))
    assert frame is None and not spec.reference_images and not spec.first_frame and not spec.last_frame
    assert client.post('/api/projects/film-a/video-estimate',json=req).status_code == 200
    assert client.post('/api/projects/film-a/videos',json=req).status_code == 200
    bad={**req,'frame_id':s.board[0].version_id}
    assert client.post('/api/projects/film-a/video-estimate',json=bad).status_code == 400
    assert not fake.submitted


def test_character_guided_extension_preserves_metadata_without_anchor(setup, monkeypatch):
    client,fake,s,root=setup
    monkeypatch.setattr(fake,'name','test-live')
    monkeypatch.setattr(flow,'CHARACTER_VIDEO_MODELS',{'fake/model'})
    monkeypatch.setattr(flow,'launch',lambda *args:None)
    frame=s.versions[0]
    frame.settings['extension']={'direction':'after','video_id':'source','start':0,'end':1}
    path=root/'sheet.png';path.write_bytes(MockImageProvider._BYTES)
    s.image_references.append({'id':'sheet','path':str(path),'media_type':'image/png','name':'Character'})
    req={**request_for(s),'frame_id':frame.version_id,'reference_mode':'character','reference_ids':['sheet']}
    _,_,spec=flow.prepare('film-a',flow.VideoRequest(**req))
    assert not spec.first_frame and not spec.last_frame
    result=client.post('/api/projects/film-a/videos',json=req)
    assert result.status_code==200,result.text
    item=flow.get('film-a',req['request_id'])
    assert item['extension']['direction']=='after'
    assert item['reference_ids']==['sheet'] and item['source_path']==''


@pytest.mark.skipif(not shutil.which('ffmpeg'),reason='ffmpeg required')
def test_waveform_extraction_and_silent_clip(setup):
    client,_,s,tmp=setup
    toned=tmp/'toned.mp4'
    flow.run_ffmpeg(['-f','lavfi','-i','color=c=red:s=64x64:r=24','-f','lavfi','-i','sine=frequency=400:sample_rate=48000','-t','0.5','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(toned)])
    toned_item=dict(id=str(uuid.uuid4()),project='film-a',kind='video',status='complete',shot_id=s.board[0].shot_id,path=str(toned),duration_s=.5,has_audio=True)
    flow.put(toned_item)
    peaks=client.get('/api/projects/film-a/film-media/'+toned_item['id']+'/waveform').json()['peaks']
    assert peaks and max(peaks)<=1 and min(peaks)>=0

    silent=tmp/'silent.mp4'
    flow.run_ffmpeg(['-f','lavfi','-i','color=c=blue:s=64x64:r=24','-t','0.5','-c:v','libx264','-pix_fmt','yuv420p',str(silent)])
    silent_item=dict(id=str(uuid.uuid4()),project='film-a',kind='video',status='complete',shot_id=s.board[0].shot_id,path=str(silent),duration_s=.5,has_audio=False)
    flow.put(silent_item)
    assert client.get('/api/projects/film-a/film-media/'+silent_item['id']+'/waveform').json()['peaks']==[]
    assert client.get('/api/projects/film-b/film-media/'+toned_item['id']+'/waveform').status_code==404


def test_regenerate_of_round_trips_through_public(setup,monkeypatch):
    client,_,s,_=setup
    monkeypatch.setattr(flow,'launch',lambda *args:None)
    original=request_for(s)
    assert client.post('/api/projects/film-a/videos',json=original).status_code==200
    regen={**request_for(s),'request_id':str(uuid.uuid4()),
           'regenerate_of':{'video_id':original['request_id'],'start':0,'end':1}}
    result=client.post('/api/projects/film-a/videos',json=regen)
    assert result.status_code==200,result.text
    assert result.json()['regenerate_of']=={'video_id':original['request_id'],'start':0,'end':1}
    listed={i['id']:i for i in client.get('/api/projects/film-a/videos').json()['items']}
    assert listed[regen['request_id']]['regenerate_of']['video_id']==original['request_id']
    assert listed[original['request_id']]['regenerate_of'] is None


def test_shot_cast_endpoint(setup):
    from moviecrew.portal import world
    client,_,s,_=setup
    world.initialize_sheets(s)
    shot=s.board[0]
    shot_obj=next(sh for scene in s.project.scenes for sh in scene.shots if sh.id==shot.shot_id)
    shot_obj.visible_character_ids=[s.project.bible.characters[0].id]
    chips=client.get('/api/projects/film-a/shots/'+shot.shot_id+'/cast').json()['chips']
    assert any(c['entity_id']==s.project.bible.characters[0].id and c['kind']=='characters' for c in chips)
    assert client.get('/api/projects/film-a/shots/does-not-exist/cast').status_code==404
