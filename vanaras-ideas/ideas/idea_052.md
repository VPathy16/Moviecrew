# Tickless — every employee's own IT agent team that fixes problems on their laptop and phone before a ticket exists
Lens: IT helpdesk automation
## Customer & pain
Payer: IT lead / head of IT at 200-2,000-person companies (often Google Workspace or M365 shops with 2-6 IT staff). Today 30-50% of tickets are password resets, VPN/Wi-Fi flakiness, "install X", access requests, offboarding chores. Existing tools (Moveworks, Aisera, Freshservice bots) are chat frontends over the ticket queue: they answer, but cannot touch the employee's actual device, and employees hate pasting screenshots. IT staff burn hours on remote sessions for 10-minute fixes.
## Product
Each employee gets a small team of vanaras. Desktop vanara: diagnoses and fixes on the laptop (flush DNS, reinstall VPN profile, clear a stuck update, install approved software) inside a scoped tool set, with device-enforced approvals. Phone vanara: the conversational front door (voice or chat, also for "my laptop won't turn on"), handles MFA re-enrolment guidance and approvals. Cloud vanara: works the admin side 24/7 (IdP, MDM, SaaS admin APIs via the MCP role-classified pipeline): provisioning, access grants, licence reclaim, offboarding runs. Shared memory means the agent remembers this user's device history, past fixes and "this Wi-Fi drops every Tuesday". Agent-to-agent sync: the phone agent hands the case to the desktop agent, which hands an admin step to the cloud agent, and a fleet-level pattern (10 laptops hit the same bad update) is spotted across users' agents without exposing personal data (reference tokens).
## Wedge (first product, first 10 customers)
"Access request and offboarding autopilot" for Google Workspace + Slack + one MDM: cloud vanara only, with approver flow on phones. Sell to 10 startups/scale-ups (100-500 staff) via IT-manager communities, founder-led, $500/month pilot. Desktop fixer added as second module once trust exists.
## Enterprise path
Per-employee team under company policy: SSO/SCIM, policy packs (which tools each vanara may use, spend and approval rules), audit log exportable to SIEM, BYO model key or private endpoint, SOC 2 (start with a vendor-lite path around month 6-9). Land in IT, expand to HR, finance ops agent teams for the same employees.
## Business model & pricing
Per-employee per-month: $3 for access/offboarding tier, $8 for full device+access team; minimum $500/month. Target ACV $10-40K. Model cost passed through or BYO key.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell platforms tied to their own stack; Microsoft Copilot/Intune is M365-centric and Google barely serves IT admins across mixed fleets. Cross-vendor neutrality (Okta + Google + Jamf + Slack) and device-enforced least privilege are not their priority; model vendors avoid liability of acting on endpoints.
## Biggest risk
Trust and security: an agent with device and admin powers is an attack surface; one bad remediation or prompt-injection incident kills the brand. Also endpoint agent distribution on Windows/macOS (UNO is Android) and incumbent bundling (ServiceNow, Moveworks/ServiceNow).
## Uses founder's existing assets
Scoped agents with locked tool sets (core safety story), on-device approvals and spend rules, reference-token privacy (user data never reaches the model), MCP pipeline classifying tools by role (IdP/MDM/SaaS admin), handover between agents, scheduled background jobs (offboarding, licence sweeps), voice, BYO key. New: desktop runtime, admin web console.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
