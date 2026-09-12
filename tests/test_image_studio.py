import base64

import pytest
from moviecrew.image import MockImageProvider
from moviecrew.image_studio import StudioImageProvider, choose_endpoint


def test_request_contains_exact_reference_bytes_and_settings(tmp_path):
    path=tmp_path/'reference.png'
    path.write_bytes(MockImageProvider._BYTES)
    calls=[]
    def transport(method,url,headers,body):
        calls.append(body)
        return {'data':[{'b64_json':base64.b64encode(MockImageProvider._BYTES).decode()}],'usage':{'cost':0.03}}
    provider=StudioImageProvider(model='test/image', options={'aspect_ratio':'16:9'}, references=[{'id':'ref','path':str(path)}], endpoint={'provider_tag':'test'}, transport=transport)
    assert provider.generate('A red coat','shot')==MockImageProvider._BYTES
    payload=calls[0]
    assert payload['model']=='test/image'
    assert payload['aspect_ratio']=='16:9'
    assert payload['provider']=={'only':['test'],'allow_fallbacks':False}
    assert base64.b64decode(payload['input_references'][0]['image_url']['url'].split(',')[1])==path.read_bytes()
    assert provider.last_cost==0.03


def test_rejects_unsupported_combinations():
    endpoints=[{'provider_tag':'test','supported_parameters':{'aspect_ratio':{'type':'enum','values':['1:1']}}}]
    with pytest.raises(ValueError):choose_endpoint(endpoints,{'aspect_ratio':'16:9'},False)
    with pytest.raises(ValueError):choose_endpoint(endpoints,{},True)
    assert choose_endpoint(endpoints,{'aspect_ratio':'1:1'},False)['provider_tag']=='test'


def test_upload_generate_variations_and_restore(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from moviecrew.crew import MovieCrew
    from moviecrew.mock import MockLLMClient
    from moviecrew.studio import StudioSession, Stage
    from moviecrew import projects
    from moviecrew.portal.app import app, _sessions
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path/'db'))
    session=StudioSession('settings-test',Stage.SHOT_DEFS,MovieCrew(MockLLMClient()).make('A lighthouse'),str(tmp_path/'media'),MockImageProvider())
    _sessions[session.session_id]=session
    projects.save(session)
    client=TestClient(app)
    ref=client.post('/api/projects/settings-test/references',content=MockImageProvider._BYTES,headers={'x-image-name':'Coat.png'}).json()['id']
    shot=session.project.scenes[0].shots[0].id
    url=f'/api/projects/settings-test/shots/{shot}'
    body={'model':'offline','options':{},'reference_ids':[ref],'variations':2,'prompt':'A red coat'}
    assert client.put(url+'/image-settings',json=body).status_code==200
    data=client.post(url+'/images',json=body).json()
    assert len(data['frames'])==2
    assert all(f['reference_ids']==[ref] for f in data['frames'])
    assert len({f['version_id'] for f in data['frames']})==2
    _sessions.pop('settings-test')
    restored=client.get('/api/projects/settings-test').json()
    assert restored['image_settings'][shot]['variations']==2
    assert restored['image_references'][0]['id']==ref
    assert client.post(url+'/images',json={**body,'reference_ids':['foreign']}).status_code==400
    assert client.post(url+'/images',json={**body,'variations':5}).status_code==400
    assert client.post('/api/projects/settings-test/references',content=b'not-an-image').status_code==400


def test_cost_estimate_only_for_unambiguous_pricing():
    from moviecrew.image_studio import estimate_cost
    endpoint={'pricing':[{'billable':'output_image','unit':'image','cost_usd':0.04}, {'billable':'input_reference','unit':'image','cost_usd':0.01}]}
    assert estimate_cost(endpoint,2,3)==0.18
    assert estimate_cost({'pricing':[]},0,1) is None
    assert estimate_cost({'pricing':[{'billable':'output_image','unit':'token','cost_usd':0.01}]},0,1) is None
    assert estimate_cost({'pricing':[{'billable':'output_image','unit':'image','cost_usd':0.01,'variant':'high'}]},0,1) is None


