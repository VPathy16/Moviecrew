## Problem

Cuts are saved as overwritten JSON; duplicate source clips and concurrent edits need stable identity and conflict handling.

## Scope

Create stable clip IDs, source-version bindings, canonical timebase, timeline revisions and typed trim/move/split/insert/replace operations. Persist undo/history and migrate existing cuts.

## Acceptance criteria

- [ ] Two concurrent saves cannot silently overwrite one another.
- [ ] Repeated use of one source video has independent clip identity and extension targets.
- [ ] Reload preserves accepted edit history; migration/export tests retain the original cut.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/37

## Tracking

Priority: **P1** · Area: **Editor reliability**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
