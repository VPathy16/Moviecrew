# Lookout — 24/7 cloud vanaras that watch your import supply chain and act within spend rules you set
Lens: Wedge: 24/7 cloud vanaras watching things for you
## Customer & pain
Owners of small cross-border product businesses (5-50 staff, $1-20M revenue: importers, DTC brands, Shopify/Amazon sellers). They pay because the losses come from things nobody is watching at 3am: a supplier quietly raising price, a container rolled or held at customs, a tariff/HS-code rule change (very volatile 2025-26), a carrier ETA slipping past a stock-out date, a marketplace listing suspended. Today: a founder or one ops person refreshing portals, forwarders' emails and spreadsheets. Misses cost thousands each.
## Product
- Cloud vanaras (the wedge): one vanara per watch domain (shipments, supplier prices, tariff/compliance, listings), each scoped to only its own read-only tools/feeds. They run continuously, on schedule and on events, with devices off.
- Phone: alerts as calls/voice notes; one-tap approvals ("rebook via air for $1,840? yes"). Approval and spend rules enforced on the device.
- Desktop: a vanara fills in the portals that have no API (customs broker, supplier portals) and exports evidence.
- Shared memory + agent handover: the shipments vanara notices a delay, hands to the inventory vanara (stock-out date computed), which hands to the purchasing vanara (draft air-freight quote, draft customer notice). The team remembers each supplier's habits and past resolutions.
## Wedge (first product, first 10 customers)
"Delay-to-stockout watcher": connect the forwarder email inbox + Shopify/Amazon inventory; get a daily 1-line brief and instant alerts only when a delay threatens a stock-out. $99/mo. First 10: founder-led outreach in importer/Amazon-seller communities and freight-forwarder referrals; offer a free 30-day audit of the past 90 days ("here is what you missed"). Guess: 10 paying is reachable in 3 months.
## Enterprise path
Per-employee teams for procurement/logistics/compliance staff of mid-size importers (200-5,000 staff): SSO, per-role tool scoping, audit log of every watch and action, company-wide rules (max spend, who approves), shared policy memory across teams; private cloud runtime and customer-held model key.
## Business model & pricing
SaaS: $99/mo starter (3 watch domains), $399/mo growth (unlimited watches, actions with approval), enterprise per-seat $40-80/mo plus platform fee. Model cost passed through or BYO key. Guess: gross margin 70%+ since watchers are mostly cheap polling with LLM only on change.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants target generic tasks; a vertical, connector-heavy long tail (forwarder portals, customs feeds, marketplace quirks) is unattractive to them. Trust posture (personal data never reaches the model, on-device approvals, spend limits) is a differentiator they are structurally slower to offer across arbitrary third-party tools. Risk that they ship generic "scheduled agents" is real but they lack the domain playbooks.
## Biggest risk
Integration long tail and accuracy: false alarms or one missed event kills trust; many freight sources lack APIs and are brittle. Also the vertical may be too narrow; mitigate by keeping the watcher engine generic and verticals as templates.
## Uses founder's existing assets
Scoped agents locked to own tools (watch domains), handover between agents, scheduled background jobs (moved to cloud), on-device approvals and spend rules (phone approval UX), reference tokens keeping personal/customer data away from the model, service-agnostic MCP pipeline classifying tools by role (fast connector onboarding), voice alerts, BYO model key.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 8
asset_fit: 8
excitement: 7
