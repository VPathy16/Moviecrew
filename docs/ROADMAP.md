# Architecture roadmap

MovieCrew today works end to end, and it works by carrying a shot as prose.
A concept becomes scenes, scenes become shots, and a shot's cinematography
lives in three free-text fields — `camera_move`, `lens`, `framing` — which are
parsed back out by `blocking.py` when Blender needs numbers, and concatenated
into a `VeoPrompt` when a model needs words.

That is why the system can render a shot but cannot yet reason about one. You
cannot diff prose, schedule it, or check whether what came back matches what
was asked for. Every item below is a step away from prose and toward data.

The order matters: each one is load-bearing for the ones after it.

---

## 1. Replace `VeoPrompt` as the centre with a backend-neutral `ShotIntent` ✅

Model-specific adapters belong only at execution boundaries.

**Done.** `ShotIntent` is what the agents produce and what everything
downstream consumes; `RenderPlan.intents` replaced `RenderPlan.prompts`.
`VeoPrompt` moved to `video.py`, which is now the only module that names the
vendor in code — `schema.py` does not know a vendor called Veo exists.

The rename was the smaller half. What makes the centre actually neutral is
that **no backend's limits are applied to production state before an adapter
is chosen**:

| | before | now |
| --- | --- | --- |
| `Shot.duration_s` | snapped to 4/6/8 on construction | any positive float |
| `Shot.reference_image_ids` | capped at 3 | uncapped |
| `select_anchors()` | forced anchors to 8s, truncated to 3 | decides anchor-or-not and which references, nothing else |
| `normalize_chains()` | split takes at Veo's extension limit | editorial chains stay whole |
| `approve()` | dropped references past Veo's cap | prepends, keeps everything |
| Cinematographer | told to emit only 4/6/8s | emits the duration the cut wants |
| Editor | chained "for Veo's extend-from-final-frame" | chains are continuous takes |
| aspect ratio | Veo's two values, or an `^\d+:\d+$` pattern that admitted `0:0` | any real ratio, both sides positive |

**Canonical state has one home.** `ShotIntent` carries no copy of the
reference images. They live on the `Shot`, storyboard approval rewrites them,
and a copy taken at plan time went stale the moment a board was approved — a
render could go out anchored to the wrong stills with nothing appearing to be
wrong. `production.resolve_shot()` builds a read-only `ShotState` from the
live project at the moment a request is constructed, and both adapters take
references explicitly. The portal's `/api/render` resolves through it, so the
browser no longer reconstructs filmmaking state and posts it back.

**Nothing is dropped silently.** A shot with the wrong scene id, a duplicate
id, a scene with no shots, or a prompter answering for a different shot now
raise `PipelineError` rather than disappearing from the plan.
`normalize_order()` guarantees a total order regardless of what the editor
proposed.

**Still prose.** `description` is a string, which is item 2's job. The centre
is neutral now; it is not yet structured.

---

## 2. Make cinematography structured

Camera transforms, lens, focus, screen-space composition, actors and blocking
become data rather than prose.

**Where we are.** `blocking.py` already computes exactly this — `Keyframe` and
`CameraBlocking` carry real positions, rotations and focal lengths — but it
derives them by parsing sentences, and throws them away once the take is
rendered. Nothing upstream ever sees a number. Actors are absent entirely:
`Shot` has no characters and no marks, and the Blender add-on stages only the
camera.

Item 1 cleared the way: `ShotIntent.description` is prose, and a structured
field can now be added beside it with the prose derived from that structure,
without any backend's constraints having to move.

**What changes.** The structure becomes the source rather than a derivation.
An agent proposes camera keyframes, a lens, a focus target, screen-space
composition and per-actor marks; a human adjusts them; the previz renders them.
Prose becomes a description generated *from* the data, for the benefit of a
model that wants words — not the place the data is stored.

This is also the fix for the binding instability measured in the live trials:
identity bound to a prose description re-rolls between generations, while
identity bound to a reference image holds. Structured actors give the prompt
builder somewhere to point.

---

## 3. Build the production graph

Stable IDs, relationships, revisions, dependencies and lineage across
characters, scenes, shots, takes and assets.

**Where we are.** Partial and filesystem-shaped. `takes.py` has stable take ids
and records which renders a take drove; `Shot` has `reference_image_ids`;
`production.resolve_shot()` is the beginning of a resolution layer — it
collects a shot's live state at execution time and is where lineage and
revision resolution will attach. But nothing records *why* a shot changed,
what a revision superseded, or which downstream artifacts a character edit
invalidates.

**What changes.** Every entity gets an identity that survives edits, and every
edge is explicit: this take was blocked from that shot revision; this render was
driven by that take; this character reference anchors those shots. Staleness
becomes computable — change a character and the system can say which boards,
takes and renders are now out of date.

---

## 4. Adopt interoperability standards

OpenUSD for spatial and world data, OTIO for editorial — rather than inventing
proprietary equivalents.

**Where we are.** Everything is bespoke: takes are a filesystem convention,
blocking is a private dataclass, and the only editorial concept is
`assembly.py` building an ffmpeg concat command.

**What changes.** Scene layout, camera and actor blocking round-trip as USD,
which is what every DCC in the industry already speaks. Cuts, timing and
assembly become OTIO, which means an edit can leave for a real NLE and come
back. Start experimentally and alongside the native format — the point is to
learn where the mapping is lossy before committing.

