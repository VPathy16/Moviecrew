# Tether — a personal agent team for every finance-ops and revenue-ops employee at mid-market companies, with controls IT can sign off in a day
Lens: Mid-market companies 200-2000 employees
## Customer & pain
The COO or Head of IT at a 200-2000 person company pays. Employees already use ChatGPT, Claude and Copilot on personal accounts (shadow AI). IT can't approve it: no audit trail, no spend limits, and customer or employee data leaks into prompts. Mid-market firms lack a 20-person AI governance team, and enterprise agent platforms (Agentforce-style) need months of integration and consultants they can't afford.
## Product
Each employee gets a small team of scoped vanaras. Phone: approvals, reminders, voice check-ins ("approve these 3 invoices"). Desktop: files, browser and internal apps for month-end close, CRM hygiene and expense chasing. Cloud: long-running jobs such as reconciliations and renewal follow-ups that run overnight. Shared memory means the desktop agent's finding ("vendor X invoice mismatched") is picked up by the cloud agent and surfaced on the phone for approval. Agent-to-agent handover replaces the employee acting as the glue. Every agent has locked tools, and approvals and spend caps are enforced on the device. Personal and customer data goes through reference tokens, so the model never sees raw records.
## Wedge (first product, first 10 customers)
"Approval Desk": one vanara per finance or RevOps person that triages invoices, expenses and discount requests. It drafts the action, and a human approves on the phone. Sell to 10 companies of about 300-800 staff, found through fractional CFOs and MSPs, with a 4-week paid pilot for 10-25 seats at about $2K. Pitch: "your team's AI, with a receipt for everything."
## Enterprise path
Start with one department, then expand seat by seat. Add SSO/SCIM, a central policy console (which tools each role may use, spend caps, model choice) and audit export to SIEM. Later add SOC 2, private-model routing and per-role vanara templates. The endpoint is a company-wide rollout, where each employee's team runs under IT policy.
## Business model & pricing
Per seat, $40-60/month for the agent team, with a platform fee of $500/month per company for the policy console. BYO model key or metered pass-through at cost plus a margin. A 500-seat company pays roughly $250-350K/year at full rollout. Partner and MSP resale adds a margin channel.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build for their own model and ecosystem. A mid-market buyer wants model-neutral, on-device enforcement across phone, cloud and desktop, and vendors have no reason to serve that mixed stack. Microsoft Copilot is priced and bundled for large enterprises. Each vendor's own agents can't be neutral about which model runs them, which is the opening for the on-device policy layer. This is a guess, and the opening may narrow.
## Biggest risk
Trust and sales cycle: a solo founder selling security-sensitive software to IT buyers, with no SOC 2 in the first year. Second risk: Microsoft or Anthropic ship "good enough" governed desktop agents and bundle them.
## Uses founder's existing assets
Scoped vanaras with locked tools, on-device approvals and spend rules, reference-token privacy layer, handover between agents, scheduled background jobs, the MCP role-classification pipeline (connects to ERP, CRM and ticketing without bespoke code), voice and BYO model key. New work: iOS/desktop clients, cloud runner, SSO and admin console.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 5
asset_fit: 8
excitement: 8
