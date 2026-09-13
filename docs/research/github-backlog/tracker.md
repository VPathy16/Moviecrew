## Filmmaking priority — The Trigger follow-up

1. #62: review, refine and approve Director story and cast before Writer.
2. #34 → #35 → #36: causal scene/shot states, informed editing and self-contained prompts. Include acting tasks, camera-relative blocking and planned cuts.
3. #63 and #45: preserve approved identity/state assets and supply the correct references. Respect #44 provider-capability dependencies.
4. #48 (small baseline) and #49 (sequence review): prove one short Everest sequence before increasing duration. Full automated review retains its listed dependencies; human review can start earlier.
5. #64: approve scene look and reference stills.
6. #65: optional staging guides for complex interactions.
7. #66 and #52: voice consistency and sound finishing.
8. #57: targeted repairs and protected approved cuts.

This execution focus does not remove security, storage or budget release gates. The Trigger is a case study; its model-specific techniques require evaluation rather than universal defaults. [Source](https://higgsfield.ai/@higgsfield.studio/projects/trigger).

## Director approval comes first

Start with #62: let the user refine the Director story and characters, regenerate direction and explicitly approve it before Writer runs. The active order is #62 → #34 → #35 → #36, followed by the short-sequence quality check.

## Current top priority: coherent filmmaking

User priority, 13 September 2026: complete #34 → #35 → #36 before broader SaaS expansion or visual polish. The first milestone is a human-reviewed four-shot Everest sequence with explicit cause and consequence, correct approved references and no repeated action. Establish the small baseline from #48 alongside this work; the full benchmark remains a later expansion.

Preserve existing films throughout. #33 remains a prerequisite for data migration; security and reliability issues remain mandatory before shared-service launch.

# MovieCrew production roadmap

This tracker organizes the September 2026 technical audit into individually resolvable work. Baseline: local audit at commit `70a863c`, including the visual timeline. Verify the target branch before implementation; this tracker does not assert that the baseline is deployed.

## Priority

- **P0:** essential story-quality work or a shared-service launch blocker. Creative and SaaS gates are distinct.
- **P1:** production workflow, evaluation and editor reliability.
- **P2:** optimization, finishing and paid-pilot work after dependencies pass.

Priority is not a license to skip dependencies: some P0 launch tests depend on P1 revision infrastructure.

## Execution order

1. Complete the scene/shot contract (#34), Editor context (#35), and prompt compilation (#36), with a small baseline from #48.
2. Review one coherent Everest sequence and repair only the deficient shots before increasing duration.
3. Complete backup/restore, persistence architecture, identity, ownership and private media.
4. Add durable jobs, transactional spending and durable input manifests.
5. Complete revisioned editing, playback/audio and output review.
6. Pass release gates, then run a capped pilot.

Keep existing paid-submission uncertainty, immutable originals and reference-delivery checks. Account provisioning, paid benchmarks and production deployment remain explicit execution steps, not side effects of closing a planning issue.

## P0 issues

- [ ] #33 — Back up existing films and prove a complete restore · Persistence · Dependencies: Ready to start
- [ ] #34 — Introduce versioned sequence and shot-state contracts · Story quality · Dependencies: Ready to start
- [ ] #35 — Give the planning Editor story beats and full shot summaries · Story quality · Dependencies: #34
- [ ] #36 — Compile shot prompts with adjacent context and approved state · Story quality · Dependencies: #34, #35
- [ ] #37 — Decide the SaaS data architecture and add migration foundations · SaaS foundation · Dependencies: #33
- [ ] #38 — Add Firebase sign-in and server-side identity verification · SaaS foundation · Dependencies: #37
- [ ] #39 — Enforce workspace permissions across every project route · SaaS foundation · Dependencies: #37, #38
- [ ] #40 — Migrate film assets to private durable R2 storage · Persistence · Dependencies: #33, #37, #39
- [ ] #41 — Separate admin provider connections from customer settings · SaaS foundation · Dependencies: #38, #39
- [ ] #42 — Replace process-local job ownership with durable workers · Reliability · Dependencies: #37, #39, #41
- [ ] #43 — Reserve generation budgets and reconcile usage in a ledger · Economics · Dependencies: #37, #39, #42
- [ ] #55 — Make tenant isolation and recovery tests a release gate · Launch gate · Dependencies: #39, #40, #41, #42, #43, #50
- [ ] #56 — Add production observability and restore runbooks · Launch gate · Dependencies: #40, #42, #43

## P1 issues

- [ ] #44 — Create a versioned provider capability registry · Provider integration · Dependencies: #34
- [ ] #45 — Select references by role and shot requirements · Creative control · Dependencies: #44
- [ ] #46 — Persist and display the exact generation input manifest · Provenance · Dependencies: #45, #40
- [ ] #47 — Separate next-shot generation from true take extension · Creative control · Dependencies: #36, #44, #46
- [ ] #48 — Build a fixed-budget film-quality benchmark and baseline · Evaluation · Dependencies: #34
- [ ] #49 — Review generated footage for technical and story defects · Evaluation · Dependencies: #46, #48
- [ ] #50 — Add clip-instance IDs and revisioned timeline saves · Editor reliability · Dependencies: #37
- [ ] #51 — Align proxy playback and export with one timing model · Editor reliability · Dependencies: #50, #40
- [ ] #52 — Add independent audio tracks, gain and fades · Editor · Dependencies: #50, #51
- [ ] #53 — Replace global UI overrides with explicit editor modules · Frontend architecture · Dependencies: #50
- [ ] #54 — Unify shot, clip and character editing around selection · UX · Dependencies: #53, #36, #46

## P2 issues

- [ ] #57 — Offer targeted repairs instead of full-film regeneration · Optimization · Dependencies: #49, #54
- [ ] #58 — Validate canvas expansion and Topaz enhancement workflows · Finishing · Dependencies: #44, #46, #51
- [ ] #59 — Publish a small evaluated set of visual recipes · Creative control · Dependencies: #44, #48
- [ ] #60 — Reuse approved cast and world assets across owned projects · Asset workflow · Dependencies: #39, #40, #46
- [ ] #61 — Launch a capped paid pilot with usage history and support · Paid launch · Dependencies: #55, #56, #43, #49, #52

## First work to resolve

#34 → #35 → #36 is the top implementation priority. Evaluate a short causal sequence before another full-film attempt. Keep #33 ahead of any data migration and retain all shared-service launch gates.