---

## 5. Turn Blender into a bidirectional client

Modify a shot in Blender and write the intent back into MovieCrew.

**Where we are.** Strictly one-way. The add-on reads a `project.json`, blocks a
camera from the shot's prose, renders a take. Anything a human improves in the
viewport is lost the moment the file closes — it exists only inside the
rendered pixels.

**What changes.** Moving the camera in Blender updates the shot's intent.
Repositioning an actor updates their marks. Blender becomes where blocking is
authored, not merely where it is displayed — and the take stops being the only
record of a human's judgement.

Depends on 2 and 3: there is nothing to write back until cinematography is
data and entities have stable ids.

---

## 6. Build the evaluator

Measure camera, blocking, identity, continuity, depth, timing — and eventually
performance — against the intended shot.

**Where we are.** Ad hoc. The live trials were assessed with throwaway scripts:
normalised cross-correlation against simulated zoom to recover camera travel,
silhouette area to track a subject, hue tracking to follow a specific actor
across frames. Those measurements are the only reason we know direction
transfers but rate does not, and that behaviour-to-character binding re-rolls
between generations.

**What changes.** Those become a real component with a real contract: given a
`ShotIntent` and a rendered clip, report per-dimension agreement. That turns
"generate and eyeball it" into "generate, score, and regenerate the dimensions
that failed" — and makes every future prompt or previz change measurable
instead of anecdotal.

Depends on 1 and 2: you cannot score a render against prose.

---

## 7. Add persistent project history

Not only files and sessions — versions, approvals, dependencies, costs and
revisions.

**Where we are.** Sessions are an in-memory dict that dies with the process.
Cost is reported per render and then forgotten. Approvals exist as a stage
transition with no record of who approved what, or what they were looking at.

**What changes.** A project has a history that outlives a process: what was
approved and when, what a revision replaced, what each attempt cost, and what
depends on what. Cost history in particular pays for itself — the four invalid
1080p renders in the early trials would have been visible as a pattern far
sooner against a ledger.

---

## 8. Support hybrid execution

`AI_RENDER`, `BLENDER_RENDER`, `UNREAL`, `LIVE_ACTION` become execution
strategies for the same `ShotIntent`.

**Where we are.** Closer than the rest. `render.RenderClient` is already an ABC
with `capabilities()` that callers branch on instead of a backend name, and
`FakeRenderClient` proves the seam. Item 1 established the shape this needs:
one canonical intent, adapters that compile it per backend
(`video.veo_prompt`, `ShotSpec.from_intent`), and backend-specific execution
planning kept at the boundary (`video.segment_for_veo`).

What is still missing is selection. `MovieCrew.render()` hard-codes the Veo
adapter, and `VideoBackend` takes a `VeoPrompt` — so it is the Veo execution
strategy wearing a general name. Making the adapter travel with the backend
is this item's first concrete task.

**What changes.** A shot's intent is independent of how it gets executed. The
same camera path, marks and composition can drive a generative render, a
Blender render, an Unreal capture, or a shot list handed to a crew on a real
set. `LIVE_ACTION` is the honest test of whether the intent representation is
genuinely backend-neutral: if it cannot brief a human camera operator, it was
never neutral, only portable between models.

---

## 9. Add production constraints

Locations, cast availability, equipment, setup time, budgets, scheduling.

**What changes.** The system starts to know that two shots share a location and
should be grouped, that an actor is available on Tuesday, that a crane costs a
day. Scheduling and budget stop being outside the tool. This is where MovieCrew
stops being a generation pipeline and becomes production software.

Depends on 3 and 8: constraints attach to graph entities, and only matter once
execution is more than one kind.

---

## 10. Then expand into full studio workflows

Sound, VFX turnover, localization, rights and provenance, delivery.

Deliberately last. Each of these is a real discipline with real formats, and
every one of them assumes the nine items above already exist — a stable graph,
structured intent, interoperable interchange, and a history to attach
provenance to. Starting here would mean building them on prose.

---

## Vocabulary

Four things that are easy to conflate, and were conflated in the code until
item 1:

- **Canonical intent** — `ShotIntent`, plus the `Shot` it belongs to. What the
  film wants. No backend's limits apply.
- **Editorial chain** — `RenderPlan.chains`. A creative statement: these shots
  play as one continuous take. Length is a directorial choice.
- **Backend execution run** — what a particular system can execute in one
  piece. `video.segment_for_veo` turns one editorial chain into however many
  Veo extend-runs it takes. A live-action unit does not segment at all.
- **Backend request spec** — `VeoPrompt`, `render.ShotSpec`. One vendor's
  shape, with that vendor's clamps applied, built at the boundary and thrown
  away after. The intent behind it stays recoverable.

## Reading the order

Items 1 and 2 are the foundation: intent as data. Item 3 makes it
addressable, 4 makes it portable, 5 makes it editable where the work actually
happens. Item 6 makes it verifiable — and is the first point at which the
system can improve itself rather than be improved by hand. Items 7 through 9
turn it into production software. Item 10 is the studio.

Nothing here is a rewrite of what exists. `blocking.py` already computes
structured camera data; `render.py` already has a neutral execution seam;
`takes.py` already has lineage; `production.py` already resolves live state at
the execution boundary. The work is mostly promoting things that are currently
derived, private, or discarded into being the thing the pipeline is actually
built on.
