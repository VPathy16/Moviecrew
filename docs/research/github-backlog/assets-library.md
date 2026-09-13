## Problem

Approved identities and environments should be reusable without copying private media or mutating historical shots.

## Scope

Add a workspace asset library with search, versioned reuse and explicit project bindings. Reusing an asset preserves provenance; updates mark affected shots for review without rewriting accepted versions.

## Acceptance criteria

- [ ] Authorized projects can bind approved versions; unrelated workspaces cannot access them.
- [ ] A costume revision lists affected shots and leaves historical inputs unchanged.
- [ ] Duplicate/import operations preserve ownership and reference lineage.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/39
- https://github.com/VPathy16/Moviecrew/issues/40
- https://github.com/VPathy16/Moviecrew/issues/46

## Tracking

Priority: **P2** · Area: **Asset workflow**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
