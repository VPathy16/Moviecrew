## Problem

Camera/lens controls need visible, repeatable outcomes rather than arbitrary equipment labels.

## Scope

Build a small set of camera/motion/light recipes with versioned provider compilation. Describe their visual outcome in simple language, keep advanced details optional and retain recipe provenance.

## Acceptance criteria

- [ ] Blind review can distinguish intended recipe effects across selected providers.
- [ ] Saved generations retain the recipe and compiler version used.
- [ ] Recipes that do not improve benchmark yield remain experimental rather than default.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/44
- https://github.com/VPathy16/Moviecrew/issues/48

## Tracking

Priority: **P2** · Area: **Creative control**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
