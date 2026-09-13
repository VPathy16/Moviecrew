## Problem

Existing project payloads reference local media paths. A database-only migration would leave films incomplete.

## Scope

Inventory the database, settings locations, references, generated media and exports. Build a backup manifest with checksums and a restore procedure. Keep secrets outside the repository and issue attachments.

## Acceptance criteria

- [ ] Restore an existing film in an isolated environment, including character references and timeline.
- [ ] Validate playback, reference delivery and export after restore.
- [ ] Report missing assets explicitly and preserve the original data until migration is accepted.

## Dependencies

None; ready to start.

## Tracking

Priority: **P0** · Area: **Persistence**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
