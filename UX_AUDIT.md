# MovieCrew workflow audit — 12 September 2026

The workspace exposes the existing crew and generation components, but is not
an end-to-end consumer filmmaking product yet. The UI should not imply that a
completed shot plan is a finished film.

## Intended customer journey

Idea → Director’s vision → Writer’s scenes → Visual design → Camera and edit
plan → Storyboard images → Review images → Generate videos → Choose clips →
Final edit and sound → Export.

Crew members remain accessible throughout this journey. The ordering of backend
agent calls should not be presented as the complete production lifecycle.

## Findings

1. **Editor is an edit planner today.** `MovieCrew.make` calls Editor before
   Prompter to establish shot order/chains and consistency anchors. Editor is
   given shot IDs, not completed clips. This order is appropriate for planning,
   but there is no corresponding post-production editor in the portal. Updated
   the role description and output to make this distinction explicit.
2. **Generated-video discovery was poor.** Saved renders appeared as download
   links beneath a camera preview. A failed model catalog request blocked the
   entire view. Added a separate Generated videos section with inline players,
   downloads, empty/error states, and independent handling of the three requests.
   Completed jobs now refresh that gallery. Submission is locked immediately
   to prevent duplicate clicks while the request is in flight.
3. **Video creation still depends on Blender previews.** The render endpoint
   resolves a take first, and the workspace has no direct image-to-video flow.
   Customers cannot yet select any storyboard frame and simply animate it.
4. **Image and video directions can diverge.** Image edits are stored in
   `draft_prompts`; video rendering uses the canonical render-plan intent.
   Image model aspect ratio/options also do not become video settings. This
   needs explicit per-media settings and a reviewable handoff, not silent copying.
5. **Selecting an image is different from approving it for production.** Version
   selection changes the storyboard; approval promotes appropriate reference
   frames. The UI needs a clear indication of which references each video will
   use, and whether later image changes need approval again.
6. **Final editing is not connected.** Assembly code exists in `assembly.py`,
   but the portal has no final timeline, preferred video selection, trim/audio
   controls, or assembled-film export endpoint. Editor currently displays only
   planned shot ordering and connected sequences.
7. **Video recovery is incomplete.** Active jobs/context are held in memory;
   a browser reload loses its polling state, and a server restart loses the job
   context. A polling error cannot establish whether generation stopped. Jobs
   need durable status, resumable polling and reconciliation before retries.
8. **Video ownership needs work before SaaS.** The takes/renders library uses
   scene and shot IDs under a shared root, not project/account identity. Different
   projects can reuse those IDs. Filtering the UI alone will not fix ownership.
   `_list_renders` can also return the same shot-level render for multiple takes;
   the gallery now deduplicates display by job ID, but lineage should be fixed
   in storage.
9. **Crew interaction is still mostly review.** Role artifacts are visible;
   per-role feedback, proposed revisions, approval and downstream invalidation
   are not implemented. These are central to the intended product experience.

## Recommended implementation order

1. Establish project-owned media and durable video jobs so assets and running
   work cannot be confused across films or lost during navigation/restarts.
2. Add a clear storyboard-to-video handoff: selected frame, prompt, model,
   supported video settings, price estimate, progress and retry/recovery.
3. Add preferred-clip selection and a first final-edit workspace: sequence,
   preview, simple trims/audio and export; reuse assembly code after addressing
   missing-audio inputs and connecting it to selected saved renders.
4. Add crew feedback as proposed, reviewable revisions with explicit downstream
   effects; retain the current usable versions until changes are approved.

## Verification and limits

Read the crew pipeline, project persistence, frame selection, render request
construction, render gallery, job polling and assembly implementation. Inspected
current local preview data: Shot 1 has three camera previews and no saved renders;
Shot 2 has neither. Verified the revised video empty/setup state in the browser
and checked JavaScript syntax. No paid video generation was performed, and this
is not a claim of successful end-to-end live generation or export.

## Implementation follow-up — 13 September

The first film journey is now connected in the local preview: project-owned video
jobs and media, explicit image reference/direction, saved video settings, clip
uploads, final clip selection/order/trims/mute, and saved MP4 export. See WORKSPACE.md
for verified behavior and limits. Earlier findings describe the state at audit time.
Conversation-based crew revision, account isolation, distributed worker leasing,
legacy asset migration and advanced sound/timeline editing remain future work.
