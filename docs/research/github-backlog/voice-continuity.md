## Problem

Dialogue across independently generated clips can change voice and break the film.

## Scope

Store a versioned voice brief per character and bind it to dialogue generation. Support approved voice references only through capable providers; descriptive prose alone must not be represented as voice cloning or a guarantee. Provide a candidate audio replacement path with sync review, retaining original picture and audio. Keep dialogue, ambience and music intent separate and respect user permissions for supplied voice media.

## Acceptance criteria

- [ ] Every dialogue job records the character voice version and actual supplied audio reference, if supported.
- [ ] Unsupported voice conditioning is clearly identified.
- [ ] Replacing audio preserves the accepted picture and permits reverting to original sound.
- [ ] Review adjacent dialogue clips for speaker similarity and mouth timing.

## Dependencies

- #34
- #44
- #52

## Source and limits

Inspired by the published [The Trigger production breakdown](https://higgsfield.ai/@higgsfield.studio/projects/trigger). These are MovieCrew implementation proposals, not guarantees of model behaviour. Do not copy or execute third-party skill files. Preserve existing films; live trials require an explicit budget.

Part of #32. Priority: **P1**.
