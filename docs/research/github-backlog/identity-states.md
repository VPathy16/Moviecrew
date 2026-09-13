## Problem

Character development needs an immutable identity anchor and explicit costume, injury and time-period variants.

## Scope

Keep the approved face original immutable. Create named character-state versions linked to that identity: wardrobe, accessories, dirt, injury and age or timeline state. Preserve original portrait pixels when assembling sheets using deterministic compositing; do not regenerate the portrait merely to lay out a sheet. Image-model edits remain candidates and must not be presented as pixel-preserving. Bind a shot to an approved state, with readable names and stable IDs. Required character, location and prop approvals must be checked before shot generation. Reuse existing world/version machinery rather than creating a second asset system.

## Acceptance criteria

- [ ] The approved face checksum survives sheet assembly and creation of costume variants.
- [ ] User can approve or reject a state independently; original and previously accepted shot bindings remain unchanged.
- [ ] Missing required assets stop submission with a specific next action.
- [ ] Compare actual generated identity against the anchor; reference delivery alone does not pass visual review.

## Dependencies

- #62
- #34

## Source and limits

Inspired by the published [The Trigger production breakdown](https://higgsfield.ai/@higgsfield.studio/projects/trigger). These are MovieCrew implementation proposals, not guarantees of model behaviour. Do not copy or execute third-party skill files. Preserve existing films; live trials require an explicit budget.

Part of #32. Priority: **P0**.
