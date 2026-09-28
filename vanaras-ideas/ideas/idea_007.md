# Briefkeep — a scoped agent team for every lawyer in small and mid-size firms, with client data that never reaches the model
Lens: Legal firms
## Customer & pain
Managing partners of 5-100 lawyer firms (US/UK/EU/India/Gulf, not one country) pay. Lawyers are billable-hour workers who lose 30-40% of their day to unbilled admin: chasing clients, deadlines, time entries, filing, first-draft correspondence. Firms ban ChatGPT/Claude use on client matters because confidentiality and privilege are at stake, so associates use it anyway on personal phones (shadow AI), or not at all. Today's legal AI (Harvey, Legora, CoCounsel) targets large firms, is research/drafting-centric, and requires sending matter data to a vendor cloud.
## Product
Each lawyer gets a small team of vanaras, each locked to its own tools.
- Phone: Intake vanara answers client messages/calls out of hours, collects facts, books consults; Deadline vanara pushes court/filing reminders and calls the lawyer; Time vanara turns the day's calls and messages into draft time entries.
- Cloud: Matter vanara works 24/7 per matter: chases documents, assembles bundles, watches e-filing portals, drafts routine letters overnight.
- Desktop: Drafting vanara works inside Word, the DMS and the browser on the lawyer's machine, using the firm's templates.
- Shared memory is per matter, with ethical walls: a vanara on matter A cannot read matter B. Handover: phone intake passes facts to the cloud Matter vanara, which passes a draft to the desktop vanara, which asks the lawyer to approve. Approvals and spend/send rules are enforced on the device, so nothing goes to a client or court without sign-off. Client names, parties and IDs are reference tokens, so the model never sees them; the audit log is exportable for the bar or insurer.
## Wedge (first product, first 10 customers)
"After-hours intake + deadline guardian" for solo and 2-10 lawyer boutique firms (immigration, family, personal injury, where inbound volume is high): Android app plus a WhatsApp/SMS number, with token-masked intake summaries into Clio or email. Sell by direct outreach and bar-association newsletters. First 10 customers are boutique firms found via founder network and LinkedIn; pilot at $99/lawyer/month. Founder reuse means MVP in about 3 months.
## Enterprise path
Move up from boutique to mid-size firms: per-matter ethical walls, SSO, DMS integrations (iManage, NetDocuments), firm-wide policy engine, admin console, audit export, bring-your-own-model-key or private endpoint. Security questionnaires are answered by the architecture itself (no client data reaches the AI). Then in-house legal teams.
## Business model & pricing
Per-lawyer seat: $99 wedge, $250-400 for the full team; firm platform fee for policy/audit at 20+ seats; BYO key keeps model cost off our margin. Target 80% gross margin.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell horizontal assistants and won't take malpractice-adjacent liability or build per-matter ethical walls and bar-specific audit. Harvey and peers are cloud-first for large firms. A device-enforced, token-masked design across phone, cloud and desktop is a poor fit for their central-cloud architectures. Microsoft Copilot is the closest threat inside Word (guess: it stays generic).
## Biggest risk
Trust and liability: a missed deadline or a wrong client message is a malpractice event, and lawyers are slow, conservative buyers. Mitigate with approval-first defaults and reminders that assist rather than replace calendaring systems. Also: Clio and others adding agents.
## Uses founder's existing assets
Scoped vanaras with locked tools (ethical walls), handover between agents (intake to matter to drafting), scheduled background jobs (deadline watch), on-device approvals and spend rules (send/file sign-off), reference-token privacy (privileged data never reaches the model), MCP role-classified pipeline (Clio, e-filing, DMS connectors), voice (intake calls), BYO model key.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
