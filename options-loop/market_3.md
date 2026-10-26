# Market research, iteration 3 (2026-09-28)
This iteration tests v2's product idea: a conformance suite for how AI agents behave on Android, and for the apps that agents call.

## 1. The AI red-team, eval and guardrail market is crowded and consolidating, but no one covers mobile
**Recent acquisitions:**
- OpenAI acquired Promptfoo on 9 Mar 2026 and is folding it into its Frontier agent platform. The tools stay open source (MIT licence). ([TechCrunch](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/))
- Check Point acquired Lakera in Sept 2025 for about $300M. ([Ctech](https://www.calcalistech.com/ctechnews/article/rj5bc1vige))
- Snyk acquired Invariant Labs in June 2025. mcp-scan is now called "agent-scan"; the CLI is free and the paid version runs through Snyk Evo. ([Snyk](https://snyk.io/news/snyk-acquires-invariant-labs-to-accelerate-agentic-ai-security-innovation/), [GitHub](https://github.com/snyk/agent-scan))
- Cisco acquired Robust Intelligence in 2024; it is now Cisco AI Defense. Enterprise pricing is quote-only. The "Explorer Edition" of its agent red-teaming is free. ([Cisco](https://blogs.cisco.com/ai/introducing-cisco-ai-defense-explorer))
- Beacon Software acquired Haize Labs on 17 Sep 2026 (Haize was valued at $100M in 2024). Harvey acquired Guardrails AI on 9 Sep 2026. ([BERI](https://www.beri.net/article/beacon-haize-labs-acquisition-ai-red-teaming-vendor-continuity-export))

**Recent funding:**
- Gray Swan raised a $40M Series A in June 2026. Samsung Next participated, and UK and US AISI judges sit on its agent-red-teaming arena. ([FinTech Global](https://fintech.global/2026/06/01/gray-swan-raises-40m-to-secure-ai-at-the-frontier/))
- Patronus raised a $50M Series B ($70M total) in June 2026 for simulated "digital worlds" for testing agents. Samsung and Datadog invested. ([TechCrunch](https://techcrunch.com/2026/06/25/patronus-ai-lands-50m-to-build-digital-worlds-that-stress-test-ai-agents/))
- HiddenLayer raised a $100M Series B in Sept 2026 (about $156M total) for agent runtime security. ([RuntimeWire](https://runtimewire.com/article/hiddenlayer-raises-100m-series-b-ai-agent-security))
- Giskard has raised about $20M, with no 2026 round found.

**Implications:**
- Generic agent red-teaming is being commoditised: free open-source tools are backed by platform giants. A solo founder cannot compete on generic prompt-injection or jailbreak testing.
- **Mobile is a gap.** None of these vendors advertises testing agents that run on Android devices (operating the UI through the accessibility service, calling AppFunctions, using system integrations).
- Mobile agent safety exists only in academic benchmarks:
  - MobileSafetyBench.
  - MobileWorldSafety (Aug 2026): 142 risk tasks on real Android apps. Every agent tested was vulnerable, with attack success rates of 40–67%. ([arXiv 2608.17659](https://arxiv.org/abs/2608.17659))
  - "Not an A11y" (Aug 2026): nine accessibility-based injection vectors, with success rates up to 82% against the MobileRun and Mobile-Use agent frameworks. ([arXiv 2608.08939](https://arxiv.org/html/2608.08939v1))
- These papers give ready-made test corpora and evidence that the problem is real, but nobody has turned them into a product.
- Device farms (BrowserStack, AWS Device Farm, Sauce Labs, Kobiton) use AI to test apps. They do not test agents. ([TestGrid](https://testgrid.io/blog/best-device-farms/))
- Watch Gray Swan and Patronus: both have Samsung money and could add a mobile product (my inference).

## 2. What the mobile security labs are doing
- **NowSecure** (23 Jul 2026) launched "AI-native testing": an MCP server, AI chat, exploit-chaining agents that run on real devices, and detection of AI-specific vulnerabilities *inside apps*. It does not test the behaviour of third-party agents. ([GlobeNewswire](https://www.globenewswire.com/news-release/2026/07/23/3332206/0/en/NowSecure-Introduces-AI-Native-Testing-to-Match-the-Speed-of-AI-Driven-App-Development.html))
  - However, NowSecure has a real-device fleet and agent tooling, so it is the lab best placed to build an agent-behaviour suite in-house. **This is the main risk to v2.**
- **DEKRA** builds in-house and partners for tooling:
  - It opened the Malaga lab in 2025, which covers "AI solutions" and uses eShard's esDynamic platform, i.e. it licenses tooling. ([eShard](https://www.eshard.com/blog/dekra-hardware-security-lab-eshard))
  - Its only recent cyber acquisition is Onward Security (Taiwan, IoT, 2023). ([RCR](https://www.rcrwireless.com/20230331/featured/test-and-measurement-dekra-buys-iot-cybersecurity-firm))
  - So the realistic model is "the lab licenses a vendor's platform", not "the lab acquires a small vendor".
- **Eydle** (a co-signer of Google's DMA post) is ISO/IEC 17025-accredited and sells "software-mediated verification" for ADA/MASA and the Cyber Resilience Act. It is the most direct competitor: an automated verification vendor already inside the ADA ecosystem. I found no agent-behaviour product from Eydle (**unverified**). ([Eydle](https://www.eydle.com/))
- **NCC Group:** I found no public mobile-agent testing offering.

## 3. Standards: no one is drafting an "agent on mobile" conformance standard
- **ETSI EN 304 223 v2.1.1** (Dec 2025) is a baseline for AI security with 13 principles. It has thin coverage of tool-use and agent risks. ([ETSI](https://www.etsi.org/deliver/etsi_en/304200_304299/304223/02.01.01_60/en_304223v020101p.pdf))
- **prEN 18282**, the CEN-CENELEC JTC21 cybersecurity standard for the AI Act, reached enquiry stage with a vote closing 30 Jul 2026. It is not cited in the Official Journal yet. ([iTeh](https://standards.iteh.ai/catalog/standards/cen/8cdcbbe8-5409-4a98-af3e-d70b39e9d7d1/pren-18282))
- **OWASP** has published:
  - the Agentic Top 10 (Dec 2025);
  - the LLM Top 10 2026 (Aug 2026);
  - the donated **Agent Control Standard** (Sep 2026), which covers runtime enforcement. ([PRN](https://www.prnewswire.com/news-releases/owasp-genai-security-project-releases-2026-top-10-for-llm-applications-debuts-agent-control-standard-and-new-resources-for-securing-generative-and-agentic-ai-302867085.html))
- **OWASP MASVS/MASWE** has no AI or agent category that I could find (**unverified**).
- **Google** (May 2026) describes its own Gemini agent safeguards: per-app scoping, purchase confirmation and prompt-injection defences. It gives no third-party test spec. ([Google](https://blog.google/security/android-gemini-intelligence-security-privacy/))
- **How an individual can contribute:**
  - OWASP projects are open GitHub projects plus Slack. An individual can propose a MASWE/MASTG "AI agent" category, or a mobile profile of the Agent Control Standard.
  - ETSI and CEN require membership, either direct or through a national mirror committee (e.g. BSI, DIN); that is slower.
  - The **cheapest standard-setting lever is OWASP MAS**, because MASA already references MASVS and MASA is what criterion (e) points to.

## 4. Buyers outside the DMA: companies exposing public MCP servers
- **Scale:** directories list 13.5k–93k MCP servers (Glama lists about 93k open-source servers; PulseMCP about 21.8k). Remote, vendor-run servers are a much smaller subset. ([PulseMCP](https://www.pulsemcp.com/servers), [mcpservers.org](https://mcpservers.org/remote-mcp-servers))
- **Who buys scanning today is mostly the *consumer* side:** enterprises vetting the servers their staff install.
  - Free scanners: Cisco mcp-scanner, Snyk agent-scan.
  - Paid: Akto (Professional plan about $1,890/month; MCP module paid), gateways such as MintMCP (sold on SOC 2). ([DecryptionDigest](https://www.decryptiondigest.com/blog/mcp-server-security-scanners-cisco-invariant-akto), [Akto](https://www.akto.io/pricing))
- I found **no evidence of MCP server *providers* paying for third-party conformance testing.** There is no directory-listing requirement that forces them to (**unverified**; Anthropic and OpenAI connector-directory review criteria still need checking).
- A CSA initiative (mcpserver-audit) is building an open audit database, which is free competition. ([GitHub](https://github.com/ModelContextProtocol-Security/mcpserver-audit))
- **Conclusion:** the "apps called by agents" leg has weak willingness to pay unless a marketplace or regulator requires attestation.

## 5. Google appeal and geofencing
- **Appeal:** no General Court filing reported as of today. Google disagrees publicly only through its blog. Under the DMA an appeal does not suspend compliance. ([CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-dma-ai-assistant-interoperability-20260/))
  - The deadline is 2 months plus 10 days from notification, i.e. roughly late September to early October 2026 (my estimate), so check again next week.
- **Geofencing:** commentators expect EEA-first rollout ([CSA](https://labs.cloudsecurityalliance.org/research/csa-research-note-eu-dma-android-ai-interoperability-2026071/)). There is no Google statement either way (**unverified**). The DMA pattern with Apple has been EU-only.

## 3 recommendations
1. **Narrow v2 to "Android agent-behaviour test corpus + harness".**
   - Build it on the MobileWorldSafety and "Not an A11y" vectors, mapped to para 125 criteria (b), (c) and (d) and to the OWASP Agentic Top 10.
   - Drop generic LLM red-teaming (commoditised) and treat MCP-provider testing as a free add-on, not a revenue leg.
2. **Sell it as a licensable platform to labs, as eShard does for DEKRA; do not hope for an acquisition.**
   - Pitch in this order: Eydle and TrustCB first (automation-minded, smaller), then DEKRA, then NowSecure (who may build their own).
   - Offer a MASA-style "agent profile" before TCA applications open on 1 Feb 2027.
3. **Claim the standard slot through OWASP.**
   - Propose a MASVS/MASWE "AGENT" category or a mobile profile of the Agent Control Standard, and co-author with the academic benchmark teams.
   - This is free, credible, and becomes what labs cite.

## Open questions for iteration 4
- Has Google filed at the General Court by about 5 Oct 2026? Is there any Google statement on EEA-only rollout?
- Is Eydle, NowSecure or TrustCB already building agent-behaviour tests? Their conference talks and job posts (e.g. "AI agent test engineer") would show it.
- Do the OWASP MAS maintainers welcome an AI/agent category? Check GitHub issues and discussions.
- Do Anthropic, OpenAI or Google connector and app directories require security attestations from MCP providers? That would create provider-side willingness to pay.
- Would Gray Swan or Patronus (both Samsung-backed) partner or compete on mobile? Does Samsung vet Perplexity-style agents with an outside vendor?
- Who wrote the MobileWorldSafety and "Not an A11y" papers? Are they potential co-founders or collaborators, and what licence covers their benchmark code?
