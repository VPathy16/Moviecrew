## Problem

Existing enhancement adapters need endpoint validation and clearer resolution/provenance reporting before production claims.

## Scope

Verify provider limits and preservation behavior; distinguish bars/crop/AI expansion/upscale; add side-by-side review and source/output/export dimension metadata. Keep approved originals immutable.

## Acceptance criteria

- [ ] Contract tests cover provider errors, recovery, audio preservation and trimmed inputs.
- [ ] A separately budgeted live run verifies each supported endpoint before general availability.
- [ ] 4K export never implies native 4K generation; replacement remains explicit.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/44
- https://github.com/VPathy16/Moviecrew/issues/46
- https://github.com/VPathy16/Moviecrew/issues/51

## Tracking

Priority: **P2** · Area: **Finishing**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
