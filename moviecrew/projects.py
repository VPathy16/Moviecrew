"""Durable single-user project library. Media remains in the existing stores.

MOVIECREW_PROJECTS_ROOT isolates installations and tests. This is not an
account authorization boundary; hosted multi-user access is a later phase.
"""
import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path

from .schema import Beat, Bible, Project, Scene, Shot, ShotIntent, RenderPlan, ContinuityFlag
from .studio import StudioSession, Stage, PlanProgress, StoryboardFrame


def root():
    path = Path(os.environ.get('MOVIECREW_PROJECTS_ROOT', str(Path.home() / '.moviecrew' / 'projects')))
    path.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connect():
    db = sqlite3.connect(root() / 'library.sqlite3', timeout=30)
    db.execute('CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, title TEXT, updated TEXT DEFAULT CURRENT_TIMESTAMP, payload TEXT NOT NULL)')
    try:
        with db:
            yield db
    finally:
        db.close()


def save(session):
    payload = {k: getattr(session, k) for k in ('session_id', 'session_dir', 'backend', 'continuity_status', 'continuity_message', 'creative_brief', 'director_review', 'planning_scenes', 'world_sheets', 'shot_sheet_versions', 'draft_prompts', 'image_settings', 'image_references')}
    payload.update(project=asdict(session.project), stage=session.stage.value,
                   board=[asdict(f) for f in session.board], versions=[asdict(f) for f in session.versions],
                   plan_progress=asdict(session.plan_progress), base_flags=[asdict(f) for f in session.base_flags])
    with connect() as db:
        db.execute('INSERT INTO projects(id,title,payload) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,payload=excluded.payload,updated=CURRENT_TIMESTAMP',
                   (session.session_id, session.project.title or 'Untitled film', json.dumps(payload)))


def listing():
    with connect() as db:
        rows = db.execute('SELECT id,title,updated,payload FROM projects ORDER BY updated DESC').fetchall()
    result = []
    for project_id, title, updated, payload in rows:
        board = json.loads(payload).get('board', [])
        cover = next((f for f in board if f.get('image_path')), None)
        result.append(dict(id=project_id, title=title, updated=updated,
                            cover_version_id=cover['version_id'] if cover else None))
    return result


def load(session_id, image_provider):
    with connect() as db:
        row = db.execute('SELECT payload FROM projects WHERE id=?', (session_id,)).fetchone()
    if not row:
        return None
    data = json.loads(row[0])
    project = data.pop('project')
    project['bible'] = Bible.from_dict(project['bible'])
    project['scenes'] = [Scene(**{**s, 'shots': [Shot(**{**shot, 'beats': [Beat(**b) for b in shot.get('beats', [])]}) for shot in s['shots']]}) for s in project['scenes']]
    if project.get('render_plan'):
        plan = project['render_plan']
        project['render_plan'] = RenderPlan(**{**plan, 'intents':[ShotIntent(**i) for i in plan['intents']], 'flags':[ContinuityFlag(**f) for f in plan['flags']]})
    data['project'] = Project(**project)
    data['stage'] = Stage(data['stage'])
    data['board'] = [StoryboardFrame(**f) for f in data['board']]
    data['versions'] = [StoryboardFrame(**f) for f in data.get('versions', [])]
    data['base_flags'] = [ContinuityFlag(**f) for f in data['base_flags']]
    data['plan_progress'] = PlanProgress(**data['plan_progress'])
    if data['plan_progress'].status in ('queued', 'running'):
        data['plan_progress'].status = 'failed'
        data['plan_progress'].error = 'Generation was interrupted by an application restart. Your completed work is preserved.'
    if data['continuity_status'] == 'running':
        data['continuity_status'] = 'failed'
    return StudioSession(**data, image_provider=image_provider)
