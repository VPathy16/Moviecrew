"""A `VideoBackend` built on any `RenderClient`.

Two backend abstractions grew up in this codebase for good reasons. Veo
renders synchronously through an SDK, so `VideoBackend` is a call that
returns a clip. Hosted generative APIs render asynchronously, so
`RenderClient` is submit/poll/fetch with a job in between. Both are right
about their own world.

What was missing is that only the first could be handed to
`MovieCrew.render()`. A whole film could be planned, boarded and previzzed
and then only Veo could shoot it, which made "backend-neutral" a claim about
the schema rather than about the pipeline. This class closes that: it wraps
a `RenderClient` and presents it as a `VideoBackend`, so the same render plan
runs on either.

Four things it does not fake:

*Chaining.* Veo continues a clip from its own final frame, which is what
makes a 21-shot continuous take one unbroken generation. A hosted model
usually has no such primitive. Rather than accept a chain and quietly render
the shots as unrelated clips, this backend asks its client what it can do:
if the model takes a video reference, the chain stays whole and each shot is
driven by its predecessor's output; if it does not, `segment()` breaks the
chain into single shots so no caller is told a take is continuous when it
is not.

*What a clip contains.* Even with a video reference, conditioning is not
extension: the model returns the new shot, not the take so far. So this
backend reports PER_SHOT output and every clip reaches the cut, where a
CUMULATIVE claim would have thrown all but the last one away.

*Duration and reference caps.* Both come from the client's own
`capabilities`, not from constants written here. A backend that grows from
10s to 30s clips needs no change in this file, and an unstated image-
reference cap sends every reference rather than silently dropping them all.

*Delivery.* A render is only a success if the clip actually arrived: a
generation that bills and then fails to download is reported as a failure,
with the cost and URL kept so it can be retried.
"""

from __future__ import annotations

import os
import time
from dataclasses import replace
from typing import Callable, Optional, Sequence

from .backend import ChainOutput, RenderResult, VideoBackend
from .render import JobStatus, RenderClient, ShotSpec
from .schema import ShotIntent

DEFAULT_RESOLUTION = "720p"


