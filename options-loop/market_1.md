# Market research — iteration 1 (2026-09-28)

## Verdict on the thesis
**It's false, but only just.** Most of the openings people usually name are already taken: MCP gateways, agent governance, consumer assistants and enterprise Android agents are crowded or owned by big tech. One structural opening appeared in July 2026 that fits UNO's architecture unusually well: the EU forcing Google to open Android to rival assistants, with **certification gates that test exactly what UNO already enforces.**

## Findings

**1. EU DMA: Android opened to rival AI assistants (strongest signal).**
- On 16 Jul 2026 the Commission issued binding specification decisions under DMA Art. 6(7). Google must give third-party assistants the same Android access Gemini has, across 11 features. [EC](https://digital-markets-act.ec.europa.eu/commission-provides-guidance-google-ai-interoperability-android-and-sharing-google-search-data-under-2026-07-16_en)
- 5 "restricted" features need certification: AppSearch app-data access, context-aware intelligence, App Actions/AppFunctions, screen automation, and system integration. The test criteria include **"user intent reconfirmation before sensitive actions," "inadvertent data disclosure minimization," and "hardening against agentic risks that would negate user intent."** [The Hacker News](https://thehackernews.com/2026/07/eu-orders-google-to-open-android-mic.html)
- To be eligible, an assistant needs **≥50,000 monthly EU users** averaged over a year. [same]
- Timeline: Google publishes draft certification terms by 1 Feb 2027 and final terms by 1 May 2027, then takes applications. Most capabilities ship in Android 18 on 1 Aug 2027. [heise](https://www.heise.de/en/news/EU-Requirements-Android-must-fully-open-up-for-third-party-AI-assistants-11367823.html), [CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-dma-android-ai-interoperability-2026071/)
- CSA flags gaps: the criteria aren't defined yet, OEM vetting goes away with nothing named to replace it, and over-privileged agents are a known problem (74% of security staff say agents get excessive access). Google (Kent Walker) is publicly arguing the security risk. **That fight creates demand for a credible "safe-by-construction" reference implementation.**
- Who pays: every non-Google assistant that wants EU system access: OpenAI, Anthropic, Mistral (Le Chat/Vibe, ~€20B valuation talks), Perplexity, and OEM assistants such as Samsung and Xiaomi. [EU AI list](https://www.data-unplugged.de/en/blog/european-ai-models)
- Crowding: no vendor found selling "DMA certification-ready agent safety" (unverified; this search was shallow).

**2. B2B agent security and MCP gateways: crowded, and the money is large.**
- Runlayer: $11M seed, then a $30M Series A (Jun 2026). AIR: $50M seed (Sequoia/Greenoaks, Sep 2026). Geordie: $30M Series A. Oasis: $120M. Noma: $132M. WitnessAI: $85M. The M&A is huge: Palo Alto–CyberArk/Protect AI, Check Point–Lakera, Google–Wiz. Gartner expects 75% of API gateways to have MCP features. [softwarestrategies](https://softwarestrategiesblog.com/2026/03/28/agentic-ai-security-startups-funding-mna-rsac-2026/), [TechCrunch](https://techcrunch.com/2026/09/01/air-raises-50m-to-help-companies-vet-the-skills-and-add-ons-ai-agents-use/), [Fortune](https://fortune.com/2026/05/28/geordie-security-governance-ai-agents/)
- **Gap:** the same source finds no mobile, endpoint or on-device agent security vendors. Every player is server-side or cloud.
- Demand: 65% of enterprises running agents had an agent incident in the last 12 months, and 35% lost money (CSA survey, via [Ramp](https://ramp.com/blog/ai-agent-spending-controls); I did not check the primary source). Agent spend controls are being built by fintechs (Ramp, Meow, Visa/Mastercard). **Avoid.**

**3. Android enterprise and frontline agents: big tech moved in during 2026.**
- Android Enterprise (23 Sep 2026): Gemini multi-step agents with admin policies to configure, restrict or disable them, plus work-profile isolation. It does **not** mention third-party agents. [Google](https://blog.google/products-and-platforms/products/android-enterprise/whats-new-android-enterprise-2026/)
- Microsoft Project Solara: agent-first AOSP devices for healthcare, retail and finance, with pilots at CVS, Target and Best Buy. [Directions on Microsoft](https://www.directionsonmicrosoft.com/build-2026-microsoft-pushes-the-agent-envelope-with-android-devices-new-windows-pcs/)
- **Avoid a head-on product.** A possible niche is policy and approval tooling for non-Gemini agents on managed fleets (unverified).

**4. AppFunctions (Android's MCP-style API).**
- Apps can act as on-device MCP servers. Callers need the EXECUTE_APP_FUNCTIONS permission. The Gemini integration was still a trusted-tester preview in May 2026. [Android Dev](https://developer.android.com/ai/appfunctions), [9to5Google](https://9to5google.com/2026/02/25/android-appfunctions-gemini/)
- Without the DMA, third-party callers probably can't hold that permission. With it, they can in the EU from Aug 2027. **This links directly to UNO's MCP classification and gating pipeline.**
- Droidrun (Berlin) raised a €2.1M pre-seed for mobile agent infrastructure based on UI control. It is a competitor or partner, but it focuses on automation, not safety. [Tech.eu](https://tech.eu/2025/07/23/droidrun-raises-eur21m-pre-seed-to-scale-mobile-native-ai-agent-infrastructure/)

**5. Regulated verticals.**
- EU AI Act: the Digital Omnibus (Reg. 2026/1744) pushed Annex III high-risk obligations to **2 Dec 2027**. Art. 50 transparency still applied from Aug 2026. For agents, high-risk rules require logging of actions and human override. [Gibson Dunn](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/), [Help Net](https://www.helpnetsecurity.com/2026/04/16/eu-ai-act-logging-requirements/)
- Legal: ABA Opinion 512 pushes lawyers toward understanding where client data goes, and some clients now forbid AI use on their data. [Attorney at Work](https://www.attorneyatwork.com/on-device-ai-for-lawyers/), [Wolters Kluwer](https://www.wolterskluwer.com/en/expert-insights/legal-experts-discuss-scaling-ai-in-first-webinar-on-wolters-kluwer-2026-future-ready-lawyer-survey)
- Healthcare is crowded with funded voice and ambient vendors (Hippocratic, Suki) and needs EHR integration and compliance certifications. **This doesn't fit a solo founder.**

## Top 3 openings, ranked

1. **"DMA-certification-ready" safety layer: SDK plus reference assistant for third-party Android agents in the EU.**
   - What it is: an intent-reconfirmation, data-minimisation and tool-gating layer, which is UNO's existing architecture.
   - Why: the regulator has written UNO's design into the pass criteria, and there are hard dates (Feb, May and Aug 2027).
   - Why big tech can't take it: Google is the gatekeeper and is arguing against third-party access, and rivals would rather buy than build Android-specific safety plumbing.
   - Buyers: EU and challenger assistants, OEMs, and MDM vendors.
   - Risk: big labs build this in-house, and the criteria are still undefined.
2. **Privacy-first EU consumer or prosumer assistant using DMA access.**
   - "Your data never reaches the AI" is a real differentiator against US labs. It would pair well with Mistral or other sovereign models.
   - Risk: the 50k EU MAU bar, plus consumer distribution is hard for a solo founder. It could run as a showcase for #1 rather than the main business.
3. **On-device approval and audit for agents in confidentiality-bound professions** (lawyers, journalists, EU regulated SMEs).
   - The pitch is an agent log and human-override trail that satisfies ABA 512 and AI Act Art. 12/14 style requirements.
   - The need is real and the market is small. It is uncrowded on mobile, but willingness to pay is unproven.

## Open questions for iteration 2
- Has Google published or leaked draft certification terms? Who are the "independent third parties" (test labs), and could UNO partner with one?
- Are OpenAI, Anthropic, Mistral, Perplexity or Samsung publicly preparing EU Android assistants, and hiring for it?
- Is anyone already selling mobile or on-device agent guardrails (Zimperium, Lookout, Jamf, Droidrun)?
- Can EXECUTE_APP_FUNCTIONS be granted to third parties outside the EU, e.g. through a role-holder or default assistant? If so, the market is global.
- Could DMA-style assistant interoperability spread to the UK (CMA SMS designation of Google), Japan (MSCA, effective Dec 2025), Brazil or Korea? That would make this global rather than EU-only.
- How would a solo founder sell into big labs: open-source SDK plus paid certification prep, or acquisition bait?
