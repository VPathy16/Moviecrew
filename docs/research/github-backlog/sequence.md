## Acting and causal direction

Add per-character goal, obstacle and observable tactic to the scene contract. Express performance through actions, gaze and timing; do not rely solely on emotion adjectives. Track prop ownership and physical condition across shots. Underplaying is a creative choice, not a universal rule.

## Director approval comes first

Start with #62: let the user refine the Director story and characters, regenerate direction and explicitly approve it before Writer runs. The active order is #62 → #34 → #35 → #36, followed by the short-sequence quality check.

## First implementation priority

This is the first task in the active #34 → #35 → #36 filmmaking milestone. Give scenes an event, character goal, obstacle and turning point; give shots an entry state, observable action and exit state. Bind approved character/costume, location and prop versions without overwriting originals. Keep this detail behind compact scene cards rather than adding a large form.

Acceptance example: the climber tests a foothold → the foothold breaks → the rope catches him → he checks the damaged anchor. Each shot must advance the event and inherit the required physical state. Preserve the existing hazard/slip/arrest/retreat fixture as additional coverage.

## Problem

Shot descriptions do not enforce narrative progression or state transitions.

## Scope

Add sequence goals and ordered beats; shot purpose, entry state, one observable action, exit state, screen direction, audio intent and approved asset-version bindings. Preserve legacy projects through defaults or migration.

## Acceptance criteria

- [ ] The four-shot Everest hazard/slip/arrest/retreat fixture has explicit causal transitions.
- [ ] Validate missing beats, duplicate IDs and contradictory required states.
- [ ] Version new plans without overwriting accepted plans; existing films still load.

## Dependencies

- #62 — Director review and approval. Coordinate contracts while implementing.

## Tracking

Priority: **P0** · Area: **Story quality**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
