## Problem

Daemon threads and process-local active sets cannot coordinate claims reliably across application processes.

## Scope

Add persisted job attempts, transactional dispatch, leases, heartbeats, provider IDs and idempotent transitions. Retain uncertain-submission quarantine. Add per-workspace and provider concurrency limits and explicit cancellation semantics.

## Acceptance criteria

- [ ] Crash tests cover before submission, ambiguous submission, polling, download and export.
- [ ] Two workers cannot concurrently own the same active lease; expired claims can be recovered safely.
- [ ] Duplicate callbacks/retries do not create duplicate accepted outputs or blindly resubmit possibly billed jobs.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/37
- https://github.com/VPathy16/Moviecrew/issues/39
- https://github.com/VPathy16/Moviecrew/issues/41

## Tracking

Priority: **P0** · Area: **Reliability**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
