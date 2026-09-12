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
the shots as unrelated clips, this backend asks its client what it can do
and keeps a take whole only when two separate things are both true:

  1. the model accepts a video reference at all, and
  2. this backend can put the predecessor's clip somewhere the next
     generation can actually read it.

They are different capabilities and only the first one is about the model.
A provider can take a video reference and still return its own results
behind auth that nothing re-attaches when the URL is passed onward, or
behind a URL that expires — so "it accepts video input" is not evidence
that the chain will hold. Delivery comes either from a client that
declares its own results are reusable
(`RenderCapabilities.produces_reusable_video_reference`), or from a
`publish` callable that rehosts the *downloaded clip* — not the
provider's URL — somewhere readable. It takes the local file because the
provider's URL is transient, auth-gated storage that an external CDN
cannot be pointed at; the file on disk after `fetch()` is the only
artifact this backend actually owns, and it is what publish is given,
only once fetching it has actually succeeded.

Without both, `segment()` breaks the chain into single shots. That is the
conservative answer on purpose: the alternative is submitting a paid
continuation against a URL already known to be unreadable, and getting back
either a failure or — worse — a clip that ignored its reference while
MovieCrew goes on claiming the take is continuous.

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
        # publish(shot_id, local_path) -> public_url. Called with the file
        # fetch() actually wrote to disk, never the provider's own URL, and
        # only once that fetch has succeeded — see _reference_url.
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

    def _reference_url(
        self, shot_id: str, *, provider_url: str, local_path: str
    ) -> Optional[str]:
        """The URL a *later* shot can be given to continue from, or None.

        Called only after `fetch()` has written `local_path` to disk — never
        before, and never when it failed. Recording a reference earlier was
        the bug this signature exists to prevent: a shot whose download
        failed would still leave behind a continuable-looking URL, and the
        next shot in the chain would submit a paid continuation against a
        predecessor that, as far as this backend can prove, was never
        actually produced.

        Two things can make a clip deliverable. A client that says its own
        results are already reusable — a provider with native asset ids,
        say — hands back its own `provider_url`, via
        `RenderCapabilities.produces_reusable_video_reference`; nothing to
        publish, since the provider is already willing to read its own
        output back. Otherwise `publish` is the general path: give it a
        callable that rehosts `local_path` — the file just fetched, not the
        provider's URL — somewhere readable (an `AssetStore`, a CDN), and
        use the URL it returns. The provider's own URL is not publishable
        as a reference in the general case: OpenRouter's `unsigned_urls`
        sit behind the same API auth as everything else — `fetch()`
        attaches a Bearer token for exactly that reason — and a URL handed
        onward in `provider.options.video_urls` carries no such header.
        """
        if self._capabilities().produces_reusable_video_reference:
            return provider_url
        if self._publish is not None:
            return self._publish(shot_id, local_path)
        return None

    # -- can this backend carry a take? --------------------------------- #

    @property
    def reference_delivery_available(self) -> bool:
        """Can a produced clip be handed to the next generation at all?

        Independent of whether any model would accept it: this is about
        getting the artifact somewhere readable, not about video input.
        """
        return (
            self._publish is not None
            or self._capabilities().produces_reusable_video_reference
        )

    @property
    def can_chain(self) -> bool:
        """Whether a take can stay continuous on this backend.

        Both halves are required — a model that consumes a video reference,
        and a predecessor artifact the next render can actually read. This
        is the single place that decision is made; `segment()` asks it
        before anything is submitted, and `render()` refuses a continuation
        that reaches it anyway.
        """
        return self._capabilities().supports_video_reference and (
            self.reference_delivery_available
        )

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
        """Keep a take whole only if this backend can actually carry it.

        Two conditions, not one. The model has to accept a video reference,
        and the previous clip has to be deliverable to it — see `can_chain`.
        Missing either, every shot stands alone, and it is decided here,
        before a single paid render is submitted, rather than discovered
        mid-take when a continuation comes back wrong.
        """
        if not chain:
            return [[]]
        if self.can_chain:
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
        # Every backend reports warnings the same way, so the key is always
        # present. An unreadable continuation is not one of them any more:
        # that is a segmentation decision now, made before any spend.
        warnings: list[str] = []

        if extend_from is not None:
            if not self.can_chain:
                # `segment()` never produces a run that asks for this, so
                # reaching here means a hand-built call. Refuse it: the only
                # alternative is a paid render against a reference this
                # backend already knows it cannot deliver.
                return self._failure(
                    spec,
                    f"cannot continue from shot {extend_from!r}: "
                    + self._why_not_chainable(),
                    extend_from=extend_from,
                    in_multishot_chain=in_multishot_chain,
                )
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

            os.makedirs(self.out_dir, exist_ok=True)
            out_path = self.client.fetch(
                job, os.path.join(self.out_dir, f"{spec.shot_id}.mp4")
            )

            if out_path is None:
                # The provider generated it and billed for it; we just could
                # not retrieve it. `fetch` is documented to return None, and
                # calling that a success would put a shot with no clip into
                # the cut. The URL and cost stay in `raw` so the spend is
                # recorded and the download can be retried. Crucially,
                # nothing below this point has run yet: no reference is
                # published or recorded for a clip that was never fetched.
                return self._failure(
                    spec,
                    "generation succeeded but the clip could not be downloaded "
                    f"from {job.video_url!r}; the render was still billed.",
                    extend_from=extend_from,
                    in_multishot_chain=in_multishot_chain,
                    raw=raw,
                )

            if job.video_url:
                # Only reachable once fetch() has actually produced a file,
                # so publish (when used) is always handed a clip that
                # exists, and the next shot in a chain never inherits a
                # reference to a download that failed.
                reference = self._reference_url(
                    spec.shot_id, provider_url=job.video_url, local_path=out_path
                )
                if reference is not None:
                    self.produced_url_by_shot_id[spec.shot_id] = reference

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

    def _why_not_chainable(self) -> str:
        """Which half of `can_chain` is missing, in words a caller can act on."""
        if not self._capabilities().supports_video_reference:
            return (
                f"model {self.model!r} does not accept a video reference, so "
                "it has no way to continue from a previous clip."
            )
        return (
            f"model {self.model!r} accepts a video reference, but this backend "
            "has no way to deliver the previous clip to it. Pass publish= to "
            "rehost each clip somewhere the provider can read, or use a client "
            "whose own results are reusable as references."
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
