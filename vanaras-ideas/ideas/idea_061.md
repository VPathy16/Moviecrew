# Tendhand — every client gets their own scoped agent team, and the agency's staff supervise all of them from one phone
Lens: Agencies running many clients
## Customer & pain
Small marketing, bookkeeping, recruiting and web-maintenance agencies (5-50 staff, 20-200 clients). Account managers juggle client chats, recurring deliverables, logins and approvals across dozens of tools. Work leaks between clients, juniors hold client credentials, and nothing runs when staff are offline. Owners pay for it in margin: one AM can handle about 8 clients, and every mistake risks a client relationship. (Sizing is my guess.)
## Product
Each client gets a "client team" of scoped vanaras. Each vanara is locked to that client's tools and data, so cross-client leakage is structurally impossible rather than a matter of policy.
- Phone: the AM gets a daily digest across all clients. They approve or reject drafted client replies and spend, and can voice-command "what is blocked for Acme?".
- Cloud: agents run recurring deliverables 24/7 (monthly reports, ad-budget pacing checks, invoice chasers, content calendars) while devices are off.
- Desktop: an agent operates tools with no API (client portals, legacy ad dashboards), inside the client's scope.
Shared memory is per client: brand voice, past decisions, contacts. Handover between agents is agent-to-agent, so a cloud reporting agent hands a flagged anomaly to the phone agent, which pings the AM for approval. Client credentials sit in the device vault and agents only see reference tokens. Staff turnover no longer loses client context.
## Wedge (first product, first 10 customers)
Start with one vertical: paid-social and SEO reporting agencies. The product is "Monday report and anomaly watcher": connect the ad accounts via MCP, and each client team drafts the report and alerts the AM with one-tap approve before send. Find the first 10 through founder outreach to boutique agency owners, agency Slack and Facebook groups, and a 30-day pilot with 3 clients each. Charge from day one.
## Enterprise path
Agencies come first and are the beachhead. They then become resellers, with white-label client teams offered to the agency's own clients. The same client-scope, approval and audit model maps to enterprise per-employee teams, and to the compliance needs of larger agency holding groups (SSO, audit export, on-prem key custody).
## Business model & pricing
Per-client-team pricing: $40-80 per client per month, with a 20-client agency paying about $1K per month. Add a staff seat fee of $30 per month. BYO model key keeps COGS low, and the agency can optionally use bundled inference at a markup. White-label tier at $500 per month base.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their agents are designed around one user with one identity. Multi-tenant scoping across 100 client contexts, with an agency-run approval workflow, is a niche vertical and a support-heavy business. On-device enforcement and vault-held credentials are a trust story that a horizontal assistant is unlikely to prioritise. Agency owners also distrust a platform that could sell direct to their clients.
## Biggest risk
Integration depth. Agencies live in ad platforms, CRMs and ticketing tools, and MCP coverage is uneven, so the wedge may stall on brittle connectors. Second risk: agencies are price-sensitive and churn when their client roster changes.
## Uses founder's existing assets
Scoped vanaras locked to their tools (the client-scope model), agent handover, scheduled background jobs, on-device approvals and spend rules, reference-token privacy (client data never reaches the model), the service-agnostic MCP pipeline with role classification (fast connector onboarding), voice for the AM's phone commands, and BYO model key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
