# Tether — a white-label agent layer that phone makers ship as the default "team" on mid-range Android
Lens: Vanaras as an OS / launcher for new phones (OEM deals)
## Customer & pain
Payer: second-tier Android OEMs (Nothing-class, Transsion-class, Motorola/HMD-class, regional brands) and their carrier partners. Google's Gemini and Samsung's Galaxy AI give flagship rivals a differentiated AI story; mid-range OEMs have only a rebranded chatbot app, and they cannot afford their own on-device agent stack. They need a reason for a buyer to pick their phone and a reason for users to stay.
## Product
A launcher-level agent layer (not a replacement OS). Phone: scoped vanaras (Messages, Calls, Reminders, Errands) on the home screen and lock screen, with approvals and spend rules enforced on-device. Cloud: the same team keeps projects going while the phone is off (a small cloud runner is the paid tier). Desktop: a companion that pairs to a laptop later. Shared memory is stored on the phone via reference tokens, so personal data never reaches the model provider; that is the privacy pitch OEMs can put on the box. Agent-to-agent handover lets a phone vanara pass a task to the cloud vanara (for example, "keep tracking this refund, ping me when it lands").
## Wedge (first product, first 10 customers)
Not OEMs first. Ship UNO as a launcher on the Play Store to prove retention and get on-device metrics. Then approach 10 small OEMs and carrier brands with a preload pilot: a 90-day trial on one mid-range SKU, with the BYO-key model (the OEM's choice of model provider) so the OEM takes no inference bill. Target the OEMs' software leads via trade shows (MWC) and ODM partners who assemble phones for them (guess: ODMs like Wingtech/Huaqin bundle software). The first 10 are likely design-win LOIs, not revenue.
## Enterprise path
The OEM channel doubles as a fleet channel: rugged and business phones sold to logistics, field-service and retail firms preload the layer with company rules (approved tools, spend caps, audit). Move from the phone team to the desktop and cloud team per employee under the company's policies.
## Business model & pricing
Per-device preload licence, roughly $0.50-$2 per activated device (guess), plus a $5-8/month cloud tier split with the OEM or carrier. Enterprise fleet: $10-20 per seat per month. Model tokens are billed through the user's own key or passed through at cost.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Google is locked into Gemini and needs OEMs to accept its terms, so it will not offer a neutral, model-agnostic layer. Apple is closed. Samsung protects its own stack. Neutral, model-agnostic, privacy-first is the gap for OEMs that fear dependence on Google. OpenAI and Anthropic sell models, not device software, and lack the per-OEM integration appetite.
## Biggest risk
OEM sales cycles are 12-18 months, and Google's GMS licence terms may discourage preloading a competing assistant slot (a guess to check). A solo founder with $30K cannot fund the long cycle unless the Play Store launcher proves demand alone.
## Uses founder's existing assets
All of UNO: the on-device approvals and spend enforcement, reference-token privacy layer, scoped agents and handover, scheduled background jobs, the MCP tool-role pipeline, voice, and BYO key. New work: launcher shell, OEM configuration and branding kit, a small cloud runner.
## Scores
market_size: 6
defensibility: 5
feasibility_solo_30k: 4
asset_fit: 8
excitement: 6
