# Market research, iteration 5 (2026-09-28): market size, comparable outcomes, non-dilutive money, accelerators

## 1. Market size: many builders, no mobile-specific estimate
- **No analyst figure isolates on-device or mobile agents** (**unverified** after searching).
- The generic "AI agent market" forecasts disagree widely and are low quality:
  - $10.9B in 2026, rising to $110B by 2032 ([MarkNtel](https://www.marknteladvisors.com/research-library/ai-agent-market.html)).
  - "1.3B agents by 2028" ([Nevermined](https://nevermined.ai/blog/ai-agent-market-size-statistics)).
  - None of these should be used in a pitch.
- **Device proxy:** Counterpoint expects GenAI phones to be 45% of 2026 shipments ([Counterpoint](https://counterpointresearch.com/en/insights/genai-smartphone-share-to-rise-to-45-percent-of-global-shipments-in-2026)). 2026 shipments are also heading for a record decline ([Counterpoint](https://counterpointresearch.com/en/insights/2026-smartphone-shipments-to-post-worst-annual-decline-on-record-as-memory-crisis-and-geopolitical-shocks-converge)).
- **Who is building agents:**
  - Qualcomm's Snapdragon 8 Elite Gen 6 (Sep 2026) is pitched as the chip for "agentic AI". It runs 30B MoE models locally in flagships from Honor, Motorola, OnePlus, Oppo, vivo, Xiaomi, iQOO and Redmi ([Qualcomm](https://www.qualcomm.com/news/releases/2026/09/snapdragon-leads-the-agentic-ai-age-with-two-of-the-world-s-fast)).
  - At MWC 2026, Samsung's Galaxy S26 and Motorola (with Perplexity/Copilot/Gemini) showed screen-aware agents ([Techspective](https://techspective.net/2026/03/22/mwc-2026-the-year-the-smartphone-mutated-into-an-ai-agent/)).
- **Realistic count of potential buyers:** about 10 OEMs, 5–10 funded agent startups or frameworks, and a long tail of apps adding AppFunctions.
  - OEMs build in-house, and the Chinese OEMs are hard for a solo EU/Indian founder to sell to.
  - Zebra and Honeywell had no public agent-guard needs that I could find (**unverified**).
- **Implication:** the audience is a developer community, not a market that analysts measure. Revenue has to come from a few integration contracts, not from licence volume.

## 2. Comparable outcomes: acquisitions came fast, and every buyer was a platform

| Company | Founded | Outcome | Price |
|---|---|---|---|
| Protect AI | 2022 | Palo Alto, closed Jul 2025 | **$634.5M** (SEC 10-K) ([SiliconANGLE](https://siliconangle.com/2025/04/28/palo-alto-networks-buys-protect-ai-reported-500m-debuts-new-cybersecurity-tools/)) |
| Lakera | 2021 | Check Point, Sep 2025 | **about $300M** ([Calcalist](https://www.calcalistech.com/ctechnews/article/rj5bc1vige)) |
| Invariant Labs (ETH spin-off) | 2024 | Snyk, Jun 2025 (about 1 year after founding) | undisclosed ([Snyk](https://snyk.io/news/snyk-acquires-invariant-labs-to-accelerate-agentic-ai-security-innovation/)) |
| Promptfoo (open-source eval/red-team tool) | 2024 | OpenAI, 9 Mar 2026 | undisclosed; had raised $23M at an $86M post-money valuation; used by 25% of the Fortune 500 ([TechCrunch](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/)) |
| Guardrails AI (open-source) | 2023 | Harvey, 9 Sep 2026 | undisclosed; founders joined Harvey's product and engineering team, so effectively a team acquisition ([Harvey](https://www.harvey.ai/blog/guardrails-ai-joins-harvey), [TNW](https://thenextweb.com/news/harvey-550m-round-15-6bn-guardrails-acquisition)) |

- **LangChain** reached a $1.25B valuation (Oct 2025) on about $12–16M ARR from LangSmith ([SiliconANGLE](https://siliconangle.com/2025/10/20/ai-agent-tooling-provider-langchain-raises-125m-1-25b-valuation/), [Contrary](https://research.contrary.com/company/langchain)). Open source turns into money through a hosted observability and eval product, which maps onto v4's hosted runner.
- **NeMo Guardrails and Llama Guard** are free from Nvidia and Meta. Generic guardrail software is priced at zero, so the defensible part has to be Android-specific.
- **Pattern:**
  - Open-source AI-safety tools get bought 1–3 years after founding, for their teams and research.
  - Buyers are security platforms (Palo Alto, Check Point, Snyk) or AI apps and labs (OpenAI, Harvey).
  - The large deals ($300–635M) went to companies with enterprise revenue. Undisclosed deals are usually acqui-hires.
- **Implication:** the realistic good outcome for AgentGuard is a team acquisition by a mobile-security vendor or an agent platform. That requires visible adoption and a public reputation for its research, not revenue.

## 3. Non-dilutive money: small, slow, and mostly closed
- **NLnet:**
  - NGI Zero Commons closed after its final call on 1 Jun 2026.
  - Its successor is Open Internet Stack "Restack", with grants of €5–50k (2026–2030) and a **deadline of 3 Nov 2026** ([NLnet](https://nlnet.nl/news/2026/20260612-NGIZero-stocktaking.html), [call](https://nlnet.nl/news/2026/20260903-call.html)).
  - Its fit for an agent guard is weak to moderate: the call is about "internet commons".
  - A new GenAI policy makes work generated mostly by LLMs ineligible, so wait for that revision.
  - Non-EU eligibility is **unverified**. Past NGI calls accepted applicants worldwide.
- **EU Digital Europe (ECCC) AI4SME:**
  - €3–5M projects co-funded at 50–75%, for EU/EEA legal entities, deadline 14 Jan 2027 ([EuroAccess](https://www.euro-access.eu/en/calls/2988/Strengthening-cybersecurity-capacities-of-European-SMEs-with-cybersecure-AI-powered-solutions)).
  - **Not a fit** for a solo founder. At most, join as a subcontractor in someone else's consortium.
- **UK AISI Challenge Fund:**
  - £50–200k, open to international applicants, but **all AISI grant programmes are currently closed**. The last deadline was 1 Apr 2026 ([AISI](https://aisi.gov.uk/grants)).
  - It favours academic and non-profit hosts, so partnering with the Picek group would help.
- **OpenAI Cybersecurity Grant:** rolling applications, awarded in $10k increments, often paid as API credits; defensive and open-source projects are preferred ([OpenAI](https://openai.com/index/openai-cybersecurity-grant-program/)). **This is the easiest fit right now.** The new $1B "Daybreak" pledge is credits, not cash ([Register](https://www.theregister.com/security/2026/09/04/openai-commits-1b-in-ai-credits-to-frontline-cyber-defenders/5294382)).
- **Frontier Model Forum AI Safety Fund:** gave $5M to 11 grantees in Dec 2025 (including Apollo, with "agent evaluation" in the RFPs). It works through RFPs, and I found no open call ([FMF](https://www.frontiermodelforum.org/updates/announcement-of-new-ai-safety-fund-grantees/)).
- **Sovereign Tech Fund:** minimum €50k, for existing "base technologies". A new library isn't eligible ([STF](https://www.sovereign.tech/programs/fund)).
- **Alpha-Omega:** $12.5M from the AI labs (Mar 2026), aimed at helping maintainers of widely used packages with the flood of vulnerability reports. It does not fund new projects ([OpenSSF](https://openssf.org/press-release/2026/03/17/linux-foundation-announces-12-5-million-in-grant-funding-from-leading-organizations-to-advance-open-source-security/)).
- **Realistic total by mid-2027:** €0–60k (NLnet or OpenAI credits), plus a possible AISI grant if a round reopens with an academic partner.

## 4. Accelerators
- **Seldon Lab (SF):** up to $500k per startup and 5–10 teams per batch, focused on AI security infrastructure. Batch 1 alumni sell to xAI and Anthropic ([Manifund](https://manifund.org/projects/ai-security-startup-accelerator-batch-2)). **Best thematic fit.** Batch 3 timing is unknown.
- **Catalyze Impact:** a non-profit AI-safety incubator that runs several programmes a year from 2026 ([Catalyze](https://catalyze-impact.org/blog/ai-safety-resilience-founding-opportunities)). Suits a founder without a co-founder.
- **Juniper Ventures:** a VC fund for AI assurance, now raising Fund II with DNV as an investor ([DNV](https://www.dnv.com/news/2026/juniper-fund2/)). Better as an investor to approach after the Seldon or Catalyze stage.
- **YC:**
  - The 2026 batches are heavy on agent infrastructure, including Alter (zero-trust for agent tool calls) and Galini (guardrails-as-a-service) ([YC](https://www.ycombinator.com/companies/industry/compliance)).
  - YC accepts the category, but a solo founder with an open-source library and no traction is a weak application.
- **Merantix** backed droidrun, so it is a warm path through that framework (**unverified** that Merantix runs an accelerator track for this).
- **Entrepreneur First** suits a founder looking for a co-founder, but its agent-security focus is **unverified**.

## 5. Open questions from market_4
- **droidrun/mobilerun and minitap mobile-use:**
  - Neither repository has a SECURITY.md or any security advisories (checked today on GitHub).
  - An issue search found no prompt-injection issues in minitap's repository. The same search on the mobilerun repository also returned none (the droidrun/droidrun name failed to resolve).
  - I found no public response to "Not an A11y" (**unverified**).
  - **This is an opening:** offer them coordinated disclosure plus a SECURITY.md and guard PR.
- **Appdome correction to market_4:**
  - Appdome **does** have an agent product, but it **detects and blocks** AI agents and "agentic AI malware" that drive apps through accessibility, using behavioural biometrics (since Jun 2025) ([Appdome](https://www.appdome.com/press-release/appdome-is-the-first-to-detect-agentic-ai-malware-on-mobile-devices/)).
  - Its "agentic" SecOps and support agents are internal tooling.
  - So Appdome is on the **opposite side** from AgentGuard: it protects apps *from* agents, while AgentGuard protects agents *from* apps and screens.
  - That makes the two complementary. An app vendor could permit a guarded agent and block an unguarded one: an **"allowed-agent attestation"** handshake.
- **Promon:** I found nothing agent-related (**unverified**).

## 3 recommendations
1. **Apply for the cheap money that is open now:**
   - OpenAI Cybersecurity Grant (rolling), for a defensive open-source Android agent guard.
   - NLnet Restack by 3 Nov 2026, framed as a mobile agent-safety commons, human-written, after checking the GenAI policy.
   - Line up the Picek group as host for the next AISI round.
   - Skip the Digital Europe call, STF and Alpha-Omega.
2. **Use a disclosure-first route into droidrun and minitap:**
   - Neither has a security policy. File a coordinated report of the "Not an A11y" vectors against their current releases, together with a PR that adds a SECURITY.md and an AgentGuard integration.
   - This is the fastest path to the kill test's "≥3 external projects".
3. **Aim for the acquihire outcome, not SaaS scale:**
   - The comparables say team acquisitions happen within 1–3 years once there is visible open-source adoption and a reputation for research.
   - Add an "agent attestation" feature that makes AgentGuard complementary to Appdome's agent blocking, which positions Appdome, Promon or Guardsquare as acquirers.
   - Apply to Seldon or Catalyze for 2027 rather than YC.

## Open questions for iteration 6
- Seldon batch 3 and Catalyze 2027 dates and eligibility (remote, non-US founder)?
- Does NLnet Restack accept non-EU applicants, and what does the revised GenAI policy say?
- Does Appdome's agent detection offer an allow-list or API for "trusted agents"? Is there a standard for agent attestation (Android Play Integrity for agents, AppFunctions caller verification)?
- Do the Samsung, Xiaomi or Honor agents run third-party GUI agents or expose an SDK? Is there any OEM security programme for agents?
- Were droidrun or minitap contacted by the "Not an A11y" authors, and have they patched anything since Aug 2026?
- Guardrails AI's actual funding and the size of the Harvey deal (for acqui-hire benchmarks).
