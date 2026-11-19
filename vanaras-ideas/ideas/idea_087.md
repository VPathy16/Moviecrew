# Leash — a scoped-permission and approval layer that lets a company's employees run AI agents without overstepping
Lens: Wedge: trust — agents that can't overstep (scopes + approvals)
## Customer & pain
Buyer: the security/IT lead (and CFO for spend) at a 100-2,000 person company where employees already run agents (Claude Cowork, Claude Code, browser agents, MCP tools). Today an agent inherits the employee's full login, so one prompt injection or bad guess can email a customer, move money or delete files. IT's only choices are "ban it" or "trust it". Audit trails are thin and approvals are ad hoc chat prompts.
## Product
Each employee gets a small team of vanaras, each locked to a role scope (e.g. "Inbox", "Repo", "Expenses") with only its own tools. Enforcement runs on the employee's device (phone and desktop), not in the model's prompt. Rules: per-tool allow/ask/deny, spend caps, recipient allowlists, time windows. Sensitive values are reference tokens, so the model never sees raw personal or customer data. The cloud vanara keeps working 24/7 but can only act inside its signed scope. Shared memory is scoped too: a vanara sees only the memory tagged for its role. Agent-to-agent handover carries a scope-narrowing token, so a handoff can never widen permissions. Approvals go to the employee's phone (tap, biometric) and escalate to a manager by policy. Every action goes into a tamper-evident log.
## Wedge (first product, first 10 customers)
Ship an MCP gateway plus Android/desktop approval app for Claude Code and Cowork users: "put your agent's tools behind Leash in 10 minutes". Free for individuals with BYO model key. Find the first 10 through dev-tool and security communities, plus small fintech, legal and agency teams that need auditability. Sell a $2K pilot: 20 seats, one policy pack, one audit export.
## Enterprise path
Policy packs (SOC2, HIPAA, finance segregation of duties), SSO/SCIM, admin console with central policy and per-employee overrides, SIEM export, on-prem or VPC relay. Security review becomes the moat: pass it once, and each new department is a policy pack.
## Business model & pricing
Free individual tier. Team $12/seat/month. Enterprise $30-50/seat/month plus a platform fee (~$20K/yr), plus usage-based charges for approval-routing and audit retention. (Guess: security tooling supports these price points.)
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor governs only its own agent and wants its own permissions model. Enterprises run several agents and models and want one neutral policy layer they control. Model vendors are conflicted: tighter limits make their agent look less capable. Neutrality across vendors is the position none of them can take.
## Biggest risk
Vendors ship good-enough native permission systems (MCP authorization, Cowork admin controls), squeezing the layer to a checkbox feature. Also, approval fatigue: too many prompts and users bypass it.
## Uses founder's existing assets
Nearly all of UNO: scoped vanaras with locked tool sets, handover between agents, on-device approvals and spend-rule enforcement, reference-token privacy, the role-classifying MCP pipeline (auto-suggests scopes for new tools), scheduled jobs, BYO model key, voice approvals ("approve the 400 dollar payment").
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 8
