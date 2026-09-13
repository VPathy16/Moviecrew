## Review the assembled sequence

Review adjacent shots and the assembled cut, not only isolated frames. Check causal progression, repeated actions, identity/state drift, screen direction and missing coverage. Use reviewer findings to request specific repair candidates rather than regenerate the whole film.

## Problem

Textual continuity checks cannot detect defects in rendered action or appearance.

## Scope

Add deterministic media checks and sampled visual review for identity, costume, prop state, screen direction and event completion. Calibrate advisory model judgments against benchmark reviewers and retain human override.

## Acceptance criteria

- [ ] Tests include corrupt/black/frozen media and deliberately inconsistent reference fixtures.
- [ ] Review shows evidence and uncertainty rather than treating a score as proof.
- [ ] A failed review does not trigger uncontrolled paid retries; accepted deviations remain recorded.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/46
- https://github.com/VPathy16/Moviecrew/issues/48

## Tracking

Priority: **P1** · Area: **Evaluation**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
