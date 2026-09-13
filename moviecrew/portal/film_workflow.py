"""Project-owned video jobs, selected cuts and local film export.

Legacy takes are never implicitly attached to a film. Every new video and export
has a durable UUID and owning project. Submission uncertainty is preserved rather
than automatically repeating a possibly billed request.
"""
from __future__ import annotations

import json
import asyncio
import logging
import math
import re
import shutil
import subprocess
import threading
import time
import uuid
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .. import projects
from ..render import ShotSpec, JobStatus

router = APIRouter()
_active: set[str] = set()
_lock = threading.Lock()
TERMINAL = {'complete', 'failed', 'uncertain'}
# Explicitly documented reference-to-video support; do not infer it from I2V.
CHARACTER_VIDEO_MODELS = {'minimax/hailuo-3', 'bytedance/seedance-2.5', 'bytedance/seedance-2.0-fast'}


def db():
    return projects.connect()


def init():
    with db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS film_items (id TEXT PRIMARY KEY, project TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL)')
        conn.execute('CREATE TABLE IF NOT EXISTS film_cuts (project TEXT PRIMARY KEY, payload TEXT NOT NULL)')


def put(item):
    with db() as conn:
        conn.execute('INSERT INTO film_items VALUES (?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',
                     (item['id'], item['project'], item['kind'], json.dumps(item)))


def items(project):
    init()
    with db() as conn:
        return [json.loads(r[0]) for r in conn.execute('SELECT payload FROM film_items WHERE project=? ORDER BY rowid DESC', (project,))]


def get(project, item_id):
    init()
    with db() as conn:
        row = conn.execute('SELECT payload FROM film_items WHERE project=? AND id=?', (project, item_id)).fetchone()
    if not row:
        raise HTTPException(404, 'Video not found in this film')
    return json.loads(row[0])


def session(project):
    from .app import _session_or_error
    value, error = _session_or_error(project)
    if error:
        raise HTTPException(404, 'Film not found')
    return value


def folder(project):
    return Path(session(project).session_dir) / 'film_media'


def public(item):
    data = {k: v for k, v in item.items() if k not in {'path', 'source_path', 'provider_url', 'spec', 'reference_paths', 'fal_status_url', 'fal_response_url'}}
    data['video_url'] = f"/api/projects/{item['project']}/film-media/{item['id']}" if item.get('path') and item['status'] == 'complete' else None
    return data


def probe(path):
    try:
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], capture_output=True, text=True, timeout=30, check=True)
        data = json.loads(result.stdout)
        video = next(s for s in data['streams'] if s['codec_type'] == 'video')
        duration = float(data['format'].get('duration') or video.get('duration') or 0)
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError('Invalid duration')
        return duration, any(s['codec_type'] == 'audio' for s in data['streams'])
    except (OSError, ValueError, StopIteration, subprocess.SubprocessError) as exc:
        raise ValueError('This file is not a readable video. MP4 or MOV is recommended.') from exc


def run_ffmpeg(args):
    result = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-xerror', '-y', *args], capture_output=True, text=True, timeout=1800)
    if result.returncode:
        logging.getLogger(__name__).error('ffmpeg failed: %s', result.stderr[-2000:])
        raise ValueError('Video processing failed. Check the source clips and available disk space.')


class VideoRequest(BaseModel):
    request_id: uuid.UUID
    shot_id: str
    frame_id: str = ''
    reference_mode: Literal['shot', 'character'] = 'shot'
    reference_ids: list[str] = Field(default_factory=list, max_length=9)
    prompt: str = Field(min_length=1, max_length=20000)
    model: str
    duration_s: int = Field(default=5, ge=1, le=60)
    aspect_ratio: str = '16:9'
    resolution: str = '720p'
    audio: bool = False


