# Tempo — an agent team that owns the calendars of small professional practices, across phone, cloud and desktop
Lens: Calendar and time as the core
## Customer & pain
Owners of 2-15 person appointment-and-deadline practices (accountancies, physio and dental clinics, boutique law firms, architects). They pay because time is their inventory: no-shows, double-booked partners, missed filing deadlines, and hours per week spent on scheduling email. Today they stitch together a booking tool, a shared calendar, a practice-management system and a receptionist. None of these knows the owner's personal life, so the practice is planned around a fictional owner.
## Product
Each person gets a team of scoped vanaras. On the phone, a Scheduler agent (calendar tools only) negotiates times by message or voice, and the person's private constraints (school run, medical, family) stay on the device as reference tokens. The AI sees "busy, cannot move" and never the reason. In the cloud, a Deadlines agent runs 24/7: it watches filing dates and matter or case clocks, works backward into prep blocks, and reschedules them when something slips. On the desktop, a Prep agent opens the files, drafts the pack and preps the browser session before each meeting. Shared memory holds the commitments graph: who owes what by when, and how long tasks really take. Agent-to-agent sync handles the handovers. A cancellation on the phone triggers the cloud agent to backfill from the waitlist, and the desktop agent to drop the prep. Approvals and spend rules limit what each agent may do without a human, for example no moving a client meeting without a tap.
## Wedge (first product, first 10 customers)
Start with solo and 2-person accountancies and physio clinics: "No-show and deadline guard". It is Android and a Google Calendar and WhatsApp connector, with a cloud job that reconfirms appointments and backfills cancellations. Target is 10 clinics or practices reached through the founder's network and local practitioner groups at about $49 per seat per month. The measurable claim is recovered appointment slots (guess: 20-40% fewer no-shows).
## Enterprise path
Practices grow to firms of 50-500. Then sell per-employee teams with a policy console: firm-wide rules on who can book whom, retention and ethical walls, and a full audit trail of agent actions. Personal-life tokens stay on-device, which is the privacy story for regulated professions. The next step is Microsoft 365 and Google Workspace admin deployment.
## Business model & pricing
Per-seat SaaS: $29 for personal (phone) and $49-99 for professional (phone, cloud and desktop). Practices pay for an optional shared team layer of about $15 per seat. BYO model key is available to cut COGS, with a managed-key premium. Guess: gross margin above 70% at moderate agent usage.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their calendar assistants are horizontal and cloud-first, and they optimise for the platform's own suite. A vertical layer needs per-profession deadline logic, local-only personal-data tokens, and cross-suite neutrality (Google and Microsoft calendars together). None of those is a priority for them. They are also cautious about autonomous actions in regulated practices.
## Biggest risk
Trust and reliability. One wrongly moved client meeting or missed deadline can end a customer. Calendar-write actions need a strong approval default, and the vertical rules may require deep per-profession work that does not scale for one founder.
## Uses founder's existing assets
Scoped, tool-locked agents (Scheduler, Deadlines, Prep), handover between agents, scheduled background jobs (reconfirmations, deadline watch), on-device approvals and spend rules, reference-token privacy for personal calendar detail, the MCP pipeline classifying calendar, messaging and mail tools by role, voice for phone negotiation, and BYO model key. New work: cloud runtime, desktop agent, and the vertical deadline packs.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
