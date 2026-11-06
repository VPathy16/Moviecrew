# Warrant — a portable identity, permission and approval layer for every AI agent an employee runs
Lens: Agent identity, permissions and approvals as the product

## Customer & pain
Buyer: head of IT/security or CISO at 200-5,000 person companies, where employees already run Claude, ChatGPT agents, Cursor, Copilot and browser agents. Today each agent inherits the employee's full OAuth token or a shared API key. Nobody can say which agent did what, on whose authority, or stop it. Spend limits, approvals and audit trails are rebuilt per vendor, or not at all. Auditors and cyber-insurers have started asking (guess).

## Product
Each employee gets a small team of scoped vanaras, each with its own identity, tool allow-list, spend cap and approval rules, instead of borrowing the human's credentials.
- Phone: approvals arrive as one-tap or voice prompts ("Cloud agent wants to pay $240 for a licence: approve?"). Enforcement runs on the device, as in UNO.
- Cloud: 24/7 project agents hold short-lived, scoped grants. They pause at approval gates and resume when the phone approves.
- Desktop: computer-use agents act only inside a declared scope (apps, folders, domains). Every click is logged against the agent identity.
- Shared memory holds one policy and one audit ledger across surfaces. Agent-to-agent handover carries a signed, narrowing delegation: an agent can pass on only a subset of its own rights. Reference tokens keep personal and company data away from the model.
Third-party agents (Claude, Cursor) connect through the MCP proxy, so Warrant governs them too.

## Wedge (first product, first 10 customers)
An MCP gateway plus phone approval app for individual developers and small teams: "give Claude Code or Cursor a scoped identity, a $ cap and phone approvals in 10 minutes." Free for individuals. The first 10 customers are 10 startups (20-100 people) reached through dev communities and the founder's network, paying for a shared audit log and policy templates.

## Enterprise path
Team plan, then SSO/SCIM (Okta, Entra), policy-as-code in git, SIEM export, SOC 2 report, per-department policy packs, an approver hierarchy (manager approves, finance for spend), and an on-prem or VPC gateway. Sell to security first, then IT, then finance for spend controls.

## Business model & pricing
$8 per employee per month for governed agent identities and the audit log. Usage-based add-on for approvals and spend-controlled payments. Enterprise around $20 per employee per month with SSO, retention and compliance exports. BYO model key means no inference cost for us.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor governs only its own agents, and no CISO wants the model vendor grading its own agents. A neutral, cross-vendor layer is structurally unattractive for them to build, in the way Okta was for Microsoft. Microsoft Entra Agent ID is the real threat inside Microsoft shops (guess), so the wedge targets mixed-vendor, non-Microsoft-only companies.

## Biggest risk
Platforms or the MCP spec absorb this as a feature, or the standards (OAuth extensions for agents) commoditise the identity piece before we have distribution. Mitigation: own the phone approval UX and the cross-surface memory, not the token format.

## Uses founder's existing assets
Scoped vanaras with locked tool sets, on-device approvals and spend rules, handover between agents, reference tokens (data never reaches the AI), the service-agnostic MCP pipeline that classifies tools by role (becomes the policy classifier), scheduled jobs, voice approvals, BYO key. Almost the whole UNO security core is the product.

## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 10
excitement: 8
