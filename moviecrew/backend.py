"""The seam between the orchestrator and whatever actually renders a shot.

`MovieCrew.render()` walks a render plan and hands each shot to a backend.
For that walk to be honest, it must not know which backend it is driving —
and until this module existed it did, because the orchestrator built a Veo
request itself and every backend was obliged to accept one.

So a backend answers three questions about itself, and the orchestrator asks
rather than assumes:

  segment()  how much of a continuous take can you execute in one piece?
  adapt()    what does this shot's intent look like as a request you accept?
  render()   run it.

`adapt()` is the whole of the vendor boundary. A `ShotIntent` says what the
film wants — 11.5 seconds, five references, 2.39:1 — and `adapt()` is where
that meets what one system can actually do. Veo snaps the duration to 4/6/8
and keeps three references; another backend keeps all five and the exact
duration; a live-action unit would ignore the question entirely. None of
those answers belongs upstream, because upstream there is no backend yet to
have an opinion.

The request type is the backend's own business, so it is a type parameter:
whatever `adapt()` returns is exactly what that backend's `render()` takes,
and no third party needs to name the type to pass one to the other.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Optional, Sequence, TypeVar

from .schema import ShotIntent

# The vendor request shape a given backend accepts — a VeoPrompt, a ShotSpec,
# a call sheet. Only the backend that produces it ever needs to name it.
Request = TypeVar("Request")


@dataclass
class RenderResult:
    shot_id: str
    status: str  # "stubbed" | "succeeded" | "failed" | ...
    backend: str
    uri: Optional[str] = None
    raw: Optional[dict[str, Any]] = None


class VideoBackend(ABC, Generic[Request]):
    """One system that can turn a shot's intent into a clip."""

    name: str = ""

    def segment(self, chain: Sequence[str]) -> list[list[str]]:
        """Split one editorial chain into runs this backend can execute.

        An editorial chain is a creative statement — these shots are one
        continuous take — and it stays whole in the render plan however long
        it runs. Backends disagree about how much of a take they can carry in
        one piece, so the split happens here and the canonical chain is never
        touched.

        The default is the honest answer for most systems, including a camera
        crew: no limit, roll the whole thing. Veo overrides it.
        """
        return [list(chain)] if chain else [[]]

    @abstractmethod
    def adapt(
        self, intent: ShotIntent, *, reference_images: Sequence[str] = ()
    ) -> Request:
        """Build this backend's request from a backend-neutral intent.

        References are passed in rather than read off the intent: they live
        on the `Shot`, which storyboard approval mutates, so they are
        resolved from live project state at the moment of execution
        (`production.resolve_shot`) rather than copied at plan time and left
        to go stale.

        Implementations must leave `intent` untouched. What the film asked
        for has to stay recoverable after a request that could not honour it.
        """
        raise NotImplementedError

    @abstractmethod
    def render(
        self,
        request: Request,
        *,
        extend_from: Optional[str] = None,
        in_multishot_chain: bool = False,
    ) -> RenderResult:
        """Execute one request built by this backend's own `adapt()`.

        `extend_from` is the shot id this one continues from within a chain,
        or None for a chain's head or a standalone shot. `in_multishot_chain`
        marks a shot belonging to a chain of two or more, which some backends
        must render differently to keep it continuable.
        """
        raise NotImplementedError
