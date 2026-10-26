# Red team, iteration 5 (attacking v4): AgentGuard as a dev-tool / open-source business

**Verdict:** v4 fixes the founder-fit problem, but AgentGuard is a feature, and part of it is the wrong kind of feature. "Input quarantine" can't protect screen-driving agents, and the frameworks it targets mostly aren't Kotlin. Rebuild it as a framework-agnostic *action firewall*, ship it upstream, and count a job, acqui-hire or grant as a success, not a consolation prize.

## Findings, ranked

**1. Quarantine doesn't work for screen agents. Only an action-layer guard does.**
- CaMeL / dual-LLM quarantine works when untrusted data can stay opaque to the planner (tool and API results).
- A screen-driving agent has to *read* the screen to act. The injected text is the observation itself. Tagging where it came from and "spotlighting" it are known to reduce attacks, not stop them.
- For AndroidWorld-style agents, the only guarantee you can enforce sits *below* the model: tap, type, launch and swipe checked against policy.
  - Is the target package in scope?
  - Is the element semantically "Pay / Send / Delete / Grant"?
  - Is the typed text a reference token or raw PII?
  - Did the agent jump to another app mid-task?

**Change:** drop "quarantine before the model sees it" as the headline claim for screen agents; keep it only for AppFunction and MCP results. Lead with an **actuation firewall**: policy plus reconfirmation plus data-taint at the executor. It doesn't depend on the model, so it can be tested and sold on honest terms.

**2. The target frameworks mostly aren't Kotlin, and they don't run on the phone.**
- droidrun, minitap mobile-use and Open-AutoGLM keep their agent loop in **Python on a host** and drive the phone over ADB or a portal APK. Operit is the main on-device Kotlin exception.
- A Kotlin-only runtime therefore fits roughly one of the five named adopters.

**Change:** split the design into (a) a Python policy/executor wrapper (a pip package that hooks each framework's action tool) and (b) a thin Kotlin on-device enforcer for on-device agents (Operit, UNO). Treat "embed" as meaning "one adapter PR per framework."

**3. Maintainers will copy the feature before they adopt the dependency.**
- VC-backed teams (droidrun €2.1M, minitap $4.1M) treat safety as part of their product story. Mobilerun already has approval gates. They'll accept a *PR*, not a solo founder's runtime sitting in their critical path.
- The Chinese projects (Open-AutoGLM/Zhipu, Operit) are unlikely to take a foreign single-maintainer dependency. They'll reimplement the idea.

**Change:** redefine "adoption" as **merged upstream PRs and adapters**, with credit and a benchmark row. Copying is the expected outcome. Plan for it and don't try to prevent it.

**4. With AppFunctions, the caller is Google, and Google embeds nothing.**
- Gemini or the system is the caller, and Google owns reconfirmation on that side (para 129). The app is the callee. On the app side, the guard reduces to "check the caller, confirm sensitive functions, minimise what you return": a few hundred lines that each app writes itself or gets from Promon/Appdome.

**Change:** cut AppFunctions from the adoption story. Keep only a small open "callee checklist + lint" for credibility.

**5. Count the paying customers: 0–5 by end of 2027.**
Walking through who might pay:
- Open frameworks: about 5 serious ones. They pay nothing.
- VC-backed framework teams: 2–3. They build it in-house.
- OEMs building agents (Samsung, Honor, Xiaomi, Oppo, vivo): about 5. They don't contract a solo vendor for core security.
- Enterprise-device vendors (Zebra, Knox partners): possible, but slow, and there's no reference customer.
- DMA-qualified services from Feb 2027: a handful. Their TCA or lab does the evidence work.
- Realistic hosted-runner revenue: 3–5 teams × $300–1,000/month ≈ **$10–60k ARR**. That's a side income, not a company. Open-core works when there are thousands of self-serve users. Here there are dozens.

**Change:** stop presenting money streams 2–5 as a revenue plan. Present them as optional options.

**6. The market is real but tiny, and it gets absorbed.**
- Android agent builders in 2027 number in the hundreds of developers, not thousands of companies.
- The probable end state:
  - Google ships system-level reconfirmation;
  - the frameworks ship built-in gates;
  - app-protection vendors add an "agent" SKU.
- Every one of these absorbs the feature, which is the textbook sign of a feature and not a company.

**Change:** say so plainly in v5, and choose the goal that fits a feature.

**7. The honest best outcome is a respected project, not a startup.**
The people who would pay for this skill set are:
- Google (Android security / AI VRP / Gemini-on-Android);
- Promon, Appdome, Guardsquare, NowSecure (NowSecure is already hiring for agentic work);
- droidrun or minitap (acqui-hire);
- labs and TCAs building DMA test criteria.

Grants are a second route:
- NLnet NGI Zero (€5–50k, needs a European dimension), the Sovereign Tech Fund or Agency, OpenSSF, and Google or Anthropic safety/OSS programmes;
- eligibility depends on the founder's location, which is **unverified**.

A cited benchmark row plus merged PRs in 3 frameworks plus a co-authored paper makes a stronger hiring or acqui-hire signal than any seed deck here.

**Change:** make the goal a two-outcome plan. It succeeds if either (A) a job, contract or acqui-hire offer at the level the founder wants, or (B) a real paying pull appears.

**8. The kill test is too loose.**
"≥3 projects use it" can be met with forks and stars.

**Change:** by 31 Dec 2026, require:
- ≥2 **merged** upstream adapter PRs;
- one public benchmark: attack success rate with vs without the firewall, on MobileWorldSafety or Not-an-A11y;
- ≥1 grant application submitted;
- ≥5 conversations with the named employer/acquirer list.

Revenue isn't in the kill test.

## Sharpest modification (v5)
**"AgentGuard" becomes "an open action firewall for screen-driving agents": a credible project first, and a company only if the market pulls.**
1. **Oct:** build the Python executor-wrapper plus policy DSL, starting with droidrun and mobile-use adapters, reusing UNO's tool-role classifier and reference tokens. The Kotlin enforcer stays in UNO as the on-device reference.
2. **Nov:** publish the before/after benchmark, co-authored with the Picek group if they're willing, and open upstream PRs.
3. **Dec:**
   - apply to NLnet or STF;
   - run targeted conversations with Promon, Appdome, NowSecure, Google Android security, droidrun and minitap;
   - bridge contract work continues throughout.
4. **2027:** incorporate only if ≥3 teams ask to pay for hosted runs or DMA evidence. Otherwise take the best offer and carry the project with you.

This rejects v0 on honest terms: "out of options" was false, but "out of *venture-scale* options in this slot" is probably true, and that's fine.
