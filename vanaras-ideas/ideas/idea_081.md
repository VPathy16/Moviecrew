# Troupe — the on-device agent team that mid-tier phone and laptop makers ship as their own AI
Lens: Partnership with a device maker
## Customer & pain
Payer: second-tier device makers (Nothing, HMD, Fairphone, Motorola-tier regional brands, rugged/enterprise handset makers, Chromebook/Android-laptop OEMs). Google's Gemini and Samsung/Apple AI crush them: they have no assistant story, no cloud budget, and a "privacy-first" pitch they cannot back with software. Their AI roadmap today is a rebadged Gemini plus a sticker. They need a differentiated, white-label, on-device-safe agent layer and a reason for carriers/enterprises to choose them.
## Product
Troupe ships as a system app/SDK the OEM brands as its own. On the phone: scoped vanaras (messages, calls, reminders, errands) with on-device approvals, spend rules and reference tokens, so personal data never reaches any model. In the cloud: the same team keeps projects moving while the device is off. On a paired laptop/desktop: a work vanara handles files and browser. Shared memory lives in an OEM-owned encrypted store (the OEM can say "your data is on your device and your account, not ours"); agent-to-agent sync hands a task from phone (an errand) to cloud (research) to desktop (produce a file) and back. BYO model key or OEM-chosen model, service-agnostic MCP pipeline so the OEM adds its own services (carrier, warranty, payments).
## Wedge (first product, first 10 customers)
Ship "Troupe for Android OEMs" as a preinstalled-quality app plus a launch kit (branding, default vanaras, OEM services as MCP tools), first sold as a paid pilot to 2-3 small brands and rugged/enterprise handset makers, who need a fleet story more than a chatbot. Meanwhile, run it as a Play Store app under the OEM's co-brand to prove retention. First 10: 3 OEM pilots, 7 carrier/enterprise fleet buyers reached through them. Guess: OEM sales cycles are 6-12 months; start with founders-led brands.
## Enterprise path
Rugged/enterprise handset makers bundle Troupe to fleets: each employee gets a team under company rules (approvals, spend caps, audit log enforced on-device). OEM MDM channel and carrier enterprise resellers give distribution without the founder building a sales force.
## Business model & pricing
Per-device licence ($1-3 per activated device, guess) plus NRE for integration ($30-100K per OEM), plus revenue share on paid cloud/desktop tiers ($5-15/user/month) and enterprise seats ($15-30/user/month).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Google will not white-label a neutral agent that lets OEMs own the relationship and memory; Gemini is Google's own funnel. Apple/Samsung serve only themselves. OpenAI/Anthropic are model vendors, not device-integrated, OEM-branded, on-device-policy products. Neutrality is the position: the OEM keeps the brand, the data and the customer.
## Biggest risk
OEM dependence: slow cycles, tiny volumes per OEM, and Google tightening Android policies (accessibility, background limits, preinstall agreements) or bundling Gemini as a mandatory GMS term.
## Uses founder's existing assets
Nearly all of UNO: scoped vanaras and handover, on-device approvals and spend rules, reference-token privacy, service-agnostic MCP classification (lets OEMs plug in their services), scheduled background jobs, voice, BYO key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 5
asset_fit: 9
excitement: 7
