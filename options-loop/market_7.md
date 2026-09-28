# Market research, iteration 7 (2026-09-28)

## Headline finding (changes the plan)
On **16 Jul 2026** the European Commission adopted a DMA specification decision (DMA.100220). It orders Google to open **11 Android AI features** to third-party assistants, free of charge.
- **What opens:**
  - Screen automation, i.e. "Computer Control", which Gemini uses today.
  - AppFunctions.
  - AppSearch data.
  - Ambient screen, mic and camera access.
  - Gemini Nano and third-party on-device models.
- **Deadlines:** Android 18 by **1 Aug 2027**; concurrent hotwords in Android 19 by Aug 2028.
- **Five sensitive features are gated by eligibility conditions**, including screen automation and AppFunctions:
  - Google may set conditions on "privacy, security and integrity" grounds only.
  - **Independent third parties certify** apps "along with Google".
  - Draft terms are due **1 Feb 2027**, open for consultation. Final terms and applications follow on **1 May 2027**, with a 4-week assessment.
- **Eligibility threshold:**
  - At least 50k EU monthly users over the past year, plus either 2 years operating in the EU or being under 2 years old with more than €50M invested.
  - **A new solo-founder assistant is excluded.**

Sources: [EC DMA portal](https://digital-markets-act.ec.europa.eu/developer-portal/interoperability/alphabet-specification-proceedings-interoperability-ai-services_en), [EC guidance 16 Jul](https://digital-markets-act.ec.europa.eu/commission-provides-guidance-google-ai-interoperability-android-and-sharing-google-search-data-under-2026-07-16_en), [THN](https://thehackernews.com/2026/07/eu-orders-google-to-open-android-mic.html), [CSA note](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-dma-android-ai-interoperability-2026071/), [Developers Digest](https://www.developersdigest.tech/blog/eu-dma-android-ai-assistant-interoperability) (secondary), [Competition System](https://thecompetitionsystem.substack.com/p/what-the-alphabet-specification-decisions) (critique: "Trusted Certification Authorities" have no basis in the DMA text, so a legal challenge is possible).

**Implication:** a regulator-mandated market is opening for *proving that a third-party agent driving apps is safe*. That is AgentGuard's exact problem, and it closes the "legit agent looks like malware" gap raised in market_6. Who the certifiers are and what criteria they use is **still undefined**.

## 1. MAS SAFR and agent-governance vendors
- **Contributors:** Ant International, Circle, HSBC, J.P. Morgan Chase, Manulife, Mastercard, OCBC and Visa (Annex A, via [search summary](https://www.mas.gov.sg/publications/monographs-or-information-paper/2026/safeguards-for-agentic-finance-at-runtime); I could not parse the PDF myself, so **unverified verbatim**).
- **Engagement route:**
  - An Expression of Interest [form.gov.sg](https://form.gov.sg/692d54b9d4e0e288131feb1a) is linked from the [MAS release](https://www.mas.gov.sg/news/media-releases/2026/mas-partners-industry-to-develop-safeguards-for-ai-agents-in-finance).
  - The new **Future of Finance Institute** will run "industry pilots and sandbox experimentation".
  - No deadline is published.
  - SAFR is a voluntary reference, not a requirement ([Ashurst](https://www.ashurstperkinscoie.com/en/insights/mas-safr-explained-singapores-runtime-governance-standard-for-agentic-ai-in-finance/)).
- **Crowding: high, for server-side and enterprise agents.**

| Vendor | Evidence | Source |
|---|---|---|
| KLA Digital | Already markets "implements the SAFR pattern, shipping today": its four dispositions (Deny, Escalate, Auto-Execute, Observe) map 1:1 onto block, approve, allow and warn | [KLA](https://kla.digital/blog/safr-mas-framework-explained) |
| Kontext (Munich) | $4M seed on 24 Sep 2026 (42CAP, a16z CSX). A local daemon checks agent tool calls against policy before execution. Targets banks; no revenue; no mobile | [TFN](https://techfundingnews.com/kontext-4m-seed-ai-agent-security-banking-fintech/) |
| Zenity | Around $185M raised; has a financial-services solution brief with Microsoft | [Zenity](https://zenity.io/use-cases/business-type/financial-services) |
| Noma | $132M raised | [LangGuard](https://langguard.ai/alternatives/zenity-vs-noma/) |
| Credo AI | Governance control plane with regulatory policy packs | [Credo](https://www.credo.ai/product) |
| Microsoft Agent 365 | GA 1 May 2026; policy controls, runtime blocking through Intune and Defender for local agents | [MS](https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/) |
| Arthur, Witness.ai, LangGuard | Also pitch bank agent governance | — |
| IBM watsonx.governance | Nothing agent-runtime-specific for banks found (**unverified**) | — |
| Holistic AI, Galileo | Not checked | — |

- **Mobile-specific agent governance vendors: none found.** "SAFR-aligned checkpoints" alone is **not a differentiator**. Only the mobile/UI-executor angle is.

## 2. Consumer privacy assistant in the EU
- **The DMA threshold blocks a new entrant from the gated features.** The eligible players:
  - **Proton Lumo:** Android app updated 23 Sep 2026. Users are *requesting* default-assistant support ([uservoice](https://protonmail.uservoice.com/forums/932842-lumo/suggestions/50480169-add-default-digital-assistant-app-capability-on)).
  - **Mistral:** Le Chat was renamed Vibe in May 2026 ([Wikipedia](https://en.wikipedia.org/wiki/Le_Chat_(AI)), **unverified**).
  - Perplexity, Brave Leo (Android, in-browser) and Kagi.
- **Privacy OEMs and ROMs:**
  - **Murena /e/OS:** its 2026 roadmap and v4 (Jun 2026) mention no AI assistant ([Duval](https://gaelduval.com/joining-the-wave-murena-e-os-2026-roadmap/)).
  - **Fairphone:** ships /e/OS as an option ([Fairphone](https://www.fairphone.com/the-fairphone-gen-6-e-operating-system)).
  - **GrapheneOS:** its community is hostile to LLMs (an issue requesting a "no LLM" policy, Sep 2026, [GitHub](https://github.com/GrapheneOS/os-issue-tracker/issues/8677)). Only hobby "gos-ai" apps exist.
  - **Nothing:** nothing found.
  - AOSP forks sit mostly outside "Google Android", so the DMA access likely doesn't apply to them (**unverified**).
- **Verdict:** partnership appetite from these OEMs and ROMs is unproven and small. A new consumer assistant is the wrong bet. **Selling safety infrastructure to the eligible assistants** (Proton, Mistral, Perplexity, Brave) is the better route.

## 3. Google roadmap
- **Android 17 QPR2 Beta 4 (31 Aug 2026)** adds Security & privacy → "**Agents**": a list of "agents that can access info or take actions within apps". It is explicitly not limited to Gemini ([Android Authority](https://www.androidauthority.com/android-17-qpr2-beta-4-agent-dashboard-3704775/)).
- **QPR2 app lock:** agents the user has allowed keep access to locked apps ([9to5](https://9to5google.com/2026/08/14/android-17-qpr2-app-lock/)).
- So an **OS-level agent permission class is being built**, consistent with DMA compliance.
- I found no Play Integrity "agent" verdict ([verdicts doc](https://developer.android.com/google/play/integrity/verdicts)); **unverified**.

## 4. Loss figures
| Source | Figure | Link |
|---|---|---|
| UK Finance 2026 | Remote banking fraud £104.4M in 2025 (−27%), cases +11% driven by mobile (+21%); total fraud £1.28bn. No malware or accessibility breakdown | [UK Finance](https://www.ukfinance.org.uk/news-and-insight/press-release/fraud-report-2026-press-release) |
| SPF Singapore | Android malware scams: at least S$2.4M across 128 cases from Feb to Apr 2025; at least S$69k in the senior-targeted wave since Apr 2026. Total scams S$913M in 2025 | [SPF 2025](https://www.police.gov.sg/media-hub/news/2025/04/20250417_police_advisory_on_the_prevalence_of_malware_scams_affecting_android_users), [SPF 2026](https://www.police.gov.sg/Media-Hub/News/2026/06/20260618_police_advisory_on_malware_enabled_scams_on_android_devices_targeting_senior_citizens), [Malay Mail](https://www.malaymail.com/news/sports/2026/02/26/singapore-police-scam-cases-drop-248pc-in-2025-losses-fall-to-s913m-but-youths-remain-most-affected/210482) |
| Hong Kong | HK$12M across 41 cases from one malware syndicate | [SCMP](https://www.scmp.com/news/hong-kong/law-and-crime/article/3266690/41-hongkongers-lost-hk12-million-regional-malware-scam-police-say) |
| I4C India | ₹19,813–22,495 crore total cyber fraud in 2025, about 75% investment scams; no malware split | [ThePrint](https://theprint.in/india/cybercrime-saw-24-spike-in-2025-indians-lost-rs-22495-crore-mainly-in-investment-scams/2859930/) |

- **Honest answer:** there is no published hard figure for accessibility-malware losses specifically.
- The best defensible framing: "UK remote-banking fraud of £104M/yr, with mobile cases growing 21%", plus Singapore's cases in the millions of S$.
- Accessibility malware is a **niche** of a large fraud pool.

## 3 recommendations
1. **Pivot the flagship positioning to "DMA-certification-ready safety layer for third-party screen-automation agents".**
   - Build a public criteria proposal: executor rules, reconfirmation for payment and banking screens, data-flow tracking, tamper-evident log, and a signed policy manifest with Key Attestation.
   - Submit it in the **Feb 2027 consultation on Google's draft eligibility terms**.
   - Pitch Proton, Mistral/Vibe, Perplexity and Brave: they must pass certification by May 2027 and have no mobile safety layer.
2. **Approach the certifiers, not only the agents.**
   - Find out who becomes a "Trusted Certification Authority": TÜV, BSI-type labs, ioXt or NCC-type firms.
   - Offer AgentGuard's benchmark and harness as test methodology. This is a strong consulting, contract or job route.
3. **Downgrade SAFR to a secondary channel.**
   - The SAFR space is crowded (KLA already claims alignment; Kontext, Zenity, Noma and Microsoft are all in it).
   - Submit the MAS EOI form once, pitched only as "SAFR checkpoints for mobile/UI-executing agents" (for example, bank RPA on Android or agentic UPI-style flows). Don't build an enterprise governance product.

## Open questions for iteration 8
- **DMA.100220 PDF:** what are the exact security criteria and certification-authority provisions for Computer Control? Can banking apps opt out or be excluded? Is it limited to GMS "Google Android" devices?
- **Consultation:** is there a public comment route for the 1 Feb 2027 draft terms, and who were the "interested parties" in the technical meetings?
- **Buyers:** do Proton, Mistral or Perplexity have mobile-agent plans or security hiring for Android screen automation?
- **Legal risk:** will Google appeal? The critique draws on the Microsoft precedent where the General Court annulled a similar private-certifier arrangement.
- **Android 17 QPR2 "Agents" page:** what permission or role backs it? Is it the same class the DMA will use?
- **SAFR PDF:** confirm the Annex A list and whether FFI pilots are open to non-Singapore vendors.
