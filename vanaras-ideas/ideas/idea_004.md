# Tether — a compliance-locked agent team for every regulated-industry employee, with policy enforced on the device
Lens: Large enterprises with strict compliance
## Customer & pain
Buyer: CISO / Head of Compliance at banks, insurers, pharma, and law and audit firms (5,000+ staff). Today they either ban AI assistants (shadow AI leaks anyway) or buy a chat tool that sends employee data to a model vendor. Agents that act (send, approve, spend, move files) are the hardest to approve: nobody can prove what an agent may touch, or reconstruct what it did.
## Product
Each employee gets a small team of scoped vanaras. On phone: approvals, calls, reminders and mobile triage. In the cloud: long-running case or matter work that continues overnight. On desktop: files, browser and internal apps. Each vanara is locked to its own tools. Handover between agents is an explicit, logged event. Shared memory holds work context, and sensitive fields are reference tokens the model never sees; they resolve only on the device or in the tenant boundary. The compliance officer writes one policy (spend limits, approval chains, data classes, allowed MCP tools by role), and it is enforced at the client, not by asking the model to behave. Agent-to-agent sync yields a tamper-evident action ledger, exportable to the SIEM and to auditors. The customer brings its own model key or a private deployment.
## Wedge (first product, first 10 customers)
Start with one workflow: "approvals and follow-ups agent" for compliance and operations staff at small regulated firms (boutique law, wealth managers, and CROs of 200 to 2,000 people). Ship an Android and desktop pilot with the ledger and policy pack, priced as a 90-day paid pilot. Target ten firms through founder network and compliance-consultant referrals, since consultants recommend tools that make audits easier.
## Enterprise path
Pilot with 20 to 50 seats, then SOC 2 Type II, a data-processing agreement, SSO/SCIM and MDM (Intune, Jamf) deployment, then a private-cloud or VPC agent runner. After that come ISO 27001, DORA/EU AI Act evidence packs, and per-region data residency. Expand by department, one policy template per role.
## Business model & pricing
Per-seat $40 to 80 per month with a platform minimum of $2K per month, plus a paid policy-pack and audit-export tier. BYO model key keeps inference off our margin. Services for policy design at the start (flag: a guess).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell horizontal assistants tied to their own model and cloud, with policy inside their own tenancy. Regulated firms distrust single-vendor lock-in and want model-agnostic, on-device enforcement across every MCP tool. A neutral control layer is not their business, and it means fewer of their own tokens.
## Biggest risk
Enterprise sales cycles and security review outlast a solo founder's $30K runway, and Microsoft's agent governance (Copilot, Entra agent IDs) could reach "good enough" bundled into existing licenses.
## Uses founder's existing assets
Reuses nearly all of UNO's core: scoped vanaras with tool locks, handover, on-device approval and spend rules, reference-token privacy, the MCP pipeline classifying tools by role, scheduled jobs, voice and BYO key. New work: the policy console, the ledger, the desktop and cloud runners, and SSO.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 4
asset_fit: 9
excitement: 7
