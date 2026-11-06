# Kishkinda — the back office of a company that has one human and twelve vanaras
Lens: Moonshot: the AI-native company where most staff are vanaras
## Customer & pain
Founders of 1-5 person companies (freelance studios, small agencies, indie SaaS, solo consultancies, small e-commerce brands) worldwide. They spend 10-20 hrs/week on invoicing, chasing payments, receipts, vendor renewals, contracts admin, tax-pack prep, and scheduling. They cannot hire, and generic AI chat can't be trusted with money or client data.
## Product
Staff-as-config: each vanara is a "hire" with a job description (scoped tools), a monthly budget (spend rules), a human manager (the founder), and an audit trail. Starter roster: Bookkeeper, Collections Clerk, Vendor Manager, Scheduler, Contracts Clerk, Chief of Staff.
- Phone: founder approves payments, sees a morning "standup" from the roster, and talks to them by voice; approvals and spend caps are enforced on-device.
- Cloud: vanaras work 24/7 - reconcile the bank feed, send dunning emails, renew or cancel subscriptions, file receipts - while the phone is off.
- Desktop: covers tools with no API (legacy banking portals, government sites, client procurement portals) via computer use.
- Shared memory + sync: Collections Clerk learns a client pays late and tells Scheduler to stop booking their work and tells Bookkeeper to accrue. Handover between vanaras is the "org chart"; personal/financial identifiers stay as reference tokens, so the model never sees raw account numbers.
## Wedge (first product, first 10 customers)
"Collections Clerk" alone: connects to invoicing tool + mailbox, chases overdue invoices in the founder's voice, escalates on the phone. Outcome-priced, easy ROI. First 10 come from freelancer/indie communities (designers, dev shops, video editors), reached through founder's UNO users and build-in-public. Add Bookkeeper as the second hire.
## Enterprise path
Same primitives (role, budget, manager, audit) become a "digital workforce" layer for departments: a finance-ops team of a 200-person firm runs vanaras under IT policy, SSO, and approval chains. Sell as "headcount-equivalent" seats, with the customer's own model keys and data-residency preserved by reference tokens.
## Business model & pricing
Per-vanara-hire subscription: $29-79/month each, bundles ("Back Office 5") at $199/month; a small % (0.5%) on recovered receivables optional. BYO model key keeps gross margin above 80%. Enterprise: per-vanara annual contracts plus an admin/audit tier.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal assistants and copilots per app; none wants liability for moving small-business money or the per-role, per-budget governance for micro-companies. Long-tail SMB back-office with human-in-loop approvals is unattractive to them at low ARPU, and cross-vendor neutrality (any bank, invoicing tool, any model) is against their incentives.
## Biggest risk
Trust and liability: one wrong payment or a mis-sent dunning email to a key client. Also that accounting incumbents (Xero, QuickBooks, Ramp, Brex) bolt on agents at the same wedge. Mitigation: read-first, approvals on everything money-out for the first 30 days.
## Uses founder's existing assets
Scoped vanaras with locked toolsets (=job descriptions), handover between agents (=org chart), on-device approvals and spend rules (=budgets), reference tokens for personal data, scheduled background jobs (24/7 work), service-agnostic MCP pipeline (any invoicing/bank tool), voice, BYO key. New: cloud runtime, desktop agent, hire/roster UI.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 8
excitement: 9
