# Market research, iteration 4 (2026-09-28)
This iteration tests three things from v3: whether stage 1 (bounty money) is real, whether there is a product-builder angle, and the open questions left from market_3.

## 1. Bounties pay for credibility, not for a living
**Google AI VRP** (launched Oct 2025):
- Flagship products include "Gemini Apps (Web, **Android**, iOS)".
- "Rogue actions" pay up to $20k and "sensitive data exfiltration" up to $15k. Quality and novelty bonuses raise the cap to $30k.
- Indirect prompt injection that causes a rogue action or exfiltration is in scope. Direct prompt injection, jailbreaks and alignment issues are out of scope.
- Sources: [The Register](https://www.theregister.com/2025/10/07/google_ai_bug_bounty/), [Infosecurity](https://www.infosecurity-magazine.com/news/google-launches-ai-bug-bounty/).
- Before the dedicated programme existed, Google had paid about $350k through its AI VRP and about $890k for AI bugs in total ([TechRadar](https://www.techradar.com/pro/security/google-paid-over-usd17-million-to-bug-hunters-in-2025)).
- A Gemini-on-Android agent bug therefore fits the programme's flagship tier.

**What real payouts look like is much lower than the caps:**
- The "Comment and Control" prompt injection (Apr 2026) hit three coding agents. The payouts were:
  - Anthropic: $100.
  - GitHub: $500.
  - Google: $1,337 for Gemini CLI.
- None of the three assigned a CVE. Sources: [TNW](https://thenextweb.com/news/ai-agents-hijacked-prompt-injection-bug-bounties-no-cve), [Repello](https://repello.ai/blog/comment-and-control-claude-code-gemini-copilot-prompt-injection).
- Perplexity has a VDP plus a private bounty, with case-by-case rewards (one example: $6k) ([Perplexity VDP](https://www.perplexity.ai/hub/security-vdp)).
- Samsung's Mobile Rewards Program (run on Bugcrowd) covers devices. I found nothing on whether it covers Galaxy AI or Perplexity agent behaviour (**unverified**; [Samsung](https://security.samsungmobile.com/rewardsProgram.smsb)).

**Android VRP (May 2026):**
- Top rewards went up: $1.5M for a zero-click Titan M exploit, and $375k for secure-element data exfiltration.
- Chrome bonuses were cut because AI-generated reports flooded the programme.
- Google now wants "concrete proof" rather than long reports ([Security Affairs](https://securityaffairs.com/191600/security/google-revamps-bug-bounty-programs-android-rewards-rise-chrome-payouts-drop-in-the-age-of-ai.html)).
- These are kernel and hardware tiers, not agent-behaviour tiers.

**Other programmes and the market overall:**
- OpenAI Safety Bug Bounty (Mar 2026): $20k standard, up to $100k, from a $1M annual pool. Agentic and MCP risks are in scope.
- Anthropic pays up to $15k.
- Gray Swan Arena runs challenges with $40k–$300k prize pools, and the top 40 participants join a paid engagement network.
- Source for these three: [Wraith](https://wraith.sh/learn/ai-bug-bounty-programs) (secondary source).
- HackerOne 2025: 1,121 programmes had AI in scope (up 270%), valid prompt-injection reports rose 540%, and 560+ valid reports came from autonomous "hackbots" ([HackerOne](https://www.hackerone.com/press-release/hackerone-report-finds-210-spike-ai-vulnerability-reports-amid-rise-ai-autonomy)).
- I found no data on how many people earn a living from AI bounties (**unverified**). Given the $100–$1,337 payouts on real agent bugs and competition from hackbots, the answer is probably very few.
- **Implication:** v3's stage 1 is a credibility play. Budget at most about $0–10k of income from it by December.

## 2. Product-builder angle: many agent frameworks, no safety runtime
**Android agent frameworks and their traction:**

| Project | GitHub stars (checked today) | Funding and notes |
|---|---|---|
| zai-org Open-AutoGLM | 26.3k | Created Dec 2025 |
| droidrun/mobilerun | 9.5k | €2.1M pre-seed (Merantix), July 2025 ([Tech.eu](https://tech.eu/2025/07/23/droidrun-raises-eur21m-pre-seed-to-scale-mobile-native-ai-agent-infrastructure/)) |
| Operit | 8.2k | |
| callstack agent-device | 4.8k | |
| minitap mobile-use | 3.2k | $4.1M seed; now repositioned as "autonomous QA" ([Pulse2](https://pulse2.com/minitap-4-1-million-seed-funding/), [minitap](https://www.minitap.ai/)) |

- Frameworks are pivoting to QA and cloud-phone infrastructure.
- Mobilerun already sells a "Banking Agent" that "pauses for approval before the final confirmation" on rented real phones ([mobilerun](https://mobilerun.ai/apps/banking/)). Approval gates are therefore a built-in feature of the frameworks, not a separate product.
- "Not an A11y" attacked exactly these frameworks (MobileRun, Mobile-Use), so their maintainers are natural recipients for disclosures and design partners.

**AppFunctions:**
- An experimental API in Android 16+ that lets an app expose functions to agents, acting as an on-device MCP server. Gemini integration is in private preview.
- Uber, DoorDash and OpenTable are live. Google says it will reach 200M+ devices by the end of 2026. Sources: [Android Developers](https://developer.android.com/ai/appfunctions), [Android Dev Blog](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html).
- Each app that exposes AppFunctions is a new "app called by an agent" and needs to validate the calls it receives. This is a real but future audience.

**Embeddable permission, approval and data-minimisation runtime for on-device agents:**
- I found no Android/Kotlin product (**unverified**).
- The generic human-in-the-loop SDKs (OpenAI Agents SDK, Vercel AI SDK, Cloudflare) are JavaScript and server-side.
- Mobile in-app-protection vendors (Appdome, Zimperium, Guardsquare, Promon) market nothing agent-specific.
- Banks' platform vendor builds this itself: Backbase's "Sentinel" issues a decision token for every action by an agent or a human, with scoped, time-limited credentials ([Backbase](https://www.backbase.com/blog/agentic-ai-banking-security)).
- **Implication:** the gap exists, but likely buyers (banks, super-apps) get this from their platform vendor or build it in-house. Promon and Appdome, which already sit inside bank apps, are the natural channel or acquirer. A standalone SDK would need to be open-source first.

## 3. Open questions from market_3
**Google appeal:**
- No General Court filing had been reported as of today.
- The General Court's sequencing ruling of 8 Jul 2026 means Google must comply while it appeals. The deadline for Android interoperability is the next major release, and 1 Aug 2027 at the latest.
- Sources: [TechTimes](https://www.techtimes.com/articles/320011/20260709/eu-court-ruling-gives-google-18-days-open-android-ai-layer-blocks-last-legal-defense.htm), [DMA portal](https://digital-markets-act.ec.europa.eu/developer-portal/interoperability/alphabet-specification-proceedings-interoperability-ai-services_en). Check the Curia register after about 5 Oct.

**Lab hiring:**
- NowSecure is hiring a "Senior Agentic Security Automation Engineer" to build agentic testing workflows and evaluation systems ([Built In](https://builtin.com/company/nowsecure/jobs)). That is AI doing the testing, not testing of agents, but NowSecure is building the capability in-house.
- I found no matching job posts at Eydle, TrustCB or DEKRA (**unverified**). DEKRA does market generic AI testing and certification.

**OWASP MAS:**
- MASWE v1.0 (Aug 2026) has 78 weaknesses and no AI or agent category.
- I found no GitHub issues on AI in the masvs, maswe or mastg repos.
- **The MAS co-chair, Carlos Holguera, is a NowSecure distinguished research engineer**, and NowSecure has contributed 320+ PRs ([NowSecure](https://www.nowsecure.com/blog/2026/07/02/owasp-mascon-vienna-showed-the-future-of-mobile-application-security/), [MASWE v1.0](https://www.nowsecure.com/blog/2026/08/18/owasp-maswe-hits-v1-0-nowsecure-platform-already-maps-to-it/)).
- So the "standards slot" v3 wants runs through the main competitor's staff. Proposing an AGENT category would hand NowSecure a roadmap.

**Connector directories:**
- **Anthropic** requires a privacy policy, a test account, read-only/destructive tool annotations and seven policy acknowledgements, one of which covers prompt injection. Review is automated plus Anthropic's own; no third-party attestation is required ([Claude docs](https://claude.com/docs/connectors/building/submission), [policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy)).
- **OpenAI** requires a CSP, a privacy policy and data minimisation, again with no attestation ([OpenAI](https://developers.openai.com/apps-sdk/app-submission-guidelines)).
- This confirms market_3: providers have no reason to pay for third-party testing.

**Paper authors:**
- MobileWorldSafety: Sujin Chen, Lijun Li, Tianyi Du, Jing Shao. Jing Shao is likely at Shanghai AI Lab (**unverified**). The paper carries the arXiv non-exclusive licence, and I found no code licence ([arXiv](https://arxiv.org/abs/2608.17659)).
- "Not an A11y": Rahul Deivasigamani, Sayeda Faatin Alvi, Andrea Derqui, Kaushal Punjabi, Stjepan Picek. Picek is at Radboud University and TU Delft (**unverified**). The paper does not say whether the authors told the framework vendors ([arXiv](https://arxiv.org/abs/2608.08939)).
- The Picek group, being EU-based and security-focused, is the better collaborator.

## 3 recommendations
1. **Reframe stage 1 as "credibility, not income".**
   - Target the Gemini-on-Android rogue-action tier (up to $20k) and OpenAI's agentic scope.
   - Plan for the realistic outcome of $0–5k, so assessments or a day job must fund the founder until 2027.
   - Measure success by public write-ups and by the vendors' reactions to them.
2. **Add a free product wedge: an open-source Kotlin "agent guard" library.**
   - It would provide an approval gate, action allow-lists, redaction of screen and clipboard data before it reaches the LLM, and validation of AppFunctions calls.
   - Test it against the harness, and pitch it to the Mobilerun and Minitap maintainers first, since their frameworks were attacked in the "Not an A11y" paper.
   - Monetise it later through assessments, or through a Promon- or Appdome-style partner. Don't sell it directly to banks, which build this themselves (Backbase).
3. **Change the standards play.**
   - Approach Holguera/NowSecure openly as potential *partners* (contributing corpus to MASTG) rather than trying to out-flank them.
   - In parallel, co-author with the Picek group, which gives academic credibility independent of NowSecure.

## Open questions for iteration 5
- Has Google filed at the General Court (Curia register, after 5 Oct)?
- What do the Samsung Mobile Rewards and Perplexity private bounties cover for agent behaviour on Galaxy devices?
- Are Gemini-on-Android bounty write-ups public (bughunters.google.com Hall of Fame, AI VRP blog), and what were the actual amounts?
- Do Mobilerun or Minitap have a security or disclosure contact, and did they respond to "Not an A11y"? Would they adopt a guard library?
- Do Promon, Appdome or Zimperium have roadmaps for "agentic threats" or accessibility-driven agent abuse?
- Would NowSecure/Holguera welcome an external MASTG AI-agent contribution, or is one planned internally (MAScon talk recordings)?
- Is the Picek group releasing code, and under what licence? Is there a Shanghai AI Lab repo for MobileWorldSafety?
