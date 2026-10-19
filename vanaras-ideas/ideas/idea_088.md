# Hando — a departing or vacationing employee's agent team stays behind as a living, queryable handover
Lens: Wedge: digital twin of an employee for handover when they leave/vacation
## Customer & pain
Buyer: heads of ops/eng/sales at 50-500 person companies, plus HR/people-ops. Every resignation, parental leave or two-week vacation loses tribal knowledge: half-finished threads, "who do I ask about X", promises made to clients. Today it is a rushed doc nobody reads; replacing a mid-level employee costs roughly 0.5-2x salary (guess, commonly cited), much of it lost context.
## Product
Hando is the wedge of Vanaras. During a 2-4 week "handover window" the employee's team of vanaras observes their work with consent:
- Desktop vanara: notes files, tools, recurring tasks, browser workflows the employee actually uses.
- Phone vanara: captures calls/messages/commitments (on-device, tokenised so personal data never reaches the model).
- Cloud vanara: keeps running scheduled jobs (weekly report, renewals chase) while the person is away.
Shared memory becomes a "twin": a scoped, permissioned knowledge base of open loops, contacts, how-tos and pending promises. Successor or covering colleague asks it questions ("what did Priya promise Acme?"), or the twin hands tasks to the successor's own agents via agent-to-agent handover. Personal/private items are filtered by the employee before release; approvals and spend rules stay enforced.
## Wedge (first product, first 10 customers)
Vacation-cover first (low emotional stakes, recurring): a 5-day Chrome/desktop + Slack/email connector via MCP that produces a "while I was away" brief and answers questions for the cover person. Then departures. First 10: agencies, small SaaS ops teams, recruiters, accounting firms reached through the founder's network and LinkedIn; per-handover pricing lets a team try it once.
## Enterprise path
Sell to people-ops for offboarding, then extend: every employee gets a standing team (Vanaras proper) with the twin as always-on continuity. Needs SSO/SCIM, audit logs, data retention, works-council-friendly consent controls, on-prem/BYO-key deployments for regulated firms.
## Business model & pricing
Per-handover: $99-299 (vacation) to $499-1,500 (departure/role transition). Then $15-30/employee/month for standing continuity. Anchored against a single lost deal or a week of a recruiter fee.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal copilots per app and per user; an employee-exit product cuts across suites, involves labor-law and consent politics, and is a small SKU for them. Cross-surface on-device capture with privacy tokenisation and BYO model key is awkward for cloud-only vendors. Weaker claim: Microsoft could bolt on Copilot memory transfer (guess).
## Biggest risk
Trust and legal: employees resent being recorded, jurisdictions (GDPR, works councils) restrict monitoring, and departing staff have little incentive to help. Mitigation is employee-owned, opt-in, review-before-release capture.
## Uses founder's existing assets
UNO's scoped vanaras with locked tools, agent handover mechanism, scheduled background jobs (the vacation-cover loop), on-device approvals/spend rules, reference-token privacy layer (employee-controlled redaction), MCP role-classification pipeline (connect Slack/CRM/email quickly), BYO key, voice (spoken handover interview).
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
