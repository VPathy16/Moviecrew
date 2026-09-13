## Problem

Existing single-user tests do not prove safe shared access or correct distributed retries.

## Scope

Build a two-user permission matrix and integration suite for direct API/media paths, stale revisions, duplicate requests, job crashes and permission changes. Audit legacy endpoints, not just new workspace routes.

## Acceptance criteria

- [ ] CI fails on cross-workspace access or forbidden spending.
- [ ] Concurrent cut-save and worker-claim tests demonstrate safe conflict behavior.
- [ ] Document covered routes and remaining gaps; public launch is blocked until the matrix passes.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/39
- https://github.com/VPathy16/Moviecrew/issues/40
- https://github.com/VPathy16/Moviecrew/issues/41
- https://github.com/VPathy16/Moviecrew/issues/42
- https://github.com/VPathy16/Moviecrew/issues/43
- https://github.com/VPathy16/Moviecrew/issues/50

## Tracking

Priority: **P0** · Area: **Launch gate**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
