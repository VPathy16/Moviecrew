## Problem

Persisted local paths prevent portable deployments and do not by themselves provide private cloud media access.

## Scope

Introduce immutable asset IDs, storage keys, checksums and provenance. Upload originals/references/proxies/exports through a resumable migration. Authorize reads before issuing bounded signed access; store keys rather than expiring URLs.

## Acceptance criteria

- [ ] An imported film plays and exports with the original local directory unavailable.
- [ ] Reference delivery and checksum validation succeed without public bucket access.
- [ ] Expired URLs can be refreshed only by authorized users; missing objects and partial uploads recover cleanly.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/33
- https://github.com/VPathy16/Moviecrew/issues/37
- https://github.com/VPathy16/Moviecrew/issues/39

## Tracking

Priority: **P0** · Area: **Persistence**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
