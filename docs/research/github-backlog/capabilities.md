## Problem

Model settings and reference limits are partly global or hardcoded, while endpoints support different operations.

## Scope

Describe endpoint-specific frames, identity/motion/audio references, count limits, durations, ratios, resolution, negative prompts, edit/extend operations and costs. Validate combinations before upload or paid submission. Preserve user intent when changing models.

## Acceptance criteria

- [ ] Unsupported operations stop before billing with an actionable explanation.
- [ ] Capability snapshots and refresh/failure behavior are tested.
- [ ] Model changes never silently discard required inputs or replace an operation with a different one.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/34

## Tracking

Priority: **P1** · Area: **Provider integration**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
