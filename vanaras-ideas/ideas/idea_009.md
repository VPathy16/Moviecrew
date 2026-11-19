# Cadence — a personal team of agents for every seller: field, phone and desk, one memory
Lens: Sales teams (field + inside sales)
## Customer & pain
VP Sales / RevOps at 20-300 person B2B companies with field reps (distributors, equipment, medtech, building materials, SaaS with on-site visits). Reps lose 60-70% of time off-selling: logging CRM notes after visits, chasing follow-up emails, prepping calls, quoting, updating forecasts. CRM data is stale because reps do the entry on a phone in a car park. Existing AI (Gong, Salesforce Einstein, Copilot) sits in the CRM and listens to calls; none acts for the rep across their day.
## Product
Each rep gets a small team of vanaras.
- Phone (Android first): "Scout" preps the next visit from memory, "Scribe" takes a voice debrief after the meeting (driving, 30 seconds) and turns it into CRM updates, follow-up drafts and tasks. Calls/WhatsApp/SMS follow-ups are drafted and sent only after approval rules.
- Cloud: "Pipeline" works overnight: re-scores deals, chases quotes, drafts proposals, reconciles the rep's notes with CRM and email, keeps running when the phone is off.
- Desktop: "Desk" fills CRM fields, builds quote spreadsheets, and uses browser/apps where no API exists.
- Shared memory holds every account, promise made, and objection heard. Agent-to-agent handover: Scribe hands a "send revised quote by Friday" commitment to Desk, which drafts it, and Pipeline follows up if the client is silent. Manager sees a commitments ledger, not surveillance.
## Wedge (first product, first 10 customers)
Voice debrief-to-CRM app for Android reps ("talk for 30 seconds, CRM is updated and follow-ups drafted"), with HubSpot/Pipedrive/Zoho connectors via the MCP pipeline. Sell to owner-run distributors and small field teams (5-30 reps) through direct outreach and rep-to-manager word of mouth; first 10 from the founder's network in India plus Gulf/SEA/Africa where Android field sales dominate. Paid pilot per team, 30 days.
## Enterprise path
Per-rep team becomes a per-org fleet: admin console for approval rules, discount and spend limits, tool scopes per role, audit logs; Salesforce/Dynamics connectors; on-device reference tokens mean customer PII and pricing never reach the model; BYO model key or the customer's own Azure/Bedrock tenant. SOC2 later.
## Business model & pricing
Per-seat SaaS, about $25-40/rep/month for the phone + cloud team, +$20 for the desktop agent; managers free. Model usage via BYO key or pass-through with margin. Land at 10 seats, expand across the team.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal assistants and CRM-bound copilots tied to their own suites. A neutral, Android-first, CRM-agnostic rep companion with per-agent tool locks and on-device approvals across messy real tools (WhatsApp, dialer, spreadsheets) is a low-margin vertical for them, and CRM vendors will not make it cross-CRM.
## Biggest risk
Reps resist another app, and CRM vendors (Salesforce, HubSpot) ship good-enough voice logging. Also Android/WhatsApp/call-access policy limits. Mitigation: make it save the rep time on day one, not serve the manager first.
## Uses founder's existing assets
Scoped vanaras with locked tools, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy layer, MCP pipeline with role classification (CRM, mail, calendar), voice, BYO model key. New: CRM connectors, cloud runner, desktop agent, manager console.
## Scores
market_size: 8
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
