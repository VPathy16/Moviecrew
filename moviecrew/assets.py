"""Where a project's media lives, and how a backend reaches it.

A generative backend fetches its inputs over the internet: the previz take
that drives a shot, the stills that fix a character's identity. It cannot
read a path on your laptop, and it will not follow a loopback address. So
every asset a render depends on needs somewhere real to live and a URL that
resolves from outside this process — which is the requirement the pipeline
has been meeting with a tunnel and a hope.

`AssetStore` is that seam. `LocalAssetStore` keeps files on disk and hands
back URLs the portal serves, which is enough for previewing and for a
tunnelled demo. `S3AssetStore` puts them in any S3-compatible bucket —
Cloudflare R2, S3, B2, MinIO — and hands back durable public URLs.

Two things this module is deliberate about.

**Content types are set explicitly, never guessed by the server.** A file
served as `application/octet-stream` is silently ignored by at least one
video backend: the render succeeds, bills in full, and never looks at the
reference. That failure cost four paid renders before anyone noticed, and it
is invisible unless you check the header. So `put()` resolves a type up
front and refuses to store a video or image it cannot type.

**Signing is stdlib.** AWS SigV4 is a few dozen lines of `hmac` and
`hashlib`, and writing it out keeps MovieCrew's core free of third-party
imports — which is what lets the package drop into Blender's bundled Python
with nothing to install.
"""

from __future__ import annotations

import hashlib
import hmac
import mimetypes
import os
import shutil
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Types a render backend will actually accept as a reference. Anything else
# is refused rather than uploaded as octet-stream and silently dropped later.
MEDIA_TYPES: dict[str, str] = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".json": "application/json",
}

_LOCAL_HOSTS = ("localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1")


class AssetError(RuntimeError):
    """An asset that could not be stored, fetched or addressed."""


def content_type_for(path: str) -> str:
    """The MIME type to store `path` under. Raises rather than guessing.

    `mimetypes` is consulted second, not first: its answers vary with the
    host's config, and an asset that types correctly on one machine and as
    octet-stream on another is precisely the bug this guards against.
    """
    suffix = Path(path).suffix.lower()
    if suffix in MEDIA_TYPES:
        return MEDIA_TYPES[suffix]
    guessed, _ = mimetypes.guess_type(path)
    if guessed:
        return guessed
    raise AssetError(
        f"refusing to store {path!r}: no known content type for {suffix!r}. "
        f"A backend that receives application/octet-stream ignores the file "
        f"and bills for the render anyway."
    )


def is_reachable(url: str) -> bool:
    """Whether a provider could plausibly fetch this URL.

    A loopback address resolves to the *provider's* machine, not ours, so a
    render pointed at one fails confusingly late — after the wait, and
    sometimes after the charge.
    """
    if not url:
        return False
    lowered = url.lower()
    if not lowered.startswith(("http://", "https://")):
        return False
    return not any(host in lowered for host in _LOCAL_HOSTS)


@dataclass(frozen=True)
class Asset:
    """One stored file and how to reach it."""

    key: str
    content_type: str
    size_bytes: int
    url: Optional[str] = None

    @property
    def is_reachable(self) -> bool:
        return is_reachable(self.url or "")


class AssetStore(ABC):
    """Somewhere a project's media lives, addressable from outside."""

    name: str = ""

    #: True when `url()` returns something a third party can fetch.
    serves_public_urls: bool = False

    @abstractmethod
    def put(self, local_path: str, key: str, *, content_type: Optional[str] = None) -> Asset:
        """Store a local file under `key`. Returns the stored asset."""
        raise NotImplementedError

    @abstractmethod
    def url(self, key: str) -> Optional[str]:
        """The URL for `key`, or None when this store cannot address it."""
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str, local_path: str) -> Optional[str]:
        """Download `key` to `local_path`. Returns the path, or None."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove `key`. Returns whether anything was removed."""
        raise NotImplementedError

    def put_reachable(self, local_path: str, key: str) -> Asset:
        """`put`, refusing to return an address a backend cannot use.

        Callers that are about to spend money on a render should use this:
        it fails here, before the request, rather than after the provider
        has tried and failed to fetch the file.
        """
        asset = self.put(local_path, key)
        if not asset.is_reachable:
            raise AssetError(
                f"{self.name} stored {key} but cannot give a publicly reachable "
                f"URL for it (got {asset.url!r}). A render backend fetches its "
                f"references over the internet."
            )
        return asset


