# Market research: iteration 2 (2026-09-28)
Deep-dive on v1's best answer: the EU DMA Art. 6(7) Android AI-interoperability decision.

## 1. Primary source checked, with corrections to market_1
Source: the Commission's final measures, DMA.100220, dated 16/07/2026 ([PDF](https://ec.europa.eu/competition/digital_markets_act/cases/202629/DMA_100220_2683.pdf), non-confidential; the full reasoning has not been published yet). Also the [developer portal](https://digital-markets-act.ec.europa.eu/developer-portal/interoperability/alphabet-specification-proceedings-interoperability-ai-services_en).

**Confirmed:**
- There are 11 features: long-press home, always-on hotword, centralised app-data access, context-aware intelligence, ambient data, structured on-device integration (AppFunctions-type), screen automation, system integration, system-level on-device models, on-device model implementation, and background execution.
- 5 are **Restricted** (para 120): app-data access, context-aware intelligence, structured on-device integration, screen automation and system integration.
- The eligibility conditions (para 125) are limited to six groups:
  - (a) functional: LLM-level reasoning and multi-step execution;
  - (b) user intent: agentic actions "honour user intent", "are only triggered with the user's intent", and "must reconfirm user intent before executing sensitive, irreversible actions";
  - (c) hardening against "input, supply chain, integration, model integrity, and infrastructure risks";
  - (d) data processed "only to the extent necessary", "minimises inadvertent data disclosure", with informed consent and transparency and control;
  - (e) "baseline mobile application security requirements";
  - (f) developer reputability: organisational processes and ongoing vulnerability monitoring.
- Timeline:
  - Draft terms by 1 Feb 2027; final terms by 1 May 2027.
  - Qualified AI Assistant (QAA) applications open 1 May 2027 and are decided within 4 weeks (8 weeks under high volume).
  - Features ship in Android 18, by 1 Aug 2027 at the latest.
  - Concurrent hotword comes in Android 19, by 1 Aug 2028.

