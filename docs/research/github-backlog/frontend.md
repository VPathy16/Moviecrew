## Problem

The growing chain of global function overrides makes state ownership and later collaboration fragile.

## Scope

Extract project store, asset browser, composer, timeline, job status and account modules incrementally. Define typed operations and lifecycle cleanup; avoid a framework rewrite without a concrete need.

## Acceptance criteria

- [ ] Existing image/video creation and timeline workflows pass regression checks.
- [ ] Navigation stops obsolete polling/listeners and preserves intended drafts.
- [ ] Each state mutation has an explicit owner; repeated mounting does not duplicate controls or actions.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/50

## Tracking

Priority: **P1** · Area: **Frontend architecture**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
