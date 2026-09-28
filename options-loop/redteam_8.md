# Red team, iteration 8: attacking v7's income leg

**Verdict:** v7's direction is right and its income product is wrong. Almost nobody will pay for Android AppFunctions work in Q4 2026. Sell **agent-safety reviews of MCP servers and tool surfaces that already ship**, with Android contracting or a job as the floor. Turn the DMA "probe" into job applications.

## Findings, ranked

**1. The package has no buyer this quarter (fatal).**
- AppFunctions is still `1.0.0-alpha10` (Jul 2026), and Gemini integration is a private preview for trusted testers ([Android Devs](https://developer.android.com/ai/appfunctions), [9to5](https://9to5google.com/2026/02/25/android-appfunctions-gemini/)).
- An ordinary app that ships AppFunctions in Nov 2026 gets **zero callers**. DMA rival assistants arrive Aug 2027 at the earliest.
- The trusted testers (Samsung, Uber, DoorDash-type partners) have large Android teams and a direct line to Google.
- For everyone else it is a roadmap item with no revenue attached, and roadmap items don't get outside budget.
- **Change:** move the offer to where agent traffic exists **now**: remote MCP servers, ChatGPT apps and Claude connectors that companies have already shipped. These get called today, and many expose `delete`, `pay` and `send` tools with thin scoping. UNO's tool-role classifier is literally a tool for auditing them.

**2. Building it is a commodity, but reviewing it is not.**
- An AppFunction is an annotation plus a service. A competent in-house team follows the docs in days.
- What they lack is judgment about the safety design:
  - which tools to expose;
  - which tools need confirmation;
  - how to handle data minimisation;
  - how to resist injection.
- **Change:** sell a fixed-price **"Agent Surface Safety Review"**:
  - 3–4 days of work;
  - covers tool-role map, over-exposure findings, confirmation and scope fixes, an injection test and a written report;
  - **€2–3.5k**, with the first two clients at 50% in exchange for a named testimonial.
- Keep "we build it" as the upsell (€6–12k), not the lead. Rates are rough and unverified; test them in week 3.

**3. No channel: v7 never says how he finds clients.**
- There is no network and no reputation. Cold emails selling a service nobody has heard of from somebody nobody knows convert at close to zero.
- **Change:** make the public artefact the channel.
  - MCP registries and GitHub list thousands of servers **with maintainers' names attached**.
  - Audit 5 popular open-source ones with the classifier.
  - Disclose privately, then publish "What 5 MCP servers let an agent do without asking" (anonymise anything unfixed).
  - A findings post, plus a direct note to each maintainer, is warm outreach that earns reputation. Add Malt, Contra and Upwork profiles for inbound.

**4. The job loop is the real income leg, and v7 buries it as "in parallel".**
- A job or contract offer is the highest-probability source of money within 90 days.
- A salaried or contract Android/Kotlin role almost certainly pays more reliably than a new solo service with no references.
- **Change:** use an explicit floor of 10 applications a week, starting in week 1. If there are no paid leads by week 6, move 70% of time to plain Kotlin contracting.
- The new services are upside, not the rent.

**5. The DMA cold-email probe will go unanswered, and the criteria note lacks credibility on its own.**
- Proton, Mistral, Perplexity and Brave get many unsolicited "safety layer" pitches.
- A criteria note from a non-security person with no CVEs or talks behind it reads as an opinion.
- **Change:**
  - **Attach the note to job or contract applications** at those same firms, where it becomes a strong work sample instead of a pitch.
  - Back every criterion with a reproducible attack plus the block from the AgentGuard demo. Evidence beats credentials.
  - Filing to the Feb 2027 consultation still costs little. Keep it.

**6. "UNO certified as a small Qualified AI Assistant" in 2027 is fantasy for a solo founder.**
- Para 125(f), developer reputability, plus ongoing obligations make this a burden a solo founder can't carry:
  - security updates and incident handling;
  - independent-certifier audits, likely paid;
  - re-certification.
- UNO also has no EU user base to justify that cost.
- **Change:** delete it from the plan. The only DMA upside worth keeping is being hired by, or contracting for, an assistant that must certify.

**7. The 31 Dec test is too soft.**
- **Change:** pass means **≥€3k invoiced or a signed offer**, plus the published audit post.
- Add a week-4 gate: at least 3 real conversations (paid leads or interviews). Otherwise cut services and go all in on the floor.

## Sharpest modification: v8 in one line
**Stop selling the future Android surface. Audit the agent surfaces that ship today, publish the findings as the funnel, and let a job or contract pay the rent.**

**Split:** 50% floor (applications and contracting), 35% reviews and the audit post, 10% AgentGuard, 5% the DMA note and consultation. Drop the OEM emails entirely.

## First 4 weeks (29 Sep – 25 Oct 2026)
- **Week 1: floor and toolkit.**
  - Reposition CV, LinkedIn and GitHub as "Android + MCP agent-safety engineer".
  - Send 10 applications or contract bids (Kotlin remote roles, MCP-building startups, Proton, Mistral and Perplexity Android roles).
  - Set up Malt, Contra and Upwork profiles.
  - Extract the classifier and confirmation gate into a minimal Kotlin/JVM "AgentGuard" CLI that takes an MCP server's tool list and outputs a risk map.
- **Week 2: audit and disclose.**
  - Run the CLI on 5 popular open-source MCP servers.
  - Hand-test injection on the top 2.
  - Disclose privately to the maintainers.
  - Record the screen-injection before/after demo.
  - Send 10 more applications.
- **Week 3: publish and sell.**
  - Publish the audit post and demo (HN, r/androiddev, the MCP Discord, LinkedIn).
  - DM 20 companies that shipped a public MCP server or ChatGPT app in 2026, offering the €2–3.5k review, with the first 2 at half price.
  - Attach the DMA criteria draft to the Proton, Mistral and Perplexity applications.
- **Week 4: follow up and gate.**
  - Chase every thread.
  - Deliver any review within 5 days.
  - Take the gate: with ≥3 real conversations, continue v8. With 0, move 80% of time to plain Kotlin contracting and job search, and keep AgentGuard as a portfolio piece.

Sources: [AppFunctions overview](https://developer.android.com/ai/appfunctions), [9to5Google on AppFunctions/Gemini](https://9to5google.com/2026/02/25/android-appfunctions-gemini/), [AndroidX alpha10 notes](https://github.com/mahozad/androidx-release-notes/releases).
