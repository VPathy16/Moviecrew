## Problem

Users need the crew’s help without navigating repeated forms or losing their working context.

## Scope

Use a contextual composer/inspector, clear next action, accessible compact controls and visible reference/cost summaries. Crew proposals show affected shots and reversible operations before paid execution.

## Acceptance criteria

- [ ] Users can edit a prompt, inspect references and return to a selected clip without losing context.
- [ ] Keyboard/touch paths exist for contextual actions; focus and error recovery are tested.
- [ ] Paid proposals require review and explicit generation; no agent directly spends through UI side effects.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/53
- https://github.com/VPathy16/Moviecrew/issues/36
- https://github.com/VPathy16/Moviecrew/issues/46

## Tracking

Priority: **P1** · Area: **UX**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
