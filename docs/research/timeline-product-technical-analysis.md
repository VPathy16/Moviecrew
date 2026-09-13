# MovieCrew timeline: product and technical analysis

**Recommendation:** Make the timeline the place where a filmmaker develops, compares and finishes a story. Prioritize trustworthy playback, recoverable editing and context-aware continuation before adding more generation controls. The current implementation is a useful single-track rough-cut editor; it is not yet a dependable SaaS editing foundation.

This assessment covers the working tree based on commit `09f55c4`, including the uncommitted export-popup and FLUX upscaling changes, inspected on September 13, 2026. Competitor comparisons use public first-party documentation. They are not hands-on comparative performance tests. No customer study, measured market-size estimate or paid generation quality benchmark was performed. Priorities, estimates and product positioning below are analytical recommendations.

## 1. Product direction

MovieCrew should serve solo creators and small creative teams making roughly 30-second to two-minute narrative films, trailers and cinematic advertisements. This is an initial customer hypothesis to validate, not established demand. These people need coherent sequences, recognisable characters, controllable pacing and an easy way to repair a weak moment without rebuilding their film.

The strongest promise is: **build the next moment of your film without losing the story you already made.** A workflow organised around model names and generated files makes users do the director’s and editor’s coordination work themselves. A story-aware timeline can retain that context and make the relevant action available at the selected cut.

The product should distinguish three operations in plain language:

- **Continue this moment:** extend continuous action, preserving its spatial and motion context where the model supports it.
- **Create the next shot:** introduce a new angle or story beat with the right cast and world references.
- **Try another take:** generate an alternative for the selected timeline occurrence and compare it before replacing anything.

A last-frame image can help anchor appearance and composition. It does not contain motion history, velocity, dialogue timing or the complete scene state. Consequently, making every new shot from the previous final frame is not a universal continuity solution. It is one reference strategy. The app should select or explain that strategy rather than presenting every model as equally capable.

## 2. Competitive evidence and implications

| Product | Documented strength | Implication for MovieCrew |
|---|---|---|
| Higgsfield Cinema Studio | Cinema controls, reusable Elements, project-level style and interchangeable generation models; its product account describes movement toward video-first, multi-shot work.[1] | A crew concept, presets and a model picker are insufficient differentiation. Carry story state into each operation and make it editable. |
| Google Flow | Scenebuilder arranges, trims and previews clips; video history preserves versions and prompts; saved frames can become references. Its documentation currently restricts extension to Veo-generated videos.[2] | Version history and contextual continuation belong in the core workflow. Model restrictions should be visible before submission. |
| Adobe Premiere | Generative Extend addresses missing editing handles, with documented limits of up to two seconds of video and ten seconds of audio.[3] | Separate “make this cut slightly longer” from generating a new sequel scene. They solve different problems. |
| Descript | Its documented timeline redesign brings scenes into the timeline, places contextual indicators there, and hides advanced tools behind an optional control.[4] | One editing surface with progressive disclosure is a defensible UX direction. Avoid separate competing scene, clip and job lists. |
| DaVinci Resolve Cut | Dedicated tools for rapid cutting and trimming, with overview and detailed editing workflows.[5] | Borrow predictable editing behaviour and navigation. Matching a professional editor’s full feature inventory is unnecessary for the initial audience. |

These sources establish advertised workflows, not comparative output quality or retention. Higgsfield’s descriptions of its internal process are company claims; they do not establish a reproducible quality advantage for a given model. Public product pages cannot reveal competitors’ inference costs or prove they operate at a loss.

MovieCrew’s potential advantage is the connection between its existing crew, approved character/world sheets, shot intentions, alternate takes and an editable sequence. That advantage is currently fragmented across screens. A filmmaker should be able to inspect what a selected shot is meant to accomplish and continue or repair it from the same workspace.

The market is converging on generation embedded in editing. Competing on the presence of an Extend button will be weak. Competing on fewer failed attempts, fewer continuity mistakes and less time assembling a usable film is more credible. This proposition must be tested with users and measured against their existing workflow.

## 3. Current implementation: assets worth retaining

The editor already has a duration-scaled visual track, drag reordering, edge trimming, a playhead, split/remove actions, context menus, imports, extension generation and a saved cut. The context menu also has a visible ellipsis entry point, which is important for discovery and keyboard access.

