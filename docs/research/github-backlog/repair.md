## Respect picture approval

Track assembly, revision and approved-cut states. After a cut is approved, later generation must create a candidate and identify affected shots and sound work; it must not replace the cut automatically.

## Problem

Regenerating a whole film wastes accepted footage and introduces new inconsistencies.

## Scope

Create review-driven repair proposals for the smallest affected shot/range. Show cost, changed constraints and dependent shots, then save a candidate for comparison and explicit replacement.

## Acceptance criteria

- [ ] An accepted neighboring shot is not regenerated automatically.
- [ ] Repair lineage, user override and before/after comparison persist.
- [ ] Benchmark reports repair cost and usability improvement under a fixed cap.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/49
- https://github.com/VPathy16/Moviecrew/issues/54

## Tracking

Priority: **P2** · Area: **Optimization**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
