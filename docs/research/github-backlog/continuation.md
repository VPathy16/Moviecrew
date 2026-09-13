## Problem

The editor currently uses a boundary still, which does not carry motion or audio history.

## Scope

Offer Next story shot, Continue this take and Lead into this clip. Use verified temporal-extension endpoints where supported and label still-boundary fallback honestly. Preview candidates before insertion.

## Acceptance criteria

- [ ] Each action preserves the intended story state and exposes its reference mode.
- [ ] Unsupported temporal extension cannot masquerade as seamless continuation.
- [ ] Tests verify trimmed boundaries, first/last roles and insertion into the intended clip instance; live endpoint checks use an explicit budget.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/36
- https://github.com/VPathy16/Moviecrew/issues/44
- https://github.com/VPathy16/Moviecrew/issues/46

## Tracking

Priority: **P1** · Area: **Creative control**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