Backend media items have durable IDs and project-scoped lookup. Export records snapshot the cut. Enhancement processing creates a separate result, preserving the original. Several generation paths persist provider IDs and support resuming work. Those foundations should survive the refactor.

Do not rebuild working generation adapters merely to adopt a new frontend framework. Extract ownership of state and media playback first, retaining compatible APIs while introducing a versioned sequence model.

## 4. Technical findings

### A. Playback is still a sequence of source swaps — P0

In `editor.js`, `loadClip()` assigns a new `player.src` at each boundary. A canvas holds the outgoing picture during loading and seeking. This hides an empty player but can hold a frame visibly; it does not provide continuous decoding or continuous audio. The handoff uses `timeupdate` and a fixed 0.025-second threshold.

MDN documents `timeupdate` as variable-frequency, approximately 4–66 Hz depending on load.[6] It is inappropriate as the sole frame-accurate cut scheduler. Frame callbacks offer better information about presented video frames, but do not by themselves guarantee seamless multi-file playback.[7]

**Recommendation:** Generate editing proxies with a consistent frame rate and audio format. Preload an adjacent clip using a bounded player pool, and use frame callbacks for observation and UI clock updates. For reliable review, offer a cached, server-rendered preview of the current sequence revision. Benchmark this bridge before committing to a custom WebCodecs compositor. A sophisticated decoding engine is expensive; adopt it only if the proxy approach cannot satisfy measured requirements.

**Release gate:** A synthetic sequence with burned-in frame numbers and audio clicks must have no inserted black frames and no missing/repeated boundary frames in the rendered output. Measure browser stalls separately from exported-file correctness.

### B. Time is represented as arbitrary seconds — P0

`CutClip` stores floating-point `start` and `end`. Keyboard trims move 0.05 seconds; export forces 24 fps. At 24 fps, one frame is approximately 0.041667 seconds, so those editing increments do not align with exported frames. Mixed source frame rates increase the ambiguity.

**Recommendation:** Use rational project frame rate and integer timeline ticks. Record source timestamps/frame metadata separately, including a policy for variable-frame-rate imports. Use half-open ranges: start inclusive, end exclusive. OpenTimelineIO provides a useful precedent for rational time and ranges; it is an interchange model, not a playback engine.[8]

Keep compatibility by migrating old seconds into a versioned sequence at an explicit project rate, retaining the original seconds in migration metadata. Show a migration preview or retain the previous cut revision so rounding is reversible.

### C. Clip occurrences do not have identities — P0

The saved clip contains `video_id`, `start`, `end` and `mute`, but no clip-instance ID. `insertExtension()` matches source video plus nearly equal trim points and refuses ambiguous matches. Two uses of the same material can therefore prevent automatic contextual insertion. Enhancement replacement uses the first matching source/range, which can target the wrong occurrence when duplicates exist.

**Recommendation:** Give each timeline occurrence its own stable ID, separate from the asset ID and shot ID. Bind jobs to that occurrence and the sequence revision that initiated them. Moving a clip should preserve the target. If it is deleted or materially retrimmed, show the result as a candidate requiring placement; never guess.

### D. Saves can overwrite newer work — P0

`saveCut()` replaces the live `cut` with the server response after awaiting the request. An edit made during that wait can be replaced by the older snapshot. The backend stores one JSON document per project without a revision check. Two browser tabs can overwrite each other’s cuts.

**Recommendation:** Add revision-checked writes, immutable client snapshots and a serialized save queue. A response should acknowledge the submitted revision rather than replace newer local state. Persist pending local edits in IndexedDB. On a revision conflict, preserve both versions and offer recovery; do not silently merge arbitrary timeline operations.

Undo currently retains up to 30 in-memory snapshots, resets when the final editor loads and has no redo counterpart. Introduce a command history with inverse operations, plus periodic persistent checkpoints. Durable history need not mean storing every pointer-move event: one drag should be one command.

### E. Playback controls have conflicting ownership — P0

The custom Play handler reloads clip zero, even after seeking elsewhere. Native video controls also remain enabled, but the custom `playing` flag is updated through separate controls. Native playback can therefore disagree with sequence advancement state.

