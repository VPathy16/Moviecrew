# Shelfhand — a pocket team of agents for the store manager, tied to the district's cloud crew
Lens: Multi-location retail chains
## Customer & pain
Payer: operations VPs and district managers of 20-300 store specialty chains (pet, vitamin, optical, cellular, discount apparel, franchised QSR-adjacent retail). Store managers run on personal phones and WhatsApp/SMS groups: shift swaps, vendor deliveries, planogram resets, cash-variance calls, maintenance tickets, HQ directives that get lost. Every store's tribal knowledge leaves with the manager (turnover 30-50%/yr). HQ's tools (task apps, intranets) get ignored because they add work instead of doing it.
## Product
Each store manager gets a Vanaras team on their phone: a Shifts agent (swaps, call-outs, covers via SMS/voice to staff), a Vendor agent (confirms deliveries, chases late orders, logs shortages), a Directive agent (turns HQ memos into store checklists and closes the loop with photo proof), a Maintenance agent (files and follows up tickets). Cloud agents run 24/7 per district: reconcile store reports, spot patterns (three stores reporting the same supplier miss), draft district digests. Desktop agent at HQ/district office does back-office: fills portals, updates spreadsheets, pulls POS exports. Shared memory is per-store (quirks, vendor contacts, what worked) and survives manager turnover; agent-to-agent sync lets a store's Vendor agent hand a recurring shortage to the district cloud agent, which negotiates a fix with the supplier. Approvals and spend caps (e.g. emergency repair under $200) are enforced on the device; store staff data stays as reference tokens.
## Wedge (first product, first 10 customers)
Store-manager phone agent doing shift-swap coordination plus HQ directive tracking, sold to 10 chains of 20-60 stores via a paid 90-day pilot in 3 stores each. Find them via franchise associations and regional retail groups; the district manager is the champion. Android-first fits: many chains use cheap Android handhelds/BYOD.
## Enterprise path
Pilot 3 stores, then district, then chain. Add SSO, MDM deployment, audit logs, policy packs (cash handling, labor law per state/country), POS/WFM connectors (Toast-like, UKG, Deputy, Shopify POS) through the MCP role-classifier. Every manager becomes a seat; HQ staff get desktop crews.
## Business model & pricing
$25-40 per store manager per month plus $8/store/month for the cloud district crew; BYO model key lowers COGS, or pass-through at cost plus margin. 100 chains x 60 stores is roughly $1M+ ARR per 100 pilots-to-rollout.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants don't ship per-store scoped agents with on-device spend rules and store-to-district handover for a low-margin vertical with 40-store customers. Microsoft Teams/Frontline is closest but assumes a desk and IT; the long tail of mid-size chains is too fragmented for them.
## Biggest risk
Frontline turnover and phone-privacy: managers may refuse work agents on personal phones, and chains move slowly; pilots may stall in procurement. Also staff-facing SMS/voice compliance (guess: TCPA-style consent rules).
## Uses founder's existing assets
Scoped vanaras with locked tools, agent handover, scheduled background jobs, on-device approvals and spend rules, reference-token privacy (staff and vendor data), MCP tool-role pipeline for POS/WFM connectors, voice for vendor and staff calls, BYO model key.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
