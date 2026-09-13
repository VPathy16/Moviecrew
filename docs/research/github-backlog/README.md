See [active filmmaking priorities](filmmaking-priorities.md) for the ordered work from The Trigger review.

> **First task:** [#62 — Director review and approval](https://github.com/VPathy16/Moviecrew/issues/62) before Writer generation, followed by #34–36.

> **Active priority:** #34 → #35 → #36: scene direction, causal shot continuity and reference-aware prompts. Validate one short Everest sequence before broader product expansion. See [tracker](tracker.md).

# MovieCrew prioritized backlog

[Master GitHub tracker](https://github.com/VPathy16/Moviecrew/issues/32)

All 29 implementation issues have scope, dependencies and acceptance criteria. GitHub is the live status source; this file records the initial backlog.

| Priority | Issue | Dependencies |
| --- | --- | --- |
| P0 | [#33 Back up existing films and prove a complete restore](https://github.com/VPathy16/Moviecrew/issues/33) | Ready |
| P0 | [#34 Introduce versioned sequence and shot-state contracts](https://github.com/VPathy16/Moviecrew/issues/34) | Ready |
| P0 | [#35 Give the planning Editor story beats and full shot summaries](https://github.com/VPathy16/Moviecrew/issues/35) | [#34](https://github.com/VPathy16/Moviecrew/issues/34) |
| P0 | [#36 Compile shot prompts with adjacent context and approved state](https://github.com/VPathy16/Moviecrew/issues/36) | [#34](https://github.com/VPathy16/Moviecrew/issues/34), [#35](https://github.com/VPathy16/Moviecrew/issues/35) |
| P0 | [#37 Decide the SaaS data architecture and add migration foundations](https://github.com/VPathy16/Moviecrew/issues/37) | [#33](https://github.com/VPathy16/Moviecrew/issues/33) |
| P0 | [#38 Add Firebase sign-in and server-side identity verification](https://github.com/VPathy16/Moviecrew/issues/38) | [#37](https://github.com/VPathy16/Moviecrew/issues/37) |
| P0 | [#39 Enforce workspace permissions across every project route](https://github.com/VPathy16/Moviecrew/issues/39) | [#37](https://github.com/VPathy16/Moviecrew/issues/37), [#38](https://github.com/VPathy16/Moviecrew/issues/38) |
| P0 | [#40 Migrate film assets to private durable R2 storage](https://github.com/VPathy16/Moviecrew/issues/40) | [#33](https://github.com/VPathy16/Moviecrew/issues/33), [#37](https://github.com/VPathy16/Moviecrew/issues/37), [#39](https://github.com/VPathy16/Moviecrew/issues/39) |
| P0 | [#41 Separate admin provider connections from customer settings](https://github.com/VPathy16/Moviecrew/issues/41) | [#38](https://github.com/VPathy16/Moviecrew/issues/38), [#39](https://github.com/VPathy16/Moviecrew/issues/39) |
| P0 | [#42 Replace process-local job ownership with durable workers](https://github.com/VPathy16/Moviecrew/issues/42) | [#37](https://github.com/VPathy16/Moviecrew/issues/37), [#39](https://github.com/VPathy16/Moviecrew/issues/39), [#41](https://github.com/VPathy16/Moviecrew/issues/41) |
| P0 | [#43 Reserve generation budgets and reconcile usage in a ledger](https://github.com/VPathy16/Moviecrew/issues/43) | [#37](https://github.com/VPathy16/Moviecrew/issues/37), [#39](https://github.com/VPathy16/Moviecrew/issues/39), [#42](https://github.com/VPathy16/Moviecrew/issues/42) |
| P0 | [#55 Make tenant isolation and recovery tests a release gate](https://github.com/VPathy16/Moviecrew/issues/55) | [#39](https://github.com/VPathy16/Moviecrew/issues/39), [#40](https://github.com/VPathy16/Moviecrew/issues/40), [#41](https://github.com/VPathy16/Moviecrew/issues/41), [#42](https://github.com/VPathy16/Moviecrew/issues/42), [#43](https://github.com/VPathy16/Moviecrew/issues/43), [#50](https://github.com/VPathy16/Moviecrew/issues/50) |
| P0 | [#56 Add production observability and restore runbooks](https://github.com/VPathy16/Moviecrew/issues/56) | [#40](https://github.com/VPathy16/Moviecrew/issues/40), [#42](https://github.com/VPathy16/Moviecrew/issues/42), [#43](https://github.com/VPathy16/Moviecrew/issues/43) |
| P1 | [#44 Create a versioned provider capability registry](https://github.com/VPathy16/Moviecrew/issues/44) | [#34](https://github.com/VPathy16/Moviecrew/issues/34) |
| P1 | [#45 Select references by role and shot requirements](https://github.com/VPathy16/Moviecrew/issues/45) | [#44](https://github.com/VPathy16/Moviecrew/issues/44) |
| P1 | [#46 Persist and display the exact generation input manifest](https://github.com/VPathy16/Moviecrew/issues/46) | [#45](https://github.com/VPathy16/Moviecrew/issues/45), [#40](https://github.com/VPathy16/Moviecrew/issues/40) |
| P1 | [#47 Separate next-shot generation from true take extension](https://github.com/VPathy16/Moviecrew/issues/47) | [#36](https://github.com/VPathy16/Moviecrew/issues/36), [#44](https://github.com/VPathy16/Moviecrew/issues/44), [#46](https://github.com/VPathy16/Moviecrew/issues/46) |
| P1 | [#48 Build a fixed-budget film-quality benchmark and baseline](https://github.com/VPathy16/Moviecrew/issues/48) | [#34](https://github.com/VPathy16/Moviecrew/issues/34) |
| P1 | [#49 Review generated footage for technical and story defects](https://github.com/VPathy16/Moviecrew/issues/49) | [#46](https://github.com/VPathy16/Moviecrew/issues/46), [#48](https://github.com/VPathy16/Moviecrew/issues/48) |
| P1 | [#50 Add clip-instance IDs and revisioned timeline saves](https://github.com/VPathy16/Moviecrew/issues/50) | [#37](https://github.com/VPathy16/Moviecrew/issues/37) |
| P1 | [#51 Align proxy playback and export with one timing model](https://github.com/VPathy16/Moviecrew/issues/51) | [#50](https://github.com/VPathy16/Moviecrew/issues/50), [#40](https://github.com/VPathy16/Moviecrew/issues/40) |
| P1 | [#52 Add independent audio tracks, gain and fades](https://github.com/VPathy16/Moviecrew/issues/52) | [#50](https://github.com/VPathy16/Moviecrew/issues/50), [#51](https://github.com/VPathy16/Moviecrew/issues/51) |
| P1 | [#53 Replace global UI overrides with explicit editor modules](https://github.com/VPathy16/Moviecrew/issues/53) | [#50](https://github.com/VPathy16/Moviecrew/issues/50) |
| P1 | [#54 Unify shot, clip and character editing around selection](https://github.com/VPathy16/Moviecrew/issues/54) | [#53](https://github.com/VPathy16/Moviecrew/issues/53), [#36](https://github.com/VPathy16/Moviecrew/issues/36), [#46](https://github.com/VPathy16/Moviecrew/issues/46) |
| P2 | [#57 Offer targeted repairs instead of full-film regeneration](https://github.com/VPathy16/Moviecrew/issues/57) | [#49](https://github.com/VPathy16/Moviecrew/issues/49), [#54](https://github.com/VPathy16/Moviecrew/issues/54) |
| P2 | [#58 Validate canvas expansion and Topaz enhancement workflows](https://github.com/VPathy16/Moviecrew/issues/58) | [#44](https://github.com/VPathy16/Moviecrew/issues/44), [#46](https://github.com/VPathy16/Moviecrew/issues/46), [#51](https://github.com/VPathy16/Moviecrew/issues/51) |
| P2 | [#59 Publish a small evaluated set of visual recipes](https://github.com/VPathy16/Moviecrew/issues/59) | [#44](https://github.com/VPathy16/Moviecrew/issues/44), [#48](https://github.com/VPathy16/Moviecrew/issues/48) |
| P2 | [#60 Reuse approved cast and world assets across owned projects](https://github.com/VPathy16/Moviecrew/issues/60) | [#39](https://github.com/VPathy16/Moviecrew/issues/39), [#40](https://github.com/VPathy16/Moviecrew/issues/40), [#46](https://github.com/VPathy16/Moviecrew/issues/46) |
| P2 | [#61 Launch a capped paid pilot with usage history and support](https://github.com/VPathy16/Moviecrew/issues/61) | [#55](https://github.com/VPathy16/Moviecrew/issues/55), [#56](https://github.com/VPathy16/Moviecrew/issues/56), [#43](https://github.com/VPathy16/Moviecrew/issues/43), [#49](https://github.com/VPathy16/Moviecrew/issues/49), [#52](https://github.com/VPathy16/Moviecrew/issues/52) |
