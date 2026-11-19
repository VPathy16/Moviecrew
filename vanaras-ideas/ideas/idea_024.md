# Pass — a personal agent team for every restaurant and hotel manager, that keeps the shift running when they are off the floor
Lens: Hospitality and restaurants (operations, not food ordering)
## Customer & pain
Payer: independent restaurant, bar and boutique-hotel owners and general managers (1-15 sites). They work 60-hour weeks across WhatsApp groups, supplier texts, rota apps, POS dashboards and booking tools. Pain: staff no-shows, last-minute shift swaps, supplier order cut-offs, stock-outs, review replies, compliance logs (temperature, cleaning, allergen sheets), and cash-flow surprises. Nothing ties these together, and the manager is the integration layer, often at 11pm.
## Product
- Phone (manager's daily life and floor): a voice-first "Floor" vanara. Manager says "Priya called in sick, cover Friday close" and it messages the bench, collects replies, and asks approval before confirming. Supplier reorders and refunds sit behind on-device spend rules and approvals.
- Cloud (the site's projects): a "Back office" vanara runs 24/7 on weekly orders, rota drafts, supplier invoice checks against delivery notes, review replies, and compliance-log reminders, even when every device is off.
- Desktop (work): a "Books" vanara drives the POS export, accounting package and supplier portals that have no API, and reconciles the week.
- Shared memory + agent sync: memory holds supplier terms, staff availability and skills, house rules ("never let bar close short-staffed") and past incidents. A no-show on phone triggers a cloud rota redraft, then a desktop update to the payroll sheet, with one approval. Staff data stays behind reference tokens, so the model never sees names or phone numbers.
## Wedge (first product, first 10 customers)
Shift-cover and supplier-reorder over WhatsApp/SMS, using the existing phone agent and BYO key. Sell to owner-operators of 1-3 venues at about $49/month. First 10 come from local hospitality owner groups, a friendly chef/bar-owner network and one hospitality trade Slack/Facebook group; founder visits, sets up in an hour, and watches the first no-show get handled.
## Enterprise path
Multi-site groups (5-100 venues) and hotel groups: per-employee teams for GM, head chef, and duty manager under group rules (spend caps per site, approval chains, audit logs, data residency). Sold via hospitality consultants and POS/booking resellers; SSO and central policy come later.
## Business model & pricing
Per-site subscription: $49 Floor, $149 full team (cloud + desktop); groups $99/site/month with policy and audit. Model costs pass through via BYO key or a small usage markup. Target 200 sites for about $20K MRR.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants will not build per-role scoped agents for a low-margin, fragmented vertical with dozens of small POS/rota tools, or handle the messy WhatsApp-with-temp-staff reality. Spend rules and PII-free design matter to owners handling payroll and supplier money. Vertical incumbents (rota and POS vendors) own one silo each, not the cross-tool handoff.
## Biggest risk
Distribution and churn in a low-margin, high-turnover vertical, plus reliability: a wrong shift message or order at service time destroys trust. Also guess: WhatsApp business API policy limits for agent-initiated messaging.
## Uses founder's existing assets
Scoped vanaras per role, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy for staff data, the service-agnostic MCP pipeline (POS, rota, supplier portals classified by role), voice for hands-busy kitchens, BYO model key. New: cloud and desktop surfaces, hospitality connectors.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