def prepare(project, req):
    from .app import _render_client
    s = session(project)
    if s.plan_progress.status != 'complete':
        raise HTTPException(409, 'Wait for the crew to finish planning')
    if not any(shot.id == req.shot_id for scene in s.project.scenes for shot in scene.shots):
        raise HTTPException(404, 'Shot not found in this film')
    frame = next((f for f in s.versions if f.shot_id == req.shot_id and f.version_id == req.frame_id and f.status == 'ok' and f.image_path), None)
    if req.reference_mode == 'shot' and (frame is None or not Path(frame.image_path).is_file()):
        raise HTTPException(400, 'Choose an existing image version for this shot')
    client, error = _render_client()
    if error:
        raise HTTPException(503, 'Your video connection needs attention in Settings')
    if req.model not in {m['id'] for m in client.models()}:
        raise HTTPException(400, 'Choose an available video model')
    caps = client.capabilities(req.model)
    if req.reference_mode == 'character':
        if client.name == 'fake':
            raise HTTPException(400, 'Character-only video requires a connected video provider')
        if req.model not in CHARACTER_VIDEO_MODELS:
            raise HTTPException(400, 'Choose H3 or Seedance for character references through OpenRouter')
        if req.frame_id:
            raise HTTPException(400, 'Character-only mode cannot include a shot frame')
        refs = {r['id']: r for r in s.image_references}
        if not req.reference_ids or len(req.reference_ids) != len(set(req.reference_ids)):
            raise HTTPException(400, 'Choose one or more distinct character references')
        if any(r not in refs or not Path(refs[r]['path']).is_file() for r in req.reference_ids):
            raise HTTPException(400, 'Choose references belonging to this film')
        if caps.max_image_references is not None and len(req.reference_ids) > caps.max_image_references:
            raise HTTPException(400, 'Too many references for this model')
    elif caps.max_image_references == 0 or not caps.supports_first_last_frame:
        raise HTTPException(400, 'Choose a model that supports a storyboard image as its first frame')
    if req.duration_s > caps.max_duration_s:
        raise HTTPException(400, f'This model supports up to {caps.max_duration_s} seconds')
    if caps.supported_durations and req.duration_s not in caps.supported_durations:
        raise HTTPException(400, 'Choose a supported duration: ' + ', '.join(map(str, caps.supported_durations)) + ' seconds')
    if req.aspect_ratio not in (caps.supported_aspect_ratios or ('16:9',)):
        raise HTTPException(400, 'Choose a supported video aspect ratio')
    if req.resolution not in (caps.supported_resolutions or ('720p',)):
        raise HTTPException(400, 'Choose a supported video resolution')
    if req.audio and not caps.supports_audio:
        raise HTTPException(400, 'This model does not support generated audio')
    if req.reference_mode == 'shot' and client.name != 'fake' and frame.model in ('offline', 'MockImageProvider'):
        raise HTTPException(400, 'Create a real storyboard image before using paid video generation')
    spec = ShotSpec(shot_id=req.shot_id, prompt=req.prompt, duration_s=req.duration_s,
                    aspect_ratio=req.aspect_ratio, resolution=req.resolution, generate_audio=req.audio)
    return client, frame, spec


@router.get('/api/projects/{project}/video-models')
def models(project: str):
    session(project)
    from .app import _render_client
    client, error = _render_client()
    if error:
        raise HTTPException(503, 'Video connection unavailable')
    result = []
    for model in client.models():
        c = client.capabilities(model['id'])
        if c.max_image_references == 0 or not c.supports_first_last_frame:
            continue
        result.append({'id': model['id'], 'name': 'Offline preview · no AI generation' if client.name == 'fake' else model.get('name', model['id']),
                       'duration_max': c.max_duration_s, 'durations': c.supported_durations, 'ratios': c.supported_aspect_ratios or ['16:9'],
                       'resolutions': c.supported_resolutions or ['720p'], 'audio': c.supports_audio,
                       'character_references': model['id'] in CHARACTER_VIDEO_MODELS})
    return {'models': result, 'offline': client.name == 'fake'}


@router.post('/api/projects/{project}/video-estimate')
def estimate(project: str, req: VideoRequest):
    client, frame, spec = prepare(project, req)
    # Estimating never uploads media or submits a generation.
    spec.reference_images = ([r['path'] for r in session(project).image_references if r['id'] in req.reference_ids]
                             if req.reference_mode == 'character' else [str(frame.image_path)])
    return {'cost': client.estimate_cost(spec, model=req.model), 'offline': client.name == 'fake'}


@router.post('/api/projects/{project}/videos')
def create_video(project: str, req: VideoRequest):
    init()
    request_id = str(req.request_id)
    with _lock:
        try:
            existing = get(project, request_id)
        except HTTPException:
            existing = None
        if existing:
            return public(existing)
        client, frame, spec = prepare(project, req)
        from dataclasses import asdict
        item = {'id': request_id, 'project': project, 'kind': 'video', 'status': 'queued',
                'shot_id': req.shot_id, 'frame_id': req.frame_id, 'prompt': req.prompt,
                'model': req.model, 'backend': client.name, 'source_path': frame.image_path if req.reference_mode == 'shot' else '',
                'reference_mode': req.reference_mode, 'reference_ids': req.reference_ids if req.reference_mode == 'character' else [],
                'reference_paths': [next(r['path'] for r in session(project).image_references if r['id'] == rid) for rid in req.reference_ids] if req.reference_mode == 'character' else [],
                'spec': asdict(spec), 'duration_s': req.duration_s, 'created': time.time(), 'offline': client.name == 'fake'}
        # Reserve the request atomically; an ID owned by another film cannot overwrite it.
        with db() as conn:
            try:
                conn.execute('INSERT INTO film_items VALUES (?,?,?,?)', (request_id, project, 'video', json.dumps(item)))
            except Exception as exc:
                raise HTTPException(409, 'This request ID has already been used') from exc
    launch(project, request_id)
    return public(item)


