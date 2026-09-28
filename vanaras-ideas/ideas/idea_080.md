# Keelson — the on-device trust layer that lets a model lab's agents run on employees' phones, clouds and desktops
Lens: Partnership with a model lab (Anthropic/Mistral/OpenAI)
## Customer & pain
Payer: the model lab's enterprise sales org (indirectly the CIO/CISO of 1,000-50,000 seat companies, especially in EU, regulated finance, health, public sector). Pain: labs have strong models and cloud/desktop agents (Claude Code, Cowork, Codex), but no credible answer to "an agent on my employee's phone touches personal and customer data, spends money, calls people". CISOs block pilots because raw data reaches the model and approvals/spend limits are enforced server-side, where they can be bypassed. Mistral in particular sells sovereignty but has no mobile agent surface.
## Product
Vanaras as a lab-partnered "agent team runtime". Phone: scoped vanaras (each locked to its own tools) run daily-life and work errands; the model only sees reference tokens, never real contacts, numbers or files. Cloud: agents keep working projects 24/7 on the lab's cloud. Desktop: computer-use agent handles files/browser/apps. Shared memory lives on the employee's device (encrypted, synced) and is exposed to cloud/desktop agents as tokens; agent-to-agent handover is signed and policy-checked on device, so a cloud agent cannot escalate beyond the scope the phone vanara granted. Company admins push rules (spend caps, approval thresholds, tool roles) that are enforced locally and produce an audit log. Lab supplies the model; Keelson supplies the enforcement, memory and handover layer.
## Wedge (first product, first 10 customers)
Not enterprise first. Ship a reference "Claude/Mistral on Android with tokenised data" app (BYO key, existing UNO), publish a small open protocol spec for scoped-agent handover + reference tokens, and get one lab's applied-AI/partnerships team to list it as a design partner (Mistral is the most reachable for a solo non-US founder; flag: guess). First 10 customers are 10 design-partner teams (5-50 seats) in EU regulated firms introduced through the lab, paying a paid pilot of about 5-10K EUR each.
## Enterprise path
Pilot team -> department -> company via the lab's enterprise contract: Keelson appears as a certified component/marketplace item in the lab's enterprise plan. Add SSO/MDM (Android Enterprise, Intune), central policy console, SOC2/ISO 27001 (needed by year 2), on-prem/sovereign-cloud deployment for Mistral-style buyers.
## Business model & pricing
Two streams: (1) per-seat 8-15 USD/month for the trust layer, sold with or through the lab; (2) revenue share/OEM licence from the lab for embedding the runtime in its own mobile apps. Model tokens are billed by the lab, so Keelson has near-zero inference cost. Target 1,000 seats early = ~150K USD ARR.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Labs want to own model and distribution, not maintain a cross-vendor, cross-OS device enforcement layer; Google/Apple/Microsoft own OSes but are each rivals to the labs and to each other, so no lab trusts them as the neutral layer. Neutrality across labs is the moat: CISOs want one policy layer over any model. Labs may build it eventually; the bet is that partnering is faster and cheaper for them than building for Android/iOS/desktop.
## Biggest risk
Dependency and channel: a lab may decline, build in-house, or change its terms; a solo founder has weak leverage in partnership talks. Mitigation: stay multi-lab and BYO-key, so the product works without any lab's blessing.
## Uses founder's existing assets
Scoped vanaras with locked tools; handover between agents; on-device approvals and spend rules; reference-token privacy (personal data never reaches the AI); service-agnostic MCP pipeline with role classification; scheduled background jobs; voice; BYO model key. New: policy console, sync of memory, cloud/desktop adapters.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 8
