"""Capability-validated Image API adapter; legacy chat image provider stays intact."""
import base64
import time
import urllib.parse
from pathlib import Path

from .image import ImageProvider
from .image_openrouter import API_ROOT, OpenRouterImageProvider, ImageError, _urllib_transport

_CACHE = {}
FIELDS = ('aspect_ratio', 'quality', 'resolution', 'background')


def discover(path):
    now = time.monotonic()
    if path not in _CACHE or now - _CACHE[path][0] > 300:
        _CACHE[path] = (now, _urllib_transport('GET', API_ROOT + path, {}, None))
    return _CACHE[path][1]


def models():
    return discover('/images/models').get('data', [])


def endpoints(model):
    return discover('/images/models/' + urllib.parse.quote(model, safe='/') + '/endpoints').get('endpoints', [])


def choose_endpoint(records, settings, has_references):
    for endpoint in records:
        params = endpoint.get('supported_parameters', {})
        if has_references and 'input_references' not in params:
            continue
        if any(key not in params or (params[key].get('type') == 'enum' and value not in params[key].get('values', [])) for key, value in settings.items()):
            continue
        if endpoint.get('provider_tag'):
            return endpoint
    raise ValueError('No provider supports this combination of settings and reference images. Choose another model or reset the options.')


def media_type(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'image/webp'
    raise ValueError('Use a PNG, JPEG or WebP image')


class StudioImageProvider(OpenRouterImageProvider):
    def __init__(self, *, options, references, endpoint, **kwargs):
        super().__init__(**kwargs)
        self.options = options
        self.references = references
        self.endpoint = endpoint
        self.last_cost = None

    def build_request(self, prompt):
        result = {'model':self.model, 'prompt':prompt, **self.options,
                  'provider':{'only':[self.endpoint['provider_tag']], 'allow_fallbacks':False}}
        if self.references:
            result['input_references'] = []
            for ref in self.references:
                raw = Path(ref['path']).read_bytes()
                uri = 'data:' + media_type(raw) + ';base64,' + base64.b64encode(raw).decode()
                result['input_references'].append({'type':'image_url', 'image_url':{'url':uri}})
        return result

    def generate(self, prompt, shot_id):
        self.last_cost = None
        payload = self._transport('POST', API_ROOT + '/images', self._headers(), self.build_request(prompt))
        if payload.get('error'):
            raise ImageError('Image provider rejected the request')
        try:
            raw = base64.b64decode(payload['data'][0]['b64_json'], validate=True)
            media_type(raw)
        except (KeyError, IndexError, ValueError) as exc:
            raise ImageError('Provider did not return a supported raster image') from exc
        self.last_cost = payload.get('usage', {}).get('cost')
        return raw


class OfflineStudioProvider(ImageProvider):
    model = 'offline'

    def __init__(self, options, references):
        self.options, self.references = options, references

    def generate(self, prompt, shot_id):
        from .image import MockImageProvider
        return MockImageProvider().generate(prompt, shot_id)


def estimate_cost(endpoint, reference_count, variations):
    """Only estimate unambiguous flat per-image pricing; never invent token costs."""
    lines = endpoint.get('pricing', [])
    if not lines:
        return None
    total = 0.0
    has_output = False
    for line in lines:
        if line.get('variant') or line.get('unit') != 'image':
            return None
        try:
            cost = float(line['cost_usd'])
        except (KeyError, ValueError, TypeError):
            return None
        if cost < 0:
            return None
        if line.get('billable') == 'output_image':
            total += cost
            has_output = True
        elif line.get('billable') in ('input_image', 'input_reference'):
            total += cost * reference_count
        else:
            return None
    return round(total * variations, 6) if has_output else None
