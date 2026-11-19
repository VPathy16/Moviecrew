# Red team, iteration 9: attacking v8

**Verdict:** v8 is disciplined but written for a founder in London. For someone probably in India it is a job hunt dressed up as a company. v9 should turn the floor into **INR-denominated runway**, drop "stranger audits strangers" in favour of **sanctioned bounties plus warm Indian buyers**, and name one company kernel with a kill date.

## Findings, ranked

**1. The floor assumes a location he probably doesn't have (fatal to the plan's numbers).**
- The founder built UNO around Swiggy and UPI. "We cannot focus on India" is about the *market*, not where he lives.
- v8's top jobs are Perplexity (NY/SF/London/Belgrade hybrid), Proton (Geneva, office-first) and minitap (Paris/London). Each means a visa or a move. A 90-day plan cannot count on any of them.
- The rates are US rates too:
  - Indian senior Android freelancers get **$35–50/h** from international clients. The Upwork median for Indian app developers is **$27/h**, not the $80–160/h v8 cites ([SecondTalent](https://www.secondtalent.com/developer-rate-card/android-developer-india/), [Upwork](https://www.upwork.com/hire/indian-app-developers/cost/)).
  - Remote US-company roles from India through an employer of record pay **$90–150k** ([Omnivoo](https://omnivoo.com/blog/remote-developer-salary-india-2026)).
  - Indian product companies pay senior Android **₹35–60 LPA**.
- **Change:** re-target the floor to three things:
  - (a) remote-from-India roles: US/EU remote-first companies via Deel/Remote, plus Perplexity/minitap *only if* the posting says remote;
  - (b) Indian AI/agent teams: Sarvam, Razorpay, PhonePe, CRED, Swiggy, Zepto;
  - (c) part-time contracting at a realistic **$35–60/h**.
- Put the founder's location in v9 as an explicit, stated assumption.

**2. The INR advantage is unused, and it is the answer to "way out, not a job" (biggest upside).**
- Contracting at $45/h for 2.5 days a week is about 80h a month, roughly **$3.6k ≈ ₹3L/month**. That is well above a Bengaluru living cost of ₹1–1.5L.
- So half the week buys an **indefinite runway** for the other half. A Western solo founder can't do that without funding.
- **Change:** rename "floor" to "runway engine". Make it a split, not a fallback: **50% paid work capped at 2.5 days a week, and 50% company, protected.**
- Replace v8's "else 80% to contracting" with this:
  - A full-time job is the fallback only if contracting doesn't reach ₹1.5L/month by 31 Dec.
  - Otherwise the company time survives even if the review offer fails.
- This is how you keep ambition without the miracle.

**3. The audit post is not a channel any more. MCP scanning is commoditised.**
- **Snyk Agent Scan** (formerly Invariant's mcp-scan) is free. Cisco has mcp-scanner. dev.to is full of "I scanned 10 MCP servers" posts. Automated "audits" sell for **$1–25** on Apify-type marketplaces ([Snyk](https://github.com/snyk/agent-scan), [dev.to](https://dev.to/ventrova/sentinel-scan-cli-vs-cisco-mcp-scanner-vs-snyk-agent-scan-comparing-open-source-mcp-security-f5a)).
- "What 5 MCP servers let an agent do" will read as post #200.
- **Change:** differentiate on what Snyk doesn't cover.
  - Snyk covers tool poisoning, description injection and secrets.
  - It does not cover the **action-authorisation layer**: which calls move money, send messages or delete data without a human gate. Nor does it cover **phone-side screen injection** against Android agents.
  - Title the post on that gap: "Scanners pass these servers; here's what an agent can still spend." Run Snyk alongside and show the delta.

**4. The legal/ethical risk is real, and v8 understates it.**
- Reading open-source code, or running it **locally**, is fine.
- Probing a company's **hosted** remote MCP server, or its ChatGPT app with live accounts, without written authorisation is unauthorised access. That exposure exists under IT Act s.43/66 (India), the CFAA (US) and the Computer Misuse Act (UK), and payment tools make it worse.
- Naming unfixed vendors invites a legal letter.
- **Change:**
  - Audit only OSS servers run locally, or targets inside published bounty scopes.
  - Use **huntr** or vendor programmes. Reported MCP CVE bounties run **$1.5k–50k** (single secondary source, unverified).
  - Apply 90-day coordinated disclosure, and never test paid tools against live accounts.
- **CVEs are also the credential this stranger lacks.** Two CVEs beat any testimonial.

**5. "A stranger in India charges €2–3.5k" won't close cold, but it will close warm.**
- Western mid-market buyers buy security from firms with contracts, insurance and a track record. Pentests start around $4k from known firms. An unknown solo reviewer with no CVEs converts near zero, whatever the price.
- The warm pool is **Indian fintech and commerce companies wiring up agent payments.** NPCI's agentic UPI pilots (with Razorpay and the major assistants) are the obvious ones. His Swiggy MCP plus on-device UPI work is directly relevant, and he can meet them in person.
- This does not break "not India": it is **B2B selling to Indian companies building for global agents**, not the consumer market he rejected.
- **Change:**
  - First two reviews priced at **₹1–2.5L**, at Indian fintechs or marketplaces.
  - EU/US at €2–3.5k only after CVEs and testimonials exist.
  - Verify the NPCI pilot status in week 1 (unverified here).

**6. v8 has no company path, so the founder will reject it.**
- 10% on AgentGuard is a hobby.
- **Change:** name the kernel. It is an **"agent action gate" for MCP servers**: server-side confirmation and spend-limit middleware using MCP elicitation, drawn from UNO's classifier and gate.
- Reviews become customer discovery. Log every finding into a shared schema.
- **31 Dec kill/continue test:**
  - Continue if ≥3 reviews or bounties show the *same* missing-gate pattern, **and** ≥1 buyer says "I'd pay monthly for this".
  - If so, spend Q1 building the middleware at 50% time, funded by the runway engine.
  - If not, archive it with no regret.
- Be honest about the risk: agent authorisation has funded players (Auth0 for AI agents, Descope, Arcade, Permit.io). The kernel survives only as **policy for actions** (spend, send, delete), not as identity or auth.

## v9 changes (sharpest)
1. Make the founder's location an explicit assumption. Re-price every rate and job for India.
2. Replace "floor" with a **runway engine**: 2.5 days a week of contracting at $35–60/h, which covers about 2× living costs.
3. Replace unsolicited audits with **locally run OSS audits plus huntr bounties** under coordinated disclosure. The goal is CVEs.
4. First buyers are Indian fintechs and marketplaces building agent payments, priced in ₹.
5. Post angle: "what scanners miss", the authorisation gap, with a Snyk comparison.
6. Name the **action-gate kernel** with the 31 Dec kill/continue test above.

## What the final (v10) answer should be
"No, you are not out of options. You are out of *consumer-app* options, and that part of your thesis is right.
- Stop building UNO as a product.
- Your working asset is the safety layer: the role classifier, the confirmation gate, and phone-executes/AI-plans.
- Living in India, 2.5 days a week of contracting pays for an indefinite runway.
- Spend the other half turning that safety layer into CVEs, paid reviews and a small action-gate product for companies exposing pay/send/delete tools to agents.
- On 31 Dec you'll know from real buyers whether it's a company. If it isn't, you'll have CVEs and a portfolio that gets you a remote agent-safety role.
- No miracle required, just 13 weeks."