**Recommendation:** One transport controller must own play, pause, seek, selected clip and sequence position. Play resumes at the playhead; an explicit restart command starts at zero. Test both pointer and keyboard interaction and remove redundant controls where they undermine this model.

### F. Timeline rendering scales with all clips — P1

`renderTiles()` rebuilds the track DOM and creates a video element for each clip thumbnail. Repeated selection and rendering can cause unnecessary metadata requests and media-element work. The cut permits 200 clips. This is a scalability risk inferred from implementation; it was not profiled under that load.

**Recommendation:** Generate thumbnail strips once and use images for the track. Virtualize offscreen regions, cache cumulative offsets, and update selection/playhead without replacing the entire track. Use an explicit media-element budget independent of clip count.

### G. Audio is too limited for finishing a film — P1

The saved model supports only a mute switch for each video occurrence. Export normalizes and concatenates clip audio but provides no music bed, voiceover track, gain envelope or cross-cut ambience editing. Good pictures alone will not produce controlled thriller pacing.

**Recommendation:** Introduce a music/ambience lane and a dialogue/voice lane with visible waveforms, volume, fades and linked trimming. Keep empty lanes hidden. Add audio-first transitions across picture cuts, then optional ducking. Avoid default dissolves or fades to black as a workaround for broken playback.

### H. AI operations are not durable timeline objects — P1

The frontend has a single `pendingInsert` value. Some operations leave the editor to generate elsewhere. Extended results were removed from the area under the timeline at the filmmaker’s request, improving visual clutter but leaving candidate discovery reliant on library navigation. A pending placement can disappear on refresh.

**Recommendation:** Store generation intent and placement with the job. Show a compact pending slot at the selected boundary, with queued/running/ready/failed states. Results belong in a take drawer attached to the slot. Acceptance changes the cut; successful generation alone does not.

### I. Export and enhancement need a unified result model — P1

Export is snapshotted, which is good. However, it has no request idempotency key, and each request creates a new record. Upscaling runs as a separate video result after export; that result is not itself a final export record. It needs a clear downloadable destination rather than merely an “Add to edit” action.

**Recommendation:** Bind preview, export and upscale artifacts to a sequence revision. Use idempotent requests, an export history with status and download actions, and clear labels distinguishing ordinary resizing from AI enhancement. Reject stale assumptions if the sequence changes while processing. Preserve older downloadable versions.

### J. SaaS job execution needs a separate hardening pass — P0 before public launch

The examined workflow launches daemon threads in the web process and keeps active job tracking in memory. Media metadata lives in SQLite and files under session directories. This is workable locally but requires explicit worker ownership, retry rules, durable storage and access control before multi-instance SaaS deployment.

The inspected `session(project)` resolves a project; it does not itself establish a user-to-project authorization check. This is a scoped observation, not a full authentication audit. Verify authentication and tenant authorization on every cut, media, generation and export endpoint before exposing them publicly.

## 5. Proposed editing experience

Use one resizable workspace: optional library on the left, preview in the centre, contextual take drawer on the right, timeline along the bottom. At rest, only preview and timeline need to dominate. Show the crew’s relevant information when a shot is selected rather than repeating all crew outputs in the editor.

The primary picture track should be magnetic: a reorder or ripple trim closes space automatically. A gap must be an explicit user-created item, not an accidental layout outcome. Add a narrow scene/beat strip above it, and reveal audio lanes when material is added. Add zoom-to-fit, horizontal scrolling, snapping with a visible guide, frame stepping, and a small set of familiar keyboard shortcuts.

Selecting a clip opens a compact contextual bar: Trim, Another take, Continue and More. Right-click and ellipsis expose identical additional actions. Every action remains reachable without right-click. A selected scene or clip should have a human-readable name such as “Roland notices the tail,” with technical shot IDs available in details.

At a cut, “Create next shot” opens a composer anchored to that boundary. It shows the outgoing image, an optional incoming image, editable action text and tagged references. Reference chips distinguish identity, location and boundary frame; users can remove individual references. Unsupported model/input combinations should be disabled with a short reason.

After generation, show the candidate in context: a few seconds before the join, the candidate, and the next clip if present. Allow Keep, Try again and Compare. The cost and exact input references remain inspectable. Do not automatically replace the film or add every attempt as a new timeline clip.

