# Persistent shot workspace

Open `/` or `/studio` for the unified MovieCrew workspace. The previous
production tools remain at `/legacy` for compatibility, outside the customer
navigation. Existing `?project=...` links also open the saved film.

Implemented:
- SQLite project library: create through planning, reopen, rename, duplicate.
- Progressive planning and durable checkpoints; interrupted plans remain readable.
- Shot navigation, debounced prompt autosave, image regeneration.
- Immutable image versions with prompt, model, creation time, and preferred selection.
- Compare versions, approve images, and view camera previews/video renders within the shot.

Storage defaults to `~/.moviecrew/projects`; set `MOVIECREW_PROJECTS_ROOT` to
isolate tests or another installation. The library is `library.sqlite3`, and
new image files are stored under the project UUID. Existing R2 rendering and
Blender paths are unchanged. Duplicate projects share immutable existing image
files; future generations write to the new project folder. Back up the database
and media together.

This milestone is a single-user local workspace, not a public SaaS deployment.
Existing temporary checkpoints from before the library are preserved in their
original locations, but are not automatically imported. New workspace projects
persist across restarts. Previously running planning jobs are marked interrupted
rather than restarted or billed again. Durable job workers, account isolation,
private signed R2 assets, consumer onboarding, and billing are later milestones. Existing shot
reference IDs remain available to the production pipeline.

Validation uses isolated settings and providers. Example:

```
MOVIECREW_PROJECTS_ROOT=/tmp/moviecrew-tests \
MOVIECREW_SETTINGS_PATH=/tmp/moviecrew-empty-settings.json \
OPENROUTER_API_KEY='' ANTHROPIC_API_KEY='' \
python -m pytest tests/test_project_library.py tests/test_portal.py tests/test_storyboard.py
```

## Image model and reference controls

The workspace now discovers models from OpenRouter's `/images/models` catalog
and derives aspect ratio, resolution, and quality choices from endpoint
capabilities. Generation pins a compatible provider; unsupported combinations
are rejected before generating. Catalog failures leave the offline choice
available instead of silently selecting a paid fallback.

Reference uploads accept PNG/JPEG/WebP signatures, up to 5 MB per file and 40
files per project. A shot can select up to four owned references (providers may
impose lower limits). References are sent as inline base64 image inputs, not
published to the bucket. Saved settings include model, options, reference IDs,
and 1–4 variations. Each variation is a separate request/version; a failed
variation stops the batch. Reported cost is recorded per successful version;
pre-generation estimates are shown only for unambiguous flat image pricing.
Unknown or token-based pricing is labeled as unavailable.

Prompt edits and model settings save automatically, including before shot
changes and navigation. The storyboard action uses each
shot's saved settings, defaulting unconfigured shots to offline generation.
Offline images are never promoted as production reference images.

Protocol reference: https://openrouter.ai/docs/guides/overview/multimodal/image-generation
Tests use injected transports; live paid generation has not been exercised.

## Unified customer interface

My films is the only library; shots use friendly sequential labels and thumbnails.
Each shot has Image and Video tabs with compact upward-opening model menus.
References and bulk image actions are collapsed below the prompt. Model-specific
image controls remain capability driven. Settings holds provider connections for
this local prototype; a hosted product should manage those server-side.

The Video tab uses the existing Blender camera previews, render estimates,
submission/polling, saved render playback, and downloads. It does not introduce
a new camera-preview upload flow. Storage/provider setup errors disable video
generation and show a readable message. Takes still use the existing scene/shot
lookup; per-account/project video isolation is required before public SaaS use.

Validation: 77 focused tests pass; JavaScript syntax and browser checks cover
root routing, shot navigation, prompt autosave, compact model menus, Settings,
and the video setup failure state. No live paid image or video generation was
performed.

## Crew-first film workspace

Films now open on Your crew, with all seven existing pipeline roles and their
actual saved outputs: Director (logline/outline), Writer (scenes), Production
designer (style/cast/locations/props), Cinematographer (shot choices), Editor
(order/pacing/chains), Prompt artist (directions linked to editable shot prompts),
and Continuity (on-demand review and flags). Role progress comes from the existing
plan progress record. Continuity results are saved to the persistent library.

Storyboard is a film-level gallery grouped by scene, with links into the image
editor, bulk generation, and approval. Shots & video retains the per-shot composer
and video flow. Individual conversational role revisions and final-film assembly
are not implemented; the crew views expose real pipeline artifacts rather than
simulated agent chats.

Validation: previous 77 checks pass; an additional continuity persistence test
passes. Browser checks cover Director/Writer outputs, storyboard-to-shot navigation,
and an offline continuity review. No paid generation was used.

