## Problem

Billing should follow verified isolation, recovery and usable-film quality rather than precede them.

## Scope

Add explicit allowances, usage history, billing-event reconciliation and support flows. Invite a small cohort with clear spend caps; measure film completion, repeated use, repair time and cost per accepted second.

## Acceptance criteria

- [ ] Payment event retries cannot duplicate credits or charges in the application ledger.
- [ ] Pilot users complete and reopen films without operator intervention.
- [ ] Document launch/rollback criteria and measured retention/economics; no unlimited promise without evidence.

## Dependencies

- https://github.com/VPathy16/Moviecrew/issues/55
- https://github.com/VPathy16/Moviecrew/issues/56
- https://github.com/VPathy16/Moviecrew/issues/43
- https://github.com/VPathy16/Moviecrew/issues/49
- https://github.com/VPathy16/Moviecrew/issues/52

## Tracking

Priority: **P2** · Area: **Paid launch**

Part of #32. Based on the September 2026 technical audit of MovieCrew at local commit `70a863c`; verify the target branch before implementation. Preserve existing projects and accepted media. Completion requires the acceptance criteria and applicable automated/manual validation, not only a merged code change.
