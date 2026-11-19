# Red team, iteration 2 (attacking v1)

**Verdict:** v1 finds a real opening but sells to the wrong side of it. The certification belongs to 5–8 well-funded assistant vendors, who won't hand a regulatory gate to a solo founder's SDK. The side with thousands of buyers who need gating is the apps being *called* by those assistants.

## Findings, ranked

**1. The wrong entity gets certified, and the SDK drops out of the value chain.**
Certification attaches to the *assistant provider*. It is run by Google or its designated testers and applies to a specific app build. Nobody certifies an SDK, and passing depends on the whole app's behaviour, not on a library it links. At best the SDK is "helpful code", which is a weak thing to sell.
*Change:* drop "certified-ready SDK" as the product. Sell something tied to the *test* (see #3), or move to the app side (see #2).

**2. The buyer count is tiny and hostile to dependency.**
The likely buyers are OpenAI, Anthropic, Perplexity, Mistral, Samsung, Xiaomi, maybe Meta and Microsoft: about 8 firms. Each has security teams and outside counsel. None will put a regulatory gate on an unaudited solo dependency, and they'd rather hire the founder than buy from them. The flip side: under DMA every *app exposing AppFunctions* (banks, commerce, travel, messaging) will be called by several rival assistants it doesn't control. Those apps need tool-role classification, consent gating, spend caps and data minimisation *on their side*. That is exactly UNO's MCP pipeline, turned around.
*Change:* make the main target "provider-side agent gating for Android apps exposing AppFunctions/MCP". This merges H2 with the DMA timing and gives hundreds of buyers instead of 8. It also works globally, because AppFunctions exists outside the EU too.

**3. Open-source plus services is consulting, and it ends when the criteria are frozen.**
Readiness work peaks around Feb–Aug 2027 and then disappears once vendors pass. There's no recurring revenue.
*Change:* build an open **conformance and red-team harness**: adversarial prompt-injection and intent-hijack scenarios, data-leak probes, and a sensitive-action reconfirmation checker for Android agents. Offer it to the independent test labs and to CSA as a candidate methodology. Recurring revenue then comes from hosted regression runs on every assistant release, since certification is per build. A test suite also stays relevant however Google writes the terms, which an SDK does not.

**4. Google writes the terms, so it can make any third-party SDK irrelevant.**
Google could require Play Integrity or attestation, its own consent-prompt APIs, or system-rendered reconfirmation dialogs. Then client-side safety code becomes redundant by design. Timing and appeals add risk: Google may challenge the decision in the General Court, and Android 18 dates can slip.
*Change:* engage now in the Commission's and CSA's process and comment on the Feb 2027 draft terms publicly, with UNO as evidence. The aim is to become a named reference, not a hopeful vendor. Also track UK CMA (Google SMS designation) and Japan MSCA as second jurisdictions.

**5. It depends on one regulation, which is a hidden "miracle".**
v1's whole thesis rests on one decision, one gatekeeper and one calendar. That's the same "miracle" dependency the founder already has, just with a Brussels address.
*Change:* require that the product earns money *without* DMA. Provider-side gating (#2) and the test harness (#3) both do: non-EU apps exposing AppFunctions or MCP still need them. Treat DMA as an accelerant, not the foundation.

**6. Runway: no revenue until mid-2027.**
Draft terms arrive Feb 2027, final terms May 2027, and the Android 18 launch is Aug 2027. That's 10+ months with no buyer pull for the certification pitch.
*Change:* in the next 90 days, go after revenue that's available now: paid pilots with 2–3 apps that already expose MCP servers (Swiggy-style commerce, fintech), and design-partner fees. Set a hard kill date: no paying or LOI-signed design partner by 31 Jan 2027 means the DMA angle is dead.

**7. The 50k EU MAU bar kills the reference assistant as a product.**
A solo founder won't reach 50k monthly EU users averaged over a year before 2028. So the reference assistant can't *itself* be certified, and it proves nothing to the testers.
*Change:* demote UNO to an open-source demo and the testbed for the harness. Stop describing it as "an assistant that passes".

**8. The alternatives were dismissed on names, not buyer evidence.**
H1 was marked "crowded", yet v1 itself notes that nobody covers mobile or on-device. Those same funded gateways (Runlayer, AIR, Noma) are acquirers or partners for a mobile enforcement module, not only competitors. H3 was never tested at all.
*Change:* reframe H1 as a "mobile/on-device module for existing MCP gateways" (partnership or acquisition path), and put 3 of the 15 discovery calls on it.

## Sharpest modification
Aim v1 at **app providers, not assistant vendors**. The offer: *"Open-source gating for any Android app that agents can call (AppFunctions or MCP): tool-role classification, consent and spend rules, data minimisation. Plus a hosted conformance and red-team suite that is DMA-aligned but not DMA-dependent."*
Cheap test, 3 weeks:
- 10 calls with apps that expose MCP or AppFunctions (commerce, fintech, travel).
- 3 calls with test labs or CSA.
- 2 calls with MCP-gateway firms.
Pass condition: at least 2 paid pilots or LOIs.
