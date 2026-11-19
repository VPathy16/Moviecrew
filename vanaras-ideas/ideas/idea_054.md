# Tally Crew — a per-employee agent team whose every action leaves audit-grade evidence for compliance teams
Lens: Compliance and audit teams

## Customer & pain
The Head of Compliance / Internal Audit at a regulated mid-size company (fintech, healthcare services, insurance brokers, 200-5,000 staff) pays. Employees already use AI agents (Copilot, ChatGPT, Claude, browser agents). Compliance cannot answer: what did the agent do, with whose data, who approved it? Today they either ban agents (shadow AI follows) or accept unlogged risk. Auditors (SOC 2, ISO 42001, EU AI Act, DORA) now ask for AI-action evidence and get screenshots and guesses.

## Product
Every employee gets a team of scoped vanaras, each locked to its own tools, and every action is written to a tamper-evident ledger.
- Phone: approvals, voice sign-off, and reminders for evidence gaps. A vanara asks "approve sending this filing?" and the approval is logged with device attestation.
- Desktop: a vanara handles files, browser and apps within a scoped tool set, and records action, tool, policy applied, and reference tokens instead of raw personal data.
- Cloud: a continuous-controls vanara runs 24/7, collecting evidence, checking spend and approval rules, and drafting audit packs.
- Shared memory plus agent-to-agent sync: handover between vanaras is itself an audited event. The auditor sees one chain: who asked, which vanara acted, which handover, which approval. The AI model only sees reference tokens, so the audit log can prove that personal data never reached the model.
Compliance teams write policy once (approval thresholds, spend caps, tool roles); the device enforces it.

## Wedge (first product, first 10 customers)
"Agent Evidence Pack": a phone-first approvals-and-ledger app for a compliance officer's own team of 5-15 people, with a monthly exportable audit report mapped to SOC 2 / ISO 42001 controls. Target: fintech and healthtech startups mid-audit, reached via vCISO firms and audit consultants (who resell). Ten customers come from 3-4 vCISO partners. Price per pilot is small; goal is the reference logo.

## Enterprise path
Pilot in the compliance team, then extend to finance and ops, then all employees. Add SSO/SCIM, policy packs per regulation, SIEM export, an auditor read-only portal, and on-prem or VPC key custody. Sell through Big-4-adjacent auditors and GRC platform integrations (Vanta/Drata-style, flagged as guess).

## Business model & pricing
Per-seat $30-60/month, plus a compliance tier ($15K-60K/year) with policy packs, the auditor portal, and evidence retention. BYO model key keeps COGS low. Services attach for control mapping.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Model vendors will not be neutral across each other's agents, and auditors want an independent witness, not the vendor grading itself. Enforcement on the device with model-blind reference tokens is architectural, not a feature toggle. Microsoft Purview will cover Copilot only; buyers run mixed agents (guess).

## Biggest risk
Audit frameworks for AI actions may standardize slowly or be absorbed by existing GRC vendors, and buyers may treat this as a feature. Also, trust: a solo vendor selling to compliance must itself be certified (SOC 2 costs money and time).

## Uses founder's existing assets
Scoped per-tool vanaras, on-device approvals and spend rules, reference-token privacy layer, handover between agents, scheduled background jobs (evidence collection), MCP tool-role classification (feeds policy mapping), voice approvals, BYO key. New: ledger hashing, report export, desktop and cloud surfaces.

## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
