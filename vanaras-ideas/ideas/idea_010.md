# Tether — a personal agent team for each support rep that drafts, remembers, and never lets customer PII touch the model
Lens: Customer support teams
## Customer & pain
Head of Support / CX Ops at 20-500 seat B2B SaaS, fintech and health-adjacent companies. Reps juggle 6-10 tools (helpdesk, CRM, billing, admin console, Slack, docs). Helpdesk-native AI (Zendesk, Intercom Fin) answers tickets but lives inside one tool; PII and compliance teams block pasting customer data into general LLMs; reps re-explain context across every case and every shift handover. Follow-ups slip, refund approvals stall, and QA is manual.
## Product
Each rep gets a small team of scoped vanaras.
- Desktop: a "case agent" reads the ticket, opens billing and admin console in the browser, and pre-assembles the answer with reference tokens, so raw customer data is detokenised only on the rep's machine at send time.
- Cloud: a "follow-up agent" works 24/7, chasing pending customers, watching for engineering fixes to ship, and reopening or updating cases overnight.
- Phone: a "shift agent" handles on-call escalations by voice or notification, and lets a manager approve a refund from their phone.
- Shared memory holds per-customer history, the rep's tone and macros, and promises made. Agent-to-agent handover means the overnight follow-up agent passes context to the morning case agent, and to the next rep on a shift change, with an approvals trail.
## Wedge (first product, first 10 customers)
A Chrome/desktop "Refund and escalation copilot" for one workflow: refunds, credits and account changes, which are multi-tool, approval-bound and PII-heavy. Enforced spend and approval rules (e.g. refunds over $50 need a manager tap) are the hook. Sell to 10 support leads via founder-network outreach and LinkedIn. Pilot with 3-5 reps each, priced per seat.
## Enterprise path
Per-employee teams under company policy: SSO, policy packs (refund limits, allowed tools, data classes), audit export, on-prem or customer-hosted tokenisation vault, BYO model key or private endpoint. Expand from refunds to all tier-1/2 workflows, then to sales ops and finance ops using the same pattern.
## Business model & pricing
Per-rep seat, $40-60/month for the team; enterprise tier $90+/seat with audit, SSO and policy packs. Pilot-to-annual conversion. Assumption (guess): 50-seat customers give ~$30K ACV.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Helpdesk vendors optimise for ticket deflection inside their own product. Big tech builds horizontal assistants and will not ship per-vertical approval and tokenisation policy tied to a support rep's cross-tool workflow. Cross-vendor neutrality (works across Zendesk, Intercom, Salesforce, Stripe) is something no single platform vendor wants to offer. Some overlap risk from Microsoft Copilot for Service; flagged as a guess.
## Biggest risk
Trust and security review: selling to compliance-minded support orgs takes long procurement cycles, and helpdesk incumbents may bolt on similar guardrails. Also the desktop surface is new (UNO is Android).
## Uses founder's existing assets
Scoped agents locked to their own tools; handover between agents; scheduled background jobs (follow-ups); approvals and spend rules enforced on-device (refund limits); reference-token privacy layer (PII never reaches the model); service-agnostic MCP pipeline (helpdesk, CRM, billing connectors); voice (escalations); BYO model key. New build: desktop client and cloud runtime.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
