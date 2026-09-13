## Problem

Text-only lighting and lens instructions can produce mismatched neighbouring shots.

## Scope

Add a scene look record with palette, exposure intent, composition, aspect ratio and camera style. Generate or select location images and representative shot stills, approve them, and bind their versions to relevant shots. Support separate looks for flashbacks or locations. Distinguish a look reference from a compulsory first frame; do not force every shot to share one composition. Compare text-only and image-guided outcomes with matched settings before adopting model-specific techniques as defaults.

## Acceptance criteria

- [ ] Adjacent shots inherit the approved scene look while retaining their own framing.
- [ ] A look revision identifies affected shots without overwriting approved media.
- [ ] Actual reference roles and unsupported provider combinations are visible before submission.
- [ ] A small controlled comparison records drift and reviewer judgement, without claiming visual guarantees.

## Dependencies

- #34
- #45

## Source and limits

Inspired by the published [The Trigger production breakdown](https://higgsfield.ai/@higgsfield.studio/projects/trigger). These are MovieCrew implementation proposals, not guarantees of model behaviour. Do not copy or execute third-party skill files. Preserve existing films; live trials require an explicit budget.

Part of #32. Priority: **P1**.
