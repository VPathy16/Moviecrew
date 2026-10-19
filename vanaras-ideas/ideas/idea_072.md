# Nemawashi — every employee's agent team pre-wires consensus and paperwork through LINE WORKS / KakaoTalk approval culture
Lens: Japan / Korea (high agent adoption, different platforms)
## Customer & pain
Who pays: 50-1,000 person Japanese and Korean firms, plus foreign subsidiaries there (the buyer is the COO or the DX/general affairs head). Decisions run on ringi (Japan) and gyeoljae (Korea): a proposal is quietly pre-socialised with each stakeholder (nemawashi), then routed through stamp-based approval chains. It burns weeks. Middle managers spend their days chasing people and reformatting documents. Staff already live in LINE / LINE WORKS / KakaoTalk / Kakao Work, not Slack or Teams. Generic Western agents ignore this social protocol and sit outside these chat platforms. (Market details are my guesses.)
## Product
Each employee gets a small team of vanaras:
- Phone: the "Pre-wire" vanara messages colleagues in LINE/Kakao, in the right register (keigo / jondaetmal), asks for informal consent, and keeps reminders and follow-ups going. It never sends anything without the owner's on-device approval.
- Cloud: the "Ringi" vanara drafts the ringi-sho / approval document from the project folder, tracks which stakeholders have softly agreed or objected, and keeps chasing 24/7.
- Desktop: the "Filing" vanara fills the company's legacy approval and expense systems, Excel templates and PDF forms with the browser and files.
- Shared memory and agent-to-agent sync: my Pre-wire agent talks to a colleague's agent ("Tanaka-san's team says yes if budget is under 2M yen"). Objections come back as structured signals, not gossip. The owner sees a consensus map before formally submitting.
## Wedge (first product, first 10 customers)
Start with one narrow job: cross-border approvals between Japanese/Korean HQs and foreign subsidiaries. Product: an Android/LINE-based "pre-wire and track" assistant for one manager, no IT integration. Get 10 customers by cold outreach to foreign-owned subsidiaries and trading firms (bilingual managers who feel the pain most), via expat communities and a Tokyo/Seoul design partner network. Use remote sales, with a part-time Japanese-speaking advisor.
## Enterprise path
Seat-based rollout per department. Then integrate with LINE WORKS / Kakao Work admin APIs, SSO, and the company's approval rules encoded as on-device policy (who may approve what, spend limits). Auditable logs satisfy compliance. Security-conscious buyers like that personal data stays out of the model (reference tokens) and that they can bring their own model key, including domestic models (e.g. Japanese or Korean LLMs).
## Business model & pricing
Per-seat SaaS, about $15-25/user/month personal tier, $40+/seat enterprise with audit and policy. Paid pilots of a few thousand dollars for a 20-seat department. BYO key keeps inference costs off my books.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Consent-building across people is a locale-specific, low-margin, culture-heavy workflow. It sits inside LINE/Kakao, which the US firms do not control. Microsoft and Google optimise for their own suites and generic assistants. LINE Yahoo and Kakao could build it, but they are platform owners and slow. The moat is local protocol knowledge plus the multi-agent negotiation graph.
## Biggest risk
Platform terms: LINE/Kakao may restrict automated messaging or unofficial integrations, and Android automation may be seen as fragile. Also sales into conservative enterprises is slow for a solo, part-time, non-native founder.
## Uses founder's existing assets
Scoped vanaras with locked tools; handover between agents; on-device approvals and spend rules (the ringi core); scheduled background jobs (chasing); reference-token privacy; the MCP pipeline for connecting local approval and expense tools; voice (calls to stakeholders); BYO model key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 5
asset_fit: 8
excitement: 7
