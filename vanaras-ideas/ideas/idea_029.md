# Keepwell — a privacy-first agent team for people whose work is confidential: their memory never leaves their hardware
Lens: Privacy-maximalists (on-device first)

## Customer & pain
Individuals and small firms bound by confidentiality: solo lawyers, therapists, investigative journalists, boutique M&A/wealth advisers, security researchers, clinicians. They are told to use AI but cannot paste client data into a cloud chatbot; bar rules, HIPAA and source protection forbid it. Today they either go without AI or use it in breach of policy. They pay for tools such as encrypted email and practice software and will pay for AI that is provably safe.

## Product
Vanaras where sensitive data never leaves the user's own devices, and the cloud sees only tokens.
- Phone: the daily-life team (calls, reminders, scheduling) runs UNO's reference-token model. The AI sees "CLIENT_7", never the name or number; the device resolves it at action time.
- Desktop: a local-model worker (open-weight model via Ollama or NPU) reads client files, drafts and redacts. Files stay on disk. Cloud models are used only on tokenised, redacted text, and only if the user allows.
- Cloud: 24/7 projects (deadline watch, research on public sources, monitoring filings) get only sanitised task specs, never raw client memory.
- Shared memory: an encrypted store, synced device-to-device with end-to-end keys; the cloud holds ciphertext only. Agent-to-agent handover carries tokens, so the phone agent can say "CLIENT_7 hearing moved" and the desktop agent resolves it locally.
- A signed, exportable audit log shows exactly what left each device. That log is the product's proof.

## Wedge (first product, first 10 customers)
"Redaction and reference-token gateway" for the Android phone plus a desktop companion: matter-aware scheduling, client-call summaries done locally, conflict-checked calendar. Sell first to solo lawyers and therapists via bar-association solo/small-firm groups and newsletters, and to journalists via press-freedom orgs. Target 10 paid pilots at $40 a month, with a plain-language "what left your device" report as the hook.

## Enterprise path
Firms with 5 to 50 professionals, then legal departments, hospitals and defence suppliers. Policy packs (approvals, spend and data-egress rules) enforced on-device, audit exports for compliance, and on-prem or VPC deployment for the shared-memory store. Per-seat team plus a compliance tier.

## Business model & pricing
Individual $30-60 a month; small firm $75 per seat; regulated enterprise $150+ per seat with audit and self-hosting. BYO model key or bundled local model. Guess: 5-8% of professionals in confidentiality-bound roles are reachable early adopters.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their business and architecture centre on cloud inference and cloud memory. Apple is closest on privacy but is a walled, single-vendor stack with limited cross-device agent orchestration. Vendors cannot credibly promise that memory never reaches them, and cross-vendor neutrality (any model, any MCP service) conflicts with their platform lock-in.

## Biggest risk
Local models on phones and laptops may be too weak for useful work, so the product feels crippled next to cloud AI. Tokenisation can also leak through context. Mitigation: narrow, high-value tasks first and independent security audit.

## Uses founder's existing assets
Reference-token layer (the core), on-device approvals and spend rules, scoped vanaras with locked tools, handover between agents, scheduled background jobs, service-agnostic MCP pipeline, BYO key, voice.

## Scores
market_size: 6
defensibility: 7
feasibility_solo_30k: 7
asset_fit: 10
excitement: 8
