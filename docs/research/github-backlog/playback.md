## Problem

Preview reloads a video element per clip and export forces 24 fps, creating potential cadence and boundary mismatches.

## Scope

Generate thumbnails/proxies, preload adjacent clips and use shared timebase/rounding rules for preview and export. Measure boundary stalls, support mixed-rate inputs, and define the output frame-rate policy.

## Acceptance criteria

- [ ] Automated fixtures compare expected cut points, duration and audio synchronization.
- [ ] A longer multi-clip edit has measured playback-stall results and a documented target.
- [ ] Missing/expired media access recovers without losing edits; proxy quality is clearly distinguished from export quality.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/50
- https://github.com/VPathy16/Moviecrew/issues/40

## Tracking

Priority: **P1** · Area: **Editor reliability**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
