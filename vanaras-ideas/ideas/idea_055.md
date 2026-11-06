# Ledgerkin — a personal team of finance agents for every AP/AR clerk, controller and founder-CFO, with spend rules enforced on the device
Lens: Finance operations (AP/AR, expenses)
## Customer & pain
Payer: controllers and finance leads at 20-300 person companies (agencies, clinics, logistics, SaaS resellers) with 1-6 finance staff and no ERP-grade automation. Pain: invoices arrive by email/WhatsApp/portals, get keyed into QuickBooks/Xero/Tally by hand; receipts chased from employees; AR reminders are awkward and inconsistent; month-end is a scramble. Existing AP-automation tools (Bill.com, Ramp, Tipalti) want a system-of-record swap and cloud access to bank and ledger credentials, which cautious owners resist.
## Product
Four scoped vanaras, each locked to its own tools. Phone: Receipt Chaser (nudges employees by message/voice, snaps receipts, matches to card lines) and Approver (owner approves bills by tap; spend rules enforced on device). Cloud: Collector (24/7 watches shared inbox, portals, ledger via MCP, drafts bills, runs AR dunning cadences, schedules payment runs). Desktop: Reconciler (drives banks and legacy portals that lack APIs, uploads statements, closes month-end checklist). Shared memory holds vendor quirks, coding rules and "how Priya likes it"; agent-to-agent handover moves an invoice from Collector to Approver to Payer with a full audit trail. Reference tokens mean bank numbers, vendor IDs and amounts of personal data never reach the model; BYO model key keeps costs and privacy under the customer's control.
## Wedge (first product, first 10 customers)
Receipt Chaser + expense reconciliation for small agencies and clinics: employees message receipts, the vanara codes them and hands a clean batch to the bookkeeper's ledger. Sell to 10 bookkeeping firms/fractional CFOs (each brings 5-20 clients), found via founder network and accountant communities. $49/client/month. Android-first, then cloud Collector.
## Enterprise path
Each finance employee already gets a team; then company-wide policy: central spend rules, approval matrices, segregation-of-duties enforced on device, SOC2 audit export, SSO. Expand from bookkeeping firms to mid-market finance teams, then every employee's expense vanara under corporate rules (T&E), the natural bridge to the full Vanaras vision.
## Business model & pricing
Per-seat $30-60/month for finance staff, $8/employee/month for expense vanara, plus per-client for bookkeeping firms. BYO key optional discount; managed model at cost plus margin. Target $3-5K ARR per small-company customer.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal agents; finance needs per-role tool lockdown, on-device spend enforcement, and integrations into long-tail ledgers and regional banks and portals. Liability for moving money is something platform vendors avoid. Microsoft may ship Copilot for Finance but tied to Dynamics/365; multi-ledger neutrality is our niche.
## Biggest risk
Trust and liability: a wrong payment or misposted entry. Also bank access without APIs (desktop portal driving is brittle), and incumbents (Ramp, Brex, Xero AI) bundling agents. Mitigation: approvals mandatory for any money movement initially; read-only plus draft first.
## Uses founder's existing assets
Scoped agents with locked tools (Reconciler cannot pay), handover between agents, scheduled background jobs (dunning, payment runs), on-device approvals and spend rules, reference-token privacy for bank/vendor data, MCP pipeline classifying tools by role (read vs write vs pay), voice for chasing receipts, BYO model key. New: cloud runner and desktop agent.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
