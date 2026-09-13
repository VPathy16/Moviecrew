"""Persisted, optimistic-concurrency Director review before Writer execution."""
from copy import deepcopy
import json
import threading
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel, Field, model_validator
from .. import projects
from ..agents import DirectorAgent

router = APIRouter()


class CastMember(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=160)
    role: str = Field(default='', max_length=1000)
    motivation: str = Field(default='', max_length=2000)
    description: str = Field(default='', max_length=3000)


class Direction(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    logline: str = Field(min_length=1, max_length=3000)
    outline: list[str] = Field(min_length=1, max_length=60)
    characters: list[CastMember] = Field(default_factory=list, max_length=40)

    @model_validator(mode='after')
    def validate_direction(self):
        if not self.title.strip() or not self.logline.strip() or any(not b.strip() or len(b)>5000 for b in self.outline):
            raise ValueError('Title, logline and story beats must not be blank or oversized.')
        ids = [c.id for c in self.characters]
        if len(ids) != len(set(ids)) or any(not c.name.strip() for c in self.characters):
            raise ValueError('Characters need unique IDs and non-empty names.')
        return self


class EditDirection(BaseModel):
    revision: int = Field(ge=0)
    draft: Direction


class RevisionRequest(BaseModel):
    revision: int = Field(ge=0)


class RegenerateRequest(RevisionRequest):
    feedback: str = Field(default='', max_length=5000)


class RestoreRequest(RevisionRequest):
    restore_revision: int = Field(ge=1)


def retain(session, draft, source):
    state = session.director_review
    state['revision'] += 1
    state['draft'] = deepcopy(draft)
    state['history'].append({'revision': state['revision'], 'source': source, 'draft': deepcopy(draft)})
    # Proposed direction never rewrites an accepted film.
    if not session.project.scenes:
        session.project.title = draft['title']
        session.project.logline = draft['logline']
        session.project.outline = list(draft['outline'])
    if state.get('approved'):
        state['needs_review'] = True


def generate_direction(session, llm):
    with session.plan_lock:
        state = session.director_review
        revision = state['revision']
        current = deepcopy(state.get('draft'))
        feedback = state.get('feedback', '')
    result = llm.complete_json(
        task='director',
        system=DirectorAgent.system_prompt + '\nAlso return characters: [{id, name, role, motivation, description}]. '
        'Use stable character IDs. Refine the supplied draft using feedback. Preserve its cast and user decisions unless feedback explicitly requests changing them.',
        user=json.dumps({'concept': session.creative_brief.get('concept', ''),
                         'creative_brief': session.creative_brief, 'current_draft': current, 'feedback': feedback}))
    # Mock/legacy Director responses may omit cast; retain user-defined cast.
    result.setdefault('characters', current.get('characters', []) if current else [])
    draft = Direction.model_validate(result).model_dump()
    with session.plan_lock:
        if session.director_review['revision'] != revision:
            raise ValueError('Direction changed during generation; retained your newer draft.')
        retain(session, draft, 'generated')
        session.plan_progress.status = 'director_review'
        session.plan_progress.stage = 'director_review'
        session.plan_progress.error = None
        projects.save(session)


def resolve(session_id):
    from .app import _session_or_error
    return _session_or_error(session_id)


def conflict(session, revision):
    from .app import _error
    state = session.director_review
    if not state:
        return _error(409, 'This film uses the existing planning flow. Start a new film to review direction before writing.')
    if session.plan_progress.status in ('running', 'queued'):
        return _error(409, 'Please wait for the current generation to finish.')
    if revision != state['revision']:
        return _error(409, 'This direction has a newer revision. Reload before editing.')
    return None


@router.put('/api/projects/{session_id}/director')
def edit(session_id: str, req: EditDirection):
    session, err = resolve(session_id)
    if err: return err
    with session.plan_lock:
        if (err := conflict(session, req.revision)) is not None: return err
        retain(session, req.draft.model_dump(), 'edited')
        projects.save(session)
        return deepcopy(session.director_review)


@router.post('/api/projects/{session_id}/director/restore')
def restore(session_id: str, req: RestoreRequest):
    from .app import _error
    session, err = resolve(session_id)
    if err: return err
    with session.plan_lock:
        if (err := conflict(session, req.revision)) is not None: return err
        previous = next((h for h in session.director_review['history'] if h['revision']==req.restore_revision), None)
        if not previous: return _error(404, 'Direction revision not found.')
        retain(session, previous['draft'], 'restored')
        projects.save(session)
        return deepcopy(session.director_review)


def regenerate_job(session):
    from .app import _build_llm
    try:
        generate_direction(session, _build_llm(session.backend))
    except Exception as exc:
        with session.plan_lock:
            session.plan_progress.status = 'failed'
            session.plan_progress.error = str(exc)
            projects.save(session)


@router.post('/api/projects/{session_id}/director/regenerate')
def regenerate(session_id: str, req: RegenerateRequest):
    from .app import _error
    session, err = resolve(session_id)
    if err: return err
    with session.plan_lock:
        if (err := conflict(session, req.revision)) is not None: return err
        if session.project.scenes:
            return _error(409, 'Existing scenes are preserved. Refine and save direction here; create a new film for a rewritten script.')
        session.director_review.pop('approved', None)
        session.director_review.pop('approved_revision', None)
        session.director_review['feedback'] = req.feedback
        session.plan_progress.status = 'running'
        session.plan_progress.stage = 'director'
        session.plan_progress.error = None
        projects.save(session)
    threading.Thread(target=regenerate_job, args=(session,), daemon=True).start()
    return {'status': 'running'}


@router.post('/api/projects/{session_id}/director/approve')
def approve(session_id: str, req: RevisionRequest):
    from .app import _error, _run_plan_job, PlanRequest
    session, err = resolve(session_id)
    if err: return err
    with session.plan_lock:
        if (err := conflict(session, req.revision)) is not None: return err
        state = session.director_review
        if state.get('approved_revision') == req.revision and session.plan_progress.status != 'failed':
            return {'status': session.plan_progress.status}
        if session.project.scenes:
            return _error(409, 'Existing scenes are preserved. Start a new film to write a different script.')
        if not state.get('draft'): return _error(409, 'Generate a direction before approving it.')
        state['approved'] = deepcopy(state['draft'])
        state['approved_revision'] = req.revision
        session.plan_progress.status = 'running'
        session.plan_progress.stage = 'writer'
        session.plan_progress.error = None
        projects.save(session)
        request = PlanRequest(**state['request'])
    threading.Thread(target=_run_plan_job, args=(session, request, str(Path(session.session_dir)/'project_checkpoint.json')), daemon=True).start()
    return {'status': 'running'}
