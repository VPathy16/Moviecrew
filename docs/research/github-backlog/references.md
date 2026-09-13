## Problem

The four-image ceiling can conflict with face, body, costume, props and location requirements.

## Scope

Add role-aware reference selection using approved asset versions and endpoint limits. Prioritize by shot purpose, show exclusions and permit explicit user choice. Treat reference-sheet compositing as an optional evaluated strategy.

## Acceptance criteria

- [ ] The user can inspect character, costume, location and boundary roles before generating.
- [ ] No required reference is silently dropped or substituted.
- [ ] Tests cover multiple characters, over-capacity inputs, stale approvals and cross-workspace references.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/44

## Tracking

Priority: **P1** · Area: **Creative control**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
