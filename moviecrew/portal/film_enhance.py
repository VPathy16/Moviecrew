"""Non-destructive canvas expansion and Topaz versions using fal's durable queue.

Contracts: fal.ai/models/topaz/upscale/video/precision/api and
fal.ai/models/fal-ai/luma-dream-machine/ray-2-flash/reframe/api.
"""
import json
import os
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from . import film_workflow as f

router = APIRouter()
ENDPOINTS = {'upscale': 'topaz/upscale/video/precision',
             'expand': 'fal-ai/luma-dream-machine/ray-2-flash/reframe'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Unexpected processing service redirect")


def queue_request(url, body=None):
    # Credentials must never follow a provider-supplied URL to another host.
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.netloc != 'queue.fal.run':
        raise ValueError('Unexpected processing service address')
    req = Request(url, data=json.dumps(body).encode() if body is not None else None,
                  headers={'Authorization': 'Key ' + os.environ.get('FAL_KEY', ''),
                           'Content-Type': 'application/json'})
    try:
        with build_opener(NoRedirect).open(req, timeout=90) as response:
            return json.load(response)
    except HTTPError as exc:
        # Do not include response bodies which can echo signed asset URLs.
        raise ValueError(f'Processing service returned HTTP {exc.code}') from None


def download(url, path):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not ((parsed.hostname or '').endswith(('.fal.media', '.fal.ai')) or parsed.hostname == 'fal.media'):
        raise ValueError('Unexpected processing download address')
    with urlopen(url, timeout=180) as response, path.open('wb') as out:
        total = 0
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > 2 * 1024**3:
                raise ValueError('Processed video exceeds the 2 GB download limit')
            out.write(chunk)


class EnhanceRequest(BaseModel):
    clip_id: str | None = Field(default=None, max_length=100)
    request_id: uuid.UUID
    video_id: str
    operation: Literal['expand', 'upscale']
    start: float = Field(default=0, ge=0, allow_inf_nan=False)
    end: float = Field(gt=0, allow_inf_nan=False)
    aspect_ratio: Literal['16:9', '9:16', '1:1'] = '16:9'
    factor: Literal[1.5, 2, 2.5, 3] = 2
    creativity: Literal[0, 1] = 0
    prompt: str = Field(default='Extend the surrounding scene with matching lighting, perspective and motion.', max_length=4000)
    preserve_center: bool = True


@router.get('/api/projects/{project}/enhancement-options')
def options(project: str):
    f.session(project)
    from .app import _asset_store
    store = _asset_store()
    return {'configured': bool(os.environ.get('FAL_KEY')),
            'storage_ready': store.serves_public_urls or store.name == 's3',
            'upscale_configured': bool(os.environ.get('OPENROUTER_API_KEY')),
            'upscale_model': 'FLUX Video Upscale', 'expand_model': 'Luma Ray 2 Flash',
            'expand_max_seconds': 30, 'upscale_max_seconds': 300}


@router.post('/api/projects/{project}/enhancements')
def create(project: str, req: EnhanceRequest):
    f.session(project)
    f.init()
    with f._lock:
        try:
            previous = f.get(project, str(req.request_id))
        except HTTPException:
            previous = None
        if previous:
            return f.public(previous)
        source = f.get(project, req.video_id)
        if source.get('offline'):
            raise HTTPException(400, 'Choose a real video; offline previews cannot use paid enhancement')
        if source['status'] != 'complete' or not source.get('path') or not Path(source['path']).is_file():
            raise HTTPException(400, 'Choose a completed video')
        if req.end <= req.start or req.end > source['duration_s'] + .05:
            raise HTTPException(400, 'Trim must be within the source video')
        limit = 30 if req.operation == 'expand' else 300
        if req.end - req.start > limit:
            raise HTTPException(400, f'Trim this selection to {limit} seconds or less')
        status = options(project)
        if not status['upscale_configured' if req.operation == 'upscale' else 'configured']:
            raise HTTPException(400, 'Connect OpenRouter in Settings for upscaling' if req.operation == 'upscale' else 'Connect fal in Settings for AI expand')
        if not status['storage_ready']:
            raise HTTPException(400, 'Connect media storage in Settings first')
        data = req.model_dump(mode='json')
        item = dict(id=data.pop('request_id'), project=project, kind='video', status='queued',
                    backend='openrouter-enhance' if req.operation == 'upscale' else 'fal-enhance', operation=req.operation, enhancement=data,
                    shot_id=source.get('shot_id', ''), source_id=source['id'],
                    model='black-forest-labs/flux-video-upscale' if req.operation == 'upscale' else 'Luma Ray 2 Flash · expand',
                    duration_s=req.end-req.start, created=time.time(), offline=False)
        with f.db() as conn:
            try:
                conn.execute('INSERT INTO film_items VALUES (?,?,?,?)', (item['id'], project, 'video', json.dumps(item)))
            except Exception:
                raise HTTPException(409, 'This request ID has already been used') from None
    f.launch(project, item['id'])
    return f.public(item)


def process(item, output):
    """Resume known jobs; an ambiguous submit is never automatically repeated."""
    is_flux = item.get('backend') == 'openrouter-enhance'
    if not os.environ.get('OPENROUTER_API_KEY' if is_flux else 'FAL_KEY'):
        item.update(status='waiting', error='Reconnect '+('OpenRouter' if is_flux else 'fal')+' in Settings, then resume.')
        f.put(item)
        return False
    spec = item['enhancement']
    source = f.get(item['project'], item['source_id'])
    trimmed = output.with_suffix('.source.mp4')
    if not trimmed.exists():
        f.run_ffmpeg(['-ss', str(spec['start']), '-i', source['path'], '-t', str(spec['end']-spec['start']),
                      '-map', '0:v:0', '-map', '0:a:0?', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
                      '-c:a', 'aac', '-movflags', '+faststart', str(trimmed)])
    raw = output.with_suffix('.processed.mp4')
    if is_flux:
        if not process_flux(item, trimmed, raw):
            return False
    else:
        if not item.get('provider_id'):
            if item['status'] in ('submitting', 'uncertain'):
                item.update(status='uncertain', error='Check fal history before submitting again.')
                f.put(item)
                return False
            if spec['operation'] == 'expand' and trimmed.stat().st_size > 100 * 1024**2:
                raise ValueError('Trim the selection further: AI expand accepts videos up to 100 MB')
            from .app import _asset_store
            asset = _asset_store().put_reference(str(trimmed), f"films/{item['project']}/enhance/{item['id']}.mp4")
            body = {'video_url': asset.url}
            if spec['operation'] == 'expand':
                body.update(aspect_ratio=spec['aspect_ratio'], prompt=spec['prompt'])
            else:
                body.update(model='Proteus', upscale_factor=spec['factor'], H264_output=True)
            item['status'] = 'submitting'
            f.put(item)
            result = queue_request('https://queue.fal.run/' + ENDPOINTS[spec['operation']], body)
            # Save the ID before validating convenience URLs: a billed job stays recoverable.
            item.update(provider_id=result['request_id'], fal_status_url=result['status_url'],
                        fal_response_url=result['response_url'], status='running')
            f.put(item)
        deadline = time.monotonic() + 1800
        while time.monotonic() < deadline:
            status = queue_request(item['fal_status_url'])
            if status['status'] == 'COMPLETED':
                break
            if status['status'] in ('FAILED', 'CANCELLED'):
                item['status'] = 'failed'
                raise ValueError('Processing did not complete. Your original video is unchanged.')
            time.sleep(4)
        else:
            item.update(status='waiting', error='Still processing. Resume to check this same job.')
            f.put(item)
            return False
        result = queue_request(item['fal_response_url'])
        if not result.get('video', {}).get('url'):
            item['status'] = 'failed'
            raise ValueError('The provider returned no processed video')
        raw = output.with_suffix('.processed.mp4')
        download(result['video']['url'], raw)
    actual, _ = f.probe(raw)
    expected, has_audio = f.probe(trimmed)
    if abs(actual - expected) > .25:
        raise ValueError('Processed duration differs from the source. Original edit retained.')
    args = ['-i', str(raw), '-i', str(trimmed)]
    if spec['operation'] == 'expand' and spec['preserve_center']:
        w, h = {'16:9':(1280,720), '9:16':(720,1280), '1:1':(1024,1024)}[spec['aspect_ratio']]
        # Reapply the source rectangle. The generated surroundings may need visual review.
        filters = (f'[0:v]scale={w}:{h},setsar=1[bg];'
                   f'[1:v]scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2,setsar=1[fg];'
                   '[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1[v]')
        args += ['-filter_complex', filters, '-map', '[v]', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p']
    else:
        args += ['-map', '0:v:0', '-c:v', 'copy']
    if has_audio:
        args += ['-map', '1:a:0', '-c:a', 'aac']
    args += ['-t', str(expected), '-movflags', '+faststart', str(output)]
    f.run_ffmpeg(args)
    return True


def process_flux(item, trimmed, raw):
    """Submit once, persist the remote ID, and resume polling without rebilling."""
    from ..render_openrouter import OpenRouterRenderClient
    from ..render import JobStatus
    from .app import _asset_store
    client = OpenRouterRenderClient(model=item['model'])
    if not item.get('provider_id'):
        if item['status'] in ('submitting', 'uncertain'):
            item.update(status='uncertain', error='Check OpenRouter history before submitting again.')
            f.put(item)
            return False
        asset = _asset_store().put_reference(str(trimmed), f"films/{item['project']}/enhance/{item['id']}.mp4")
        spec = item['enhancement']
        body = {'model': item['model'], 'upscale_factor': spec['factor'],
                'creativity': spec.get('creativity', 0),
                'input_references': [{'type': 'video_url', 'video_url': {'url': asset.url}}]}
        item['status'] = 'submitting'
        f.put(item)
        result = client._call('POST', '/videos', body)
        if not result.get('id'):
            raise ValueError('No job ID returned. Check OpenRouter history before retrying.')
        item.update(provider_id=result['id'], status='running')
        f.put(item)
    deadline = time.monotonic() + 1800
    while time.monotonic() < deadline:
        job = client.poll(item['provider_id'])
        if job.status == JobStatus.SUCCEEDED:
            # Download through the authenticated, fixed OpenRouter content endpoint.
            from urllib.parse import quote
            job.video_url = client.api_root + '/videos/' + quote(item['provider_id'], safe='') + '/content'
            if not client.fetch(job, str(raw)):
                raise ValueError('Could not download the upscaled video; resume to retry.')
            item['cost'] = job.cost
            return True
        if job.status == JobStatus.FAILED:
            if job.raw is not None:
                item['status'] = 'failed'
            raise ValueError('OpenRouter upscaling failed. Your original is unchanged.')
        time.sleep(4)
    item.update(status='waiting', error='Still processing. Resume to check the same job.')
    f.put(item)
    return False


class FrameRequest(BaseModel):
    shot_id: str
    video_id: str | None = None
    time_s: float = Field(default=0, ge=0, allow_inf_nan=False)
    reference_id: str | None = None
    version_id: str | None = None


@router.post('/api/projects/{project}/editor-frame')
def editor_frame(project: str, req: FrameRequest):
    """Copy a library image or a trimmed clip boundary into an owned starting frame."""
    from ..studio import StoryboardFrame
    from .. import projects
    s = f.session(project)
    if not any(shot.id == req.shot_id for scene in s.project.scenes for shot in scene.shots):
        raise HTTPException(404, 'Shot not found')
    if sum(bool(v) for v in (req.video_id, req.reference_id, req.version_id)) != 1:
        raise HTTPException(400, 'Choose one image or video frame')
    frame = StoryboardFrame(shot_id=req.shot_id, prompt_used='', status='ok', model='Editor reference')
    dest = f.folder(project)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / (frame.version_id + '.png')
    if req.video_id:
        source = f.get(project, req.video_id)
        if source.get('offline'):
            raise HTTPException(400, 'Choose a real video as the starting reference')
        if source['status'] != 'complete' or req.time_s >= source['duration_s']:
            raise HTTPException(400, 'Choose a frame within a completed video')
        f.run_ffmpeg(['-ss', str(req.time_s), '-i', source['path'], '-frames:v', '1', str(path)])
    else:
        if req.reference_id:
            source = next((r.get('path') for r in s.image_references if r['id'] == req.reference_id), None)
        else:
            version = next((v for v in s.versions if v.version_id == req.version_id and v.status == 'ok'), None)
            if version and version.model in ('offline', 'MockImageProvider'):
                raise HTTPException(400, 'Choose a generated or uploaded image; this is an offline preview')
            source = version.image_path if version else None
        if not source or not Path(source).is_file():
            raise HTTPException(404, 'Image not found in this film')
        # Decode to PNG rather than just changing an uploaded JPEG's extension.
        f.run_ffmpeg(['-i', source, '-frames:v', '1', str(path)])
    if not path.is_file():
        raise HTTPException(400, 'Could not extract this frame')
    frame.image_path = str(path)
    with s.plan_lock:
        s.versions.append(frame)
        projects.save(s)
    return {'frame_id':frame.version_id, 'shot_id':req.shot_id}


class ExtensionBoundary(BaseModel):
    clip_id: str | None = Field(default=None, max_length=100)
    video_id: str
    start: float = Field(default=0, ge=0, allow_inf_nan=False)
    end: float = Field(gt=0, allow_inf_nan=False)
    direction: Literal['before', 'after']


@router.post('/api/projects/{project}/extension-boundary')
def extension_boundary(project: str, req: ExtensionBoundary):
    """Prepare a boundary reference without submitting a paid generation."""
    from .. import projects
    s = f.session(project)
    source = f.get(project, req.video_id)
    if source['status'] != 'complete' or req.end <= req.start or req.end > source['duration_s']:
        raise HTTPException(400, 'Choose a valid trimmed range in a completed clip')
    shot_id = source.get('shot_id') or next((shot.id for scene in s.project.scenes for shot in scene.shots), None)
    if not shot_id:
        raise HTTPException(400, 'This film needs a shot before generating an extension')
    # Decode frame timestamps; duration - 1/24 can select the wrong frame at other FPS.
    if req.direction == 'after':
        import subprocess
        result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                                 '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json',
                                 source['path']], capture_output=True, text=True, check=True, timeout=60)
        times = [float(row['best_effort_timestamp_time']) for row in json.loads(result.stdout).get('frames', [])
                 if 'best_effort_timestamp_time' in row]
        times = [t for t in times if req.start <= t < req.end]
        if not times:
            raise HTTPException(400, 'There is no video frame inside this selection')
        at = max(times)
    else:
        at = req.start
    created = editor_frame(project, FrameRequest(shot_id=shot_id, video_id=req.video_id, time_s=at))
    with s.plan_lock:
        frame = next(v for v in s.versions if v.version_id == created['frame_id'])
        frame.settings['extension'] = req.model_dump(exclude_none=True)
        frame.settings['boundary_time_s'] = at
        projects.save(s)
    return {**created, 'anchor_position':'last_frame' if req.direction == 'before' else 'first_frame',
            'image_url':f"/api/projects/{project}/versions/{created['frame_id']}/image"}