**Corrections to market_1 and v1:**
- **The 50k MAU threshold is wrong for Android.** It applies to *Search data sharing* recipients ([THN](https://thehackernews.com/2026/07/eu-orders-google-to-open-android-mic.html)). The Android measures contain no user-count threshold. This means a small or new assistant can apply, which makes it much easier for UNO to become a certified reference assistant itself.
- **Who certifies is more specific than "independent third parties".** Google must create a **Trusted Certification Authorities (TCA) Programme** (paras 127–128):
  - Approval is free of charge and must be "in line with existing schemes for certification authorities".
  - Google "shall accept certifications issued by TCAs without imposing further requirements" and "shall not revoke" TCA certifications.
  - Google can also certify directly, for free (para 129).
  - **TCA applications open 1 Feb 2027**, three months before assistant applications.
- **Not only assistants can be certified.** "Qualified Services" that are not AI assistants can also get Restricted features, and the same TCAs certify them (para 137). The buyer pool is wider than assistants: any agentic app qualifies.
- **User opt-out (para 135).** Users can opt out of the certification requirement per service, without developer mode. Uncertified apps can still reach power users, which weakens the "must certify" pressure somewhat.
- **Geography is not stated.** The measures define devices as Google-certified Android devices, and no EEA geofence appears in the text. Whether Google ships these features EU-only is **unverified** and is a key question.

## 2. Who is preparing to use it
- **No public statements found** from OpenAI, Anthropic, Mistral, Microsoft or Meta about applying. Coverage is commentary only ([TNW](https://thenextweb.com/news/google-eu-android-gemini-rivals-dma), [AndroidHeadlines](https://www.androidheadlines.com/2026/04/eu-google-android-third-party-ai-integration-competition-dma-ruling.html)).
- **Perplexity already has system-level access through an OEM deal, globally:**
  - Galaxy S26 ships with "Hey Plex", side-button access and read/write to Samsung Notes, Calendar and similar apps.
  - Bixby uses Perplexity APIs.
  - Sources: [9to5Google](https://9to5google.com/2026/02/22/samsung-galaxy-s26-perplexity-integration/), [Perplexity](https://www.perplexity.ai/hub/blog/perplexity-apis-deliver-powerful-ai-to-the-world-s-largest-android-device-maker).
- **Google** opposes the decision:
  - Kent Walker has spoken against it.
  - Google's [5 Aug 2026 blog](https://blog.google/security/android-ai-security-eu-dma/) says Google and OEMs "must retain the authority for... approval, suspension, and revocation" of agents.
  - I found no General Court appeal yet. The filing window is roughly now (**unverified**).

## 3. Vendors and labs positioning
- **The labs are already lined up, on Google's side.** Twelve people co-signed Google's blog, including:
  - DEKRA (an EU notified body), Applus+ Laboratories, SGS, NowSecure, NCC Group, Leviathan Security;
  - TrustCB, a certification body;
  - Copper Horse, Eydle and Calif.
- Several of these are already Google **App Defense Alliance MASA** authorised labs: DEKRA, NowSecure, NCC, Leviathan, Bishop Fox, Prescient and TAC Security ([ADA](https://appdefensealliance.dev/masa/masa-assessors)).
- Criterion (e), "baseline mobile app security", almost certainly maps to MASA/MASVS (**my inference**). **These firms are the likely TCAs.** A solo founder will not become a TCA.
- **Gap:**
  - MASA labs test app security, not agent behaviour: intent reconfirmation, prompt injection, data minimisation during agentic runs.
  - Zimperium and NowSecure are adding AI to *their own* testing and SOC tooling ([Zimperium](https://zimperium.com/resources/zimperium-launches-new-ai-empowered-mobile-soc-agent-to-bolster-security-teams-defending-mobile-devices), [NowSecure](https://www.nowsecure.com/blog/2026/08/12/how-nowsecure-is-using-ai-to-advance-mobile-app-security-testing/)). They are not testing third-party *agents*.
  - I found no vendor selling an "agentic behaviour test suite for Android assistants" (**unverified**; Eydle should be checked).
  - The labs will need exactly this methodology and tooling for criteria (b), (c) and (d).

## 4. Is it global?
| Jurisdiction | Status | Assistant-level Android access? |
|---|---|---|
| UK CMA | Android SMS designation 22 Oct 2025. The 23 Sep 2026 proposals put AI assistants on a yearly choice screen; consultation closes 9 Oct ([PinMeTo](https://www.pinmeto.com/news/uk-cma-search-choice-screen-ai-assistants-2026/)) | Choice screen only so far; no interop yet |
| Japan MSCA | In force 18 Dec 2025 and covers OS-feature interop. JFTC is considering AI agents next ([KU Leuven](https://www.law.kuleuven.be/ccm/blog/posts/japan_mobile_software_competition_act)) | Possible; the scope for assistants is **unverified** |
| Brazil PL 4675/2025 | Urgency approved Mar 2026; not law yet ([CSIS](https://www.csis.org/blogs/charting-geoeconomics/unpacking-brazils-latest-effort-regulate-digital-markets)) | Interop powers exist in the bill; 2027+ |
| Korea | Only the AI Basic Act (Jan 2026); no platform act | No |
| US DOJ | Mehta remedies ban exclusive deals for Gemini and Assistant for 6 years; cross-appeals are pending ([DOJ](https://www.justice.gov/opa/pr/department-justice-wins-significant-remedies-against-google)) | No interop mandate, but OEMs can now pre-install rival assistants |

**Verdict:** assistant *certification* is EU-only for now. The criteria are likely to become a de facto global standard if Google runs one programme worldwide, and Japan and the UK are the next candidates.

## 5. Outside regulation
- **AppFunctions: no.** `EXECUTE_APP_FUNCTIONS` is `internal|privileged`, i.e. system apps only; a `normal` level sits behind a flag with a device allowlist ([Android Dev](https://developer.android.com/ai/appfunctions); AOSP detail via a secondary source, **verify**).
- **Screen automation: no for Play apps.** Play policy says "Any use of the Accessibility API that enables an app to autonomously initiate, plan, and execute actions or decisions is strictly prohibited" ([Play](https://support.google.com/googleplay/android-developer/answer/10964491?hl=en)). Advanced Protection mode also revokes non-accessibility-tool access.
- **Default assistant role: yes, globally**, via ROLE_ASSISTANT (long-press invocation and screen context), but it gives no action powers.
- **Outside the EU, the only routes to agentic power are OEM partnerships** (the Perplexity–Samsung model) **or sideloading.** So the EU decision really is the only open door. It also shows that OEMs are a second buyer: they grant system access and need their own vetting once "OEM vetting" becomes the fallback.

## 3 recommendations for v1
1. **Fix the facts and re-aim the product.**
   - Drop the 50k MAU claim.
   - Drop "UNO sells certification" (the TCAs are established labs).
   - Reposition as the **agentic conformance test suite and SDK that TCAs and applicants both use** for criteria (b), (c) and (d): intent-reconfirmation tests, prompt-injection and data-disclosure harnesses, and audit-log evidence packs.
   - The first buyers are the labs themselves (DEKRA, NowSecure, NCC, Applus+, SGS, TrustCB). This is a partnership sale, not selling to the big labs directly.
2. **Get certified as a Qualified AI Assistant yourself**, now that there is no user threshold. Being among the first certified in May–Aug 2027 is the credibility proof, and it is "reference implementation" marketing.
3. **Make the consultation window the go-to-market.**
   - Submit comments on Google's draft terms (Feb 2027) with an open-source reference spec for criteria (b) and (d). This is a cheap way to become known.
   - In parallel, pitch OEMs (Samsung, Xiaomi, Nothing, Motorola) doing Perplexity-style deals as a non-EU buyer of the same vetting.

## Open questions for iteration 3
- Will Google geofence to the EEA, or run one global QAA programme?
- Has Google filed a General Court appeal? It would not suspend the deadlines by default.
- Are TCAs interested in an agent-testing partner, or building in-house? Talk to DEKRA, NowSecure and TrustCB. What does Eydle do?
- What would the evidence for criteria (b) and (c) look like: an ETSI EN 303 645-style scheme, OWASP MASVS plus the OWASP Agentic Top 10?
- Does Japan's MSCA OS-interop clause already cover assistant or agent features?
- Would OEMs (Samsung, Xiaomi, Honor) pay for third-party agent vetting outside the EU?
