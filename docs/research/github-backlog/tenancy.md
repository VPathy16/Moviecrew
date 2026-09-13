## Problem

Project-scoped IDs provide association but do not establish user authorization.

## Scope

Create owner/editor/viewer policies and centralized authorization. Cover projects, legacy session routes, duplication, references, world sheets, drafts, jobs, resume, cuts, exports and downloads. Carry workspace context into background jobs.

## Acceptance criteria

- [ ] Two unrelated users cannot read or mutate each other’s work using direct IDs or URLs.
- [ ] Viewer cannot generate, edit, change membership or spend credits.
- [ ] Permission changes apply consistently to new requests; return safe non-disclosing errors.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/37
- https://github.com/VPathy16/Moviecrew/issues/38

## Tracking

Priority: **P0** · Area: **SaaS foundation**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
