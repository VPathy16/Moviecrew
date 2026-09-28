# Dockhand — a team of agents that chases, reconciles and re-plans for every freight coordinator
Lens: Supply chain and logistics coordinators
## Customer & pain
Coordinators at small and mid freight forwarders, 3PLs and importer/distributor firms (5-200 staff) pay. Each one juggles 40-150 live shipments across email, WhatsApp, carrier portals, spreadsheets and phone calls. The day is spent chasing ETAs, ports, customs docs, detention/demurrage deadlines and truckers. Missed cutoffs cost real money (demurrage, missed vessel, angry customer). Existing TMS/visibility tools show status but do not do the chasing; coordinators still work by hand, evenings and weekends included.
## Product
Each coordinator gets a small team of vanaras.
- Phone: a "Chaser" vanara calls and messages truckers, drivers and warehouses (voice + WhatsApp/SMS), with per-shipment approvals; the coordinator gets a morning brief and exception pings, and can answer by voice while driving or on the dock.
- Cloud: a "Watcher" vanara runs 24/7 on each shipment (carrier/port APIs, email inboxes via MCP), computes deadline risk (free-time expiry, cutoff, ETA drift) and drafts re-plans overnight while devices are off.
- Desktop: a "Paperwork" vanara operates the browser and files: checks invoice vs packing list vs bill of lading, fills carrier portal and customs forms, and books slots in portals that lack APIs.
Shared memory holds per-shipment state, per-trucker reliability, customer preferences and the coordinator's decisions. Agent-to-agent sync: Watcher flags a risk, hands to Chaser to call, Chaser's answer is handed to Paperwork to amend the booking; nobody re-briefs anyone. Customer contact details stay as reference tokens; the model never sees them.
## Wedge (first product, first 10 customers)
Start with one narrow job: detention/demurrage and pickup-slot chasing for container import coordinators. Phone-first Chaser plus Watcher on the coordinator's own email forwarding rule; no integration project. Sell to 10 small forwarders and customs brokers via LinkedIn and trade communities (freight forwarder networks), starting in one region, $99/seat/month, 30-day pilot measured in avoided demurrage dollars.
## Enterprise path
Move from individual seats to a whole ops floor: shared team memory per account, company approval and spend rules (e.g. agents may rebook up to $X without sign-off), audit logs of every call and message, SSO, and a TMS/ERP connector layer (MCP pipeline classifies tools by role). Then multi-branch rollout at 3PLs with per-customer rulebooks.
## Business model & pricing
Per-coordinator seat $99-199/month, plus usage pack for voice minutes. Enterprise: $60-120/seat/month at volume plus onboarding fee. BYO model key option lowers cost for security-minded buyers. Possible outcome-based kicker on demurrage saved (guess).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants will not build shipment-level workflows, carrier portal quirks, trucker call scripts or freight-specific approval rules; the market is fragmented and unglamorous. Microsoft/Google could bundle generic agents, but the value here is the domain rulebook plus phone-calling in many languages plus device-enforced approvals, which are integration-heavy niche work.
## Biggest risk
Reliability and trust: an agent making a wrong booking or promising the wrong thing to a trucker has an immediate cost, and incumbents (project44, Flexport-type platforms, Cargowise ecosystem) may add "AI chasing" features. Also voice calling to counterparties needs consent and compliance handling (guess).
## Uses founder's existing assets
Scoped vanaras with locked tools (Chaser cannot touch bookings), handover between agents, scheduled background jobs (Watcher cadence), approvals and spend rules on device, reference tokens for contact data, service-agnostic MCP classification for carrier/TMS tools, voice, BYO key. New: cloud runtime, desktop agent, freight integrations.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
