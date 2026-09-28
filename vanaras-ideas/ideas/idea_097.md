# Tether — the on-device agent runtime that assistant apps embed instead of building their own
Lens: Contrarian: sell the backend to other assistant apps (white-label Vanaras)

## Customer & pain
Payers: companies shipping an assistant inside their own app (neobanks, telcos, health/insurance apps, super-apps, device OEMs, AI-companion startups, voice-assistant startups). They all hit the same wall: getting from "chat" to "does things" needs scoped tools, approvals, spend limits, privacy guarantees and background jobs. Each rebuilds this badly, and their security/legal teams block launch because the LLM sees personal data and one agent holds every tool. Pain: 6-12 months of agent-infrastructure work plus a compliance veto.

## Product
An SDK (Android first, then iOS/web) plus a cloud sync service. Host apps embed:
- Scoped agents ("vanaras"), each locked to its own tools, with handover between them.
- On-device approvals and spend rules the model cannot bypass.
- Reference tokens so personal data never reaches the model.
- A service-agnostic MCP pipeline that classifies tools by role.
- Scheduled background jobs, voice, and BYO or host model key.
Phone: the embedded agents run inside the host app. Cloud: the same agents keep running jobs while the device is off, via a policy-mirroring runner. Desktop: a thin agent lets the host's users' agents act on files and the browser. Shared memory plus agent-to-agent sync means a user's agents in App A and the host's other surfaces share one context store, encrypted and owned by the host. Handover works across surfaces, e.g. phone agent starts an errand, cloud agent finishes it overnight.

## Wedge (first product, first 10 customers)
Ship "Tether Guard": a drop-in Android module for approvals plus spend rules plus tokenised data, wrapping any existing LLM tool-calling loop. It is small, integrates in days, and answers a security-review blocker. Target the first 10 from small AI-assistant and companion apps, fintech/expense apps and voice-assistant startups. Reach them through founder outreach, open-sourcing the policy engine, and a sample app built on UNO. Pilot pricing gets design partners in cheaply.

## Enterprise path
Host apps become platforms. Big enterprises (banks, telcos) then embed Tether in their employee and customer apps. Add a policy console, audit log export, SSO and on-prem or VPC sync, SOC 2 and data-residency options. Every employee's team then runs under the company's rules, which is the Vanaras end state delivered through partners.

## Business model & pricing
Free open-source policy core. Paid SDK license: platform fee of $500-2,000/month for small apps, plus per active agent-user per month ($0.05-0.30) and per-background-job-hour cloud fees. Enterprise: annual contracts of $50-250K. (Numbers are guesses.)

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build their own assistants and OS-level agents; a neutral, model-agnostic runtime that lets rivals' apps keep their brand, data and BYO model is against their interest. Host apps do not want to give OS vendors their user relationship. Model vendors sell tokens, not embedded policy runtimes, though they may ship agent SDKs (flagged risk).

## Biggest risk
Platform-layer commoditisation: OS-level agent frameworks (Android/Apple intents-plus-agent APIs) or model-vendor agent SDKs could bundle "good enough" approvals and privacy, and B2B SDK sales cycles are slow for a solo founder.

## Uses founder's existing assets
Nearly all of UNO: scoped-agent engine and handover, on-device approvals and spend rules, reference-token privacy layer, MCP role-classifying pipeline, scheduler, voice, BYO key. UNO becomes the reference app. New work: SDK packaging, multi-tenant sync, docs.

## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
