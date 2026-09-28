# Market research, iteration 9 (2026-09-28): who pays for MCP reviews, the scanner crowd, and the India base

## Headline
- **Buyers do pay for MCP reviews, but the market price is set by solo sellers at about $1.5–5k.** v8's €2–3.5k "Agent Surface Safety Review" sits exactly on the going rate, so it isn't a premium product.
- **Tool-role classification is already done at scale by someone else.** PolicyLayer sorts 518k tools across 32.8k MCP servers into Read, Write, Execute, Destructive, Financial and Other. AgentGuard must not claim that as its edge.
- **For an India-based founder, the job/contract floor is strong.**
  - Remote senior AI work for US companies pays ₹60–80 LPA.
  - Contracting pays $50–150/h.
  - Even at the low end of those ranges the floor covers living costs many times over.

## 1. Evidence of paid MCP and agent security reviews
| Seller | Offer | Price | Notes |
|---|---|---|---|
| **Pyfio mcp-audit** (Andreas Tissen, solo, Soltau DE) | Manual audit, 3 days | **€2,500** | Also a SaaS: Pro €19–29/mo, Team €99/mo, Enterprise €25–120k/yr. 3 unnamed testimonials, including a fintech. Solo operator, which proves the solo model exists; traction is **unverified**. [audit.pyfio.com](https://audit.pyfio.com/) |
| **MCPScan / MCP Signoff** | Handoff pack / security-review readiness pack / pack plus manual testing | **$1,500 / $2,500 / $5,000** | Free `npx` CLI serves as the funnel. This is **the same "CLI → fixed audit" model as v8.** [getmcpscan.xyz](https://getmcpscan.xyz/) |
| **Bonis Systems** (Wyoming) | 1 server, ≤10 tools, report in 10 days, 1 re-test | Private offer | Sold through AWS Marketplace. [AWS](https://aws.amazon.com/marketplace/pp/prodview-l6bptm6t7cpea) |
| **Zealynx** (Wrocław) | Code and design review of an MCP server, 2–4 weeks | Quote; intro offer $500 for $2,400 of time | [Zealynx](https://www.zealynx.io/services/ai-audits/mcp-security-audit) |
| **Software Secured** | AI/LLM/MCP pentest | From **$10,800** | [list](https://www.softwaresecured.com/post/best-ai-penetration-testing-services) |
| **Trail of Bits, Bishop Fox, NCC, Praetorian, NetSPI** | AI and agent testing inside broader engagements | Custom/enterprise | Trail of Bits ships a free mcp-context-protector ([ToB MCP](https://trailofbits.com/mcp/)). Bishop Fox has AIMap, which scans exposed MCP servers ([BF](https://bishopfox.com/blog/introducing-aimap-security-testing-for-ai-agent-infrastructure)). |

- **No public case study** names a company that bought a standalone MCP review. Demand is inferred from sellers existing and posting prices, not from verified buyers (**unverified**).
- **Tailwind:** the Vulnerable MCP Project lists 50 vulnerabilities, 13 of them critical, as of Aug 2026 ([Cybersecify](https://cybersecify.com/blog/mcp-server-pentest-methodology-2026/)).

## 2. Scanner crowding (it is high)
- **Free or open-source scanners:**
  - Cisco mcp-scanner (YARA rules plus an LLM plus Cisco's AI Defense API).
  - Snyk Agent Scan (the former Invariant; free Skill Inspector; Evo pricing not public).
  - Enkrypt, which has an open-source gateway and a scanner.
  - Akto (free tier).
  - Docker MCP Gateway.
  - Pipelock.
- **Venture-backed platforms:**
  - Runlayer ($11M).
  - Zenity ($38M Series B).
  - Backslash ($27M).
  - Noma, Lasso, Nightfall.
- Sources: [dev.to 15 tools](https://dev.to/luckypipewrench/best-ai-agent-security-tools-2026-15-options-compared-ekg), [PipeLab](https://pipelab.org/blog/mcp-scanner-comparison-2026/), [Enkrypt](https://www.enkryptai.com/product/mcp-scanner), [Akto](https://www.akto.io/mcp-security), [Snyk](https://snyk.io/news/snyk-launches-agent-security-solution/).
- **Role classification is already taken.** [PolicyLayer](https://policylayer.com/research/state-of-mcp) classifies tools by verb and schema, and its gateway applies allow/deny/require-approval rules per category. Its research counts 12,718 destructive tools and 4,818 financial ones ([risk](https://policylayer.com/risk)). The OWASP MCP cheat sheet already recommends confirmation for destructive, financial and data-sharing actions ([OWASP](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html)).
- **The gaps still open (none found in the scanners or in PolicyLayer):**
  1. **Personal-data and messaging roles** ("send on the user's behalf", "reads PII") as distinct classes.
  2. **The mobile side:** AppFunctions and Android screen-agent injection.
  3. **The consumer-app viewpoint:** "what can ChatGPT or Gemini do inside *my* app", as opposed to the enterprise viewpoint of "which MCP servers may my employees use".
- **SaaS pricing floor:** €19–99/mo (Pyfio). A solo SaaS here is a race to the bottom against free tools from Cisco and Snyk.

## 3. India-based founder economics
- **Salaries:**
  - Senior Android in India: ₹22–48 LPA; FAANG ₹35–60 LPA ([resumevera](https://resumevera.com/salary-guide/android-developer), [Glassdoor](https://www.glassdoor.com/Salaries/bangalore-india-senior-android-developer-salary-SRCH_IL.0,15_IM1091_KO16,40.htm)).
  - Senior AI engineers working remotely for US companies: **₹60–80 LPA** ([taggd](https://taggd.in/blogs/ai-engineer-salary/), [Omnivoo](https://omnivoo.com/blog/remote-developer-salary-india-2026)). Aggregator figures, so medium confidence.
- **Contract rates:**
  - Upwork/Toptal senior AI: $50–150/h.
  - Uplers: $25–70/h.
  - Managed offshore: $15–25/h ([adsnipper](https://adsnipper.com/blog/cost-to-hire-ai-developer/)).
  - **So €2.5k for a 3–4-day review is about $80–100/h**: a good rate from India, and not undercut by the US-priced sellers.
- **Remote and India roles:**
  - Perplexity has India listings on Indeed and Naukri ([Indeed](https://in.indeed.com/q-perplexity-careers-in-india-jobs.html)). Its Ashby board didn't render, so **whether its Android roles are open to India is unverified**. v8's Android role lists Belgrade, London, NY and SF.
  - LiteLLM hires India-remote ([Wellfound](https://wellfound.com/role/l/ai-engineer/india)).
  - YC startups hire remote ([YC jobs](https://www.ycombinator.com/jobs/role/software-engineer/remote)).
  - **Implication:** Proton (Geneva) and minitap (Paris) are relocation plays, not the realistic floor.
- **Bootstrapped proof from India:** **Astra Security** (New Delhi) is an Indian pentest SaaS.
  - About **$9.8M ARR with no VC**, per Latka ([Latka](https://getlatka.com/companies/getastra.com)). Business Wire reports a 2025 raise, so **"bootstrapped" is contested** ([BW](https://www.businesswire.com/news/home/20250205502953/en/Astra-Security-Raises-Funding-to-Simplify-Cybersecurity-With-AI-Driven-Pentesting)).
  - Customers in 70+ countries, including Loom and HackerRank.
  - Astra already markets AI/MCP pentests, so it's a competitor and also a potential employer or partner ([Astra](https://www.getastra.com/blog/ai-security/llm-and-ai-penetration-testing-companies/)).
  - BrowserStack is the classic bootstrapped Indian dev-tool company.

## 4. Startup programmes open to Indian solo founders
| Programme | Terms | Deadline / status | Source |
|---|---|---|---|
| **YC W27** | Standard deal | Deadline **2 Nov 2026**; decisions by 11 Dec; batch Jan–Mar in SF | [ycroaster](https://www.ycroaster.com/tools/yc-application-deadline), [YC](https://ycombinator.com/apply) |
| **EF Bangalore** | Equity-free stipend, then up to about ₹2.3Cr (~$250k); solo founders with no idea welcome | Fall-26 cohort already started; watch for the next round | [startupfunds](https://startupfunds.in/funding/entrepreneurs-first-ef-bangalore-fall-26) |
| **Antler India** | "Before Day Zero" for solo founders 3–6 months from starting | — | [Antler](https://www.antler.co/residency/india) |
| **Peak XV Surge** | Up to $5M | Wants traction | [Surge](https://surge.peakxv.com/) |
| **Emergent Ventures India** | Small grants | 19th cohort in Sep 2026 skews to deep tech; a cheap long shot | [MR](https://marginalrevolution.com/marginalrevolution/2026/09/emergent-ventures-india-19th-cohort.html) |

- AI Grant and Seldon were **not verified** this round.

## 3 recommendations
1. **Keep the review offer but change its positioning.**
   - Stop selling "a tool-role risk map", which PolicyLayer, Cisco and Snyk give away. Sell a **consumer-app agent-safety review**: which of your MCP / ChatGPT-app / AppFunctions actions can pay, send or expose PII without confirmation, plus live injection tests from web and screen content.
   - Price at **$2.5k** (matching Pyfio and MCPScan), with a $5k tier that adds manual testing.
   - Use the free CLI only as a funnel. Build on Cisco or Snyk scanners rather than competing with them, and add a PII/messaging role layer plus an Android layer.
2. **Put the India floor first, in this order:**
   1. India-remote roles at US AI startups (₹60–80 LPA target: LiteLLM, YC remote roles, Perplexity India listings).
   2. Toptal/Contra at $60–100/h.
   3. Relocation roles (Perplexity Belgrade/London, Proton, minitap) only as stretch goals.
   - Also approach **Astra Security, Akto and Enkrypt**, which have Indian roots and sell AI/MCP security, for a contract or a job: "I'll build your mobile/agent-action test module."
3. **Apply to YC W27 by 2 Nov at almost no cost**, using the audit post and AgentGuard as evidence. Register interest for the next EF Bangalore cohort. Don't count on either; it's a one-evening option.

## What the final answer should be
- **The core claim:** the founder is not out of options.
- **The base:** from India, a remote senior Android/AI-agent job or contract (₹40–80 LPA, or $50–100/h) is the dependable base, and is achievable within about 90 days.
- **The upside:** paid consumer-app agent-safety reviews at about $2.5k. Buyers exist at that price, shown by solo sellers posting prices publicly (Pyfio, MCPScan). Differentiation comes from mobile, PII/messaging actions and injection tests, not from generic MCP scanning.
- **The optional bets:** a YC W27 application by 2 Nov and EF/Antler as later options.
- **Kill SaaS ambitions for now.** The scanner market is crowded with free tools from Cisco and Snyk and with venture-funded gateways. Revisit only if reviews reveal a repeatable need that nobody serves.
