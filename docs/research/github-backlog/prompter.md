## Self-contained direction compiler

Compile ordered sections for scene intent, approved reference roles, physical state, camera-relative blocking, timed action, performance and sound. Include only relevant constraints within provider limits. Prefer concrete positive descriptions where suitable and test negative-prompt behaviour per model; never hard-code the claim that negation always fails. Validate contradictions before submitting.

## First implementation priority

Third task in the active #34 → #35 → #36 milestone. Compile self-contained provider prompts from scene intent, current and adjacent shot states, approved asset descriptions and role-specific image bindings. Include observable timed action and intended ending state; resolve references explicitly rather than relying on phrases such as “same as before.” Keep identity, staging and visual-style references distinct. Preserve approved portraits and asset versions.

Completion requires a reviewed short sequence, not merely passing schema tests. Prepare offline checks first; live generation uses an explicit budget. Record actual supplied inputs and distinguish successful reference delivery from visible adherence in the result.

## Problem

The Prompter receives one shot at a time, without explicit neighboring events or the last accepted outcome.

## Scope

Pass current and adjacent shot summaries, approved reference bindings and sequence intent. Separate creative intent from provider prose and version the compiler. Distinguish hard cuts from continuous action.

## Acceptance criteria

- [ ] A hard-cut insert retains story/identity state without copying the previous composition.
- [ ] Prompts contain a feasible observable action and intended exit state.
- [ ] Tests cover neighbor changes, immutable accepted inputs and legacy prompt compatibility.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/34
- https://github.com/VPathy16/Moviecrew/issues/35

## Tracking

Priority: **P0** · Area: **Story quality**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
