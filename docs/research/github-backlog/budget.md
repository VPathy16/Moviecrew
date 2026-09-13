## Problem

Cost estimates alone do not prevent concurrent overspending or establish an auditable customer balance.

## Scope

Add transactional reservations, provider-cost records, customer debit/credit entries, spending caps and idempotent reconciliation. Track failed paid attempts and distinguish unknown provider cost from zero.

## Acceptance criteria

- [ ] Concurrent requests cannot exceed the workspace budget.
- [ ] Duplicate events settle a reservation once; failed and uncertain jobs follow documented policies.
- [ ] Users see estimated, reserved and settled amounts; support can reconcile a job without secret payloads.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/37
- https://github.com/VPathy16/Moviecrew/issues/39
- https://github.com/VPathy16/Moviecrew/issues/42

## Tracking

Priority: **P0** · Area: **Economics**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