For continuation, freeze the originating boundary and character-sheet versions in the job request. A later change to a sheet should not silently change the meaning of an already queued job. Optional continuity checks should flag likely mismatches for review; they should not claim certainty or automatically rewrite the cut.

## 6. Recommended technical design

Introduce a versioned `Sequence` with project ID, sequence ID, revision, frame-rate numerator/denominator, canvas, tracks and export settings. Each `ClipInstance` has its own ID, asset ID, source range, timeline placement, gain/mute and optional shot/scene linkage. `GenerationIntent` records target occurrence, base revision, operation, frozen references, boundary media, prompt, selected model and provider job ID.

Keep media immutable. A generated replacement or upscale creates a new asset and optionally a take linked to an existing shot. Timeline membership is a separate relationship. This avoids confusing asset ownership, scene identity and clip placement.

Extract the current script into small modules: sequence state and commands; timeline geometry; transport and media pool; generation jobs; export workflow; UI components. Use TypeScript if adopted incrementally for schemas and commands. A framework rewrite is not itself the objective. The current wrappers around global functions should disappear behind explicit interfaces.

Preview and export should consume the same normalized sequence representation. Backend rendering must have deterministic trim, frame-rate, audio and gap semantics. Thumbnail generation, proxies, waveforms and renders should be cached by asset or sequence revision. Store resulting objects durably, with lifecycle policies that preserve original and accepted material.

For public SaaS, use a durable worker queue and a transactional job store. Retain provider IDs before polling, distinguish rejection from uncertain submission, and reconcile after restart. Do not automatically resubmit a request whose billing outcome is unknown. Add project authorization and signed media access at the service boundary.

## 7. Prioritized delivery backlog

Estimates are directional engineering days for an experienced developer, excluding extensive design iteration and unpredictable provider work. They overlap and should not be treated as a fixed deadline.

| Priority | Work item | Acceptance criterion | Rough effort |
|---|---|---|---|
| P0 | Stable clip IDs and sequence revisions | Duplicate source clips can receive independent takes/extensions | 2–4 days |
| P0 | Save queue, conflicts and recovery | Edits made during a slow save survive; two-tab conflict is recoverable | 3–5 days |
| P0 | Single playback controller | Play resumes at playhead; native/custom state cannot diverge | 2–3 days |
| P0 | Proxy playback and boundary verification | Tested continuous review on representative devices; accurate rendered boundaries | 5–10 days |
| P0 | Frame-based trim/export semantics | Burned-in-frame fixture exports exactly the expected range | 3–5 days |
| P0 launch | Durable workers and tenant checks | Restart does not duplicate billing; cross-project access is denied | Scope separately after auth audit |
| P1 | Boundary composer and take drawer | Generate, compare and accept without leaving the timeline | 4–7 days |
| P1 | Persistent generation placement | Refresh/reorder during generation preserves correct target | 2–4 days |
| P1 | Thumbnail strips and virtualization | 200-clip benchmark stays within chosen resource targets | 2–4 days |
| P1 | Music, voice and fades | Continuous ambience survives picture cuts and matches export | 5–10 days |
| P1 | Export/upscale history | Each artifact has revision, status, download and original retained | 2–4 days |
| P2 | Scene grouping and continuity hints | Review and move a scene without losing its shot relationships | 4–7 days |
| P2 | Interchange export | A supported external editor receives tested cut/media timing | 3–6 days |

The first milestone should contain no new model integration. It should make a 20-second film reliably playable, editable and recoverable. The second milestone makes continuation and alternate takes coherent. The third adds enough audio and finishing to complete a two-minute film. This sequence addresses the reported problems before increasing feature surface area.

## 8. Market validation and commercial measures

Recruit a small initial cohort of 8–12 target creators, including people who currently assemble generated footage manually. Give each the same supplied set of assets and a 30-second story objective. Observe completion without coaching. Compare time to a usable sequence, editing errors and confidence with their normal process. This is discovery, not statistically representative market validation.

Separately test AI continuation with frozen inputs across representative cases: dialogue, walking, vehicle motion, action and location changes. Record provider settings and total spend across failed attempts. Review joins blind where possible. A successful single clip does not establish general model superiority.

Use **cost per accepted second** and **time to approved sequence** as primary product measures. Track candidate acceptance, retries per accepted shot, first-session completed film rate, lost-edit incidents, export success and repeat project creation. Label generation completion separately from user acceptance.

