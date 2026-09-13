## Planned transitions and coverage

Return a reason for each cut, required coverage and expected movement or sound connection. Request editable head/tail handles within supported generation durations and record the actual available handles; do not assume arbitrary frame counts can be requested. Keep the short Everest sequence as the first acceptance case.

## First implementation priority

Second task in the active #34 → #35 → #36 milestone. The Editor must receive scene intent and shot states, explain causal ordering and identify missing coverage or repeated actions. Assess transitions using screen direction, action and sound intent. Validate on the four-shot Everest sequence before scaling to a full film.

## Problem

EditorAgent.build_user receives only shot IDs, preventing informed judgments about story order.

## Scope

Update agents.py and crew.py to send the sequence objective, shot summaries, durations and entry/exit states. Return order, transition choices and concise reasons while retaining ID/order validation.

## Acceptance criteria

- [ ] Tests show meaningful action changes influence the supplied editorial context.
- [ ] Unknown, duplicated or missing shot IDs are rejected or normalized explicitly.
- [ ] The Everest fixture has human-reviewable ordering and cut rationale.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/34

## Tracking

Priority: **P0** · Area: **Story quality**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
