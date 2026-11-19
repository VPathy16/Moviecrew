# Shortlist — a personal agent team for every recruiter that sources, screens and schedules without candidate data ever reaching the AI
Lens: Recruiters and HR teams
## Customer & pain
Agency recruiters and in-house talent teams (5-50 seats). Each recruiter juggles 30+ open reqs across LinkedIn, ATS, email, WhatsApp/SMS and calendars. Most of the day is chasing, rescheduling and copy-pasting. Existing AI sourcing tools are risky: pasting candidate CVs into a chatbot breaches GDPR/DPDP and client contracts, so HR legal blocks them. Agencies pay per recruiter; in-house HR pays via the TA budget.
## Product
- Phone: a "Candidate Chaser" vanara texts/calls candidates (voice), confirms interview slots, nudges after silence, and asks the recruiter for approval before any offer-stage message. Runs on-device reference tokens, so names, phones and CVs never reach the model.
- Cloud: a "Sourcer" vanara runs 24/7 against each req: builds Boolean searches, pulls from job boards/ATS via MCP, ranks and drafts outreach while the laptop is closed.
- Desktop: a "Coordinator" vanara operates the ATS, LinkedIn Recruiter and Excel trackers in the browser (computer use) where there is no API, and updates records.
- Shared memory + agent sync: what a candidate said on a call (salary, notice period, visa) is instantly visible to the Sourcer and Coordinator; a desktop shortlist triggers phone scheduling; handover between agents is audited per candidate.
## Wedge (first product, first 10 customers)
Interview scheduling and candidate chasing on Android + WhatsApp/SMS/voice for solo and small-agency recruiters (2-10 seats), sold as "get 10 hours a week back". Find the first 10 via recruiter communities, LinkedIn and ex-colleagues; 30-day pilot with approval rules preconfigured. Priced simply, BYO model key keeps costs near zero for the founder.
## Enterprise path
Per-recruiter teams under a company policy: which tools each vanara may touch, spend and message-volume caps, mandatory human approval for rejections and offers, and an audit log for bias/compliance (NYC LL144, EU AI Act high-risk hiring rules). Sell to TA heads, then HR/legal sign-off using the "no PII to model" architecture as the selling point. Integrations via MCP: Greenhouse, Lever, Workday, Ashby.
## Business model & pricing
Per-seat SaaS: about $49/recruiter/month starter (phone + scheduling), $149 full team (cloud + desktop agents); enterprise $60-100k/yr plus compliance/audit tier. Usage add-on for voice minutes. (Pricing is a guess.)
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal assistants and cannot ship recruiter-specific approval rules, per-candidate audit, or take liability for hiring compliance. LinkedIn (Microsoft) is a conflicted platform and will not orchestrate across competitors' ATSs and boards. Vertical workflow plus governance is a small market to them.
## Biggest risk
Platform hostility: LinkedIn and job boards restrict automation and scraping, and messaging channels (WhatsApp Business) have policy limits. Also, legal risk of automated screening bias if approvals are skipped.
## Uses founder's existing assets
Scoped vanaras with locked tools; agent handover; scheduled background jobs (chasing, sourcing runs); on-device approvals and spend rules; reference tokens keeping PII from the AI; MCP pipeline with role classification (ATS/calendar/messaging tools); voice calls; BYO model key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 8
asset_fit: 8
excitement: 6
