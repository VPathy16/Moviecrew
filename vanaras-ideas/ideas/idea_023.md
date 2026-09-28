# Shiftmate — a team of AI agents for every plant supervisor, on the phone, in the cloud and at the PC
Lens: Manufacturing plants
## Customer & pain
Mid-size discrete manufacturers (50-500 staff, auto-parts, plastics, metal fabrication, packaging) in India, SE Asia, Mexico, Eastern Europe. The plant manager and shift supervisors pay. Today the plant runs on WhatsApp groups, paper shift logs, Excel and a half-used ERP. Breakdowns, quality holds, missing material and shift handovers get lost in chat. Supervisors spend 2-3 hours a day chasing people and typing reports. Big MES/IIoT suites cost six figures and need IT teams these plants don't have.
## Product
- Phone (supervisor, on the floor): voice-first. "Line 4 down, hydraulic leak" creates a downtime ticket, calls maintenance, tells the planner, and writes the shift log. Shift-handover agent produces a spoken and written briefing for the next supervisor.
- Cloud: 24/7 agents watch machine-stop feeds, PLC/OPC-UA or sensor exports, and ERP/Excel orders. They chase suppliers, draft 8D/quality reports, reschedule jobs, and escalate when a delay threatens a customer delivery.
- Desktop: a computer-use agent fills ERP screens and Excel sheets that have no API, and pulls the daily OEE report.
- Shared memory + agent-to-agent sync: the maintenance agent knows what the quality agent saw at 2am. A handover from the phone agent starts cloud work, and the result comes back as one approval on the supervisor's phone. Memory of past failures per machine becomes the plant's institutional knowledge, which survives staff turnover.
## Wedge (first product, first 10 customers)
Shift handover and downtime logging by voice in local languages, over WhatsApp/phone, with no integration needed. Sell it as a paid pilot on a single line for $300/month. Get the first 10 through the founder's own network, industrial-estate associations and contract-manufacturer owners. Target: 3 plants in 3 months.
## Enterprise path
Move from one line to the plant, then to multi-plant groups: per-role agent teams (supervisor, maintenance, quality, planner, stores), SSO, on-prem or VPC data residency, audit logs, and company rules on who may approve spend or stop a line. Then integrations with SAP B1, Tally, Odoo and Siemens/Rockwell data. Group procurement follows.
## Business model & pricing
Per-plant subscription: $300/month per line, $1.5-3K/month per plant with unlimited supervisors. Bring your own model key is optional. Enterprise multi-plant contracts of $50-200K a year. Add usage pricing for the desktop agent.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants will not build shop-floor voice workflows in regional languages, per-plant memory, or approval rules for stopping a line. Microsoft and Siemens go top-down to large enterprises, while a 200-person plant with a WhatsApp culture is too small and too messy for them. The domain playbook and the on-floor trust are the moat. (Guess: their factory copilots stay tied to their own MES stacks.)
## Biggest risk
Shop-floor adoption and noise: voice recognition in loud plants and mixed languages, plus supervisors who distrust new tools. Long pilots to paid conversion in conservative owner-run firms is the second risk.
## Uses founder's existing assets
Scoped vanaras with their own tools (maintenance, quality, planner agents), handover between agents, scheduled background jobs, on-device approvals and spend rules (line-stop and purchase approvals), reference tokens so production and supplier data never reach the model, the service-agnostic MCP pipeline for ERP/Excel/WhatsApp tools, voice, and BYO model key.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
