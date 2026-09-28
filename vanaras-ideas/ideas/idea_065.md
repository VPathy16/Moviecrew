# Claimwise — a team of scoped AI agents for every insurance claims handler, with the claim file's memory kept on the handler's own machine
Lens: Insurance claims handlers
## Customer & pain
Payers: mid-size insurers, MGAs and third-party administrators (TPAs), plus independent loss adjusters and public adjusters. A handler carries 80-150 open files. The day is chasing claimants, repairers, medical providers and brokers by phone, email and WhatsApp; re-keying into a core claims system (Guidewire, Duck Creek, legacy); reserve reviews; diary follow-ups; and fraud and regulatory clocks (acknowledge in X days, decide in Y). Leakage, complaints and turnover come from missed follow-ups. Vendors that exist today (claims automation platforms) sell to the insurer's IT and replace workflow; handlers still live in email, phone and spreadsheets. Claim files are full of health and financial data, which makes cloud AI hard to approve.
## Product
Each handler gets a small team of vanaras.
- Phone: a Claimant-contact vanara (calls or messages claimants, reads back status, collects photos and documents, book repairer slots by voice) and a Diary vanara (reminders and regulatory clocks per file). Scoped tools only: it can message but cannot approve payment.
- Cloud: a Case-watch vanara runs 24/7 on the handler's open files. It chases missing documents, watches for repairer quotes, and drafts letters overnight.
- Desktop: a Systems vanara drives the core claims screens and the handler's email and files to key in notes and updates, and stops for approval before any reserve or payment change.
Shared memory holds a per-claim timeline (who said what, what is outstanding, promises made). Agent-to-agent handover: the phone vanara hears "the car is a write-off", hands to the desktop vanara to update the system, which hands to cloud to prepare the total-loss letter. Personal data stays as reference tokens: the model sees "Claimant-7 / Policy-12", real names and medical details are resolved on-device at send time. Approval and spend rules (authority limits by handler grade) are enforced locally.
## Wedge (first product, first 10 customers)
Sell to independent loss adjusters and small TPAs (5-50 handlers): "Diary and claimant chase" on the phone, for USD 60 per handler per month, BYO model key. No integration needed, since it works off email, calls and a shared inbox. First 10: adjusters found via LinkedIn and adjuster associations, plus one friendly TPA pilot for a case study.
## Enterprise path
Pilot with a mid-size insurer's single claims team; prove cycle-time and complaint reduction. Then the desktop vanara plus MCP connectors to the core system, SSO, audit logs, and authority-limit policy managed by the claims director. Privacy architecture (tokens, on-device) answers the insurer's data-protection review, the usual sales blocker.
## Business model & pricing
Per-seat subscription USD 60-120 per handler per month; enterprise USD 150-250 with audit and admin; optional per-claim pricing for TPAs. Model cost passes through via BYO key or metered.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Generic assistants do not ship per-claim memory, regulatory clock logic, authority-limit enforcement, or insurance-specific audit. Vertical distribution to claims managers is slow, unglamorous work. Frontier labs sell horizontal seats and would rather be the model under it (BYO key makes that a tailwind).
## Biggest risk
Insurer procurement and regulation cycles (12-18 months), and liability if an agent mishandles a claim communication; also incumbent claims platforms adding their own agents (guess).
## Uses founder's existing assets
Scoped vanaras with locked tools (contact vs approve), handover between agents, scheduled background jobs (diary, clocks), on-device approvals and spend rules (authority limits), reference-token privacy for claimant data, MCP pipeline for connecting mail, calendar and claims systems by tool role, voice for claimant calls, BYO key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
