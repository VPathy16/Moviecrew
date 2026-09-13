# MovieCrew competitive technical analysis

## Executive assessment

MovieCrew has a credible foundation for a guided filmmaking product: a creative brief, a role-based crew, approved cast and world sheets, model adapters, saved generations, and a visual editing timeline. Its next investment should be reliable story progression and a secure production backend. More model choices and cosmetic refinement alone will not make it competitive.

The proposed positioning is **a guided studio for completing coherent short films, with visible control over characters, story beats, revisions, and spending**. This is a product hypothesis to validate, not an established competitive advantage. Higgsfield, Google Flow, Runway, and LTX already cover substantial portions of that workflow.

The most consequential code finding is that the planning Editor receives only shot IDs. The Prompter receives one shot at a time, and the Continuity agent reviews scenes and prompts rather than rendered video. These interfaces are too narrow to reliably supervise narrative progression. Improving these contracts is a higher-value next step than adding another model menu.

The public-SaaS blockers are separate: there is no authenticated workspace boundary in the inspected project/settings routes; persisted project payloads still refer to local media paths; workers use process-local coordination; and timeline saves have no revision conflict detection. These are launch gates, not reasons to discard the existing implementation.

## Scope and evidence

The code baseline is commit **70a863c**, including the preceding visual-timeline work in **dacf97b**. Public documentation was checked on **13 September 2026**. Competitor features below are documented product capabilities, not independently measured generation quality. Availability may depend on model, plan, region, and rollout. No paid competitor generation benchmark was executed for this assessment.

MovieCrew findings come from the local repository and the previously inspected desktop workflow. The recorded prior Python run passed 730 tests; that run is not a production-readiness or multi-user test. No new full-suite run was performed for this research. Competitors’ databases, queues, prompt templates, and private infrastructure are unknown and are not inferred from their interfaces.

The assessment focuses on narrative shorts and compact commercial films. Avatar presentation tools and social-template editors are adjacent markets, but they are less direct comparators for shot sequencing and character continuity. LTX is included because its script-to-production workflow overlaps particularly closely with MovieCrew.

## Competitive baseline

| Product | Documented capability most relevant to MovieCrew | Product implication |
| --- | --- | --- |
| Higgsfield Cinema Studio | Reusable Elements, directing controls, project visual settings, before/after extension | Cast sheets and camera menus are baseline features, not sufficient differentiation |
| Google Flow | Frames and ingredients, saved versions, frame reuse, Scenebuilder | Make references and iteration visible in the main creation workflow |
| Runway | Reference media, reusable Workflows, generative editing, Final Cut assembly | Users expect generation, editing, and reusable operations to connect |
| Luma Dream Machine | Video modification with character and keyframe guidance | Preserving an existing performance is a different operation from generating a new one |
| LTX Studio | Script/storyboard, reusable Elements, timeline and sound design | An end-to-end crew proposition already has direct competition |

These entries summarize the official product sources discussed below. They are not feature-quality scores. A feature not verified here should be treated as unknown rather than absent.

### Higgsfield: curated cinematography and persistent creative context

Higgsfield documents shared project settings, reusable characters/locations/props, and an AI Director that prepares prompts for review. Its Cinema Studio 4.0 guide describes forward/backward extension and regional video edits. Those are vendor-described capabilities; this report does not certify seamless output or physical realism. [Higgsfield Cinema Studio guide](https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-cinema-studio).[^1]

