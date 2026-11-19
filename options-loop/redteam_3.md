# Red team, iteration 3 (attacking v2)

**Verdict:** v2 points at the right gap (nobody tests how mobile agents *behave*). But it sells a "standard" the founder has no standing to write, to labs that don't buy from solo vendors. Pick one mobile-agent security *skill* and prove it with public findings. The suite, the lab deals and any certification come later, as results of that proof.

## Findings, ranked

**1. Labs don't license tools from a solo founder. They hire people and subcontract.**
- DEKRA, NCC, NowSecure and Applus+ already run test tooling from established vendors, their own, or free and open tools (MobSF, Frida, Burp).
- NowSecure *is* a tooling vendor.
- A TCA "in line with existing schemes" means ISO/IEC 17025- or 17065-style method validation. A lab won't anchor an accredited method on a one-person dependency.
- What labs *do* buy from small players is specialist hours: contractors, and scenario content they can absorb into their own method.

*Change:* replace "license the suite to TCAs" with "be the agent-behaviour subcontractor or test-content supplier to 1–2 labs". The suite is open. Sell days and scenario packs, not seats.

**2. The evals and red-teaming space is crowded and consolidating. The mobile slice is thin, and that's the only slice worth having.**
- Promptfoo went to OpenAI. Lakera went to Check Point, Protect AI to Palo Alto, and Prompt Security to SentinelOne.
- Still active: Giskard (EU), Patronus, Haize, Gray Swan (arenas with UK AISI), HiddenLayer, and the open UK AISI Inspect.
- Academic mobile-agent benchmarks already exist: AndroidWorld, MobileSafetyBench, and AgentDojo-style injection suites.
- The generic "prompt-injection test suite" is a commodity. The only open space is on-device: injection through notifications, screen content, intents, clipboard, AppFunctions arguments, and cross-app data leaks during screen automation.

*Change:* build *on* Inspect and AndroidWorld, as an Inspect task pack plus an emulator harness, rather than competing with them. Position it narrowly as "the Android attack surface for agents". Borrowed infrastructure is where the credibility comes from.

**3. The standardisation problem is real, but it's statistical, not fatal.**
- Agents are non-deterministic. Model versions drift. Server-side models change after certification. Screen state varies.
- A pass/fail on one run is meaningless.

*Change:*
- Define tests as scenario plus N runs plus a threshold, e.g. "reconfirmation fired in ≥99% of 200 seeded runs; zero exfiltration across all runs".
- Run them on emulator snapshots, with a physical-device spot-check.
- Publish the method, not just the tests.
- This also exposes a gap Google's terms must address (certifying a build whose model changes server-side). Filing that as a consultation comment is free positioning.

**4. The founder isn't credible as a standards author yet, and v2 ignores it.**
An app builder with no CVEs, papers or lab history does not write the test that DEKRA signs. The credential in this field is found vulnerabilities.

*Change:* in the next 90 days, responsibly disclose 2–3 real agent-hijack or leak bugs in shipping Android agents:
- Gemini on Android
- Perplexity on Galaxy S26
- OEM agents such as Honor or Xiaomi
- MCP-exposing apps

Write them up publicly. That one move is the portfolio, the marketing and (see #6) the revenue.

**5. "Get UNO certified" is a distraction before mid-2027, and a trap after.**
- Applications open 1 May 2027. Before that it's zero value.
- Certification then brings ongoing obligations: vulnerability monitoring, criterion (f) organisational processes, and re-certification per build. A solo founder would be carrying compliance for a product nobody pays for.
- Worse, it makes the founder a *test subject* of the labs they want to supply. That's a conflict of interest, since supplier and candidate are the same entity.

*Change:* keep UNO only as the open deliberately-vulnerable/hardened testbed ("DVAA: Damn Vulnerable Android Agent" plus a fixed version). Decide about applying in Q2 2027, and only if a lab relationship won't be compromised.

**6. The "90-day DMA-independent revenue" is the right test, with the wrong buyer.**
- MCP-server apps won't pay for tests of agents they don't own, and they have no deadline.
- Faster money that doesn't depend on the DMA:
  - (a) AI bug bounties. Google's AI VRP pays up to about $30k for rogue actions and data exfiltration, and OpenAI and Anthropic run programmes too.
  - (b) Fixed-price "agent abuse assessments" of $8–20k for fintech and commerce apps that ship in-app agents or MCP servers. They have a real incentive: fraud, and the AI Act and DORA.

*Change:* the kill criterion becomes "≥1 accepted bounty or paid assessment plus 1 public write-up by 31 Dec 2026", not "2–3 MCP pilots".

**7. Four buyer segments at once is not a focus.**
v2 names labs, applicants, OEMs and MCP apps. That's four sales motions for one person. OEM vetting is a Samsung-procurement fantasy for now.

*Change:*
- **Sequence:** findings, then assessments (apps), then a lab subcontract (from Feb 2027, once TCA applications open), then applicants (from May 2027).
- **Drop OEMs** until a lab partner brings them.

**8. The Google-writes-the-test risk is underweighted.**
Para 129 lets Google certify directly, for free. Google can also publish its own conformance tests (compare CTS/VTS), which would commoditise any third-party suite the day the terms land.

*Change:* aim to have scenarios *adopted into* Google's or the labs' method via consultation comments and OWASP (Agentic Top 10 or a MASTG agent section). Don't try to own a rival suite. Being cited beats selling.

## Sharpest modification
Turn v2 into a **"mobile-agent offensive researcher" wedge**:
1. Build an open Inspect/AndroidWorld-based harness, "Android agent attack surface" scenarios, with UNO as DVAA.
2. Hunt and disclose real bugs in shipping Android agents, which earns bounties and credibility.
3. Sell fixed-price agent-abuse assessments to fintech and commerce apps.
4. From Feb 2027, offer scenario packs and contract hours to 1–2 TCA labs, and submit the statistical method to the Google consultation and OWASP.

**Kill test:** by 31 Dec 2026, ≥1 accepted bounty or paid assessment, and ≥1 public write-up that gets a lab or vendor to reply. If neither happens, the founder lacks the offensive edge, and the whole conformance direction should be abandoned.
