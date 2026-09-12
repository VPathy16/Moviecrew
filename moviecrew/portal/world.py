"""Reviewable cast/world sheets and an explicit gate before cinematography."""
import copy
import json
import threading
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from .. import projects
from ..brief import BriefedLLM
from ..crew import MovieCrew
from ..schema import Character, Location, Prop

router = APIRouter()
KINDS = {'characters': Character, 'locations': Location, 'props': Prop}


def session(project):
    from .app import _session_or_error
    value, error = _session_or_error(project)
    if error:
        raise HTTPException(404, 'Film not found')
    return value


def initialize_sheets(s):
    for kind in KINDS:
        for entity in getattr(s.project.bible, kind):
            key = kind+':'+entity.id
            s.world_sheets.setdefault(key, dict(key=key, kind=kind, entity_id=entity.id,
                name=entity.name, description=entity.description, notes={}, reference_ids=[],
                version=1, approved_version=None, history=[]))


def response(s):
    initialize_sheets(s)
    sheets = list(s.world_sheets.values())
    return {'sheets': sheets, 'ready': bool(sheets) and all(x['version']==x['approved_version'] for x in sheets),
            'has_shots': any(scene.shots for scene in s.project.scenes), 'status':s.plan_progress.status}


@router.get('/api/projects/{project}/world')
def read_world(project: str):
    s=session(project)
    with s.plan_lock:
        return response(s)


class SheetEdit(BaseModel):
    name: str = Field(min_length=1,max_length=200)
    description: str = Field(min_length=1,max_length=6000)
    notes: dict[str,str] = Field(default_factory=dict)
    reference_ids: list[str] = Field(default_factory=list,max_length=12)
    version: int


def mutable(s):
    if s.plan_progress.status in ('queued','running') or s.image_lock.locked():
        raise HTTPException(409,'Wait for the current generation to finish')


@router.put('/api/projects/{project}/world/{key}')
def edit_sheet(project: str,key: str,req: SheetEdit):
    s=session(project)
    with s.plan_lock:
        mutable(s)
        initialize_sheets(s)
        sheet=s.world_sheets.get(key)
        if not sheet: raise HTTPException(404,'Sheet not found')
        if req.version!=sheet['version']: raise HTTPException(409,'This sheet changed. Reopen it before saving.')
        if not req.name.strip() or not req.description.strip(): raise HTTPException(400,'Give this sheet a name and description')
        if any(ref not in {r['id'] for r in s.image_references} for ref in req.reference_ids): raise HTTPException(400,'Choose references from this film')
        if len(req.notes)>12 or any(len(v)>3000 for v in req.notes.values()): raise HTTPException(400,'Keep sheet notes under 3000 characters each')
        sheet['history'].append({k:copy.deepcopy(v) for k,v in sheet.items() if k!='history'})
        sheet.update(name=req.name.strip(),description=req.description.strip(),notes=req.notes,reference_ids=req.reference_ids,version=sheet['version']+1)
        projects.save(s)
        return sheet


class NewSheet(BaseModel):
    kind: str
    name: str = Field(min_length=1,max_length=200)
    description: str = Field(min_length=1,max_length=6000)


@router.post('/api/projects/{project}/world')
def add_sheet(project: str,req: NewSheet):
    if req.kind not in KINDS: raise HTTPException(400,'Choose character, environment or asset')
    s=session(project)
    with s.plan_lock:
        mutable(s)
        entity=KINDS[req.kind](id=uuid.uuid4().hex,name=req.name,description=req.description)
        getattr(s.project.bible,req.kind).append(entity)
        initialize_sheets(s)
        projects.save(s)
        return response(s)


class Approval(BaseModel):
    version: int


@router.post('/api/projects/{project}/world/{key}/approve')
def approve(project: str,key: str,req: Approval):
    s=session(project)
    with s.plan_lock:
        mutable(s)
        sheet=s.world_sheets.get(key)
        if not sheet: raise HTTPException(404,'Sheet not found')
        if req.version!=sheet['version']: raise HTTPException(409,'Review the latest sheet before approving')
        sheet['approved_version']=sheet['version']
        projects.save(s)
        return response(s)


class SheetImage(Approval):
    model: str = 'offline'
    view: Literal['sheet', 'face', 'full_body', 'accessories', 'costume'] = 'sheet'


