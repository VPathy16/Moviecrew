# LabRelay — an agent team for every academic lab that keeps the lab's memory when students graduate
Lens: Academic labs
## Customer & pain
Who pays: PIs and department research-computing offices (grant overhead or lab discretionary funds). Pain: a lab is a 4-8 year rotating cast of PhD students and postdocs. Every graduation wipes out tacit knowledge: which cluster queue works, why run 14 was discarded, which reviewer wanted which control, which instrument booking quirks matter. Meanwhile PIs drown in admin: grant reporting, IRB/data-use compliance, reagent orders, meeting scheduling, and chasing students for status.
## Product
- Phone: each lab member's vanara handles daily life plus lab logistics (instrument slots, meeting nags, voice-note capture of bench observations, reminders for incubations and deadlines).
- Cloud: project vanaras own each paper or grant. They run long jobs 24/7: re-running analyses on new data, monitoring training or sim jobs on the cluster, drafting methods sections from the run log, tracking the reporting calendar.
- Desktop: a scoped desktop vanara operates lab software (instrument PC exports, reference manager, spreadsheets, browser portals) under approval rules.
- Shared memory + sync: one lab memory (experiment log, decisions, "why we did X") persists across people. Handover between agents becomes handover between students: an outgoing student's vanaras hand a structured "project dossier" to the incoming student's vanaras. Reference tokens keep unpublished data, subject data and student personal info away from the model; only the lab's on-device/cloud vault resolves them.
## Wedge (first product, first 10 customers)
"Graduation handover": a phone + cloud tool that interviews a departing student by voice over their last 8 weeks, cross-references their logs and files, and produces a living, queryable dossier the next student's agent can use. Sell to 10 friendly PIs (one-lab pilots, free semester then a small fee) from personal/academic contacts. Guess: 2-3 pilot labs reachable via founder's network; unvalidated.
## Enterprise path
Lab, then department, then university research office (data-governance, IRB, export-control rules enforced as approval/spend policies), then pharma/biotech R&D and national labs, which have the same turnover and far bigger budgets. Enterprise = "every employee gets a team under company rules".
## Business model & pricing
Per lab seat: ~$25/member/month; lab plan ~$300/month; department licences ~$20-50K/yr (guess). BYO model key keeps COGS low; universities often already hold model credits.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Generic assistants are per-user and horizontal. Labs need compliance-grade data isolation, per-project handover across people, and instrument/cluster integrations: a tiny, slow, fragmented market with heavy procurement, unattractive to platforms. Universities also resist sending unpublished data to vendors, favouring the token-based approach.
## Biggest risk
Academic budgets are tiny and procurement is slow, and PIs may not value "knowledge retention" until it hurts; the handover can be mistaken for surveillance by students. Mitigation: pilot with PIs, keep the student in control of what is shared.
## Uses founder's existing assets
Scoped vanaras and agent handover (the core mechanic), scheduled background jobs (monitoring/reporting), on-device approvals and spend rules (compliance), reference tokens (data never reaches AI), MCP tool classification (lab software and cluster tools), voice (bench capture and exit interviews), BYO key (university-provided keys). Needs new: cloud and desktop surfaces.
## Scores
market_size: 5
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 8
excitement: 6