## First complete film workflow (13 September)

The unified workspace now uses project-owned video and export records in the
project library, through `film_workflow.py`. It no longer assigns legacy Blender
clips to a film merely because scene/shot IDs match. Existing clips can be
explicitly uploaded to a chosen shot; originals remain untouched in legacy storage.
Uploads are validated and converted to browser-playable MP4 in background work.

The Video tab selects a storyboard image reference and saves separate video
direction/model/duration/aspect/resolution/audio settings. Provider capabilities
restrict the controls. This is image conditioning through the existing render
adapter, not a guarantee that a model will use the image as its exact first frame.
Estimating never uploads media or starts a generation. Live submission publishes
only the selected owned frame through the configured storage provider.

Each generation has a durable client request UUID, provider job ID, owning film,
reference version and request snapshot. Known jobs resume polling after restart.
An ambiguous submission is marked uncertain and is never automatically billed
again. Temporarily inaccessible known jobs can be resumed without resubmission.
This local worker uses process-local execution locks: run a single server worker.
A distributed deployment still needs transactional leases and account isolation.

Final edit saves an ordered list of owned clips, in/out trims, per-clip mute and
landscape/portrait/square output format. Export normalizes video/audio and produces
a saved MP4 with playback/download. Silent inputs receive a silent audio track.
Missing sources fail visibly; export does not silently omit clips. There is no
music upload/mixing, transitions, advanced timeline or conversational crew revision
in this first edit workspace. Existing clip audio and supported generated sound
are available. New video/cut/export records are not cloned by Duplicate yet.

Offline generation is explicitly a demo. Legacy mock PNG fixtures produce a
labelled placeholder clip; this is never described as AI-generated footage.
Verification includes project ownership, idempotency, uncertain submissions,
resume without resubmission, separate video drafts, real ffmpeg trims/concatenation,
portrait export, silent inputs, and persisted playback. Browser verification
created a demo clip, saved a 1.5-second trim, exported it (1.536 seconds including
encoding padding), and reopened the saved edit/export after a server restart.
Live paid video generation has not been exercised.

## Opening creative brief

New film now asks for story, film type, genre, language, movie reference titles
and the qualities to borrow from those references. Genre/language accept custom
values; references and their notes are optional. The brief persists with the
session, is copied with a duplicated project, and appears in the Director view.
`BriefedLLM` adds the same brief to each role's input, preserving the role's schema,
including on-demand continuity. Old saved sessions open with an empty brief.
Language guides creative text and intended dialogue; this is not a separate
translation/dubbing feature or a guarantee of a video's speech accuracy.
Validation: all seven roles receive the brief; storage round-trip and existing
portal/library checks pass (32 checks). No paid generation was used.

## Cast & world approval gate

New films created by the unified workspace request `review_world: true`. The
planning pipeline stops after Director, Writer and Designer; scene records contain
zero shots and the session is saved as `awaiting_approval`. The camera/edit/prompt
phase starts only through the backend approval gate, using the approved project
and shared cast/world context, without rerunning the earlier roles. Legacy API
clients retain the explicit one-pass behavior when `review_world` is omitted.

Cast & world has character, environment and recurring asset sheets. Editable
fields cover appearance/personality/wardrobe/poses/voice, layout/light/time/palette,
and material/scale/use. Reference images can be uploaded or generated with an
explicit model choice (offline by default). Each save creates a version; history
retains earlier text/reference selections. Editing or generating a reference
invalidates the current approval. Text-only sheets can also be approved.

Every sheet needs current approval before initial shots can be built. Sheet
versions are recorded per shot. Later changes identify shots using earlier
versions; the customer chooses which future image drafts/references to update.
Existing generated images and videos are preserved. Applying updates does not
rerun generation or change previously rendered video. Image generation currently
accepts up to four references; the editor exposes its reference selections.
Existing films are not retroactively blocked or regenerated.

Validation: 86 focused checks pass, including zero cinematography calls before
approval, no Director/Writer rerun at handoff, version conflicts, reopening the
gate, and preservation of image versions when applying later sheet revisions.
Browser QA created a new offline film, saved a wardrobe revision, generated a
placeholder sheet reference, verified 1/3 and 2/3 approval kept shots locked,
then reopened and created shots only after 3/3 approvals. Paid generation was
not exercised.

## Minimal creative workspace refresh — 13 September 2026

Reference: user-supplied Supercomputer recording, reviewed for its quiet sidebar,
spacious canvas, and contextual controls. This is a local MovieCrew UI update.

