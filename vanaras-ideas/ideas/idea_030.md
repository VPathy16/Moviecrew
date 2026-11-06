# Tresor Crew — an EU-resident AI team per employee, where personal data never leaves the country
Lens: Sovereign AI in the EU (data residency)
## Customer & pain
Buyers: CIOs/DPOs at 200-5,000 person EU firms in regulated sectors (public bodies, hospitals, law and notary firms, banks, defence suppliers, German Mittelstand). They are blocked from rolling out US-hosted agents (GDPR, Schrems II fears, NIS2, DORA, EU AI Act), so staff use shadow ChatGPT anyway. Sovereign LLM hosting exists (Mistral, Aleph Alpha, STACKIT, OVH), but no sovereign agent layer that acts on phones and desktops.
## Product
Each employee gets a team of scoped vanaras. Phone: calls, reminders, errands, approvals. Desktop: files, browser, apps via computer use. Cloud: long-running project agents in an EU-region tenant. Reference-token design means names, numbers and documents stay on the device or in the EU vault; the model only sees tokens, so even a non-EU model can be used without personal data leaking. Shared memory is stored EU-side, encrypted with customer-held keys. Agent-to-agent handoff (phone hears a client request, cloud drafts, desktop files it) is logged as an auditable trail, mapped to GDPR Art. 30 records and AI Act logging.
## Wedge (first product, first 10 customers)
Phone-and-desktop "Compliance-safe assistant" for one profession: small EU law/notary/tax firms (5-50 staff). Sold as a pilot at EUR 40 per seat per month. Works with BYO key to an EU-hosted model (Mistral, or Scaleway/STACKIT inference). First 10 customers from founder outreach to bar associations and Steuerberater networks in DE/NL/FR, plus one design partner offering a public reference. A data-flow diagram is the sales collateral.
## Enterprise path
Move from pilot to SSO/SCIM, admin policy console (spend and approval rules pushed to devices), customer-managed keys, on-prem/sovereign-cloud deployment on STACKIT, OVH, IONOS. Certifications: ISO 27001, then C5 (DE), SecNumCloud (FR) via a hosting partner. Public-sector procurement through framework partners and integrators.
## Business model & pricing
Per-seat SaaS EUR 35-60 per month, enterprise EUR 80+ with private deployment; annual contracts, plus paid implementation. Model inference passed through at cost or BYO. Sovereign-cloud marketplace listings as a channel.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They offer EU data boundaries, but the customer is still contractually exposed to US CLOUD Act jurisdiction, which is the exact objection. A US vendor cannot credibly sell "no US entity ever holds your data". The on-device tokenisation means even the model provider never sees personal data. Big tech also optimises for one surface and one ecosystem, not neutral cross-surface agents.
## Biggest risk
Sovereignty is a procurement checkbox that slows sales (12-24 month cycles), and the EU model providers may build their own agents (Mistral Le Chat with agents) and bundle them. Also, desktop computer-use quality is model-dependent.
## Uses founder's existing assets
Reference-token privacy layer (the core differentiator), on-device approvals and spend rules (become admin policy), scoped vanaras and handover (audit trail), MCP role-classifying pipeline (connect to EU SaaS such as DATEV, Personio, Nextcloud), scheduled jobs (cloud), BYO model key (EU model choice), voice. Android app is the phone surface; desktop and cloud are new builds.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
