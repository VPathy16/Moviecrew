# Closeout — the meeting ends, the agents start executing what was decided
Lens: Wedge: meeting-to-action (agents execute what was decided)
## Customer & pain
Buyer: heads of ops / chiefs of staff at 50-500 person services firms (agencies, consultancies, clinics groups, construction and property managers) who run many client/vendor meetings. Pain: decisions die after the call. Notetakers (Otter, Fireflies, Copilot) produce summaries and action-item lists; a human still sends the follow-up email, books the slot, updates the CRM, raises the PO. Studies-style guess (flag: unverified): 30-50% of action items never get done.
## Product
Phone vanara: joins by voice/calendar, captures decisions, pings each owner with a one-tap "approve" for their items (handles errands, reminders, calls). Cloud vanara: turns the decision into a tracked project, runs 24/7 (drafts the SOW, chases replies, retries, reschedules) and reports back. Desktop vanara: does the work in apps with no API (fill the portal, update the spreadsheet, file the doc). Shared memory holds per-meeting decisions, owners, deadlines and precedents ("last time we approved a discount of 8%"); agent-to-agent handover moves an item from the phone agent (approval) to the cloud agent (scheduling) to the desktop agent (data entry) without a human relaying. Each agent only has the tools for its role; spend and send rules are enforced on-device; personal data stays as reference tokens, never reaching the model.
## Wedge (first product, first 10 customers)
Android + web app: "Closeout" for one meeting type: client weekly calls. After each call, produce 3-6 executed outcomes (follow-up email drafted and sent on approval, calendar holds, CRM/task updates) and an "executed vs. promised" ledger. First 10: founder's network of small agencies and consultancies; free 4-week pilot, then paid. Success metric: percentage of action items closed within 48h.
## Enterprise path
Per-employee vanara team under company policy: admin console for approval and spend rules, tool allow-lists, audit log of every decision-to-action chain, SSO, BYO model key or private endpoint, data residency. Expand from one team to a department, then to the ledger across meetings (org-wide commitments tracking), then other Vanaras wedges (onboarding, handover) on the same memory.
## Business model & pricing
Per seat $25-40/month for people running meetings; free for attendees who only approve. Usage-based pass-through for model calls when not BYO key. Enterprise: $60+/seat with audit/policy features. Guess: 40 seats x $30 = $1.2K MRR per early firm.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They will summarise and suggest, inside their own suite. Cross-vendor execution (Zoom + Gmail + Outlook + niche CRMs + legacy portals) with per-agent tool scoping and on-device approval is not their incentive; each is locked to its own ecosystem and cloud-side data. Risk they add basic actions is real, so the moat is the decision-to-outcome ledger and policy layer.
## Biggest risk
Trust: one wrongly sent email or wrong booking kills adoption; also meeting capture on Android/desktop (consent, recording legality, platform limits) and notetaker incumbents adding "actions".
## Uses founder's existing assets
Scoped vanaras with locked tools, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy, service-agnostic MCP tool pipeline (role classification), voice, BYO model key. New: meeting capture, cloud runner, desktop agent.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
