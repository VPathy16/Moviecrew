# Tether — a per-employee agent team with policy enforced on the device, sold to CIOs as the agent control plane
Lens: Top-down sale to CIOs
## Customer & pain
The CIO, with the CISO co-signing, pays. Employees already run Copilot, Claude, ChatGPT and homemade agents on personal keys. IT cannot see what they touch, cap their spend, keep customer or HR data from model providers, or prove any of it to auditors. The options today are "ban it" (shadow AI persists) or "trust vendor logs" (not enforcement). Regulated firms (banks, insurers, pharma, EU public sector) are stalling rollouts for this reason.
## Product
Each employee gets a small team of scoped agents. Phone: calendar, messages, on-the-go approvals. Cloud: long-running project work 24/7 in a company-controlled tenant. Desktop: files, browser, apps. Shared memory is a per-employee, company-owned store with retention rules. Handover means a phone approval releases a cloud job that drives a desktop task. Policy is enforced at the device or runtime edge, below the model: per-agent tool allowlists, spend caps, approval rules, and reference tokens so the model never sees raw sensitive data. The CIO console offers role-based policy templates, the handover graph, spend per employee and exportable audit trails.
## Wedge (first product, first 10 customers)
Start with an Android and desktop "agent firewall": wrap existing MCP tools with role scoping, approvals, spend caps, tokenised data and audit export. Sell a 90-day paid pilot for 25 to 50 seats in one function (finance ops or support) at mid-size regulated companies. First 10 come from the founder's network, CISO/CIO communities, and EU/UK financial and public-sector firms under AI Act and DORA pressure. Guess: 30 to 40 percent of pilots convert.
## Enterprise path
25 seats, then a department (300), then the company (5,000+). Land via the CISO security review, expand via the CIO's AI programme. Requires SSO/SCIM, SOC 2 Type II, EU data residency, MDM deployment (Intune, Jamf) and a private-cloud option. Resell through MSPs and Big-4 AI-governance practices.
## Business model & pricing
Per-seat platform fee of about $30 to $50 per user per month (guess). Customers bring their own model keys or buy usage at cost plus margin. Pilots $15K to $30K flat. Add-ons: private cloud, longer audit retention, custom policy packs.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor governs its own agents, and a CIO will not let a model vendor grade its own homework. A neutral, cross-vendor layer enforcing below the model conflicts with their incentive to route data and usage to their own cloud. Microsoft (Entra Agent ID, Purview) is the closest threat but is strongest inside its own stack; the wedge is mixed-vendor and phone-first.
## Biggest risk
Governance gets bought as a feature: Microsoft or a security incumbent (Okta, Zscaler, CrowdStrike) ships "good enough" agent controls first, while long CIO sales cycles outlast the founder's runway.
## Uses founder's existing assets
Scoped, tool-locked vanaras; agent handover; on-device approvals and spend rules; reference tokens keeping personal data from the AI; the MCP pipeline that classifies tools by role (becomes policy templates); scheduled background jobs; voice; BYO model key.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 5
asset_fit: 9
excitement: 8
