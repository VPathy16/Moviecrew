## Problem

Current settings modify installation-wide environment values; ordinary customers must not control shared provider credentials.

## Scope

Move production credentials behind server-managed secret references and admin-only configuration. Keep customer settings limited to profile/preferences. Preserve local settings migration, mask secrets, and define provider-cache invalidation.

## Acceptance criteria

- [ ] Customers cannot view or update provider/R2 keys or deployment paths.
- [ ] Existing connections migrate without exposing values in responses or logs.
- [ ] Credential rotation affects new jobs without changing persisted job provenance.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/38
- https://github.com/VPathy16/Moviecrew/issues/39

## Tracking

Priority: **P0** · Area: **SaaS foundation**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
