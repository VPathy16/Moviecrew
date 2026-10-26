# Tailbuy — every employee's own procurement agent team that buys within policy, on the device
Lens: Procurement and purchasing inside companies
## Customer & pain
Mid-size companies (100-2,000 staff) whose tail spend (SaaS seats, contractor tools, travel add-ons, lab and office supplies, small services under ~$5K) is 20-30% of spend but ungoverned. Employees buy on cards or beg Finance; procurement teams see it 60 days later in Ramp/Coupa exports. Requesters hate intake forms; procurement hates shadow spend. Payer: Head of Procurement / CFO.
## Product
Each employee gets a small team of vanaras. Phone: a "Requester" vanara takes a voice or text ask ("we need 3 more Figma seats and a monitor arm") and does the errand. Cloud: a "Sourcer" vanara runs 24/7, gathers quotes, checks existing contracts, and chases vendors by email. Desktop: a "Filer" vanara operates portals with no API (vendor sites, legacy ERP screens) via computer use. Shared memory holds preferred vendors, past prices, contract terms and the employee's own habits. Handover: Requester -> Sourcer -> Approver vanara (the manager's phone) -> Filer, each locked to only its own tools. Company policy (spend limits, approved vendors, dual approval above thresholds) is enforced on the device/agent runtime, not in a prompt. Reference tokens keep card numbers and employee data out of the model.
## Wedge (first product, first 10 customers)
A phone + Slack "buy anything under $500" agent for 20-100 person startups that already use Ramp/Brex: it finds the vendor, fills the checkout, asks the manager to approve on their phone, pays with a virtual card and files the receipt. Sell to 10 founder/ops-lead friends and YC-style communities. BYO model key keeps cost near zero for me.
## Enterprise path
Move up from virtual cards to policy packs (per department rules), then integrations with Coupa/SAP Ariba/NetSuite as system of record, SSO/SCIM, audit exports, SOC 2, and a vendor-side agent portal so vendors' agents quote back to buyer agents. Enterprise buys the "one team per employee under company rules" story directly.
## Business model & pricing
Per-employee seat ($8-15/month) for the agent team, plus 0.3-0.5% platform fee on governed spend above a threshold, and a fixed fee for portal-automation connectors. A 500-person company is roughly $60-90K/year ARR (estimate).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell horizontal assistants and models, not spend-control liability. Buying involves cards, vendor onboarding and audit trails that they avoid. Coupa/SAP will bolt on chat agents but are tied to central workflows, not per-employee agents across phone, cloud and desktop.
## Biggest risk
Trust and liability: one wrong purchase or a fraudulent vendor page destroys credibility, and card issuers (Ramp/Brex) could copy the wedge with their own agent.
## Uses founder's existing assets
Scoped vanaras with own tools, handover between agents, on-device approvals and spend rules (the core), reference tokens for card/personal data, the MCP pipeline classifying tools by role (read vs pay), scheduled background jobs for vendor chasing, voice for requests, BYO model key.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