- Persistent workspace sidebar; responsive horizontal navigation on phones.
- Idea-first home with a central composer and a quieter saved-film library.
- Compact new-film composer: format, genre, and language use upward popovers;
  movie references expand on demand. Required genre validation opens its control.
- Crew role cards switch focused, readable outputs. Long role names wrap correctly.
- Character/environment/asset sheets separate Overview, Look & details, and
  Reference views with keyboard-accessible tabs; saving reads all tabs.
- Laptop shot picker becomes a horizontal strip to give the preview more room.
- Existing generation, video library, approval gates, and storage settings retained.

Verification: JavaScript syntax and diff checks; 30 targeted portal/creative brief/
world gate tests pass. Browser checks at desktop and 390px: film creation in the
isolated offline preview, genre validation, cross-tab sheet edits and version save,
crew navigation, saved video access, and R2 fields. Live generation not exercised.

## Character studio — face, body, accessories, costume

Character sheets now offer four ordered generation options with separate editable
notes and saved latest reference IDs. Full-body/costume requests prioritize earlier
identity references. Regenerating replaces that stage's selected reference while
retaining the prior asset and sheet snapshot. Environment and prop sheets retain
generic reference generation. Upload management is collapsed in the character UI.
These are selectable stages, not mandatory generation gates; approval remains at
the sheet level. Live identity quality depends on the chosen image provider.

Verified all four actions in the offline browser preview, saved face direction on
reload, and 31 portal/brief/world tests including reference priority, regeneration
history, persistence and invalid-stage rejection. No paid generations run.

## Approved sheet references in shot generation

Switching image models now preserves reference selections. Shot generation binds
approved sheet versions server-side and sends the actual image bytes through the
Image API adapter, with per-reference character/view labels in the prompt. Provider
reference order now matches request order. Saved frames record the attached IDs.
Estimates also bind shot references. More than four combined references stops with
a clear error instead of silently omitting sheets; this is the app's current limit.

36 tests passed, including a Gemini-named test model with intercepted transport:
all four exact image byte payloads, pinned approved versions, frame metadata, and
reference overflow rejection. No live Gemini request was made.

## Multi-model image selection

The public image-model catalog is now visible even when this preview has no API
key. Character sheets use a searchable upward-opening picker inside the dialog;
shots keep their existing picker. Live generation still requires a configured
OpenRouter connection and a reference-compatible endpoint. Successful sheet
generation retains the selected model. No model is hardcoded to Gemini.

Verified catalog browsing and FLUX selection in the browser without generating.
11 image/world tests pass, including two provider model IDs with identical
reference payload behavior and catalog visibility without credentials.

## Live GPT Image 2 / Seedance 2.5 test

Project: ea44be1c-7295-489a-8f99-f62ea17e5705 in isolated QA storage.
GPT Image 2 generated a real face sheet and a 16:9 shot using its reference ID.
The first Seedance 2.5 result was H.264, 854x480, 4.041667 seconds; reported video
charge $0.415481. Visual review found it did NOT preserve the starting shot.

Root cause: video images were sent in legacy provider.options.image_urls rather
than OpenRouter's top-level frame_images/input_references. Updated the adapter,
wired film workflow first_frame, and filtered first-frame-incompatible models.
56 render/film workflow tests pass. Documentation:
https://openrouter.ai/docs/cookbook/video-generation/image-to-video

A second paid-test submission using the corrected first-frame request returned no
job ID and is stored as uncertain: 18d37264-cb03-4871-83c0-ebfa9fb042ee. No further
submission was made because acceptance/billing could not be confirmed. The initial
error detail was lost by the old workflow; future uncertain submissions now retain
sanitized provider error details. Corrected live video continuity is NOT verified.
Temporary test credentials were removed after the run. Images and video remain.

## Verified start-frame follow-up

R2 reference publishing now generates a one-hour signed GET URL and compares the
returned bytes before any paid video request. Durable asset publishing is unchanged.
Seedance rejected the synthetic portrait as a possible real person. MiniMax H3 Max
accepted the same selected shot at its supported five-second duration. Video
64c0f7db-0a1e-4d44-b2b2-5d3064d8a615 completed (5.184 seconds); first-frame and
three-second visual inspection confirmed the original composition and identity.
Character sheets condition GPT Image 2; the resulting shot is the video's exact
first frame. OpenRouter prioritizes frame_images over input_references, so separate
character sheets are not additionally consumed in this video mode.

Explicit HTTP rejections are now failed, while ambiguous submissions remain
uncertain and are never automatically resubmitted. Video duration choices respect
the live model catalog. Validation: 725 tests passed; inline JavaScript syntax and
git whitespace checks passed. Temporary test credentials stay outside the repo.
