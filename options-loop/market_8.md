# Market research, iteration 8 (2026-09-28): the income leg of v7

## Headline
Demand for "agent-ready Android app" work is **real but pre-commercial**, and Google is commoditising the easy part.
- **Where AppFunctions stands:**
  - Still an experimental preview (`androidx.appfunctions` 1.0.0-alpha10).
  - Gemini's end-to-end integration is private preview, reached through an **Early Access Program form**. Registering does not guarantee access.
  - Only "a limited number of apps and system agents can access the entire pipeline" ([Android docs](https://developer.android.com/ai/appfunctions), [EAP form](https://forms.gle/GN5ybjQFhzHRCguM7)).
- **Google is also doing the work for free:**
  - It ships an official **AppFunctions agent skill** that generates the code and tests it over ADB ([Jul 2026 blog](https://android-developers.googleblog.com/2026/07/build-intelligent-android-apps-appfunctions.html)).
  - Gemini task automation reached **40+ apps** (shopping, restaurants, travel, tickets, e.g. Etsy and Expedia) through a "no-code change" UI-automation path ([9to5](https://9to5google.com/2026/07/22/gemini-task-automation-samsung/), [May blog](https://android-developers.googleblog.com/2026/05/the-android-show-developers-cut-2026.html)).
- **Implication:** plain "add AppFunctions to your app" is a thin, shrinking service. The billable part is **safety and design**: which functions to expose, confirmation and authorisation for payment or messaging actions, data minimisation, and hardening against injection. That matches v7's "agent-safe" framing, but no buyer demand for it has been observed yet.

## 1. Demand for agent-ready app work
- **AppFunctions adoption beyond ride-hailing and food:**
  - KakaoTalk (messages, calls) is an early tester.
  - "25 apps' use cases" run locally across OEMs.
  - Google's own Calendar, Notes and Tasks, and Samsung Gallery, use it.
  - The public reference app is Google's sample JetPacker, not a customer ([May blog](https://android-developers.googleblog.com/2026/05/the-android-show-developers-cut-2026.html), [9to5 Feb](https://9to5google.com/2026/02/25/android-appfunctions-gemini/)).
  - The initial automation partners were Lyft, Uber, Grubhub, DoorDash, Uber Eats and Starbucks.
- **No documented partner criteria.** Getting into the Gemini integration means the EAP form, then Google picks. No published criteria were found (**unverified** whether any exist privately).
- **MCP on the consumer side is mainstream on the server side.** ChatGPT Apps (MCP-based) include Booking.com, Expedia, Spotify, Uber, DoorDash, Canva, Zillow and others. PayPal, Walmart, Instacart, OpenTable and TheFork were announced ([Fantasy](https://fantasy.co/latest/the-apps-inside-chatgpt-playbook-how-brands-are-preparing-for-openai-app-sdk), [OpenAI](https://openai.com/index/introducing-apps-in-chatgpt/)). Big brands build these in-house. The mid-market is the plausible client pool.
- **Agencies already selling it:**
  - **SCAND** has a dedicated "Android AppFunctions & AI Agent Integration" page: readiness audit, implementation, Gemini integration. No public prices; outstaffing or dedicated-team models ([SCAND](https://scand.com/services/android-appfunctions-ai-agent-integration/)).
  - The MCP-server service market is crowded and cheap at the low end:
    - Upwork gigs run $350 / $500 / $2,500 by tier ([Upwork gig](https://www.upwork.com/services/product/development-it-a-custom-mcp-server-for-your-ai-agent-1906508401626549581)).
    - Marketplace rates are $30–150/h ([Upwork](https://www.upwork.com/hire/mcp-server-developers/)).
    - Focused fixed-scope builds run €3–10k ([secondary](https://inspiredbyfrustration.com/blog/hire-mcp-server-developer)).
    - Agency minimums are $10–25k ([Entrans](https://www.entrans.ai/blog/custom-mcp-server-development-companies)).
- **Job posts naming AppFunctions or "agent-ready apps": none found** on the general boards (searched Sept 2026).

## 2. Rates (mostly SEO aggregators, so low confidence)
| Profile | Rate | Sources |
|---|---|---|
| Senior Android, US freelance | $80–160/h; one median $61/h | [Lemon](https://lemon.io/rate-calculator/android-developers/), [Arc](https://arc.dev/employer-blog/freelance-developers-cost/) |
| Senior Android, Eastern Europe | $30–50/h | same |
| AI agent / MCP engineer, US contract | $119–240/h, with claims of $300 for scarce specialists | [KORE1](https://www.kore1.com/ai-engineer-contract-rates-2026/), [SecondTalent](https://www.secondtalent.com/cost-to-hire/ai-agent-developer/) |

- **Trend:** mid-level Android rates are flat; senior and AI-feature rates are rising.
- **Note:** agent rates are for server-side LLM work. There is no benchmark for mobile agent safety.

## 3. Hiring (verified pages where linked)
| Company | Role | Location | Pay | Link |
|---|---|---|---|---|
| **Perplexity** | Android Mobile Engineer | Hybrid NY/SF/London/**Belgrade** | $180–240k | [Peerlist](https://peerlist.io/company/perplexity_a/careers/android-mobile-engineer/jobhjknng8r8e6raaca8o9jgodp6pa) |
| **Perplexity** | MTS Android, *Computer Growth* | — | — | [freehire](https://freehire.me/jobs/member-of-technical-staff-android-engineer-computer-growth-perplexity-vdqxzmdr) |
| **Proton** | Senior Android, Geneva | Office-first | — | [Greenhouse](https://job-boards.eu.greenhouse.io/proton/jobs/4932186101) |
| **Mistral** | Staff Mobile Engineer, Le Chat/Vibe | Paris | — | [Taro](https://www.jointaro.com/jobs/mistral-ai/staff-mobile-engineer-react-native-le-chat/) |
| **minitap** (Paris; $4.1M seed; 100% on AndroidWorld) | Senior Product Engineer | Paris or remote from London | €70–130k | [careers](https://www.minitap.ai/careers) |
| **minitap** | Forward Deployed Engineer | Paris or remote from London | €55–80k | same |
| **Google** | "Apps, Pixel" (agentic engineering); "GDC AI Applications and Agents" | — | — | [Pixel](https://careers.google.com/jobs/results/76806086312501958-software-engineer/), [GDC](https://www.google.com/about/careers/applications/jobs/results/126988379509138118-software-engineer-gdc-ai-applications-and-agents) |

- **Perplexity:** Computer now runs on Android, plus a local "Portable Computer" agent ([Android Authority](https://www.androidauthority.com/perplexity-portable-computer-local-ai-agent-3703083/)). That makes it **the most relevant buyer or employer**: it is a mobile agent with a direct DMA stake.
- **Proton:** the role is **office-first**. It spans Mail, Drive, VPN, **Lumo** and Meet; the post mentions "privacy-preserving AI" and prefers security experience.
- **Mistral:** the role is **React Native**, so the fit is weak.
- **minitap:** a mobile-agent QA company. No safety role.
- **Google:** no role explicitly naming AppFunctions was found (**unverified**; search careers directly).
- **droidrun/mobilerun:** pivoted to "cloud phones for agents". No careers page found.
- **Security vendors:**
  - Zimperium (May 2026) and Appdome (Mar 2026) launched *agentic SOC/compliance* agents, i.e. AI **for** mobile security, not security **against** agents ([Zimperium](https://www.prnewswire.com/news-releases/zimperium-launches-new-ai-empowered-mobile-soc-agent-to-bolster-security-teams-defending-mobile-devices-302763836.html), [Channel Insider](https://www.channelinsider.com/security/tools-and-platforms/appdome-makes-agentic-ai-announcements/)).
  - Nothing found for Promon or NowSecure.
  - The "agent-safe app" angle is still open at the vendors: a pitch opportunity and a hiring hook.

## 4. The DMA consultation
- **The earlier public consultation is closed.**
  - It ran 27 Apr – 13 May 2026. Submissions were not published but were shared with Alphabet ([EC](https://digital-markets-act.ec.europa.eu/dma100220-consultation-proposed-measures-interoperability-google-android-article-67-dma_en)).
  - ITIF published its own comment ([PDF](https://www2.itif.org/2026-comments-interoperability-google-android.pdf)).
  - The "numerous technical meetings" were between Google and the Commission. **No attendees are named** ([EC portal](https://digital-markets-act.ec.europa.eu/developer-portal/interoperability/alphabet-specification-proceedings-interoperability-ai-services_en)).
- **The Feb 2027 route:** Google must publish draft terms "for consultation by third parties and the Commission". **The mechanism is not yet specified.** It is probably a Google-hosted page, so watch the EC portal and the Android developer blog. The 50k MAU / €50M test applies to the **Search data** programme, not the assistant programme ([Bratby](https://bratby.law/dma-specification-decisions-google/)). This confirms v7's correction.
- **Appeal:** as of 21 Jul no appeal had been announced. The ~2-month-plus-10-day window closes around late September or early October 2026; **check whether a case T-xxx/26 appears**. Kent Walker publicly warned of risks to "privacy and security guardrails" ([Popular AI](https://www.popularai.org/p/replace-gemini-on-android-eu-rules)).
- **Rival statements:** none found from Proton, Brave, Mistral or Perplexity about using the access. Proton Lumo users are asking for default-assistant support (see market_7).

## 3 recommendations
1. **Reframe the offer from "make your app agent-ready" to "agent-safety review for apps exposing AppFunctions or MCP".**
   - What it covers: threat model, exposure map, confirmation and authorisation design, and an injection test suite.
   - Price: a €3–6k fixed-price audit, with implementation as an upsell.
   - Why: plain implementation competes with Google's free skill, SCAND and $500 Upwork gigs. Target the mid-market apps that transact (fintech, marketplaces, travel) and are in, or applying to, the EAP.
2. **Put Perplexity first in the job and partner loop, then minitap and Proton.**
   - Perplexity has an Android agent product (Computer, Portable Computer), a Belgrade and London hybrid option, and a direct DMA interest.
   - Lead with the AgentGuard injection-blocking demo.
   - Also pitch Zimperium, Appdome and Promon a "defend apps against rogue or injected agents" content or contract piece. It's a gap in their 2026 launches.
3. **Pre-register for the DMA route cheaply.**
   - Register for the AppFunctions EAP with UNO. It's free and signals intent.
   - Email the Commission's DMA contact to ask how third parties can comment on the 1 Feb 2027 draft.
   - Publish the para-125 criteria note **before** Feb 2027, so it exists when the draft lands.

## Open questions for iteration 9
- Did Google file a General Court challenge to DMA.100220 by early October? (Search the curia.europa.eu case list.)
- Which body hosts the Feb 2027 draft-terms consultation, and is there a sign-up list?
- Do any Google, Samsung or Perplexity job ads mention "agent safety", "prompt injection" or "AppFunctions"? (Check LinkedIn and Ashby directly.)
- Is there real buyer spend on "agent-safety audits" for consumer apps? Find 3 case studies or RFPs.
- Does droidrun/mobilerun have funding or hiring? Is Perplexity Computer on Android using Accessibility, and does it have a safety layer?
