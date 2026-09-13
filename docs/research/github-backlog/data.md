## Problem

Single-user SQLite payloads need explicit ownership, revisions and transactional job/accounting records.

## Scope

Write an architecture decision evaluating Firebase Auth plus PostgreSQL against Firebase Auth plus Firestore. PostgreSQL is the proposed default, not an already-approved deployment. Implement repository interfaces and versioned migrations for users, workspaces, memberships, projects, assets, timelines, jobs and usage; keep SQLite for local mode.

## Acceptance criteria

- [ ] Document the selected store, operating requirements and rollback strategy.
- [ ] Import a backup into an owner workspace with stable project IDs.
- [ ] Migration is resumable and repeatable; no cloud purchase or secret is required by unit tests.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/33

## Tracking

Priority: **P0** · Area: **SaaS foundation**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
