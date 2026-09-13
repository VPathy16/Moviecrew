## Problem

Film sound currently lacks the basic independent control needed for coherent sequences.

## Scope

Add one music/ambience track initially, waveform navigation, clip gain/mute, fades and audio offsets. Keep edit operations deterministic and persist them in timeline revisions.

## Acceptance criteria

- [ ] Preview and export use matching audio offsets and fade behavior.
- [ ] Silent clips, mixed sample rates and trim boundaries export without unintended gaps or clipping.
- [ ] Undo and reload preserve sound edits; uploads remain workspace-owned.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/50
- https://github.com/VPathy16/Moviecrew/issues/51

## Tracking

Priority: **P1** · Area: **Editor**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
