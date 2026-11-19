# Clerkwise — a per-advisor team of AI agents for small wealth/insurance firms, licensed per seat, with client PII that never reaches the model
Lens: Pricing: enterprise seat licences
## Customer & pain
Buyer: the COO/compliance officer of a registered investment advisory (RIA) or independent insurance brokerage with 5-100 advisors (US first; UK/EU/India equivalents later). Advisors drown in follow-ups, meeting prep, CRM updates, form chasing, and reminders across phone calls, texts and desktop tools. Firms ban ChatGPT-style tools because client PII and off-channel messaging create regulatory exposure (recordkeeping rules, e.g. SEC/FINRA). Compliance wants AI but cannot get an audit trail or data control. (Regulatory details are from memory; verify.)
## Product
Each advisor gets a seat = a small team of vanaras.
- Phone: Scribe agent handles reminders, call notes and client follow-up drafts; Scheduler agent handles calendar and errands. Approvals and spend/send rules run on the device.
- Cloud: Prep agent runs overnight, building meeting briefs, chasing missing documents, and monitoring account/renewal dates.
- Desktop: Ops agent fills CRM and custodian/carrier forms, and files documents.
- Shared memory holds client context as reference tokens; the model sees "CLIENT_A, renewal in 30 days", never names, SSNs or balances. Real values are substituted on the device only at the moment of action.
- Agent-to-agent handover: a call note on the phone becomes a cloud task, then a desktop form fill, with one immutable log of who did what under which rule. Compliance exports the log as an archive-ready record.
## Wedge (first product, first 10 customers)
"Post-meeting autopilot": after each client call or meeting, the phone agent captures notes and action items, and the desktop agent updates the CRM and drafts a compliant follow-up for advisor approval. Sell a paid 60-day pilot to 10 small RIAs (5-15 advisors) via founder-led outreach and compliance-consultant referrals. Pilot fee $3K per firm, credited to the annual licence.
## Enterprise path
Small firm -> multi-office RIA/broker networks and their compliance platforms. Needs: SSO/SCIM, admin policy console (allowed tools per role, spend and send limits), SOC 2 Type I then II, archive integrations, BYO model key or firm-hosted model endpoint. Channel partnership with RIA compliance consultants and custodian tech marketplaces.
## Business model & pricing
Per-advisor seat licence: $79/month (annual contract), plus $25/month per support-staff seat. Compliance console and log export included at 5+ seats; premium tier $129 with firm-hosted model and custom policies. Model usage is BYO key (or pass-through at cost plus margin). 10 firms x 10 seats x $79 = ~$95K ARR (guess).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants target general users and huge enterprises; a vertical, on-device-policy product for 20-advisor firms is too small and too compliance-specific for them. Their agents send data to their own clouds; a "model never sees PII" architecture conflicts with their data-hungry personalisation. They are also better as suppliers: BYO key makes them our infrastructure, not our rivals.
## Biggest risk
Compliance and regulatory sign-off: if firms' counsel will not accept AI-drafted client communications or the log format, sales cycles stall. Second: desktop reliability on brittle custodian portals. Mitigation: agents only draft and prefill, humans approve.
## Uses founder's existing assets
Reference-token PII isolation (core pitch), on-device approvals and spend rules (compliance controls), scoped vanaras with locked tool sets (role separation), handover between agents (call-to-CRM chain), scheduled background jobs (overnight prep), MCP pipeline with tool role classification (CRM/calendar/forms connectors), voice (call notes), BYO model key. New work: cloud runner, desktop agent, admin console, audit export.
## Scores
market_size: 6
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
