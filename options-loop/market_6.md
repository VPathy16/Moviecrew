# Market research, iteration 6 (2026-09-28): the ambitious branch (agent identity, attestation and trust)

## 1. Web side: consolidating fast and owned by big platforms; nothing covers mobile
- **Standard:**
  - The IETF webbotauth WG adopted HTTP Message Signatures for bots as draft-ietf-webbotauth-httpsig-protocol-00 on 1 Sep 2026. It is built on RFC 9421, with Cloudflare and Google as co-authors ([IETF](https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/)).
  - A companion registry draft adds "Signature Agent cards" ([IETF](https://datatracker.ietf.org/doc/draft-meunier-webbotauth-registry/)).
- **Cloudflare:**
  - Signed agents have been treated as Verified bots since 1 Jul 2026, with a Direct/Intermediary field.
  - Qualifying needs honest cryptographic self-identification plus non-abusive behaviour ([CF docs](https://developers.cloudflare.com/bots/concepts/bot/signed-agents)).
  - AWS WAF and Akamai also verify these signatures (secondary source, **unverified**: [crawlbase](https://crawlbase.com/blog/web-bot-auth-signed-agents/)).
- **Payments:**
  - Visa's Trusted Agent Protocol (Oct 2025) uses Web Bot Auth signed headers checked against a Visa directory of agent keys. It launched with 12 partners, including Adyen, Stripe, Shopify, Fiserv and Worldpay ([GitHub](https://github.com/visa/trusted-agent-protocol), [Visa](https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21716.html)).
  - Mastercard Agent Pay uses agentic tokens: an MDES token bound to an agent, a merchant scope and a consent policy ([Stellagent](https://stellagent.ai/insights/mastercard-agent-pay-agentic-tokens), secondary).
  - Both networks joined Google's AP2, which uses signed intent and cart mandates ([Cloudflare](https://blog.cloudflare.com/secure-agentic-commerce/)).
- **Bot-management vendors all shipped "agent trust" products:**
  - HUMAN AgenticTrust verifies cryptographic signatures ([HUMAN](https://www.humansecurity.com/applications/agentic-ai/)).
  - DataDome Agent Trust has seen over 30B agent requests in 2026, including 16.4M attempts in Q1 to impersonate a single AI platform ([DataDome](https://securityboulevard.com/2026/05/agent-trust-at-datadome-the-ai-control-plane-for-managing-your-agentic-traffic/)).
  - Akamai launched its agentic framework on 15 Jun 2026 ([StockTitan](https://www.stocktitan.net/news/AKAM/akamai-unveils-agentic-security-framework-to-power-trusted-ai-driven-kkg1mkunpvj5.html)).
- **Funding:**

| Company | Raised | Focus | Source |
|---|---|---|---|
| Baselayer | $35M Series A (22 Sep 2026, M13 lead, $40M total) | "Know Your Agent" for banks | [TechTimes](https://www.techtimes.com/articles/327943/20260923/baselayer-raises-35m-build-ai-agent-identity-verification-no-law-yet-requires.htm) |
| Oak | $60M seed (Jul 2026, Accel/Greylock/CRV) | Enterprise identity for humans, machines and agents | [PRN](https://www.prnewswire.com/news-releases/oak-raises-60m-in-seed-funding-to-build-the-ai-native-identity-operating-system-302826349.html) |
| AIR | $50M | Vetting agent skills | [TC](https://techcrunch.com/2026/09/01/air-raises-50m-to-help-companies-vet-the-skills-and-add-ons-ai-agents-use/) |
| Browserbase | $67.5M total, $300M valuation (Jun 2025) | Ships Web Bot Auth identity with Stytch | [Browserbase](https://www.browserbase.com/identity) |
| Skyfire (KYAPay) | only $9.5M | Agent payments and KYA | [Tracxn](https://tracxn.com/d/companies/skyfire/__-gSNwLdAbLR2EH3jQO5ja24BZ2dqjmKWC_BS3-4pf1s) |

  - Persona also sells a "Know Your Agent" product.
- **Who's winning:** Cloudflare with Visa and Google own the protocol layer. Incumbents own verification (HUMAN, DataDome, Akamai). KYA money goes to identity and fintech companies with bank distribution. **A solo founder cannot compete on the web side.**
- **Mobile:** none of these covers an agent driving a native app through accessibility or ADB. They all authenticate HTTP requests. An on-device agent tapping a bank app sends no signature the app can check.

## 2. Mobile side: blocking, not attesting; the trust gap is real and unfilled
- **Google:**
  - **Play Integrity's `appAccessRiskVerdict`** flags apps that can capture the screen or control the device through accessibility, and exempts genuine accessibility tools ([docs](https://developer.android.com/google/play/integrity/verdicts)). It has no "trusted agent" class, so a legitimate agent looks like malware.
  - **Android 17 Advanced Protection** revokes accessibility access from any app not flagged `isAccessibilityTool` ([THN](https://thehackernews.com/2026/03/android-17-blocks-non-accessibility.html)). That kills accessibility-based agents (droidrun portal, Operit) for security-conscious users.
  - **AppFunctions** execution requires the privileged permission EXECUTE_APP_FUNCTIONS, limited to system or assistant-role callers ([MS Learn mirror](https://learn.microsoft.com/en-us/dotnet/api/android.app.appfunctions.appfunctionmanager?view=net-android-36.0), [Android blog Jul 2026](https://android-developers.googleblog.com/2026/07/build-intelligent-android-apps-appfunctions.html)). Caller verification is done by the OS; third-party agents are simply excluded.
  - **Gemini's UI-automation framework** (Feb/May 2026) needs "zero code" from developers and starts with curated food, grocery and rideshare apps. The posts describe no way for apps to detect agent-driven sessions, opt out, or verify which agent is driving ([Android blog](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html), [Google security](https://blog.google/security/android-gemini-intelligence-security-privacy/)).
  - **Net effect:** Google gives its own agent privileges and leaves third-party agents to blocklists.
- **Appdome:**
  - Appdome has a **"Trusted AI-Assistants Identifiers"** setting: a regex allow-list of *package names* (for example Google Assistant). Any other assistant with screen analysis enabled raises a threat event (search snippet from [Appdome how-to](https://www.appdome.com/how-to/mobile-malware-prevention/android-malware-detection/detect-ai-assistant-malware-using-ai/); I could not confirm it on the page).
  - Package names can be spoofed through sideloading, and allow-listing says nothing about the agent's *policy*.
  - This is the exact gap a cryptographic "guarded-agent attestation" would fill.
- **Approov** (Apr 2026) pitches runtime app attestation against AI-driven *attackers*, not trusted agents ([Approov](https://approov.io/blog/urgent-need-for-runtime-attestation-in-ai-agent-security)).
- **Zimperium's agents** are SOC tooling. I found nothing from Promon or Guardsquare.
- **Nobody offers a mobile agent attestation or allow-good-agent SDK** (searched and found none; **unverified** as absolute).

## 3. Demand evidence: strong fraud pain, but buyers currently pay to BLOCK agents
- **Attack volume:**
  - Kaspersky counted 56% more Android banker attacks in 2025, and unique banker packages rose 271% to 255,090 ([Kaspersky](https://www.kaspersky.com/about/press-releases/the-number-of-trojan-banker-attacks-on-smartphones-increased-by-56-in-2025)).
  - Zimperium's Aug 2026 report found 34 families targeting 1,243 financial brands in 90 countries, with malware-driven fraudulent transactions up 67% year on year ([Zimperium](https://zimperium.com/resources/new-zimperium-report-finds-banking-malware-expands-global-reach-targeting-1200-financial-apps)).
  - I found no clean loss figure in dollars.
- **Banks:** DBS/POSB restricts app use when sideloaded apps plus accessibility are detected ([DBS](https://www.dbs.com.sg/personal/support/general-digibank-security-malware-jailbroken-device.html)). The regulators in Singapore, India, Malaysia and Hong Kong push in-app protections.
- **Regulators:**
  - **MAS SAFR (3 Jul 2026)** calls for "governance checkpoints that verify and record an AI agent's proposed actions before execution": policy-bound execution plus an audit trail ([MAS](https://www.mas.gov.sg/news/media-releases/2026/mas-partners-industry-to-develop-safeguards-for-ai-agents-in-finance), [PDF](https://www.mas.gov.sg/-/media/mas-media-library/development/fintech/ai-safr/safr.pdf)).
    - That is AgentGuard's design, *but for the institution's own agents*. It says nothing on identity or consumer mobile.
  - **RBI:** two-factor authentication directions took effect 1 Apr 2026, with nothing on agents. NPCI has run agentic UPI pilots with OpenAI, Anthropic and Sarvam ([Aapti](https://aapti.in/blog/from-prompts-to-payments-the-rise-of-agentic-ai-in-payments/)).
  - **EU:** neither PSD3 nor the PSR addresses agent payments. Technical service providers can share liability for fraud losses ([financialregulations.eu](https://financialregulations.eu/blog/psd3-psr-eu-payment-services-guide)).
- **Verdict:**
  - Banks pay today (Appdome, Promon, Zimperium) to *block* accessibility control.
  - The "allow good agents" buyer appears only once consumer agents drive banking or commerce apps at scale. Google's curated rollout suggests that is 2027 or later, and Google will likely solve its own agent first.
  - The attestation opportunity is real but premature, and a platform (Google, or Appdome with its customers) is best placed to capture it.

## 4. Open items from market_5
- **Seldon:** only batch 2 (Jan–Apr 2026, in person in SF, up to $500k) is documented. The batch 3 dates and non-US eligibility are not published ([Manifund](https://manifund.org/projects/ai-security-startup-accelerator-batch-2)). **Unverified.**
- **Catalyze:** "global incubator", about 15 organisations incubated; the public page gives no dates or format ([Catalyze](https://catalyze-impact.org/incubator)). **Ask directly.**
- **NLnet Restack:**
  - Deadline 3 Nov 2026 noon CET.
  - The revised GenAI policy is **not yet published**. Mostly LLM-generated work is ineligible, and new rules on transparency and logging are coming, with "no exceptions".
  - NLnet itself advises waiting for the new policy before applying ([NLnet](https://nlnet.nl/news/2026/20260903-call.html)).
  - Non-EU eligibility is still **unverified** (the FAQ URL returned 404).

## 3 recommendations
1. **Don't build a standalone company around attestation.**
   - The web layer is owned by Cloudflare, Visa and Google.
   - Mobile buyers pay to block, and Google is privileging its own agent.
   - Keep attestation as a *research artefact plus spec proposal*: a signed "policy manifest" that an AgentGuard-wrapped agent presents, verified by an Android Key Attestation–backed key. Publish it as an IETF-style draft or blog post that reuses Web Bot Auth semantics (a Signature Agent card) for on-device agents.
   - This is cheap, earns reputation, and is attractive to acquirers.
2. **Reframe AgentGuard around MAS SAFR.**
   - "Runtime governance checkpoints that verify and record proposed actions before execution" is the regulator's own language.
   - Pitch the executor firewall plus audit log as SAFR-aligned for fintechs and banks building their own mobile or RPA agents: a compliance buyer that exists now, rather than the future "allow good agents" buyer.
   - Target the MAS BuildFin.ai contributors (see the annex of the SAFR PDF).
3. **Approach Appdome with a concrete gap: its package-name allow-list.**
   - Offer a proof of concept that replaces the regex allow-list with cryptographic verification of a guarded agent's policy.
   - This is the most direct acqui-hire or partnership wedge, and it also fixes Android 17's "legit agent looks like malware" problem.

## Open questions for iteration 7
- **SAFR:** what does the annex list (partner firms and contacts)? Is there a consultation deadline or a sandbox that AgentGuard could join?
- **Appdome:** does the Trusted AI-Assistants setting support signing-certificate pinning, and can it be driven through an API? How many of its bank customers enable agent blocking?
- **Google:** is there a roadmap for third-party agents getting EXECUTE_APP_FUNCTIONS or UI automation (the Android 17 QPR or 18 betas)? Is an "agent" category planned in Play Integrity?
- **Baselayer and Persona KYA:** does either touch mobile or on-device agents? They are potential partners or acquirers.
- **NLnet:** has the revised GenAI policy been published, and what is the geographic eligibility? **Seldon and Catalyze:** email for batch dates and whether remote or non-US founders are accepted.
- **Money:** find a hard dollar figure for bank losses to accessibility-based fraud (FS-ISAC, UK Finance, I4C India).
