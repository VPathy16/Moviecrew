# Majlis — a sovereign, on-prem team of AI agents for every employee of Gulf enterprises
Lens: Middle East enterprises (sovereign cloud)
## Customer & pain
Paying buyer: CIO/CDO of Gulf banks, government entities, telcos, energy and healthcare groups (UAE, KSA, Qatar). They are pushed by national AI agendas (Vision 2030, UAE AI strategy) to give staff AI assistants, but data-residency rules (KSA PDPL, UAE PDPL, NCA/ADGM/DIFC controls, central-bank outsourcing rules) make Copilot/ChatGPT Enterprise hard or slow to approve. Result: pilots stall, staff use shadow AI on phones, and nothing acts on the employee's behalf, it only chats. Arabic/English code-switching and WhatsApp-centric work habits are poorly served.
## Product
Each employee gets a team of scoped vanaras (Inbox, Calendar/Errands, Documents, Approvals). Phone: voice and messaging in Arabic/English, reminders, approvals. Desktop: agent works files, browser, internal apps. Cloud: long-running jobs (report prep, renewals, tender tracking) running inside the customer's sovereign region or on-prem, model choice being a local-hosted model (Falcon/Jais-class, or a private-deployed frontier model) or the customer's own key. Shared memory lives in the customer tenant; agent-to-agent handover means a phone request ("prepare the board pack") continues on cloud overnight and finishes on desktop. On-device approvals and spend rules, plus reference tokens so personal and customer data never reaches the model, become a compliance story: auditors see policy enforced at the edge, not just promised.
## Wedge (first product, first 10 customers)
"Approvals and follow-up agent" for managers: phone-first agent that chases, drafts and routes approvals across email/Teams/WhatsApp Business under policy. Sell a 60-day paid pilot for 50 seats to mid-size regulated firms (insurers, family conglomerates, free-zone authorities) via a Gulf integrator/reseller partner, since the founder has no local network yet (assumption). First 10: 2 integrators plus 8 pilots at ~$15-25K each.
## Enterprise path
Pilot, then department (100-500 seats), then group. Deliver as a container bundle for sovereign clouds (G42/Core42, Khazna, stc, Oracle/Azure/AWS Gulf regions) and air-gapped on-prem. Get ISO 27001, then local certifications (NCA ECC, UAE IA) with partner help. Admin console for rules: which tools each vanara can use, spend limits, audit export.
## Business model & pricing
Per-seat $25-40/month, minimum 100 seats; annual platform/deployment fee $30-100K; paid onboarding and custom connectors; model cost passed through or BYO key. Reseller margin 20-30%.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They do offer Gulf regions, but not per-customer on-prem, model-agnostic, Arabic-workflow tailoring; their agents are tied to their own stack and model. A neutral, policy-at-the-edge layer that runs on any local model and any tool is off-strategy for them and slow to prioritise for a regional market. Risk: Microsoft sovereign Copilot narrowing this (flagged guess).
## Biggest risk
Sales cycle and trust: government/bank procurement is slow, relationship-driven, and a solo foreign founder with no local presence may not close before the money runs out; also local-model quality for agentic tool use.
## Uses founder's existing assets
Scoped per-tool vanaras, handover between agents, on-device approvals and spend rules, reference-token privacy layer, service-agnostic MCP tool-classification pipeline, scheduled background jobs, voice, BYO model key. New: desktop and cloud runtimes, multi-tenant admin, Arabic tuning.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 4
asset_fit: 8
excitement: 8
