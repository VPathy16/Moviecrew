# Sealed Desk — a per-caseworker AI team for public agencies that keeps citizen data on the device and every action approved and logged
Lens: Government and public sector
## Customer & pain
Payer: mid-size municipalities, county/district social-service and permitting offices, and small national agencies (start in EU/UK/US states/Australia). Caseworkers drown in forms, emails, resident calls and deadline tracking. Cloud AI is effectively banned: procurement, GDPR/data-residency rules, and fear of citizen data reaching a model vendor. So staff use shadow ChatGPT (a compliance incident) or nothing.
## Product
Each caseworker gets a small team of scoped vanaras. Phone: reminds on statutory deadlines, drafts resident call-backs and SMS, voice notes into case notes. Desktop: fills forms, moves data between legacy systems via computer use, prepares case files. Cloud: runs overnight queues (renewals, permit checks, backlog triage) with no device on. Shared memory holds case context as reference tokens: the model sees "APPLICANT_17, income band B", never the name or ID; real values are resolved only on the device or inside the agency's network. Agent-to-agent handover: intake agent -> eligibility agent -> letter agent, each with its own locked tool set. Approvals and spend/action rules are enforced on the device, and every step lands in an audit log an ombudsman can read.
## Wedge (first product, first 10 customers)
"Deadline & correspondence desk": one vanara that watches a caseworker's mailbox and case list, tracks statutory response deadlines, and drafts replies for approval, PII tokenised. Sell to 10 small councils/permitting offices via a paid 90-day pilot (~EUR 5K), using their own model endpoint (BYO key, e.g. a sovereign-hosted or Azure-region model). Target via civic-tech networks and procurement frameworks for pilots under the tender threshold (guess: many EU/US thresholds sit around 50-140K).
## Enterprise path
Same architecture is the enterprise product: per-employee teams under org policy. Government forces the hard parts first (audit, tokenisation, on-prem model, role rules), which then transfer to regulated industries: health insurers, banks, utilities, courts. Add central policy console, SSO, and certifications (ISO 27001, SOC 2, later FedRAMP/C5 via a partner).
## Business model & pricing
Per-seat annual licence, about EUR 40-60 per caseworker per month, plus a setup/integration fee for pilots. Model cost is passed through (BYO key or agency-hosted). Public-sector ACVs 20-150K; multi-year frameworks.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell horizontal assistants and rely on data reaching their cloud; per-agency tokenisation, on-device enforcement and model neutrality cut against their platforms. Government is slow, low-margin, bespoke per country. Microsoft Copilot is the real competitor, but it needs tenant data in Microsoft's cloud and broad permissions, which is what agencies distrust. Sovereignty-minded buyers want a non-hyperscaler layer.
## Biggest risk
Public-sector sales cycles, procurement and security questionnaires can outlast a solo founder's runway; one leak ends the company. Mitigate with small-pilot thresholds and a narrow read-mostly wedge.
## Uses founder's existing assets
Reference-token privacy layer (core pitch), on-device approvals and spend rules (audit and control), scoped vanaras with handover (workflow roles), scheduled background jobs (deadline watch, overnight queues), service-agnostic MCP pipeline (adapters to legacy case systems), BYO model key (sovereign model), voice (field workers). Android suits agency-managed devices.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 4
asset_fit: 9
excitement: 7
