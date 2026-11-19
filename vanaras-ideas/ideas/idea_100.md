# Leash — the phone-held authority layer that lets any AI agent act for you, within limits you set
Lens: Wild card (strongest idea, ignoring lenses)
## Customer & pain
Individuals and small teams running long-lived agents (cloud coding agents, desktop computer-use agents, MCP tools) who are afraid to give them real authority. Today it is all-or-nothing: paste an API key and hope, or babysit every prompt. Later, the CISO/CFO who must let 500 employees' agents touch email, repos, SaaS and cards, and has no per-agent identity, spend cap, or audit trail that spans vendors.
## Product
Leash is a vendor-neutral control plane where the phone is the root of trust.
- Phone: holds the policy (per-agent scopes, spend caps, allowed tools, time windows) and is where approvals land (biometric tap, voice "approve"). Enforcement of approval and spend rules runs on-device, as UNO does today.
- Cloud: a thin MCP gateway. Cloud agents (Claude Code on the web, others) connect to Leash instead of directly to tools; each call is checked against policy and either passes, is blocked, or waits for a phone approval. Agents keep working 24/7; only risky steps wake the human.
- Desktop: a small local proxy wraps computer-use and file/browser agents with the same scopes and approval hooks.
- Shared memory + agent-to-agent sync: one ledger of who (which agent, on whose behalf) did what, spent what, was denied what. Handover between agents carries a narrowed, expiring grant (a child agent never gets more authority than its parent). Personal data is passed as reference tokens, so the model provider never sees raw secrets.
## Wedge (first product, first 10 customers)
"Approvals and spend caps for your coding agent": an MCP gateway plus Android app. Point Claude Code or any MCP client at it; get push approvals for deploys, purchases, and destructive commands, and a hard daily spend cap. Target 10 heavy solo agent users and indie founders found via agent communities; free for early users, private beta with weekly feedback. Buildable solo in ~3 months from the existing UNO approval/spend/MCP-role code.
## Enterprise path
Team policies, SSO, and per-employee agent identities; central policy pushed to phones and gateways; audit export to SIEM; SOC 2 later. Sell to security/finance as "agent IAM plus corporate card controls for agents". Each employee's team of vanaras sits under company rules, which is exactly the stated vision.
## Business model & pricing
Free: one agent, basic caps. Pro $12/month: unlimited agents, spend rules, audit history. Team $15 per seat/month with central policy. Enterprise $40+ per seat/year-contract with audit/SIEM, on-prem gateway. Optional small fee on brokered agent payments (guess: 0.5 to 1%).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor will ship guardrails for its own agents only. Customers run mixed agents and need one neutral authority and one audit log; no vendor will police a competitor's agent. Apple/Google own the device but not agent semantics. Neutrality is the moat, and it is the same reason Okta survived Microsoft.
## Biggest risk
Big vendors' native permission systems become "good enough" and the standard (MCP auth, agent identity specs) absorbs the gateway, leaving no room for a separate product. Also cold start: value depends on agents actually routing through Leash.
## Uses founder's existing assets
Device-side approvals and spend rules (core), scoped agents locked to their own tools (policy model), handover between agents (narrowing grants), service-agnostic MCP pipeline classifying tools by role (risk tiers for the gateway), reference tokens (privacy), scheduled background jobs, voice approvals, BYO key.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 8
asset_fit: 10
excitement: 8