def test_background_support_is_validated_and_sent():
    endpoint={'provider_tag':'test','supported_parameters':{'background':{'type':'enum','values':['transparent','opaque']}}}
    assert choose_endpoint([endpoint],{'background':'transparent'},False)==endpoint
    with pytest.raises(ValueError):choose_endpoint([endpoint],{'background':'invalid'},False)
    provider=StudioImageProvider(model='test/image',options={'background':'transparent'},references=[],endpoint=endpoint,transport=lambda *a: {})
    assert provider.build_request('A lamp')['background']=='transparent'


@pytest.mark.parametrize("model", ["google/gemini-test-image", "openai/gpt-test-image"])
def test_image_models_receive_pinned_character_images(tmp_path, monkeypatch, model):
    import importlib
    from fastapi.testclient import TestClient
    from moviecrew.crew import MovieCrew
    from moviecrew.mock import MockLLMClient
    from moviecrew.studio import StudioSession, Stage
    from moviecrew import projects
    portal=importlib.import_module('moviecrew.portal.app')
    monkeypatch.setenv('MOVIECREW_PROJECTS_ROOT',str(tmp_path/'db'))
    session=StudioSession('gemini-refs-test',Stage.SHOT_DEFS,MovieCrew(MockLLMClient()).make('A lighthouse'),str(tmp_path/'media'),MockImageProvider())
    portal._sessions[session.session_id]=session
    character=session.project.bible.characters[0]
    views={}
    for view in ['face','full_body','accessories','costume']:
        path=tmp_path/(view+'.png');path.write_bytes(MockImageProvider._BYTES+view.encode())
        views[view]=view
        session.image_references.append({'id':view,'name':view,'path':str(path),'media_type':'image/png'})
    key='characters:'+character.id
    approved=dict(key=key,kind='characters',entity_id=character.id,name=character.name,description='Keeper',notes={},version=1,approved_version=1,reference_ids=list(views),character_views=views)
    session.world_sheets[key]={**approved,'version':2,'reference_ids':[], 'history':[approved]}
    shot=session.project.scenes[0].shots[0].id
    session.shot_sheet_versions[shot]={key:1}
    projects.save(session)
    calls=[]
    def transport(method,url,headers,body):
        calls.append(body)
        return {'data':[{'b64_json':base64.b64encode(MockImageProvider._BYTES).decode()}]}
    def provider(s,req):
        return StudioImageProvider(model=req.model,options={},references=[next(r for r in s.image_references if r['id']==ref) for ref in req.reference_ids],endpoint={'provider_tag':'test'},transport=transport)
    monkeypatch.setattr(portal,'validate_image_settings',provider)
    client=TestClient(portal.app)
    url=f'/api/projects/{session.session_id}/shots/{shot}/images'
    result=client.post(url,json={'model':model,'prompt':'Keeper climbs the cliff','reference_ids':[]})
    assert result.status_code==200,result.text
    assert len(calls)==1
    assert len(calls[0]['input_references'])==4
    for view,reference in zip(views,calls[0]['input_references']):
        assert base64.b64decode(reference['image_url']['url'].split(',')[1])==(tmp_path/(view+'.png')).read_bytes()
    assert 'Reference 1:' in calls[0]['prompt'] and 'face' in calls[0]['prompt']
    assert 'costume' in calls[0]['prompt']
    assert result.json()['frames'][0]['reference_ids']==list(views)
    # Exceeding the reference budget must stop before transport, not silently truncate.
    too_many=client.post(url,json={'model':model,'prompt':'Cliff','reference_ids':['extra']})
    assert too_many.status_code==400 and len(calls)==1
    estimate=client.post(f'/api/projects/{session.session_id}/image-estimate',json={'model':'offline','shot_id':shot,'reference_ids':['extra']})
    assert estimate.status_code==400
    portal._sessions.pop(session.session_id,None)


def test_model_catalog_visible_without_credentials(monkeypatch):
    import importlib
    portal=importlib.import_module('moviecrew.portal.app')
    monkeypatch.delenv('OPENROUTER_API_KEY',raising=False)
    monkeypatch.setattr(portal.image_studio,'models',lambda:[{'id':'provider/model-a','name':'Model A'},{'id':'provider/model-b','name':'Model B'}])
    result=portal.image_models()
    assert not result['configured']
    assert [m['id'] for m in result['models']]==['offline','provider/model-a','provider/model-b']