class LocalAssetStore(AssetStore):
    """Files on disk, addressed through the portal.

    The default, and enough for everything except a real render: the portal
    serves the bytes, so a browser can play them. Whether a *provider* can
    reach them depends on `base_url` pointing somewhere outside this machine
    — a tunnel, a LAN address, a deployment.
    """

    name = "local"

    def __init__(self, root: str, *, base_url: str = "") -> None:
        self.root = Path(root).expanduser()
        self.base_url = base_url.rstrip("/")

    @property
    def serves_public_urls(self) -> bool:
        return is_reachable(self.base_url)

    def _path(self, key: str) -> Path:
        """Resolve `key` under the root, refusing anything that escapes it."""
        candidate = (self.root / key).resolve()
        root = self.root.resolve()
        if not candidate.is_relative_to(root):
            raise AssetError(f"key {key!r} resolves outside the asset root")
        return candidate

    def put(self, local_path: str, key: str, *, content_type: Optional[str] = None) -> Asset:
        ctype = content_type or content_type_for(local_path)
        destination = self._path(key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if Path(local_path).resolve() != destination:
            shutil.copyfile(local_path, destination)
        return Asset(
            key=key,
            content_type=ctype,
            size_bytes=destination.stat().st_size,
            url=self.url(key),
        )

    def url(self, key: str) -> Optional[str]:
        if not self.base_url:
            return None
        return f"{self.base_url}/{urllib.parse.quote(key)}"

    def get(self, key: str, local_path: str) -> Optional[str]:
        source = self._path(key)
        if not source.is_file():
            return None
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        shutil.copyfile(source, local_path)
        return local_path

    def delete(self, key: str) -> bool:
        path = self._path(key)
        if not path.is_file():
            return False
        path.unlink()
        return True


# ---------------------------------------------------------------------- #
# S3-compatible                                                           #
# ---------------------------------------------------------------------- #


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def signing_key(secret: str, date_stamp: str, region: str, service: str) -> bytes:
    """The SigV4 derived key: date -> region -> service -> 'aws4_request'."""
    k = _sign(f"AWS4{secret}".encode("utf-8"), date_stamp)
    k = _sign(k, region)
    k = _sign(k, service)
    return _sign(k, "aws4_request")


def sigv4_headers(
    *,
    method: str,
    url: str,
    payload: bytes,
    access_key: str,
    secret_key: str,
    region: str,
    service: str = "s3",
    now: Optional[datetime] = None,
    extra_headers: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    """Headers that authenticate one S3 request. Pure, so it is testable.

    Kept separate from the transport for the same reason the rest of this
    package separates them: signing is exacting, easy to get subtly wrong,
    and the failure mode is a 403 that tells you nothing useful.
    """
    now = now or datetime.now(timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    parts = urllib.parse.urlsplit(url)
    host = parts.netloc
    canonical_uri = urllib.parse.quote(parts.path or "/", safe="/~")
    canonical_query = parts.query

    payload_hash = _sha256(payload)
    headers = {
        "host": host,
        "x-amz-content-sha256": payload_hash,
        "x-amz-date": amz_date,
    }
    headers.update({k.lower(): v for k, v in (extra_headers or {}).items()})

    signed_headers = ";".join(sorted(headers))
    canonical_headers = "".join(f"{k}:{headers[k]}\n" for k in sorted(headers))
    canonical_request = "\n".join(
        [method, canonical_uri, canonical_query, canonical_headers, signed_headers, payload_hash]
    )

    scope = f"{date_stamp}/{region}/{service}/aws4_request"
    to_sign = "\n".join(
        ["AWS4-HMAC-SHA256", amz_date, scope, _sha256(canonical_request.encode("utf-8"))]
    )
    signature = hmac.new(
        signing_key(secret_key, date_stamp, region, service),
        to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    out = {k: v for k, v in headers.items()}
    out["Authorization"] = (
        f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    return out


class S3AssetStore(AssetStore):
    """Any S3-compatible bucket: Cloudflare R2, AWS S3, B2, MinIO.

    `public_base` is what makes a stored object addressable to a render
    backend — an R2 custom domain or `r2.dev` address, an S3 website
    endpoint, a CDN in front of either. Without it the store still works for
    put/get, but `url()` returns None and `put_reachable` refuses, which is
    the correct answer: a private bucket cannot serve a reference.
    """

    name = "s3"

    def __init__(
        self,
        *,
        bucket: str,
        endpoint: str,
        access_key: str,
        secret_key: str,
        region: str = "auto",
        public_base: str = "",
        transport=None,
    ) -> None:
        self.bucket = bucket
        self.endpoint = endpoint.rstrip("/")
        self.region = region
        self.public_base = public_base.rstrip("/")
        self._access_key = access_key
        self._secret_key = secret_key
        self._transport = transport or _urlopen_transport

    @property
    def serves_public_urls(self) -> bool:
        return is_reachable(self.public_base)

    def _object_url(self, key: str) -> str:
        return f"{self.endpoint}/{self.bucket}/{urllib.parse.quote(key, safe='/~')}"

    def url(self, key: str) -> Optional[str]:
        if not self.public_base:
            return None
        return f"{self.public_base}/{urllib.parse.quote(key, safe='/~')}"

    def put(self, local_path: str, key: str, *, content_type: Optional[str] = None) -> Asset:
        ctype = content_type or content_type_for(local_path)
        payload = Path(local_path).read_bytes()
        url = self._object_url(key)
        headers = sigv4_headers(
            method="PUT",
            url=url,
            payload=payload,
            access_key=self._access_key,
            secret_key=self._secret_key,
            region=self.region,
            extra_headers={"content-type": ctype},
        )
        self._transport("PUT", url, headers, payload)
        return Asset(key=key, content_type=ctype, size_bytes=len(payload), url=self.url(key))

    def get(self, key: str, local_path: str) -> Optional[str]:
        url = self._object_url(key)
        headers = sigv4_headers(
            method="GET",
            url=url,
            payload=b"",
            access_key=self._access_key,
            secret_key=self._secret_key,
            region=self.region,
        )
        try:
            data = self._transport("GET", url, headers, None)
        except AssetError:
            return None
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        Path(local_path).write_bytes(data or b"")
        return local_path

    def delete(self, key: str) -> bool:
        url = self._object_url(key)
        headers = sigv4_headers(
            method="DELETE",
            url=url,
            payload=b"",
            access_key=self._access_key,
            secret_key=self._secret_key,
            region=self.region,
        )
        try:
            self._transport("DELETE", url, headers, None)
        except AssetError:
            return False
        return True


def _urlopen_transport(method: str, url: str, headers: dict[str, str], payload: Optional[bytes]):
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise AssetError(f"{method} {url} failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise AssetError(f"{method} {url} unreachable: {exc.reason}") from exc


# ---------------------------------------------------------------------- #
# Selection                                                               #
# ---------------------------------------------------------------------- #

BUCKET_ENV = "MOVIECREW_S3_BUCKET"
ENDPOINT_ENV = "MOVIECREW_S3_ENDPOINT"
ACCESS_KEY_ENV = "MOVIECREW_S3_ACCESS_KEY"
SECRET_KEY_ENV = "MOVIECREW_S3_SECRET_KEY"
REGION_ENV = "MOVIECREW_S3_REGION"
PUBLIC_BASE_ENV = "MOVIECREW_ASSET_BASE_URL"


def build_asset_store(*, local_root: str, local_base_url: str = "") -> AssetStore:
    """The configured store: S3-compatible when credentials are set, else local.

    Same shape as the render and LLM backends — a bucket is opted into by
    setting credentials, and the offline path is the default so nothing
    requires an account to run.
    """
    bucket = os.environ.get(BUCKET_ENV, "")
    endpoint = os.environ.get(ENDPOINT_ENV, "")
    access_key = os.environ.get(ACCESS_KEY_ENV, "")
    secret_key = os.environ.get(SECRET_KEY_ENV, "")

    if bucket and endpoint and access_key and secret_key:
        return S3AssetStore(
            bucket=bucket,
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            region=os.environ.get(REGION_ENV, "auto"),
            public_base=os.environ.get(PUBLIC_BASE_ENV, ""),
        )
    return LocalAssetStore(local_root, base_url=local_base_url)
