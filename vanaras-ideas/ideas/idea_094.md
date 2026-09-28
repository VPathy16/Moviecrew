# Quietly — a silent agent team for solo professionals that does the work and sends one morning brief
Lens: Contrarian: no chat UI at all, agents work silently and report
## Customer & pain
Solo professionals and micro-practices (independent bookkeepers, immigration/paralegal consultants, physio and therapy clinics, freelance architects) who pay about $30-80/month. They are drowning in admin: chasing documents, rescheduling, follow-ups, renewals. Chat-based AI assistants add a new chore: prompting, reviewing and babysitting. They want fewer interactions, not a smarter chat box.
## Product
No chat UI. The only surfaces are (1) a daily digest ("Done / Needs your yes / Noticed") and (2) one-tap approval cards. Setup is a one-time onboarding: connect tools, set rules ("never spend over $50, never email a client without approval on first contact").
- Phone vanara: watches messages, calls and calendar; drafts replies and books slots; queues approvals on-device with spend rules enforced locally.
- Cloud vanara: runs standing jobs 24/7 (renewal deadlines, invoice chasing, document-gap checks) while devices are off.
- Desktop vanara: does file and browser work (fills portals, reconciles spreadsheets, files documents).
Shared memory holds client state ("Ms. Rao's visa docs: 3 of 5 received"). Agent-to-agent handoff means a phone message triggers a cloud checklist, which triggers a desktop portal filing, with no human in the loop until an approval is needed. Reference tokens keep client PII off the model.
## Wedge (first product, first 10 customers)
"Follow-up Ghost": one vertical (independent bookkeepers preparing tax season) where the agent chases clients for missing documents by SMS/WhatsApp, checks them against a checklist and reports the gaps each morning. First 10 customers come from bookkeeper communities and forums, on a 30-day paid pilot at $49/month. Android-first via UNO, with a cloud worker for the schedules.
## Enterprise path
Firms of 5-50 people: per-seat teams, admin-set policy (spend caps, approval routing, allowed tools), audit log of every silent action, and a firm-wide digest. Buyers are the partners, who value liability-safe automation with auditable approvals. Later: SSO, data-residency and on-prem reference-token vaults.
## Business model & pricing
Per-seat subscription: $49 solo, $39/seat for firms, plus usage-based overage for cloud hours. BYO model key discount for power users. Vertical add-on packs (checklists, portal connectors) at $15/month.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their products are built around chat engagement and horizontal general use. A vertical, policy-bound, silent-by-default product that touches client PII on-device across small-firm tools is low-priority and liability-heavy for them. Anthropic and OpenAI would rather supply the models; we are the distribution and trust layer. (Guess: this may erode as they ship background agents.)
## Biggest risk
Trust: a silent agent making a wrong client-facing action is worse than a chatty one. Mitigation is approval-by-default, with autonomy earned per rule. Second risk: users still want to talk to it, and the no-chat stance could feel restrictive (flagged as a guess).
## Uses founder's existing assets
Scoped, tool-locked vanaras; handover between agents; scheduled background jobs; on-device approvals and spend rules; reference tokens keeping personal data from the AI; MCP tool-role classification for connecting practice tools; voice for optional calls; BYO model key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
