## Top implementation priority

Add an explicit Director approval gate before Writer generation. This is the first step in the coherent-filmmaking milestone tracked by #32, ahead of #34–36.

## Problem

The current pipeline calls Writer immediately after Director completes. The Director screen displays the resulting outline but does not let the user refine it, define characters and approve the direction before scenes are written.

## Required flow

Concept and creative brief → Director proposal → edit story and characters / regenerate direction → approve and continue to Writer.

## Scope

- Pause and persist after Director generation; do not invoke Writer automatically.
- Show an editable title, logline and story outline in the compact Director workspace.
- Support adding, editing and removing character definitions: name, role, motivation and essential identity notes. These become the cast requirements for later visual character sheets; image generation is not required at this step.
- Provide a small feedback composer and Regenerate direction action. Carry the creative brief, current edits and character definitions into regeneration. Preserve explicitly locked decisions.
- Retain previous Director revisions and allow restoring one. Do not silently overwrite a user-edited draft with an asynchronous result.
- Provide one clear Approve & continue to Writer action. Writer receives exactly the approved Director revision and cast definitions.
- Persist draft, revision and approval state across refresh/restart. Prevent duplicate generation and show progress, errors and retry paths.
- If an approved direction changes after scenes exist, retain the accepted work and mark dependent scenes as needing review. Do not silently regenerate Writer or spend credits.
- Keep legacy completed films readable and preserve their existing cuts and assets.

## Acceptance criteria

- [ ] Creating a film ends at a persisted Director review state; a spy/mock proves Writer has not been called.
- [ ] User edits the story, adds a character, regenerates with feedback and can restore the earlier revision.
- [ ] Approval starts Writer once using the exact approved outline and character definitions.
- [ ] Refresh, duplicate clicks, failed generation and stale regeneration results cannot lose edits or start unwanted downstream jobs.
- [ ] Changing direction after Writer completion preserves prior scenes and identifies stale dependencies.
- [ ] The UI remains compact, with contextual editing and a clear next action.

## Dependencies and validation

Ready to start. Coordinate the new draft/revision contract with #34; then #35 and #36 consume approved direction. Use offline tests first. Live generation must use an explicit budget. No cloud migration is required for this local workflow improvement.
