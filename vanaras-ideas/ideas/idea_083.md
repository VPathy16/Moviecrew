# Leash — the on-device permission and privacy layer that lets any AI agent act on a phone without seeing personal data
Lens: Acquisition target positioning (build to be bought)
## Customer & pain
Payers: (1) agent/app builders (startups shipping phone or desktop agents) who cannot get enterprise or app-store approval because agents hold broad tool access and see raw personal data; (2) later, CISOs who must let employees run agents on BYOD phones. Today each builder hand-rolls approvals, spend caps and redaction, badly. Phone OS makers and model labs face the same unsolved problem: agents acting for users need scoped, auditable, revocable authority.
## Product
An SDK plus runtime: Leash sits between any model and any tool (MCP). Each agent ("vanara") is locked to a role-scoped tool set; personal data is swapped for reference tokens so the model never sees it; approvals and spend rules are enforced on-device, not by the model. Phone runtime is UNO's engine, extracted. Cloud agents and desktop agents (Cowork-style) call the same policy engine through a signed policy bundle, so one rulebook governs all three surfaces. Shared memory is stored as tokenised references, so a cloud agent can hand work to the phone agent ("book it, needs your approval") without the cloud ever holding raw data. Agent-to-agent handover carries the permission scope, which can only narrow, never widen.
## Wedge (first product, first 10 customers)
Open-source Android library plus a hosted policy console: "add safe approvals and spend limits to your agent in an afternoon". Target 10 seed-stage agent startups and MCP-tool vendors via the MCP community, GitHub and a public "agent safety benchmark" of prompt-injection attacks that Leash blocks. Free tier, paid audit log and policy sync. UNO itself is reference app number one.
## Enterprise path
Policy console becomes an admin plane: per-employee agent teams under company rules, SSO, audit export, device attestation, data-residency. Sold to security teams as "agent MDM". The same rulebook then covers phone, cloud and desktop agents.
## Business model & pricing
Free SDK; $0.50-$2 per active agent-device per month for sync and audit; enterprise $8-15 per seat per month. Real goal is a strategic exit: acquirers buy the team, standard and installed base, not revenue. Target 2-3 years, tens of thousands of devices, a recognised open spec.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They will build first-party versions for their own agents, but each is locked to its own model and OS. Neutral, model-agnostic, cross-OS enforcement is what an enterprise with mixed agents wants, and no single vendor can credibly offer it. That gap is also why they buy: acquiring a neutral standard with adoption is faster than building trust in one. (Guess: Google, Microsoft and Anthropic are most plausible acquirers; Apple unlikely.)
## Biggest risk
An OS-level permission model (Android or iOS agent APIs) ships and makes the layer redundant before adoption. Mitigation: be the reference implementation, contribute to the spec, stay compatible.
## Uses founder's existing assets
Scoped-tool vanaras, handover between agents, on-device approvals and spend rules, reference-token privacy, MCP tool role classification, scheduled jobs, BYO key (proves model neutrality). Voice and UNO app become demo and dogfood.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
