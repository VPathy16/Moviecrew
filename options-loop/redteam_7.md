# Red team, iteration 7: the outside view on v6

**Verdict:** v6 is a strategy for a five-person, funded standards team, handed to one person with no runway. Cut it to one income goal plus one public proof, and run one cheap probe of the direction the loop dropped too early: UNO as the built-in assistant on de-Googled EU phones.

## Findings, ranked

**1. v6 can't be done by one person in 90 days.**
- Count the workstreams:
  - three positionings;
  - PRs to two Python frameworks plus a Kotlin enforcer;
  - disclosure etiquette with the paper authors;
  - a benchmark with adaptive attacks and utility metrics;
  - two grants;
  - an IETF/FIDO draft;
  - a relying-party pilot;
  - bridge contract work, which takes 2–3 days a week.
- That leaves roughly 25 working days for about eight projects. Gate 0 alone needs outside maintainers to merge PRs, and the founder doesn't control that timing.
- **Change:** cut to one goal, "paid by 31 Dec 2026", with one public proof that supports it. Remove these from the plan, not just defer them:
  - the IETF/FIDO profile;
  - Gate 1 and Gate 2;
  - SAFR;
  - NLnet;
  - the Appdome replacement proof of concept.

**2. The loop drifted away from the founder's assets.**
- The founder owns a **Kotlin consumer assistant**.
- v6 asks him to:
  - write Python adapters for other people's ADB frameworks;
  - do academic benchmarking;
  - write standards drafts.
- None of that uses UNO's code. It only reuses UNO's *ideas*.
- Each round rewarded defensibility and punished "consumer". Six rounds of that produced "security plumber".
- **Change:** anything in v7 must ship code that already exists in UNO: the tool-role classifier, the privacy gateway, the approvals and spending rules, and the vanara scopes.

**3. The SAFR positioning fails on procurement, not on product.**
- Under MAS's AI risk guidelines and its outsourcing and TRM rules, institutions can't hand governance off to vendors. Vendor due diligence expects:
  - a legal entity;
  - ISO 27001 or SOC 2;
  - insurance;
  - financial statements;
  - support SLAs;
  - often a local presence.
- A solo, foreign, open-source author passes none of these checks.
- The people who actually sell to these institutions are:
  - Accenture, the Big Four, and local integrators (NCS, ST Engineering);
  - core and digital banking vendors (Temenos, Backbase);
  - hyperscaler governance stacks;
  - funded guardrail vendors.
- There is also a product mismatch. Bank "agents" are backend LLMs that call tools. They are not Android screen-drivers, so an executor firewall for taps and typing is the wrong layer.
- MAS's route for outsiders is to contribute to the open industry toolkit, and that earns credit, not revenue.
- **Change:** drop SAFR as a buyer. At most, cite it in one blog post as evidence that regulators want "check before execute".

**4. Directions the loop never seriously tested.** Each is red-teamed against v6.

- **A. UNO as the default assistant on de-Googled EU Android (Murena/e/OS, Fairphone, Volla, iodéOS).**
  - *For:*
    - These makers ship no Gemini and sell on privacy.
    - An OEM can grant a pre-installed app system privileges today, with no DMA certification needed.
    - "The AI never sees your data, and you bring your own key" is exactly their pitch.
    - They are small enough to take a meeting with a solo developer.
  - *Against:*
    - The user base is small (hundreds of thousands of devices, not verified).
    - OEM licence revenue is small.
    - Some of their users distrust cloud LLMs entirely, so a local-model option may be needed.
  - *Vs v6:* it uses UNO as it is, costs about 5 emails, and gives an answer in 30 days. It is the best-fitting untested option.
- **B. DMA-qualified privacy assistant for EU consumers (UNO re-aimed).**
  - *For:* v2 confirmed there is no user threshold, so UNO can apply.
  - *Against:*
    - Certification only opens in May 2027.
    - It requires ongoing compliance work.
    - Mistral, Perplexity and OpenAI will certify first and outspend him on distribution.
  - *Vs v6:* it is a 2027 option, not a 90-day plan. Keep it alive through A: the same app, certified later if A gets traction.
- **C. Agent integration for Android apps (a productised contract offer).**
  - *For:*
    - Apps now need AppFunctions and MCP surfaces for Gemini, and after Aug 2027 for DMA rival assistants too.
    - The founder has shipped exactly this plumbing: role classification, gating, spending rules.
    - It is services, which pay now, and it works *with* big tech rather than against it.
  - *Against:*
    - It is not venture-scale.
    - Google's tooling will commoditise the easy half.
  - *Vs v6:* it is the same runway v6 assumes ("bridge contract work"), with a sharper label and far better odds than grants.
- **Also considered:** privacy-gateway middleware for one regulated profession, for example lawyers on managed Android. It has a real need, but enterprise sales cycles are long, which is fatal without runway.

**5. v6's odds are presented honestly but acted on wrongly.** v6 rates the ambitious track below 5%, yet it takes most of the workload. At those odds it shouldn't compete with rent for time.

## Sharpest modification: v7 in one line
**"Android agent-safety engineer, proven in public": earn from C, prove with AgentGuard-lite, probe A.**

90 days (to 31 Dec 2026):
1. **Income (about 60% of time).** Sell a fixed-scope "make your Android app agent-ready and agent-safe" package (AppFunctions/MCP surface plus confirmation and spending rules), and run job loops in parallel.
   - Target: ≥1 paid engagement or offer.
2. **One proof (about 30%).**
   - Extract UNO's Kotlin executor rules, reference tokens and approvals into one open-source library.
   - Write one post: a screen-injection attack against a driven agent, shown with and without the library.
   - One `before_action` hook PR to droidrun, as a nice-to-have. Skip the separate benchmark paper and the grants.
3. **One probe (about 10%).** Pitch UNO as the privileged built-in assistant to Murena, Fairphone, Volla and iodé.
   - If one of them agrees to a pilot build, that becomes the 2027 plan, and DMA certification (B) follows it.
   - If none reply within 30 days, drop it and don't reopen it.

**Kill everything else.** That means SAFR, the IETF/FIDO profile, the attestation proof of concept, NLnet, and Gates 1 and 2.

**Re-check the thesis on 31 Dec.** The founder is not out of options if he is earning from agent-integration work and has one public artefact. If he has neither, the market has answered.

Sources: [MAS AI risk guidelines consultation (Bird & Bird)](https://www.twobirds.com/en/insights/2026/singapore/mas-consults-on-proposed-guidelines-on-artificial-intelligence-risk-management), [MAS AI risk toolkit with industry](https://www.mas.gov.sg/news/media-releases/2026/mas-partners-industry-to-develop-ai-risk-management-toolkit-for-the-financial-sector), [CSA note on MAS/SAFR](https://labs.cloudsecurityalliance.org/research/csa-research-note-singapore-mas-emergency-ai-governance-2026/), [Commission DMA decision on Android AI interoperability](https://digital-markets-act.ec.europa.eu/commission-provides-guidance-google-ai-interoperability-android-and-sharing-google-search-data-under-2026-07-16_en). The de-Googled OEM user numbers are unverified.
