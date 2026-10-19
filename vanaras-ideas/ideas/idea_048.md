# Redline Crew — a team of agents that keeps a small firm's contracts, quotes and client documents current, consistent and compliant, even while laptops are closed
Lens: Documents and knowledge work as the core
## Customer & pain
Owner-run professional-services firms of 5-50 people (boutique law, accounting, architecture, consulting, insurance brokers) and the ops lead who pays. Their product is documents: engagement letters, proposals, SOWs, statements, filings. The same facts (rates, party names, dates, clauses) live in dozens of files, emailed versions and heads. Versions drift, a stale rate goes into a proposal, a renewal clause is missed, and senior people spend evenings on formatting and cross-checking. Existing tools are either generic chat over files or heavy DMS/CLM suites built for big firms.
## Product
Three vanaras share one document memory (facts, clauses, versions, who-approved-what).
- Desktop: "Drafter" works in Word/PDF/Drive/email with computer use, assembles documents from the firm's own precedents, and redlines against the memory.
- Cloud: "Watcher" runs 24/7 on the shared folders and mailbox: flags a changed rate across open drafts, upcoming renewals and deadlines, and inconsistencies between client documents.
- Phone: "Signer" delivers a short brief to the partner (voice or text): what needs approval, what changed, and approve or reject with one tap or a spoken reply. Approval and spend rules run on-device.
Agent-to-agent sync: when the partner approves a new rate on the phone, Watcher finds all affected drafts and Drafter prepares the redlines for review. Client personal data is held as reference tokens, so the model sees the clause but not the identity.
## Wedge (first product, first 10 customers)
"Renewal and drift watch": connect a shared drive and mailbox, and get a weekly phone brief listing expiring contracts, rate mismatches and missing signatures. Start with 10 boutique firms reached through founder-network and bar/CPA/architects association groups, offered as a paid 60-day pilot. Start with one vertical (small accounting or boutique law) to build the precedent library.
## Enterprise path
Firms grow into departments: legal ops, procurement, finance inside mid-size companies. Add SSO, per-employee teams, policy packs (who may approve what, redaction rules), audit log export, and the company's own model key or private endpoint. Sell top-down to legal or finance ops, then to every employee's team.
## Business model & pricing
Per-seat SaaS: about $60 per professional per month, plus a firm-level plan (about $300/month) for the cloud watcher and audit log. BYO model key lowers cost of goods. Later add compliance packs as annual add-ons.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal assistants tied to their own suites; a vertical firm's precedents, approval rules and clause-level audit trail are unglamorous, per-industry work. Cross-suite neutrality (Word plus Drive plus email plus phone) and on-device approval with tokenised client data are things a single-vendor assistant has weak incentives to provide. Legal-tech incumbents (Harvey, Ironclad) target large firms.
## Biggest risk
Trust and liability: one wrong redline or missed deadline harms a client. Also Microsoft Copilot bundling might be judged "good enough". Mitigation is human-approval on every outbound change and narrow scope. (Guess: firm willingness to pay $60/seat is unvalidated.)
## Uses founder's existing assets
Scoped agents with locked tools (Drafter, Watcher, Signer), handover between agents, scheduled background jobs (Watcher), on-device approvals and spend rules, reference-token privacy, the MCP pipeline (Drive, mail, DMS connectors classified by role), voice for the partner brief, BYO model key. New build: desktop agent, cloud runner, shared document memory.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
