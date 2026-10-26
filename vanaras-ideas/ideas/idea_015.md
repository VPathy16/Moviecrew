# Handlr — a private agent team that runs a solo creator's business while they film
Lens: Creators and influencers
## Customer & pain
Mid-tier creators (20K-500K followers, YouTube/Instagram/TikTok/newsletter) who earn from brand deals, and their 1-3 person managers. Pain: 40% of the week is business admin: brand inboxes, rate negotiation, contract chasing, invoice follow-up (net-60 payments), deliverable deadlines, FTC/ASA disclosure checks, repurposing clips, and answering DMs. Existing tools (Stan, Beacons, Passionfroot, spreadsheets) are dashboards; the creator still does the work. Creators also will not hand DMs, bank data and brand contracts to a cloud AI.
## Product
Three vanaras with scoped tools:
- Phone (Deals vanara): triages brand emails and DMs, drafts replies in the creator's voice, asks approval by tap or voice note ("accept at 1.4x rate, no exclusivity"), and calls or texts about invoices. Spend and commitment rules (never accept exclusivity, never quote under a floor) are enforced on-device.
- Cloud (Pipeline vanara): 24/7 tracks each deal as a project: deliverable dates, usage-rights expiry, invoice status, reminders, chasing late payers, weekly earnings digest, media-kit refresh from live analytics.
- Desktop (Post vanara): from raw footage on the laptop, cuts shorts, writes captions, checks disclosure and brand-safety terms from the contract, uploads drafts.
Shared memory holds the creator's rates, tone, brand history and contract clauses; handoffs: a deal accepted on the phone spawns a cloud project and a desktop task ("brand X wants 3 reels by Friday"). Reference tokens mean DMs, bank details and follower PII never reach the model.
## Wedge (first product, first 10 customers)
Android app: "Deals inbox" only. Connect Gmail, get brand emails classified, auto-draft replies, invoice-chaser with approvals. Sell $29/mo. First 10: recruit from creator Discords, r/NewTubers and micro-influencer managers via cold DMs offering free setup; target creators with 3+ deals/month.
## Enterprise path
Talent agencies and MCNs (10-200 creators): one console for rules (rate floors, category conflicts), audit logs, per-creator teams under agency policy. Then brand marketing teams' influencer ops (each employee gets a team; the brand side negotiates against creator agents with agent-to-agent protocols).
## Business model & pricing
Creator $29-79/mo by deal volume; manager/agency seat $99/mo plus $15 per managed creator; optional 1% success fee on recovered late invoices. BYO model key lowers COGS. (Guess: 5K creators at $40 = $2.4M ARR.)
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Creator business ops is a niche vertical with messy long-tail workflows and platform-specific etiquette; general assistants stay horizontal. Platforms (YouTube, Meta) are conflicted and will not read DMs across competitors. The on-device privacy and approval rules are a trust story that cloud-first vendors struggle to match.
## Biggest risk
Access: Instagram/TikTok DM APIs are restricted, so the wedge relies on email and manual share-sheet, which may limit the magic; also creators churn and have low willingness to pay.
## Uses founder's existing assets
Scoped vanaras and handover (Deals/Pipeline/Post), scheduled background jobs (invoice chasing), on-device approvals and spend rules (rate floors), reference-token privacy, MCP pipeline classifying Gmail/calendar/invoicing tools by role, voice approvals, BYO key, Android app as the phone surface.
## Scores
market_size: 6
defensibility: 5
feasibility_solo_30k: 8
asset_fit: 8
excitement: 7
