# Walkback — walk the site talking to your phone; by the time you sit down, the paperwork is done on your desktop
Lens: Wedge: cross-device handoff demo ('start on phone, finish on desktop')
## Customer & pain
Site superintendents and project engineers at mid-size specialty contractors (electrical, mechanical, drywall, 20-300 staff; US/UK/AUS/Gulf). They walk the job 2-3 hours a day, then spend 1-2 hours at night re-typing observations into daily logs, RFIs, punch lists, safety forms and subcontractor emails across Procore/Autodesk, Excel and Outlook. The employer pays because the paperwork is late, incomplete and drives disputes and delayed payments. (Pain level is my estimate from general industry knowledge.)
## Product
Phone vanara (voice + photo, works offline in dead zones): the super talks and snaps while walking; it tags location, trade and urgency. Desktop vanara: on reaching the office laptop, it takes the handoff and fills the daily log, drafts RFIs with the photos attached, updates the punch list spreadsheet, and prepares sub emails, all inside the actual apps via computer use, so no API integration is needed. Cloud vanara: keeps running overnight, chasing open RFIs, watching weather and delivery schedules, and queuing a morning brief back on the phone. Shared memory means "the crack by grid C4 from Tuesday" resolves correctly, and the agent-to-agent handoff carries context so nothing is re-explained. Each vanara is scoped: the desktop one can draft but not send to the owner's rep without approval.
## Wedge (first product, first 10 customers)
One demo: "walk, talk, sit down, done." Ship an Android app plus a Windows/Mac desktop companion that produces a finished daily log and punch list in the customer's existing templates. Sell to 10 specialty contractors through 3 to 5 superintendents each, at a flat pilot fee. Founder gets access via a foreman's YouTube/LinkedIn outreach and a two-week free pilot on one live job; the daily-log-done-before-dinner outcome is easy to measure.
## Enterprise path
Per-super seat to per-project, then company-wide: admin console for templates, retention and approval rules, audit log of every agent action, SSO, and per-project data segregation. Later sits above Procore/Autodesk as the field layer for every trade, and extends to inspectors, facilities and utilities field crews.
## Business model & pricing
$79 per field user per month, $25K-$150K per year contracts at 50-300 users; add-on for owner/GC reporting packs. Founder's target: 300 seats = about $285K ARR. BYO model key optional for cost control.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants will not ship offline-first field capture with construction templates and per-trade scopes; Procore and Autodesk own the record system but not the cross-app desktop glue. It's a niche vertical too small for them and too workflow-specific to matter.
## Biggest risk
Desktop computer-use reliability inside legacy construction apps, and long enterprise sales cycles with conservative buyers. Also Procore may launch its own voice capture (a guess).
## Uses founder's existing assets
Android voice and reminders shell; scoped vanaras with own tools; handover between agents; scheduled background jobs (overnight chasing); approval and spend rules enforced on-device; reference tokens so site data and names never reach the model; MCP pipeline for connecting Procore/email/Excel; BYO model key.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