For an illustrative economic model, if 60 seconds are generated at an assumed $0.10 per second and four attempts are needed on average, generation costs $24 before storage, enhancement, compute and support. Reducing attempts to two lowers that component to $12. These are invented scenario assumptions, not current vendor prices. The example explains why useful reference selection and take comparison can matter more commercially than a small per-call discount.

Price only after measuring accepted-output economics and willingness to pay. Avoid promising unlimited video generation while provider costs are variable. A workspace subscription with transparent metered generation is a hypothesis to test; it is not yet a validated business model. BYOK can ease early testing but is likely friction for nontechnical customers.

## 9. Verification plan and launch gates

Use automated unit tests for commands and time mapping; API tests for ownership, revisions and idempotency; integration tests for media rendering; and browser tests for user workflows. Do not rely only on DOM string assertions or successful provider responses.

Required scenarios: duplicate a source twice and extend one occurrence; trim while a save is in flight; refresh during a job; change the cut before a result returns; open the same sequence in two tabs; undo and redo a reorder; seek then play; import mixed frame rates; cut across silent and audible clips; upscale a saved export and download the result.

Build deterministic test videos containing frame counters, distinct colours and audio impulses. Compare rendered timing automatically, and inspect browser playback under throttled networking and CPU load. Test Safari and Chromium on representative hardware. Initial performance targets should be agreed before implementation—for example a responsive drag interaction under 50 ms and an explicit stall budget—then measured, not presented as achieved.

No new live benchmark was performed for this analysis. The source inspection establishes structural problems and likely failure modes; it does not quantify their incidence. Competitor documentation establishes capabilities, not comparative usability. Before a public launch, complete a separate security and deployment audit.

## 10. Decision

Invest in the timeline now, with reliability as the first deliverable. Preserve the compact appearance already established, but replace its fragile state and playback mechanisms. Make story continuation, reference selection and take review the distinguishing workflow. Audio and export completion should follow closely; additional effects and model choices should wait until a creator can finish a coherent film without managing file lists or recovering edits manually.

## Sources and code evidence

[1]: https://higgsfield.ai/blog/how-we-built-cinema-studio
[2]: https://support.google.com/flow/answer/16935718?co=GENIE.Platform%3DDesktop&hl=en
[3]: https://helpx.adobe.com/in/premiere/desktop/edit-projects/edit-with-generative-ai/generative-extend-faq.html
[4]: https://feedback.descript.com/changelog/the-new-timeline-is-on
[5]: https://www.blackmagicdesign.com/products/davinciresolve/cut
[6]: https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/timeupdate_event
[7]: https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback
[8]: https://opentimelineio.readthedocs.io/en/v0.17.0/api/python/opentimelineio.opentime.html

1. Higgsfield, [Inside Higgsfield #1: How We Built Cinema Studio][1], August 12, 2026; accessed September 13, 2026. Vendor account of product design and capabilities.
2. Google Flow Help, [Edit videos & build scenes in Google Flow][2], accessed September 13, 2026. Current desktop workflow and extension restrictions.
3. Adobe Help, [Generative Extend FAQ][3], accessed September 13, 2026. Scope and limits of extension.
4. Descript Changelog, [The new timeline is ON][4], accessed September 13, 2026; publication date not exposed in retrieved text. Design direction, not universal account rollout verification.
5. Blackmagic Design, [DaVinci Resolve — Cut][5], accessed September 13, 2026. Editing workflow reference.
6. MDN, [HTMLMediaElement: timeupdate event][6], accessed September 13, 2026. Browser event timing.
7. MDN, [HTMLVideoElement: requestVideoFrameCallback][7], accessed September 13, 2026. Presented-frame observation.
8. OpenTimelineIO, [opentimelineio.opentime API, version 0.17.0][8], accessed September 13, 2026. Explicit version used for conceptual time representation, not an assertion about the latest release.

Local code examined: `moviecrew/portal/static/editor.js` (transport, timeline, history, placement and export UI); `moviecrew/portal/static/studio.html` (saveCut and final-edit integration); `moviecrew/portal/film_workflow.py` (cut schema, save/export endpoints, rendering and worker launch); `moviecrew/portal/film_enhance.py` (enhancement and boundary processing). Findings refer to the inspected working tree and may change after implementation.
