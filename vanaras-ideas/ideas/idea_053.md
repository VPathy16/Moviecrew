# Nightwatch Vanaras — a per-analyst agent team that carries the SOC shift handover across phone, cloud and desktop
Lens: Security operations teams
## Customer & pain
Mid-size SOCs and MDR providers (10-60 analysts) pay. Alert fatigue, 24/7 shift rotation and lossy handovers hurt: context lives in each analyst's head, tickets and chat. Analysts hesitate to let AI touch live tooling because an agent with broad EDR/IAM access is itself a risk, and pasting incident data into LLMs breaks policy.
## Product
Each analyst gets a team of scoped vanaras.
- Cloud (triage): runs 24/7 on the alert queue, enriches IOCs, clusters duplicates, drafts case notes. Read-only tools only.
- Desktop (investigator): drives the analyst's browser and consoles (SIEM, EDR, ticketing) and pulls evidence into the case.
- Phone (on-call): pages the analyst by voice or push, summarises the incident in 20 seconds, and takes approvals like "isolate host X? yes" with biometric confirmation.
- Response: the only agent with containment tools, and only via approval and spend/blast-radius rules enforced on the device.
Shared memory holds the case timeline, analyst preferences and past-incident patterns, so the shift handover is automatic: the outgoing analyst's vanaras brief the incoming analyst's team. Reference tokens keep usernames, IPs and hostnames out of the model, which matters for regulated customers. Tools are classified by role (read / enrich / contain), so any MCP-exposed security tool plugs in without custom integrations.
## Wedge (first product, first 10 customers)
Start with the phone on-call and handover product: "Shift handover + approve-on-phone" for Slack/PagerDuty/Jira-based teams, needing no deep SIEM integration. Target small MDRs and security consultancies in the founder's network, plus Discord/Reddit blue-team communities. Sell a $1K/month pilot to 10 teams of 5-15 analysts, BYO model key.
## Enterprise path
SOC 2 Type II, an on-prem or VPC agent runtime, SSO/SCIM, audit-log export to the SIEM, per-role policy packs, then tiers to the CISO's whole org (IR, GRC, cloud security), each employee with their own team under central rules.
## Business model & pricing
Per-analyst seat, $150-250/month, plus a platform fee for policy and audit. An MDR margin story helps: fewer analyst hours per alert. Later, usage-based cloud triage compute (guess).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Microsoft Security Copilot and Google SecOps will build agents tied to their own stacks. Neither is neutral across a customer's mixed vendor tools. Neither offers on-device approval-and-token enforcement per analyst, and neither runs a personal on-call layer on the analyst's phone. Model vendors sell models, not vertical guardrails.
## Biggest risk
Trust and liability: one wrong containment action breaks a customer, and security buyers have long sales cycles and demand certifications a solo founder cannot fund at first. Also, established AI-SOC startups (Torq, Dropzone, Prophet-type players; flagged as guess) are well funded and move fast.
## Uses founder's existing assets
Scoped vanaras with locked tool sets, handover between agents, scheduled background jobs, device-enforced approvals and spend rules, reference-token privacy layer, MCP role-classification pipeline, voice calls for paging, and BYO model key. Android app becomes the on-call surface; cloud and desktop are new builds.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 5
asset_fit: 8
excitement: 8