Its engineering account describes camera/lens presets tuned through output review and generation metadata carried forward with frames. It also acknowledges that the result is an interpretation of optical character, not literal camera simulation. That is a useful distinction for MovieCrew: a camera selector must produce a perceptible, tested change rather than merely append an equipment name. [Inside Cinema Studio](https://higgsfield.ai/blog/how-we-built-cinema-studio).[^2]

**Recommendation:** maintain a small set of evaluated visual recipes. Persist the recipe version, resolved prompt, provider configuration, and source-frame provenance. Explain presets through visible outcomes such as handheld tension or compressed perspective. Put lens specifications behind an advanced control. Do not copy a large equipment catalogue before demonstrating that the available providers respond reliably to it.

### Google Flow: references as visible creative objects

Flow distinguishes ingredients from first/last frames, supports selecting project assets in prompts, and documents reusable character references. Its editing documentation describes version history, saving individual frames, and arranging/trimming clips in Scenebuilder. [Creation guide](https://support.google.com/flow/answer/16353334?hl=en), [Editing guide](https://support.google.com/flow/answer/16935718).[^3][^4]

Feature support is explicitly model-dependent. The current matrix distinguishes generation, references, editing, and extension rather than treating all models as interchangeable. [Model support matrix](https://support.google.com/flow/answer/16352836?hl=en).[^5]

**Recommendation:** show what each attachment actually controls. A character reference is identity guidance; a start frame specifies a visual boundary; a motion reference supplies performance information. Do not hide a reference substitution behind a generic attachment thumbnail. Preserve generation history as a first-class asset stack, with the accepted version separate from the newest version.

### Runway: editing and repeatable workflows

Runway documents node-based Workflows with generation and media utilities, plus labeled reference media. These provide examples of reusable creative operations and explicit input mapping. [Workflows](https://help.runwayml.com/hc/en-us/articles/45763528999699-Introduction-to-Workflows), [Reference media](https://help.runwayml.com/hc/en-us/articles/52963720640275-Using-reference-media-to-guide-your-generations).[^6][^7]

Its Final Cut guide includes arranging, trimming, splitting, independent audio tracks, and shot detection. Its separate Edit Studio guide describes prompt-based modification of existing footage and lists input restrictions; some additional editing modes remain described as upcoming. [Final Cut](https://help.runwayml.com/hc/en-us/articles/52685547867667-Trimming-and-Assembling-Clips-in-Studio), [Edit Studio](https://help.runwayml.com/hc/en-us/articles/51683104370451-Creating-with-Edit-Studio).[^8][^9]

**Recommendation:** distinguish deterministic timeline edits from generative video edits. Trimming should be immediate and predictable. Changing a costume should create a reviewable paid candidate. MovieCrew should eventually expose reusable recipes, but its primary interface should stay task-based; a node graph would add unnecessary complexity for its initial audience.

### Luma: performance preservation and boundary control

Luma documents workflows combining source video, character references, and edited keyframes. Its Ray3 Modify guide includes a specific caveat about which timestamp is used for an end keyframe in that workflow. The API modification documentation inspected lists Ray 2-family models, illustrating why app capabilities must not be assumed to exist in the same form in an integration endpoint. [Ray3 Modify guide](https://lumalabs.ai/learning-hub/ray3-modify-user-guide), [Modify API guide](https://docs.lumalabs.ai/docs/modify-video).[^10][^11]

**Recommendation:** add performance-preserving editing only through a verified provider adapter. Treat source motion, identity, first frame, and last frame as distinct constraints. Test the actual endpoint, returned duration, and frame behavior. A model accepting two images is not proof that it preserves the intended performance or reaches a required pose.

### LTX: the closest workflow-level comparison

LTX describes concept/script entry points, storyboarding, reusable characters/objects/locations, a timeline, sound design, and collaboration. This overlaps directly with MovieCrew’s brief-to-film ambition. [LTX Studio](https://ltx.io/studio).[^12]

**Recommendation:** make the crew valuable through decisions users can inspect: why a shot is needed, which story event it advances, what changed between takes, and which shots are affected by a character revision. Naming agents Director and Editor is not enough if their inputs do not contain the information needed for those jobs.

## MovieCrew code audit

The following are code observations and their engineering implications. File references refer to the inspected baseline; line numbers may move after subsequent edits.

| Finding | Evidence | Consequence | Priority |
| --- | --- | --- | --- |
| Editor sees IDs only | `agents.py:263–278`; `crew.py:428–430` | No reliable basis for judging action order or dramatic progression | P0 creative quality |
| Prompt writer sees a single shot | `agents.py:246–247`; `crew.py:439` | Neighboring action, prior result, and sequence intent are not explicit inputs | P0 creative quality |
| Continuity checks text | `agents.py:250–260` | A successful textual check cannot validate rendered appearance or action | P0 creative quality |
| Project lookup lacks user context | `portal/app.py:197`; `projects.py` | Project-scoped lookups do not establish user authorization | P0 public launch |
| Settings change process environment | `settings.py`; `portal/app.py:788–808` | Configuration is installation-wide, not per customer | P0 public launch |
| Local paths remain part of persistence | `projects.py:34`; `film_workflow.py:77–83,390` | Database migration alone does not make media durable or portable | P0 public launch |
| Workers use daemon threads and local sets | `film_workflow.py:245–250,522` | Multi-process claims and restart recovery need stronger coordination | P0 public launch |
| Cuts overwrite a JSON document | `film_workflow.py:437–473` | Concurrent editing can lose updates; no persisted undo/revision history | P1 reliability |
| Image reference binding has a four-image ceiling | `portal/app.py:1491–1542` | Face, body, costume, props and environment can exceed the allowed set | P1 creative control |
| Preview reloads one video element per clip | `static/editor.js:35` | Potential gaps and playback-clock discontinuities across cuts | P1 editor quality |
| Export forces 24 fps | `film_workflow.py:494–520` | Output timing and motion cadence may differ from mixed-rate sources | P1 editor quality |

P0 creative quality means necessary to substantiate the filmmaking promise. P0 public launch means necessary before allowing unrelated customers onto a shared service. They are different release gates.

### What should be retained

The implementation already has valuable safeguards. Jobs and cuts belong to projects. Generation requests reserve identifiers, and ambiguous provider submissions are retained as uncertain rather than automatically billed again. Reference preparation verifies downloaded bytes. Approved world-sheet versions can be pinned to shots. Uploads have a size limit and media validation. Exports snapshot the selected cut, and enhancements create candidates rather than silently replacing originals.

Keep these behaviors during migration. The criticism is not that persistence, validation, or recovery are absent; it is that their current scope is a local, single-user installation. A wholesale rewrite would risk losing useful guarantees.

## Sequence intelligence

### The missing production contract

A sequence needs a goal, ordered changes of state, and a reason for each cut. A shot needs an entry state, one observable event, an exit state, and constraints inherited from the film. The current descriptions can contain some of that information in prose, but they do not enforce it as a shared contract.

Add a structured `SequencePlan` with ordered beat IDs, narrative objective, time/location continuity, character state, screen direction, and intended transitions. Add a `ShotPlan` with these fields:

- `beat_id`, `purpose`, `entry_state`, `action`, `exit_state`.
- `character_version_ids`, `location_version_id`, `prop_version_ids`.
- `camera_intent`, `screen_direction`, `eyeline_target`, `lighting_state`.
- `planned_duration`, `transition_in`, `transition_out`, `audio_intent`.
- `required_constraints`, `optional_constraints`, and `evaluation_questions`.

The Editor should receive the full ordered shot summaries and these fields. The Prompter should receive the current shot, adjacent shot summaries, approved visual references, and the most recent accepted boundary state. Give agents only the context needed for the decision, but ensure that context includes the decision’s subject matter.

### A concrete Everest test sequence

| Shot | Event | Required exit state | Why the next shot follows |
| --- | --- | --- | --- |
| 1 | Climber crosses the exposed ridge toward a cornice | Right boot reaches unstable snow; axe remains in right hand | Establish the hazard before showing its failure |
| 2 | Snow fractures under the boot | Foot drops and weight shifts downhill | Motivate the arrest action |
| 3 | Climber drives the axe into the slope | Axe is planted; body stops sliding | Resolve immediate danger |
| 4 | Climber regains balance and turns away from the summit | Body faces the descent; planted axe is recovered | Show a decision and changed direction |

This is a proposed 20-second benchmark, not a claim about footage already produced. Each shot has one principal event. Wardrobe consistency alone cannot make the sequence pass. If shot 2 does not establish the slip, shot 3 becomes unmotivated even when the actor looks identical.

Do not automatically use every preceding final frame as the next opening image. For a continuous take, temporal conditioning may help. For a hard cut to a boot insert, the composition should change. Carry character and event state across that cut while generating a new composition.

### Separate three continuation operations

1. **Next story shot:** create a new composition that advances the next beat. Identity and state continue; the camera may cut.
2. **Continue this take:** preserve motion and camera trajectory using an actual temporal extension capability where supported.
3. **Lead into this clip:** generate a preceding action constrained by an ending frame or verified backward extension.

MovieCrew’s current editor continuation extracts a still at the trimmed boundary and submits it as a first or last frame. That is a valid boundary-conditioned generation, but it does not supply velocity, prior camera motion, or preceding audio. Label it honestly. Native video extension, where available, is a separate provider operation; Luma’s API documentation illustrates that distinction. [Video generation and extension](https://docs.lumalabs.ai/docs/python-video-generation).[^13]

### Prompt compilation and reference selection

Store creative intent independently of provider-specific prose. Compile it into a versioned adapter request. For image-to-video, emphasize the change over time while referencing the established visual composition. For character-reference video, specify identity, environment, action, and framing explicitly. Use negative prompts only when the selected endpoint actually supports them.

Replace the fixed global image-reference limit with endpoint capabilities and a visible reference-selection step. A wide shot might need costume silhouette and environment more than a face close-up. Preserve the current fail-before-generation behavior when requirements do not fit. Never silently drop a required actor or costume reference. Compositing a reference sheet is an optional workaround to evaluate, not guaranteed equivalent to separate inputs.

Persist an input manifest containing immutable asset IDs and hashes, their intended roles, crop/resize transforms, exact prompt, model/endpoint version, settings, and provider job ID. This can prove which inputs were sent. It cannot prove that a model obeyed them; the product should keep those two claims separate.

## Evaluation and economical iteration

Evaluate generated footage, not just prompts. First apply deterministic checks: decodable file, expected duration range, frame size, audio presence, and black/frozen-output detection with tolerances. Then sample beginning/middle/end frames and event-relevant segments for visual review. Identity, wardrobe, prop possession, screen direction, and event completion need separate judgments.

A vision model may help flag likely problems, but its score should be advisory until calibrated against human review. It can misread faces, occluded props, and rapid motion. Always allow users to accept an intentional deviation and record their decision. Do not turn uncertain automatic judgments into unlimited paid retries.

Build a benchmark of 12 short briefs spanning one-person action, two-person interaction, object handoff, costume continuity, camera movement, and dialogue. For each candidate configuration, allow a fixed number of attempts and the same budget. Include both matched-model comparisons, where accessible, and best-workflow comparisons. Record that these answer different questions.

Measure:

| Metric | Definition |
| --- | --- |
| Accepted seconds per dollar | Duration included in a human-approved cut divided by total generation spend |
| Beat completion | Planned observable events clearly represented in the accepted sequence |
| Continuity defects per cut | Identity, prop, spatial or temporal inconsistencies at shot boundaries |
| Attempts per accepted shot | All paid attempts, including rejects, divided by accepted shots |
| Time to first coherent preview | Brief submission to a reviewable sequence that communicates the story |
| Human repair time | Minutes spent correcting references, prompts, sequencing and edits |
| Reliability | Lost-job, duplicate-submit, export-failure and unrecoverable-media rates |

These are proposed measurements; there are no benchmark results yet. Use blind reviewers where possible and retain every attempt to avoid comparing selected highlights. The practical success criterion is reducing repairs and improving usable sequence yield under the same spending limit.

## Editor and UX architecture

### Keep one project and one working context

Preserve the compact timeline and contextual menu. The next interaction improvement is one persistent inspector/composer that follows the selection: a shot exposes action and references; a clip exposes trim and continuation; a character exposes approved identity assets. Keep technical settings behind small controls, while showing the next recommended action in ordinary language.

The crew should provide explanations and proposals within that context. For example, the Director can propose a missing reaction shot, and the Editor can preview its insertion point. A proposal must show the affected clips, cost estimate, and reversible result before paid execution. Every agent action should map to a typed operation rather than directly manipulating UI state.

### Build a versioned timeline model

Represent clips as instances with stable IDs, source-version IDs, source in/out positions, track, timeline position, gain, and transform. The same source can appear twice without confusing selection or extension insertion. Store edit operations such as trim, move, split, insert and replace against a timeline revision. Reject stale revisions with a recoverable conflict response.

Use integer ticks with an explicit rational timebase. Floating-point seconds remain useful at API boundaries, but frame-accurate editing requires a canonical representation and an explicit rounding policy. Proxy playback and export must use the same edit decisions. Add audio gain, fades, one independent music/ambience track, and waveform navigation before pursuing elaborate motion graphics.

The current preview reloads a video element at boundaries; assess stalls before claiming seamless playback. Start with thumbnails, low-resolution proxies and preloaded adjacent clips. Generate a stitched review proxy for longer cuts when needed. A browser compositor is a later option if overlapping tracks justify its complexity.

### Distinguish canvas operations

Keep Fit, Crop, AI expand, and Upscale separate. Fit changes framing with bars; Crop removes edges; AI expand synthesizes new material; Upscale changes resolution and may reconstruct detail. Review expansions and enhancements side by side before replacement. Keep the original resolution, provider output dimensions, export dimensions, and enhancement history in metadata. Selecting 4K export must not imply native 4K generation.

## SaaS architecture and Firebase decision

### Recommended default

For this codebase, the preferred target is **Firebase Authentication + managed PostgreSQL + private R2 + the existing Python API and separate workers**. Firebase Authentication can establish user identity while a different database stores films. The backend verifies the identity token before authorization. [Firebase token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens).[^14]

This is an architectural recommendation, not a requirement to buy or configure services now. PostgreSQL fits the growing relationships between workspaces, memberships, assets, revisions, jobs and usage records. Row-level security can add defense in depth when roles and policies are correctly configured; privileged roles require special care. [PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).[^15]

Firestore remains a viable alternative if minimizing operational components is the overriding preference. The earlier Firebase-plus-R2 proposal is workable. The deeper audit changes the preferred default because MovieCrew needs transactional editing and accounting across related records, not because Firestore lacks persistence or transactions.

| Choice | Best fit | Required discipline |
| --- | --- | --- |
| Firebase Auth + PostgreSQL | Relational ownership, revisions, usage reconciliation, operational reporting | Migrations, connection management, explicit tenancy and backups |
| Firebase Auth + Firestore | Document-oriented application and client subscriptions | Small documents, deliberate indexes, transactional revisions, server authorization |
| Existing SQLite | Local development and single-installation use | Permanent local storage and backups; not the shared-service target |

Do not copy the entire current project JSON into one Firestore document. The standard document limit is 1 MiB, and character histories and generations grow over time. Separate projects, shots, asset versions, jobs, and revisions. [Firestore limits](https://firebase.google.com/docs/firestore/quotas).[^16]

Server Firestore libraries bypass client Security Rules. Consequently, using the Admin SDK would still require authorization in every Python route; securing frontend queries alone would not protect backend project access. [Firestore server security](https://firebase.google.com/docs/firestore/security/insecure-rules).[^17]

### Proposed entities and ownership

| Entity | Essential responsibility |
| --- | --- |
| User | Stable authentication subject and profile; username is display data |
| Workspace / Membership | Owner, editor and viewer permissions |
| Project / Scene / Shot | Story structure and approved production plan |
| Asset / AssetVersion | Immutable media identity, storage key, lineage and provenance |
| SheetVersion / ShotBinding | Approved character/world state used by a specific shot |
| Timeline / TimelineRevision / ClipInstance | Reversible editing and concurrent-save protection |
| GenerationJob / JobAttempt | Submitted intent, provider state, leases and recovery |
| UsageReservation / LedgerEntry | Budget reservation and final cost reconciliation |
| AuditEvent | Who changed permissions, generated media, or selected a new version |

Authorize through workspace membership, then project ownership, then asset/job membership. Carry workspace context into workers; do not trust a project ID supplied by the browser. Test direct URLs, downloads, exports, duplicate-project routes, settings, resumptions, and reference uploads with unrelated users.

### Media persistence and migration

R2 should hold durable originals, proxies, thumbnails, audio and exports. The database stores object keys and checksums, not expiring signed URLs or laptop paths. Issue short-lived read access after authorization. R2 supports presigned S3 URLs; possessing such a URL grants the encoded access until expiry. [R2 presigned URLs](https://developers.cloudflare.com/r2/api/s3/presigned-urls/).[^18]

Migration must cover every local reference in saved sessions as well as the database itself. Inventory and back up the SQLite library, referenced directories, and settings; upload media with checksums; create mappings from local paths to immutable asset IDs; assign existing projects to an owner workspace; and verify playback, reference delivery and export in the new environment. Retain a read-only original backup until restoration is proven.

Provider settings belong in a server-managed secret store with admin-only controls. Ordinary customers should choose creative models and quality, not configure bucket credentials. Workspace-specific bring-your-own-key support can be a later feature, using encrypted secret references rather than process-wide environment mutation.

### Job reliability and spending

Keep the current uncertain-submission state. Replace process-local worker ownership with durable job leases, heartbeat timestamps, attempt records, and a queue or database-backed dispatcher. Record the job and dispatch intent transactionally, then let a worker claim it. Provider callbacks and polling should converge through idempotent state transitions.

There is no general exactly-once guarantee across a database and an external paid API. Use provider idempotency where offered, detect duplicate callbacks, and quarantine ambiguous requests when provider history cannot resolve them. Add per-workspace concurrency limits and global provider quotas before opening paid generation to multiple users.

Reserve a maximum authorized cost before submission, reconcile actual usage once known, and release unused reservations. Preserve provider costs separately from customer credits and adjustments. Do not put credential-bearing URLs or raw provider payloads into customer-visible errors or analytics.

## Economics and operating model

Consumer subscriptions are not a reliable proxy for wholesale generation cost. Higgsfield’s credit documentation distinguishes included access from credit consumption. Runway’s developer documentation publishes model-specific API rates and minimums. Use the actual endpoint’s current rates for MovieCrew estimates. [Higgsfield credits](https://higgsfield.ai/creator-hub/help-center/credits/how-credits-work), [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/).[^19][^20]

Track generation, reference-input charges where applicable, image preparation, failed paid attempts, enhancement, export compute, storage, delivery and support. Pricing by generated seconds alone hides the cost of rejected takes. For each film, report total spend and accepted duration, and give the user a budget remaining indicator.

A draft-first workflow can control risk: approve the beat plan, review reference images, generate a short representative sequence, then approve the larger spend. A cheaper draft and an expensive final generation are not necessarily identical performances; distinguish deterministic upscaling from a new generation that may change the action.

Launch with explicit allowances and spending caps. Validate repeat usage and usable-footage cost before designing broad unlimited plans. The initial market hypothesis is solo creators and small teams making short narrative pieces; willingness to pay and retention still need customer evidence.

## Implementation sequence and acceptance gates

The following is an order of delivery, not a calendar promise. Effort depends on deployment choices, provider integration restrictions and live-generation validation.

| Stage | Deliverable | Acceptance gate |
| --- | --- | --- |
| 0 — Preserve | Backup, media inventory, owner mapping, benchmark fixtures | Restore one existing film including references and export in isolation |
| 1 — Sequence contract | Full Editor context; adjacent-shot Prompter context; entry/action/exit state | Everest benchmark has explicit causal beats and human-approved story order |
| 2 — Provider contract | Role-aware references, capability registry, immutable input manifests | Unsupported combinations stop before billing; sent assets are inspectable |
| 3 — SaaS foundation | Authentication, memberships, private media, admin secrets | Two-user isolation tests cover every protected route and asset path |
| 4 — Durable execution | Job leases, idempotency, reservations and reconciliation | Crash/retry tests preserve jobs and prevent known duplicate submissions |
| 5 — Editor reliability | Clip IDs, revisioned saves, proxy preview, audio track | Concurrent saves cannot silently overwrite; preview/export timing matches |
| 6 — Quality loop | Output review, targeted repair, cost/yield benchmark | Measured improvement over baseline at equal budget, with all attempts retained |
| 7 — Paid pilot | Clear allowance, usage history, support and recovery | A small invited cohort completes films without operator intervention |

Stages 1–2 can improve the private local product before the SaaS launch gates are complete. Stages 3–4 are required before shared paid access. Introduce component boundaries in the frontend incrementally: project store, asset browser, composer, timeline, jobs and account controls. Replace the current chain of global function overrides rather than adding more overrides for collaboration and revisions. A framework switch by itself will not solve state ownership.

For public deployment, add structured logs and traces keyed by workspace, project, shot, job and attempt; monitor queue age, provider latency, download failures and storage pressure. Exercise backup restoration, token revocation, permission changes, billing reconciliation and server termination during each job phase. These checks should be release gates with repeatable fixtures.

## Immediate engineering tasks

1. Change `EditorAgent.build_user` to receive story beats and shot summaries; update its call site and tests. Verify ordering decisions respond to meaningful scene changes rather than ID patterns.
2. Introduce the sequence/shot contract and pass adjacent context into the Prompter. Preserve the original approved brief and version every generated plan.
3. Build an input-manifest preview showing the actual character, costume, location and boundary references. Keep payload verification separate from visual adherence review.
4. Inventory all local media and design the ownership migration before selecting a production database. Establish Firebase Auth and PostgreSQL as the proposed default; make an explicit architecture decision before implementation.
5. Add stable clip-instance IDs and timeline revisions before collaborative editing. Preserve existing cuts through a tested migration.

Do not spend the next cycle building dozens of model presets, a complex node editor, automatic full-film regeneration, or elaborate compositing. Demonstrating coherent sequences, recoverable paid work and private persistent projects will provide stronger evidence that MovieCrew is ready to become a product.

## Sources

External sources are official product or engineering documentation, accessed 13 September 2026. Undated pages are recorded as undated; rolling documentation may change after this assessment.

[^1]: Higgsfield. “How do I use Cinema Studio?” Dated 1 August 2026. [Original source](https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-cinema-studio)
[^2]: Higgsfield. “Inside Higgsfield #1: How We Built Cinema Studio.” Dated 12 August 2026; page also indicates later updates. [Original source](https://higgsfield.ai/blog/how-we-built-cinema-studio)
[^3]: Google Flow Help. “Create videos in Google Flow.” Undated. [Original source](https://support.google.com/flow/answer/16353334?hl=en)
[^4]: Google Flow Help. “Edit videos & build scenes in Google Flow.” Undated. [Original source](https://support.google.com/flow/answer/16935718)
[^5]: Google Flow Help. “Learn about Google Flow models & supported features.” Undated. [Original source](https://support.google.com/flow/answer/16352836?hl=en)
[^6]: Runway Help. “Introduction to Workflows.” Undated. [Original source](https://help.runwayml.com/hc/en-us/articles/45763528999699-Introduction-to-Workflows)
[^7]: Runway Help. “Using reference media to guide your generations.” Undated. [Original source](https://help.runwayml.com/hc/en-us/articles/52963720640275-Using-reference-media-to-guide-your-generations)
[^8]: Runway Help. “Trimming and Assembling Clips in Studio.” Undated. [Original source](https://help.runwayml.com/hc/en-us/articles/52685547867667-Trimming-and-Assembling-Clips-in-Studio)
[^9]: Runway Help. “Creating with Edit Studio.” Undated. [Original source](https://help.runwayml.com/hc/en-us/articles/51683104370451-Creating-with-Edit-Studio)
[^10]: Luma, Davicho Barona. “Ray3 Modify: User Guide.” Dated 12 December 2025. [Original source](https://lumalabs.ai/learning-hub/ray3-modify-user-guide)
[^11]: Luma API documentation. “Modify Video.” Undated. [Original source](https://docs.lumalabs.ai/docs/modify-video)
[^12]: LTX. “The AI platform for video production.” Undated. [Original source](https://ltx.io/studio)
[^13]: Luma API documentation. “Video Generation.” Undated. [Original source](https://docs.lumalabs.ai/docs/python-video-generation)
[^14]: Firebase. “Verify ID Tokens.” Rolling documentation. [Original source](https://firebase.google.com/docs/auth/admin/verify-id-tokens)
[^15]: PostgreSQL 18 documentation. “Row Security Policies.” Rolling documentation. [Original source](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
[^16]: Firebase. “Usage and limits.” Rolling documentation. [Original source](https://firebase.google.com/docs/firestore/quotas)
[^17]: Firebase. “Fix insecure rules.” Rolling documentation. [Original source](https://firebase.google.com/docs/firestore/security/insecure-rules)
[^18]: Cloudflare R2 documentation. “Presigned URLs.” Rolling documentation. [Original source](https://developers.cloudflare.com/r2/api/s3/presigned-urls/)
[^19]: Higgsfield. “How Do Higgsfield Credits Work.” Page indexed as published August 2026. [Original source](https://higgsfield.ai/creator-hub/help-center/credits/how-credits-work)
[^20]: Runway Dev. “API Pricing & Costs.” Rolling documentation. [Original source](https://docs.dev.runwayml.com/guides/pricing/)

### Code evidence

MovieCrew, commit `70a863c`, local repository `/Users/lakshmipriyasridharan/AI/MovieCrew/Moviecrew`. Relevant source files: `moviecrew/agents.py`, `crew.py`, `schema.py`, `projects.py`, `settings.py`, `assets.py`, `portal/app.py`, `portal/world.py`, `portal/film_workflow.py`, `portal/film_enhance.py`, `portal/static/editor.js`, and `portal/static/studio.html`. The audit concerns this checkout; it does not establish the state of GitHub main or any other deployment.
