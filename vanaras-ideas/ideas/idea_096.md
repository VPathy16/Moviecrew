# Vanaras Vault — a $199 always-on box that holds a small firm's client data, rules and agents, so AI never touches the raw files
Lens: hardware (a dedicated device or hub)
## Customer & pain
Owners of 3-30 person regulated practices (accountancies, immigration/law firms, dental and physio clinics, architects). They want AI agents on client work but cannot put client files in a chat app or a US cloud, and staff already paste them there ("shadow AI"). Their IT is an MSP or the owner's nephew. Today they either ban AI or accept the risk. Insurers and regulators are starting to ask for proof of control.
## Product
A small silent box (N100 mini-PC or Pi-class, pre-flashed, on the office desk) that acts as the firm's "kennel".
- Phone: each staff member's vanaras (UNO port) talk to the box, not the internet; approvals and spend rules pushed to the phone.
- Desktop: a light agent reads and writes local files and the practice software; it only ever sees reference tokens for client names, IDs and amounts.
- Cloud/24-7: the box runs scheduled jobs (chase missing documents, draft filings, reconcile) while laptops are off; only redacted prompts leave, with the firm's own model key.
- Shared memory lives on the box, encrypted, per-employee plus per-firm. Agent-to-agent handover (phone intake vanara to desktop drafting vanara) happens over the LAN, and the box keeps a tamper-evident audit log, the thing insurers want.
## Wedge (first product, first 10 customers)
Sell the "AI Use Control Box" to solo and small accountancy/immigration practices: install in 15 minutes, mobile app pairs by QR, ships with 3 vanaras (document chaser, deadline watcher, client-reply drafter). Reach the first 10 via 2-3 local professional associations and one MSP, at a hand-delivered pilot price. Hardware is off-the-shelf; the software also runs on a spare PC, so no hardware risk before demand is proven (about 20 units bought upfront, roughly $3K).
## Enterprise path
Fleet management for MSPs (one console, many client boxes), then per-branch boxes for larger firms and clinics chains, SSO, policy packs by regulation (GDPR, HIPAA, ICAI), and eventually a virtual-appliance tier for corporates that want the same control on their own servers.
## Business model & pricing
$199 box at about cost plus $29 per seat per month, including audit log and policy packs. MSP resale margin 25 percent. Model tokens are BYO key or passed through at cost. About 15 seats per firm gives roughly $5K ARR per customer (guess).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their business is cloud inference and their own model; a neutral, model-agnostic box that redacts before anything reaches them cuts against that. Copilot-style products are per-vendor and sell to large accounts through enterprise sales; a 10-person practice with a $199 box is too small and too fragmented for them.
## Biggest risk
Small firms may accept "good enough" cloud AI with a compliance checkbox, making the box a nice-to-have; second risk is support burden of physical devices on a solo founder.
## Uses founder's existing assets
Reference-token layer (personal data never reaches the AI), on-device approvals and spend rules, scoped vanaras and handover, scheduled background jobs, MCP tool-role classification (to connect practice software), voice, BYO model key. The Android app becomes the box's phone client.
## Scores
market_size: 6
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 8
excitement: 6