CHARACTER_VIEWS = {
    'face': ('Face', 'Close-up casting portrait, front and three-quarter facial views. Clearly establish facial identity, hair and age. Neutral background, no accessories obscuring the face.'),
    'full_body': ('Full body', 'Head-to-toe front and side views of the SAME person as the face reference. Establish height, build and proportions in simple neutral everyday clothing. Keep feet fully visible.'),
    'accessories': ('Accessories', 'An accessory design sheet: the character’s jewellery, glasses, bags and personal carried objects. Show individual objects clearly, their scale and materials, with small wearing/holding references where useful. Preserve the established identity.'),
    'costume': ('Costume', 'Full-length final costume fitting on the SAME established character. Preserve face and body proportions. Incorporate the selected accessories. Show front and back garment views with fabrics, colours and footwear clearly visible.'),
}



@router.post('/api/projects/{project}/world/{key}/generate-image')
def generate_sheet_image(project: str,key: str,req: SheetImage):
    from .app import ImageSettingsRequest,validate_image_settings
    from ..image_studio import media_type
    s=session(project)
    with s.plan_lock:
        mutable(s)
        sheet=s.world_sheets.get(key)
        if not sheet or req.version!=sheet['version']: raise HTTPException(409,'Reopen the latest sheet')
        if req.view != 'sheet' and sheet['kind'] != 'characters': raise HTTPException(400,'Character views are only available for characters')
        if len(sheet['reference_ids'])>=12 and not sheet.get('character_views',{}).get(req.view): raise HTTPException(400,'Keep at most twelve references on a sheet')
        if not s.image_lock.acquire(blocking=False): raise HTTPException(409,'An image is already generating')
        snapshot=copy.deepcopy(sheet)
    try:
        # Use an explicit project setting if provided; otherwise the free preview.
        settings={'model':req.model,'options':{}}
        views=snapshot.get('character_views',{})
        # Latest identity references take priority over miscellaneous uploads.
        prior = {'face': [], 'full_body': ['face'], 'accessories': ['face','full_body'], 'costume': ['face','full_body','accessories']}.get(req.view, [])
        refs=list(dict.fromkeys([views[v] for v in prior if views.get(v)] + snapshot['reference_ids']))[:4]
        provider=validate_image_settings(s,ImageSettingsRequest(**{**settings,'reference_ids':refs}))
        prompt=f"Create a production reference sheet for {snapshot['kind']}: {snapshot['name']}. {snapshot['description']}. Details: {json.dumps(snapshot['notes'])}. Consistent subject, clear reference views, neutral layout."
        if req.view != 'sheet':
            title,instruction=CHARACTER_VIEWS[req.view]
            prompt += f"\nCreate only the {title} stage. {instruction}\nSpecific direction: {snapshot['notes'].get(title,'')}"
        data=provider.generate(prompt,key)
        image_type=media_type(data)
        ref_id=uuid.uuid4().hex
        path=Path(s.session_dir)/'references'/f'{ref_id}.png'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
        with s.plan_lock:
            sheet['history'].append({k:copy.deepcopy(v) for k,v in sheet.items() if k!='history'})
            s.image_references.append({'id':ref_id,'name':sheet['name']+' · '+CHARACTER_VIEWS.get(req.view,('Reference',))[0],'path':str(path),'media_type':image_type,'view':req.view,'model':req.model})
            if req.view != 'sheet':
                previous=sheet.setdefault('character_views',{}).get(req.view)
                sheet['reference_ids']=[r for r in sheet['reference_ids'] if r!=previous]
                sheet['character_views'][req.view]=ref_id
            sheet['reference_ids'].append(ref_id)
            sheet['model']=req.model
            sheet['version']+=1
            projects.save(s)
            return response(s)
    finally:
        s.image_lock.release()


@router.post('/api/projects/{project}/world/build-shots')
def build_shots(project: str):
    s=session(project)
    with s.plan_lock:
        mutable(s)
        state=response(s)
        if state['has_shots']: raise HTTPException(409,'This film already has shots. Existing shots and media are preserved.')
        if not state['ready']: raise HTTPException(409,'Approve every cast, environment and asset sheet first')
        if s.plan_progress.status!='awaiting_approval': raise HTTPException(409,'This film is not waiting for cast and world approval')
        approved=copy.deepcopy(s.project)
        for sheet in s.world_sheets.values():
            entity=next(e for e in getattr(approved.bible,sheet['kind']) if e.id==sheet['entity_id'])
            entity.name=sheet['name']
            entity.description=sheet['description']+'\n'+'\n'.join(f'{k}: {v}' for k,v in sheet['notes'].items() if v)
            entity.reference_images=[r['path'] for r in s.image_references if r['id'] in sheet['reference_ids']]
        s.plan_progress.status='running'
        s.plan_progress.stage='cinematography'
        projects.save(s)
    threading.Thread(target=finish,args=(s,approved),daemon=True).start()
    return {'status':'running'}