def launch(project, item_id):
    with _lock:
        if item_id in _active:
            return
        _active.add(item_id)
    threading.Thread(target=work, args=(project, item_id), daemon=True).start()


def work(project, item_id):
    item = get(project, item_id)
    try:
        dest = folder(project)
        dest.mkdir(parents=True, exist_ok=True)
        output = dest / (item_id + '.mp4')
        if item['status'] in TERMINAL:
            return
        if item.get('backend') == 'fal-enhance':
            from .film_enhance import process
            if not process(item, output):
                return
        elif item['kind'] == 'export':
            export_movie(item, output)
        elif item.get('backend') == 'upload':
            run_ffmpeg(['-i', item['source_path'], '-map', '0:v:0', '-map', '0:a:0?', '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(output)])
        elif item.get('offline'):
            # A clearly labelled playable demo, never passed off as an AI video.
            spec = item['spec']
            w, h = (640, 360) if spec['aspect_ratio'] == '16:9' else (360, 640)
            try:
                from ..image import MockImageProvider
                if Path(item['source_path']).read_bytes() == MockImageProvider._BYTES:
                    raise ValueError('Legacy mock image')
                run_ffmpeg(['-loop', '1', '-i', item['source_path'], '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo',
                        '-t', str(spec['duration_s']), '-vf', f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1',
                        '-r', '24', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(output)])
            except ValueError:
                # Older mock frames were signature-only PNG fixtures. A demo
                # placeholder stays explicitly offline and cannot enter paid work.
                item['demo_placeholder'] = True
                run_ffmpeg(['-f', 'lavfi', '-i', f'color=c=0x263329:s={w}x{h}:r=24',
                            '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', str(spec['duration_s']),
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart', str(output)])

        else:
            from .app import _render_client, _asset_store
            client, error = _render_client()
            if error or client.name != item['backend']:
                item.update(status='waiting', error='Reconnect the original video provider in Settings, then resume.')
                put(item)
                return
            if not item.get('provider_id'):
                if item['status'] in ('submitting', 'uncertain'):
                    item.update(status='uncertain', error='Submission may have reached the provider. Check its job history before generating again.')
                    put(item)
                    return
                store = _asset_store()
                if not store.serves_public_urls and store.name != 's3':
                    raise ValueError('Connect media storage in Settings before generating a video')
                from ..image_studio import media_type
                spec = ShotSpec(**item['spec'])
                if item.get('reference_mode') == 'character':
                    spec.first_frame = None
                    spec.last_frame = None
                    spec.reference_images = []
                    for rid, path in zip(item['reference_ids'], item['reference_paths']):
                        mime = media_type(Path(path).read_bytes())
                        suffix = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp'}[mime]
                        asset = store.put_reference(path, f"films/{project}/characters/{rid}.{suffix}")
                        spec.reference_images.append(asset.url)
                else:
                    mime = media_type(Path(item['source_path']).read_bytes())
                    suffix = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp'}[mime]
                    asset = store.put_reference(item['source_path'], f"films/{project}/frames/{item['frame_id']}.{suffix}")
                    spec.reference_images = [asset.url]
                    spec.first_frame = asset.url
                # Persist non-secret input evidence, without expiring signed URLs.
                item['input_evidence'] = {'mode': item.get('reference_mode', 'shot'),
                                          'frame_images': 0 if item.get('reference_mode') == 'character' else 1,
                                          'input_references': len(spec.reference_images) if item.get('reference_mode') == 'character' else 0}
                item['status'] = 'submitting'
                put(item)
                job = client.submit(spec, model=item['model'])
                if not job.job_id:
                    detail = re.sub(r'https?://\S+', '[provider URL]', str(job.error or ''))
                    detail = re.sub(r'sk-or-v1-[A-Za-z0-9]+', '[redacted]', detail)[:500]
                    rejected = (job.raw or {}).get('http_status') in (400, 401, 402, 403, 404, 422, 429)
                    item.update(status='failed' if rejected else 'uncertain', error=('The provider rejected this request.' if rejected else 'The provider did not return a job ID. Check its history before retrying.') + (' Details: '+detail if detail else ''))
                    put(item)
                    return
                item.update(provider_id=job.job_id, status='running')
                put(item)
            deadline = time.monotonic() + 1800
            while time.monotonic() < deadline:
                job = client.poll(item['provider_id'])
                if job.status == JobStatus.SUCCEEDED:
                    item['cost'] = job.cost
                    saved = client.fetch(job, str(output))
                    if not saved:
                        item.update(status='waiting', error='Video completed but could not be downloaded. Resume to recover it.')
                        put(item)
                        return
                    break
                # The adapter encodes transport errors as FAILED without raw provider data.
                if job.status == JobStatus.FAILED and job.raw is None:
                    item.update(status='waiting', error='Could not confirm provider status. Resume checks this same job without billing again.')
                    put(item)
                    return
                if job.is_terminal:
                    item['status'] = 'failed'
                    raise ValueError(job.error or 'Video generation did not complete')
                time.sleep(3)
            else:
                item.update(status='waiting', error='Still processing. Resume to check the existing job.')
                put(item)
                return
        duration, _ = probe(output)
        item.update(status='complete', path=str(output), duration_s=duration, error=None)
        put(item)
    except Exception as exc:
        state = 'uncertain' if item.get('status') == 'submitting' else ('waiting' if item.get('provider_id') and item.get('status') != 'failed' else 'failed')
        item.update(status=state, error=str(exc))
        put(item)
    finally:
        with _lock:
            _active.discard(item_id)


@router.get('/api/projects/{project}/videos')
def list_videos(project: str):
    session(project)
    return {'items': [public(i) for i in items(project)]}


@router.post('/api/projects/{project}/videos/{item_id}/resume')
def resume(project: str, item_id: str):
    session(project)
    item = get(project, item_id)
    if item['status'] in ('complete', 'failed', 'uncertain'):
        raise HTTPException(409, 'This job cannot be resumed automatically')
    launch(project, item_id)
    return public(item)


@router.get('/api/projects/{project}/film-media/{item_id}')
def media(project: str, item_id: str, download: bool = False):
    session(project)
    item = get(project, item_id)
    if item['status'] != 'complete' or not item.get('path') or not Path(item['path']).is_file():
        raise HTTPException(404, 'Video is not ready')
    return FileResponse(item['path'], media_type='video/mp4', filename=(item_id+'.mp4') if download else None)


@router.post('/api/projects/{project}/shots/{shot_id}/upload-video')
async def upload(project: str, shot_id: str, request: Request):
    s = session(project)
    if not any(shot.id == shot_id for scene in s.project.scenes for shot in scene.shots):
        raise HTTPException(404, 'Shot not found')
    item_id = str(uuid.uuid4())
    dest = folder(project)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / (item_id+'.upload')
    total = 0
    try:
        with path.open('wb') as output:
            async for chunk in request.stream():
                total += len(chunk)
                if total > 250*1024*1024:
                    raise HTTPException(413, 'Choose a video smaller than 250 MB')
                output.write(chunk)
        try:
            duration, _ = await asyncio.to_thread(probe, path)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        init()
        item = {'id': item_id, 'project': project, 'kind': 'video', 'status': 'queued',
                'shot_id': shot_id, 'duration_s': duration, 'source_path': str(path), 'created': time.time(), 'model': 'Uploaded clip', 'backend': 'upload', 'offline': False}
        put(item)
        launch(project, item_id)
        return public(item)
    except Exception:
        path.unlink(missing_ok=True)
        raise


class CutClip(BaseModel):
    video_id: str
    start: float = Field(default=0, ge=0, allow_inf_nan=False)
    end: float = Field(gt=0, allow_inf_nan=False)
    mute: bool = False


class CutRequest(BaseModel):
    clips: list[CutClip] = Field(max_length=200)
    aspect_ratio: str = '16:9'
    fit: Literal['contain', 'cover'] = 'contain'
    resolution: Literal['720p', '1080p', '4K'] = '720p'


def validate_cut(project, cut):
    if cut.aspect_ratio not in ('16:9', '9:16', '1:1'):
        raise HTTPException(400, 'Choose landscape, portrait or square')
    for clip in cut.clips:
        item = get(project, clip.video_id)
        if item['kind'] != 'video' or item['status'] != 'complete':
            raise HTTPException(400, 'Choose a completed video')
        if clip.end <= clip.start or clip.end > item['duration_s'] + .05:
            raise HTTPException(400, 'Trim must be within the video duration')


@router.get('/api/projects/{project}/cut')
def read_cut(project: str):
    session(project)
    init()
    with db() as conn:
        row = conn.execute('SELECT payload FROM film_cuts WHERE project=?', (project,)).fetchone()
    return json.loads(row[0]) if row else {'clips': [], 'aspect_ratio': '16:9'}


@router.put('/api/projects/{project}/cut')
def save_cut(project: str, req: CutRequest):
    session(project)
    validate_cut(project, req)
    payload = req.model_dump(exclude_defaults=True)
    payload['clips'] = [c.model_dump() for c in req.clips]
    payload['aspect_ratio'] = req.aspect_ratio
    with db() as conn:
        conn.execute('INSERT INTO film_cuts VALUES (?,?) ON CONFLICT(project) DO UPDATE SET payload=excluded.payload', (project, json.dumps(payload)))
    return payload


@router.post('/api/projects/{project}/exports')
def create_export(project: str):
    cut = CutRequest(**read_cut(project))
    validate_cut(project, cut)
    if not cut.clips:
        raise HTTPException(400, 'Add at least one clip to the final edit')
    item = {'id': str(uuid.uuid4()), 'project': project, 'kind': 'export', 'status': 'queued', 'cut': cut.model_dump(), 'created': time.time()}
    put(item)
    launch(project, item['id'])
    return public(item)


def canvas_filter(w, h, fit='contain'):
    if fit == 'cover':
        return f'scale={w}:{h}:force_original_aspect_ratio=increase:force_divisible_by=2,crop={w}:{h},setsar=1'
    return f'scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1'


def export_movie(item, output):
    short = {'720p':720, '1080p':1080, '4K':2160}[item['cut'].get('resolution', '720p')]
    long = short * 16 // 9
    w, h = {'16:9': (long, short), '9:16': (short, long), '1:1': (short, short)}[item['cut']['aspect_ratio']]
    temp = output.parent / (item['id']+'_parts')
    temp.mkdir(exist_ok=True)
    try:
        parts = []
        for index, clip in enumerate(item['cut']['clips']):
            source = get(item['project'], clip['video_id'])
            _, has_audio = probe(source['path'])
            part = temp / f'{index}.mp4'
            length = clip['end'] - clip['start']
            args = ['-ss', str(clip['start']), '-i', source['path']]
            if clip['mute'] or not has_audio:
                args += ['-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo']
            args += ['-t', str(length), '-map', '0:v:0', '-map', '1:a:0' if clip['mute'] or not has_audio else '0:a:0',
                     '-vf', canvas_filter(w, h, item['cut'].get('fit', 'contain')),
                     '-r', '24', '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(part)]
            run_ffmpeg(args)
            parts.append(part)
        manifest = temp / 'clips.txt'
        manifest.write_text(''.join(f"file '{p.name}'\n" for p in parts))
        run_ffmpeg(['-f', 'concat', '-safe', '1', '-i', str(manifest), '-c:v', 'copy', '-af', 'aresample=async=1:first_pts=0', '-c:a', 'aac', '-movflags', '+faststart', str(output)])
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def recover():
    init()
    with db() as conn:
        pending = [json.loads(r[0]) for r in conn.execute('SELECT payload FROM film_items')]
    for item in pending:
        if item['status'] == 'submitting':
            item.update(status='uncertain', error='The app restarted during submission. Check provider history before generating again.')
            put(item)
        elif item['status'] in ('queued', 'running'):
            launch(item['project'], item['id'])

@router.get('/api/projects/{project}/video-drafts')
def video_drafts(project: str):
    session(project)
    init()
    with db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS film_video_drafts (project TEXT, shot TEXT, payload TEXT, PRIMARY KEY(project,shot))')
        return {r[0]: json.loads(r[1]) for r in conn.execute('SELECT shot,payload FROM film_video_drafts WHERE project=?', (project,))}


@router.put('/api/projects/{project}/video-drafts')
def save_video_draft(project: str, req: VideoRequest):
    video_drafts(project)
    s = session(project)
    if not any(shot.id == req.shot_id for scene in s.project.scenes for shot in scene.shots):
        raise HTTPException(404, 'Shot not found')
    payload = req.model_dump(mode='json')
    payload.pop('request_id')
    with db() as conn:
        conn.execute('INSERT INTO film_video_drafts VALUES (?,?,?) ON CONFLICT(project,shot) DO UPDATE SET payload=excluded.payload', (project, req.shot_id, json.dumps(payload)))
    return payload
