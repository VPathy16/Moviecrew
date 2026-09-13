## Problem

Users need to verify which references and settings were actually sent, separately from whether the model followed them.

## Scope

Save asset IDs/hashes, roles, transforms, resolved prompt, compiler version, endpoint/settings, provider job ID and parent generation. Add a readable input inspector and immutable version history.

## Acceptance criteria

- [ ] Every generation can show its submitted inputs without exposing signed URLs or keys.
- [ ] Changing a sheet or draft does not rewrite old manifests.
- [ ] Provider request tests match the stored manifest; UI labels sent-input evidence separately from adherence review.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/45
- https://github.com/VPathy16/Moviecrew/issues/40

## Tracking

Priority: **P1** · Area: **Provenance**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