class GenerativeVideoBackend(VideoBackend[ShotSpec]):
    """Drives a `RenderClient` through the synchronous `VideoBackend` seam.

    One instance is meant to render one film: `produced_url_by_shot_id`
    records every successful render so a later shot in the same chain can be
    driven by its predecessor's output.
    """

    # Conditioning on a reference video is not extension. The model is given
    # the previous clip to match and returns only the new shot, so every
    # clip in a run is its own footage and all of them belong in the cut.
    # Reporting CUMULATIVE here would make assembly keep the last clip of a
    # chain and silently drop the rest.
    chain_output = ChainOutput.PER_SHOT

    def __init__(
        self,
        client: RenderClient,
        *,
        model: str,
        out_dir: str = "renders",
        resolution: str = DEFAULT_RESOLUTION,
        generate_audio: bool = False,
        poll_interval_s: float = 5.0,
        timeout_s: float = 900.0,
        publish: Optional[Callable[[str, str], str]] = None,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.client = client
        self.model = model
        self.out_dir = out_dir
        self.resolution = resolution
        self.generate_audio = generate_audio
        self.poll_interval_s = poll_interval_s
        self.timeout_s = timeout_s
        self._publish = publish
        self._sleep = sleep
        self._monotonic = monotonic
        self.produced_url_by_shot_id: dict[str, str] = {}

    def _reference_url(self, shot_id: str, video_url: str) -> str:
        """The URL a *later* shot should be given to continue from.

        A finished render's own URL is not necessarily one the provider can
        fetch. OpenRouter returns results under `unsigned_urls`, which sit
        behind the same API auth as everything else — `fetch()` attaches a
        Bearer token for exactly that reason — and a URL handed onward in
        `provider.options.video_urls` carries no such header.

        `publish` is the way out: give it a callable that puts the clip
        somewhere publicly readable (an `AssetStore`, a CDN) and returns
        that URL. Without one, the raw result URL is passed on and the
        provider may or may not be able to read it.
        """
        if self._publish is None:
            return video_url
        return self._publish(shot_id, video_url)

    @property
    def name(self) -> str:
        """Report the wrapped client's identity, not the wrapper's.

        A take recorded as rendered by "generative" would say nothing about
        what actually made it.
        """
        return self.client.name

    # -- what this backend can do ------------------------------------- #

    def _capabilities(self):
        return self.client.capabilities(self.model)

    def segment(self, chain: Sequence[str]) -> list[list[str]]:
        """Keep a take whole only if this model can actually carry it.

        With a video reference, each shot can be driven by the previous
        one's output, so the chain survives as a chain. Without one, there is
        no mechanism to continue anything and the honest answer is that every
        shot stands alone.
        """
        if not chain:
            return [[]]
        if self._capabilities().supports_video_reference:
            return [list(chain)]
        return [[shot_id] for shot_id in chain]

    def adapt(
        self, intent: ShotIntent, *, reference_images: Sequence[str] = ()
    ) -> ShotSpec:
        """Build a `ShotSpec`, clamped by what the client says it accepts."""
        capabilities = self._capabilities()
        spec = ShotSpec.from_intent(
            intent,
            reference_images=reference_images,
            resolution=self.resolution,
            generate_audio=self.generate_audio and capabilities.supports_audio,
        )
        spec.duration_s = capabilities.clamp_duration(intent.duration_s)
        spec.reference_images = capabilities.cap_image_references(
            spec.reference_images
        )
        return spec

    # -- execution ----------------------------------------------------- #

    def render(
        self,
        request: ShotSpec,
        *,
        extend_from: Optional[str] = None,
        in_multishot_chain: bool = False,
    ) -> RenderResult:
        spec = request
        warnings: list[str] = []

        if extend_from is not None:
            predecessor_url = self.produced_url_by_shot_id.get(extend_from)
            if predecessor_url is None:
                # The take is broken either way; say so rather than render a
                # shot that silently is not a continuation of anything.
                return self._failure(
                    spec,
                    f"no rendered output for predecessor shot {extend_from!r} "
                    "(it may have failed); cannot continue the take.",
                    extend_from=extend_from,
                    in_multishot_chain=in_multishot_chain,
                )
            spec = replace(spec, reference_video=predecessor_url)
            if self._publish is None:
                warnings.append(
                    "continuing from the predecessor's own result URL, which "
                    "may require API auth the provider will not send. Pass "
                    "publish= to host the clip somewhere publicly readable."
                )

        raw = {
            "model": self.model,
            "prompt": spec.prompt,
            "duration_s": spec.duration_s,
            "aspect_ratio": spec.aspect_ratio,
            "resolution": spec.resolution,
            "reference_image_count": len(spec.reference_images),
            "reference_video": spec.reference_video,
            "extend_from": extend_from,
            "in_multishot_chain": in_multishot_chain,
            "warnings": warnings,
        }

        try:
            job = self.client.submit(spec, model=self.model)
            raw["job_id"] = job.job_id

            deadline = self._monotonic() + self.timeout_s
            while not job.is_terminal:
                if self._monotonic() > deadline:
                    raise TimeoutError(
                        f"render for shot {spec.shot_id} did not finish within "
                        f"{self.timeout_s}s"
                    )
                self._sleep(self.poll_interval_s)
                job = self.client.poll(job.job_id)

            raw["cost"] = job.cost
            raw["status"] = job.status.value

            if job.status is not JobStatus.SUCCEEDED:
                return self._failure(
                    spec,
                    job.error or f"render {job.status.value}",
                    extend_from=extend_from,
                    in_multishot_chain=in_multishot_chain,
                    raw=raw,
                )

            if job.video_url:
                raw["video_url"] = job.video_url
                self.produced_url_by_shot_id[spec.shot_id] = self._reference_url(
                    spec.shot_id, job.video_url
                )

            os.makedirs(self.out_dir, exist_ok=True)
            out_path = self.client.fetch(
                job, os.path.join(self.out_dir, f"{spec.shot_id}.mp4")
            )

            if out_path is None:
                # The provider generated it and billed for it; we just could
                # not retrieve it. `fetch` is documented to return None, and
                # calling that a success would put a shot with no clip into
                # the cut. The URL and cost stay in `raw` so the spend is
                # recorded and the download can be retried.
                return self._failure(
                    spec,
                    "generation succeeded but the clip could not be downloaded "
                    f"from {job.video_url!r}; the render was still billed.",
                    extend_from=extend_from,
                    in_multishot_chain=in_multishot_chain,
                    raw=raw,
                )

            return RenderResult(
                shot_id=spec.shot_id,
                status="succeeded",
                backend=self.name,
                uri=out_path,
                raw=raw,
            )
        except Exception as exc:
            return self._failure(
                spec,
                str(exc),
                extend_from=extend_from,
                in_multishot_chain=in_multishot_chain,
                raw=raw,
            )

    def _failure(
        self,
        spec: ShotSpec,
        error: str,
        *,
        extend_from: Optional[str],
        in_multishot_chain: bool,
        raw: Optional[dict] = None,
    ) -> RenderResult:
        raw = dict(raw or {})
        raw.setdefault("model", self.model)
        raw.setdefault("extend_from", extend_from)
        raw.setdefault("in_multishot_chain", in_multishot_chain)
        raw["error"] = error
        return RenderResult(
            shot_id=spec.shot_id,
            status="failed",
            backend=self.name,
            uri=None,
            raw=raw,
        )