def finish(s,approved):
    from .app import _build_llm
    try:
        llm=BriefedLLM(_build_llm(s.backend),s.creative_brief,asdict(approved.bible))
        result=MovieCrew(llm).make('',approved_project=approved,run_continuity=False)
        with s.plan_lock:
            s.project=result
            for scene in result.scenes:
                relevant=[x for x in s.world_sheets.values() if x['kind']=='props' or x['entity_id'] in scene.character_ids or x['entity_id']==scene.location_id]
                for shot in scene.shots:
                    s.shot_sheet_versions[shot.id]={x['key']:x['approved_version'] for x in relevant}
                    refs=list(dict.fromkeys(ref for x in relevant for ref in x['reference_ids']))
                    shot.reference_image_ids=list(dict.fromkeys(shot.reference_image_ids+[r['path'] for r in s.image_references if r['id'] in refs]))
                    s.image_settings[shot.id]={'model':'offline','options':{},'reference_ids':refs[:4],'variations':1}
            s.base_flags=list(result.render_plan.flags)
            s.plan_progress.status='complete'
            s.plan_progress.stage='complete'
            projects.save(s)
    except Exception as exc:
        with s.plan_lock:
            s.plan_progress.status='awaiting_approval'
            s.plan_progress.stage='world_review'
            s.plan_progress.error=str(exc)
            projects.save(s)

class ApplyWorld(BaseModel):
    shot_ids: list[str] = Field(min_length=1,max_length=500)


@router.post('/api/projects/{project}/world/apply-to-shots')
def apply_to_shots(project: str,req: ApplyWorld):
    s=session(project)
    with s.plan_lock:
        mutable(s)
        if not response(s)['ready']: raise HTTPException(409,'Approve the latest sheets before applying them')
        all_shots={shot.id:shot for scene in s.project.scenes for shot in scene.shots}
        if any(sid not in all_shots for sid in req.shot_ids): raise HTTPException(404,'Choose shots in this film')
        for scene in s.project.scenes:
            relevant=[x for x in s.world_sheets.values() if x['kind']=='props' or x['entity_id'] in scene.character_ids or x['entity_id']==scene.location_id]
            new_ids={r for sheet in relevant for r in sheet['reference_ids']}
            old_ids={r for sheet in relevant for version in [sheet,*sheet['history']] for r in version['reference_ids']}
            for shot in scene.shots:
                if shot.id in req.shot_ids:
                    remaining=set(s.image_settings.get(shot.id,{}).get('reference_ids',[]))-old_ids
                    if len(remaining|new_ids)>4:
                        raise HTTPException(400,'This shot needs more than four references. Select fewer references on its sheets before applying.')
        for scene in s.project.scenes:
            relevant=[x for x in s.world_sheets.values() if x['kind']=='props' or x['entity_id'] in scene.character_ids or x['entity_id']==scene.location_id]
            ref_ids=list(dict.fromkeys(r for sheet in relevant for r in sheet['reference_ids']))
            old_ids={r for sheet in relevant for version in [sheet,*sheet['history']] for r in version['reference_ids']}
            old_paths={r['path'] for r in s.image_references if r['id'] in old_ids}
            details='\n'.join(sheet['name']+': '+sheet['description']+'; '+'; '.join(f'{k}: {v}' for k,v in sheet['notes'].items() if v) for sheet in relevant)
            for shot in scene.shots:
                if shot.id not in req.shot_ids: continue
                shot.reference_image_ids=[p for p in shot.reference_image_ids if p not in old_paths]+[r['path'] for r in s.image_references if r['id'] in ref_ids]
                settings=s.image_settings.setdefault(shot.id,{'model':'offline','options':{},'variations':1})
                combined=[r for r in settings.get('reference_ids',[]) if r not in old_ids]+ref_ids
                if len(set(combined))>4: raise HTTPException(400,'This shot needs more than four references. Select fewer references on its sheets before applying.')
                settings['reference_ids']=list(dict.fromkeys(combined))
                intent=next((i for i in s.project.render_plan.intents if i.shot_id==shot.id),None)
                base=s.draft_prompts.get(shot.id,intent.description if intent else shot.description).split('\n\nApproved cast and world:\n')[0]
                s.draft_prompts[shot.id]=base+'\n\nApproved cast and world:\n'+details
                s.shot_sheet_versions[shot.id]={sheet['key']:sheet['approved_version'] for sheet in relevant}
        projects.save(s)
        return {'updated_shots':req.shot_ids,'message':'References and image drafts updated. Existing images and videos are unchanged.'}
