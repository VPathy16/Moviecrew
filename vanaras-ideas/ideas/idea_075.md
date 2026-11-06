# Cashvana — a crew of agents that chases your unpaid invoices and only gets paid when money lands
Lens: Pricing: outcome-based
## Customer & pain
Freelancers, small agencies, consultancies and tradespeople (1-30 people) worldwide. Late payment is their biggest unpaid-admin problem: the average small B2B invoice is paid weeks late (guess: 30-50% of invoices overdue at any time), owners hate chasing clients, and collections agencies take 20-30% and damage relationships. The owner pays with cash they recover, so no budget line is needed.
## Product
Three vanaras with different locked toolsets:
- Phone vanara (UNO): messages, WhatsApp/SMS and voice calls to the client's accounts contact, in the owner's tone; the owner approves the escalation ladder once.
- Cloud vanara: watches invoices 24/7 (accounting MCP: Xero, QuickBooks, Zoho, Stripe), schedules reminders, tracks promises ("will pay Friday"), and re-checks the bank feed.
- Desktop vanara: logs into client procurement portals (Ariba-style, Coupa), fixes missing PO numbers, resubmits invoices, downloads remittance advice.
Shared memory holds each client's payment behaviour, contacts, and past promises. Agent-to-agent sync: a phone call promise instantly reschedules the cloud check and tells the desktop agent to prepare the portal resubmission. Bank and client details stay as reference tokens; the model never sees raw account data. Spend and send rules (no legal threats, no messages after 8pm, discounts capped) are enforced on device.
## Wedge (first product, first 10 customers)
Android app + Xero/QuickBooks connector: "connect, approve the ladder, we chase only invoices already 15+ days overdue." Free to start. First 10 customers from freelancer/agency communities (designers, dev shops, UK/US/India/Gulf), recruited by offering a 90-day pilot at 6% fee.
## Enterprise path
Same crew for each AR clerk and account manager in mid-size companies: per-employee team, company policy (tone, discount authority, jurisdiction rules like debt-collection law), audit log of every message, shared memory of customer promises across sales, finance and support. Sell later as an outcome-priced AR-automation layer next to ERP.
## Business model & pricing
Success fee only: 5-8% of invoices collected that were overdue at onboarding and paid after first contact (flat 3% if paid within 3 days of a reminder; nothing if the client pays unprompted, verified by timestamped attribution log). Enterprise: base seat fee plus 2-4% of incremental recovery vs. baseline DSO. Guess: gross margin high, as agent cost is cents per invoice.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Taking a percentage of a customer's cash and being liable for dunning conduct is a business they avoid; it needs per-jurisdiction compliance, phone/WhatsApp presence and portal-by-portal grind. Horizontal assistants sell seats, not recovery. Intuit and Xero could, but are tied to one ledger and use email-only reminders.
## Biggest risk
Attribution disputes and client-relationship damage: customers may claim they would have paid anyway, and a badly worded chase costs a client. Also debt-collection regulation varies by country (guess: mostly B2B is lighter).
## Uses founder's existing assets
UNO scoped vanaras, approvals and spend/send rules on device, handover between agents, scheduled background jobs, reference-token privacy for bank data, service-agnostic MCP pipeline (accounting tools classified by role), voice for calls, BYO model key to cut cost.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 8
excitement: 8
