# Keelhaul — self-hosted agent teams for regulated small firms, with a policy engine you own and can audit
Lens: Open-source, self-hosted Vanaras

## Customer & pain
Payer: small regulated professional firms (5-100 staff): law practices, accountancies, clinics, boutique wealth advisers, EU/UK/Indian/US mid-market. Their staff already paste client data into ChatGPT or Copilot. Compliance officers cannot approve that (GDPR, HIPAA, SRA, client confidentiality) and cannot audit what a cloud agent did. They want agents but need data to stay inside, with proof.

## Product
Open-source (Apache-2.0 core) Vanaras runtime the firm hosts on its own box or private VPC.
- Phone: each staffer's vanara handles calls, reminders, client messages. Reference tokens mean client PII never reaches the model, so a hosted model is usable.
- Cloud: a self-hosted worker runs matter/case projects 24/7 (deadline tracking, document chasing) on the firm's server.
- Desktop: a desktop agent handles files, browser and practice-management apps.
- Shared memory lives in the firm's own Postgres. Agent-to-agent sync is handover with signed, logged messages between surfaces.
- One policy file (approvals, spend caps, tool scopes, data classes) is enforced on-device and server-side, and the same file applies to every employee's team. Every action is written to an append-only audit log the compliance officer can export.
- BYO model key, or a local model for the most sensitive matters.

## Wedge (first product, first 10 customers)
"Audited Vanara" for one vertical, starting with UK/Indian solo-to-20 person law or accountancy firms. It is a phone plus a small self-hosted server, with a fixed template: deadline reminders, client chasers with approval, and a monthly audit report. Ten customers come from founder-led outreach via bar and accountancy forums, plus open-source GitHub traction. A paid setup of $500-1,500 covers onboarding and installs.

## Enterprise path
Open core. The same runtime scales to per-employee teams: SSO/SCIM, central policy distribution, fleet audit, and air-gapped deployments for banks and hospitals. Sell to the CISO or compliance head as "agents you can prove things about". Certifications (SOC 2 for the managed option, ISO 27001) come later, funded by revenue.

## Business model & pricing
Free core. Paid Team edition at $15-25 per seat per month (policy management, audit exports, SSO). Managed hosting at $40 per seat. Enterprise contracts at $60k+ per year with support and compliance packs. Services for setup are an early cash source.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their agents run on their clouds, and their business is hosted inference and lock-in. A neutral, model-agnostic runtime the customer owns cuts against that. Microsoft does offer compliance tooling but only inside its own stack. Open source removes the trust objection they cannot answer. Expect them to ship "enterprise controls", so the moat is neutrality and self-hosting.

## Biggest risk
Self-hosting burden: small firms have no IT staff, so installs and upgrades could eat the founder's time. Also, open source may give away the product with few paying seats (guess: 2-5% conversion).

## Uses founder's existing assets
- Scoped vanaras with locked tool sets: become the policy unit.
- On-device approvals and spend rules: the enforcement layer, extended to the server.
- Reference-token privacy: the key selling point for regulated data.
- MCP role-classification pipeline: connects practice-management and document tools.
- Handover, scheduled jobs, voice, BYO key: reused directly.

## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
