# Red team, iteration 4 (attacking v3): founder fit and economics

**Verdict:** v3 keeps the right gap (nobody tests or guards how agents behave on Android) and hands it to the wrong person. It turns a solo product builder into a freelance offensive-security researcher, with income that won't cover rent. Keep the slot. Ship the defensive product and the developer test tool, which a builder can win, and treat bug hunting as marketing rather than income.

## Findings, ranked

**1. v3 is a career change, not a pivot.**
Nothing in v0 says the founder hunts bugs, reverses APKs or writes exploits. What v0 shows is someone who builds products: a privacy architecture, an MCP gating pipeline, scoped sub-agents, voice and UPI flows. Offensive research is a separate craft with a long ramp. It also has a crowded bench of specialists: prolific independent AI-injection researchers and the academic teams behind MobileWorldSafety and "Not an A11y", who already have the corpora. v3's own kill test ("otherwise the founder lacks the offensive edge") admits the plan depends on a skill nobody has shown the founder has.
**Change:** before anything else, ask the founder directly: "Would you enjoy spending 6 months breaking other people's agents?" If the answer is no, v3 is dead whatever the market says.

**2. The v0→v3 trajectory optimises for reviewers, not for this founder.**
Each loop took the most defensible criticism and moved one step further from the assets: app → SDK → test suite → researcher. "Uncrowded" is partly because the slot is small, and partly because it suits people unlike this founder. UNO's best code ends up as "Damn Vulnerable Android Agent", a target for other people. That throws away the rarest asset v1 identified: the working guard layer.
**Change:** add a fit criterion to every later iteration: "Does this use what the founder has already built and enjoys doing?"

**3. Bounties and assessments won't pay the bills.**
AI bug bounties pay out unevenly. Many prompt-injection reports get triaged as out of scope or low severity unless they show a concrete rogue action. Two or three accepted bugs by December could add up to low thousands, or nothing. The v3 plan still contains no runway figure, and none of v0–v3 has one.
**Change:** state how many months the founder can last. Name a bridge income that uses skills they already have: contract Android/Kotlin or agent-integration work at 2–3 days a week.

**4. The $8–20k "agent abuse assessments" have no buyer and no seller credibility.**
- Fintech and commerce apps buy pentests from firms that have references, insurance and CREST- or OSCP-certified staff. They don't buy from a first-time solo tester.
- Their "in-app agents" are mostly chat over their own APIs. They are not screen-driving agents, so the Android-specific attack surface in v3 (notifications, accessibility, cross-app leakage) mostly belongs to the assistant vendors, not to these apps.
**Change:** drop this as a revenue line in 2026.

**5. "License the corpus to labs" contradicts "open harness".**
eShard can license esDynamic to DEKRA because it is a long-established company with a closed, deep platform. A solo founder's open-source scenario corpus is free to fork, and red team 3 already showed that labs hire people rather than license from solo vendors. The step-4 revenue has nothing to protect.
**Change:** if labs matter at all, sell them a maintained product with an SLA (for example, a hosted runner and evidence reports), not the corpus itself.

**6. The product-builder version of the same insight exists, and v3 skipped it.**
Every paper cited in v3 is evidence of a missing *defence*, not only a missing test. There are two products a builder can ship:
- **(a) "AgentGuard for Android":** an open-source runtime/library that any on-device agent embeds. It covers:
  - quarantining untrusted screen, notification and clipboard text before it reaches the planner;
  - intent reconfirmation for sensitive tool roles (reusing UNO's classifier);
  - reference-token data minimisation;
  - a tamper-evident action log that exports as evidence for DMA criteria (b), (c) and (d).
- **(b) "Espresso for agents":** a CI test runner. A team points it at their Android agent build, it runs the injection and leakage scenarios on an emulator with statistical pass thresholds, and it fails the build on regressions.

Red team 2's objection ("8 vendors won't adopt a solo SDK") applies to the big assistants, not to the long tail. That tail is open-source and startup Android agent frameworks (DroidRun, mobile-use and AutoGLM-style projects), OEM and enterprise-device agents, and apps adding AppFunctions/MCP surfaces. All of them are self-serve developers.

**7. The kill test measures the wrong thing.**
"Accepted bounty + a lab reply" tests offensive skill and luck.
**Change:** by 31 Dec 2026, require all three:
- the runtime and runner are public;
- ≥3 external agent projects run or integrate it (PRs, issues or a named user);
- ≥1 paying user (a support contract or hosted runs), or one design partner with a signed LOI.
If this fails and the founder *does* enjoy breaking agents, fall back to v3.

**8. The platform risk is the same, so don't choose the harder job because of it.**
Google may ship system-rendered reconfirmation or its own conformance tests (para 129), which hurts both the runtime and the tester. The runtime is less exposed outside the EU, where many agents run without Google's help and still need guards.

## Sharpest modification
Keep v3's slot and its research inputs, but make the founder a *product builder for the Android agent-safety layer*:
1. **Oct–Nov:**
   - extract UNO's guard layer into an open-source runtime;
   - wrap the Inspect/AndroidWorld scenarios as a CI runner that tests *any* agent, UNO included, with before/after numbers.
2. **Publish one comparison:** a named open framework with and without the runtime, measured against MobileWorldSafety attacks. This is the credibility write-up, and the one piece of research v3 needs, done in a way that suits a builder.
3. **Revenue in this order:**
   - bridge contract work;
   - paid hosted runs and evidence reports for teams;
   - integration contracts with OEMs or enterprise-device vendors;
   - a DMA readiness add-on from Feb 2027.
4. **Bounties:** opportunistic only, as a side effect of building the runner.
