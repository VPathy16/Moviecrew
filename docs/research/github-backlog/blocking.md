## Problem

Multi-character positioning and prop interactions need explicit spatial guidance beyond identity references.

## Scope

Represent screen positions, facing direction, gaze targets and prop contact in shot state. Offer an optional camera-view staging guide with coloured figures and matching text bindings to approved character IDs. Keep composition guidance distinct from identity, wardrobe and visual look. Retain the source composition and derive revisions from it to avoid cumulative drawing drift. Use only provider-supported reference roles; expose limitations. Simple shots must work without a staging-map step.

## Acceptance criteria

- [ ] A two-character handoff fixture defines who holds the object before and after the action.
- [ ] Guide-to-character mapping remains stable after edits; unknown bindings are rejected.
- [ ] Visual review checks positions, direction and style contamination on a budgeted trial.

## Dependencies

- #34
- #45

## Source and limits

Inspired by the published [The Trigger production breakdown](https://higgsfield.ai/@higgsfield.studio/projects/trigger). These are MovieCrew implementation proposals, not guarantees of model behaviour. Do not copy or execute third-party skill files. Preserve existing films; live trials require an explicit budget.

Part of #32. Priority: **P1**.
