# Retainer — a Vanaras team that runs a solo practice's client work, with a privilege wall built in
Lens: Solo professionals (consultants, lawyers, accountants) as first customers
## Customer & pain
Solo and micro-practice professionals (independent consultants, solo lawyers, small bookkeeping/tax practices) pay. They are the whole firm: billing, chasing documents, client messages, deadlines, and the actual work. Client confidentiality blocks them from pasting client data into generic AI tools, so admin eats roughly 30-40% of their week (guess). Their ethics rules (bar, CPA, NDAs) make "just use ChatGPT" risky.
## Product
Each client matter is a "case" with its own scoped vanaras and its own memory partition, so client A's facts can never reach client B.
- Phone: an intake/comms vanara handles client calls and messages by voice, sets reminders, and drafts replies. Deadlines and hearings are tracked. Approvals are one tap.
- Cloud: a matter vanara runs 24/7 on a client folder (chasing missing documents, drafting engagement letters, preparing recurring filings, monitoring inbound email) and queues finished work for approval.
- Desktop: a work vanara operates the practice's local tools (Word, Excel, tax/accounting software, a browser) in a locked-down scope per matter.
Shared memory plus agent-to-agent handover: a client's call on the phone becomes a task in the cloud, then a draft on the desktop, then an approval back on the phone. A per-matter audit log records who or what touched what, which is exportable as a professional-conduct record. Reference tokens keep client PII off the model.
## Wedge (first product, first 10 customers)
"Matter-scoped Retainer for Android + web": intake calls, deadline reminders, and document-chase for solo immigration/family lawyers and solo bookkeepers. Get the first 10 through direct outreach, bar-association and CPA-chapter communities, and one co-founder-style design partner per profession. Charge from day one. Keep it in one jurisdiction-neutral workflow first (document chase and comms), not legal drafting.
## Enterprise path
Solo practices become small firms (2-20 seats), and each partner and staff member gets a team under firm-wide rules: conflict walls between matters, retention policy, and admin-set spend and approval limits. This leads to in-house legal and finance teams, and to any regulated department needing "ethical wall" agents. The audit log and BYO model key (or the firm's own tenant) support procurement.
## Business model & pricing
$79/month per professional (Solo), $149/month with desktop agent and cloud matters (Pro), $99 per seat per month for firms with the admin console. Usage is on the customer's own model key, so gross margin stays high. Guess: 300 Pro customers reach roughly $540K ARR.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal assistants with one shared memory, which is the opposite of what a lawyer needs: hard partitions per client. Vertical compliance, per-profession workflows, and liability for confidentiality are unattractive, low-ACV work for them. They also will not run on a phone with reference-token isolation across vendors.
## Biggest risk
Trust and liability: one leak or one wrong deadline ends a practice. Professions are conservative, and bar or CPA rules on AI use vary and may change. Mitigations are human approval on every outbound item and a narrow first workflow.
## Uses founder's existing assets
Scoped vanaras with locked tool sets (matter partitions), handover between agents, scheduled background jobs (deadline and document-chase loops), on-device approvals and spend rules (send-approval gate), reference tokens (client PII never reaches the AI), the MCP tool-role pipeline (connect practice-management, email and calendar tools), voice (intake calls), BYO model key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
