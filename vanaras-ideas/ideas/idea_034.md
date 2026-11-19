# Tether — a handoff and sync layer that lets agents on phone, cloud and desktop pass work, memory and approvals to each other
Lens: Agent-to-agent protocol / sync layer sold to other agent builders

## Customer & pain
Payers are teams building agent products (startups, and enterprise platform teams) that now ship agents on more than one surface: a mobile app, a cloud worker, a desktop or browser agent. Today each surface has its own memory and its own auth, and they cannot hand work to each other. Builders hand-roll queues, state blobs and "resume" hacks. Result: an agent started on the phone cannot continue on the desktop, an approval given on one device is lost on another, and a cloud job that needs a human stalls silently. MCP standardised tool access and A2A standardised discovery and messaging, but neither gives durable cross-device handoff, scoped shared memory, or device-enforced approvals (guess: a gap that remains open in 2026).

## Product
An SDK (Kotlin, Swift, TypeScript, Python) plus a hosted relay. Core primitives:
- Handoff: a typed, resumable work item passed from agent A to agent B, across devices, with state, tool scope and deadline. Works when a device is offline (queued, delivered on wake).
- Shared memory: per-user or per-employee namespaced memory with per-agent read/write scopes. Sensitive fields are stored as reference tokens; only the owning device resolves them, so the relay and the model never see raw personal data.
- Approvals and spend rules: policy is defined once, enforced on the device that holds the user's authority; the cloud agent asks and the phone approves.
- Scheduled and background jobs with a shared job ledger.
In the Vanaras product, phone, cloud and desktop agents talk through Tether. Memory written by the phone agent is available to the desktop agent, and a cloud project agent pings the phone for approval.

## Wedge (first product, first 10 customers)
Open-source Android SDK plus a small relay: "give your mobile agent a cloud twin and phone approvals in an afternoon." Target indie and seed-stage agent builders on MCP communities, and companies building coding, sales or ops agents that need a human approval on a phone. Ship a free tier, get about 10 design partners through direct outreach and a public demo (phone approves a cloud coding agent's deploy). Vanaras itself is customer zero.

## Enterprise path
Sell to platform teams as the control plane for employee agent fleets: SSO/SCIM, audit log of every handoff and approval, data residency, self-hosted relay, policy packs. Every employee's team of agents syncs through the company's tenant, which is the same enterprise story as Vanaras.

## Business model & pricing
Open-source SDK (Apache 2.0), paid hosted relay. Free up to 1K handoffs/month; Team about $99 to $499/month usage-based (per active agent-pair and sync volume); Enterprise $50K+/year for self-host, audit and SSO. Guess: gross margin above 80 percent since it moves small messages.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each will build sync within its own stack (Microsoft across Copilot surfaces, Apple within its OS). A neutral layer across vendors' models, and across Android, iOS, Windows and Linux, conflicts with their lock-in incentives. Google's A2A spec is a protocol, not a hosted device-aware sync service; they may bless it as standard rather than operate it.

## Biggest risk
Protocol and infrastructure businesses need adoption before revenue; a big vendor could ship "good enough" handoff in its agent SDK, or A2A/MCP extensions could absorb the features. Solo founder cannot win a standards war.

## Uses founder's existing assets
Handover between agents, scheduled background jobs, on-device approvals and spend enforcement, reference-token privacy model, and the MCP tool-role pipeline are extracted from UNO into the SDK. The Android app becomes the reference client and customer zero.

## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
