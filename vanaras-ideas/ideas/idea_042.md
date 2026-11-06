# Brokerhand — a compliant AI crew in the pocket of every independent insurance and mortgage broker
Lens: Phone-first entry leveraging existing UNO
## Customer & pain
Solo and small-shop insurance, mortgage and loan brokers (1-5 people). They live on their phone: client WhatsApp/SMS/calls, document chasing, renewal reminders, and re-keying the same client data into carrier and lender portals. They lose deals to slow follow-up, and they are barred or nervous about pasting client PII (IDs, incomes, health data) into ChatGPT. The broker pays; a single extra closed policy or loan per month covers the subscription.
## Product
- Phone vanara (UNO core): chases clients for missing documents, sends renewal and payment reminders, drafts replies, takes call notes by voice. Client PII is held as reference tokens on the device, so the model never sees it.
- Cloud vanara: runs overnight. It compares quotes, builds the submission pack, monitors renewal calendars, and tracks each application's status.
- Desktop vanara: fills carrier and lender portals from the tokenised client file. It has its own scoped tools and approval gates, and every submission needs a tap from the broker.
- Shared memory holds a client file: what was promised, what is missing, and which consents exist. Handover moves work between vanaras: the phone agent gets the documents, the cloud agent packs them, the desktop agent submits them, and the phone agent tells the client. Approvals and spend rules are enforced on the device, which produces an audit trail regulators like.
## Wedge (first product, first 10 customers)
Renewal and document-chasing bot on Android that works over the broker's own WhatsApp/SMS. Price is $39/month. Find the first 10 through broker associations, local broker WhatsApp groups and LinkedIn, in one country and one product line (for example motor and health insurance, or home loans). Success metric: renewals retained, and days from documents requested to documents received.
## Enterprise path
Brokerage networks and aggregators (50-2,000 agents) buy a managed tier. It has central policy (which portals, which data classes, approval thresholds), per-agent audit export, a compliance officer console, and integration with an agency management system. Each broker keeps their own team while the firm sets the rules, which is the Vanaras enterprise model in a small vertical.
## Business model & pricing
$39/month for the phone crew, $99/month with cloud and desktop vanaras. Network tier: $60-120 per seat per month plus onboarding. Model usage is BYO key at the start and bundled later. The target is about 80% gross margin at ~$15 model cost per seat.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
General assistants will not build per-jurisdiction broker compliance workflows, portal automations and audit trails for a small niche. Their cloud-first designs also fail on the promise that client PII never reaches the model. Vertical depth, carrier-portal know-how and broker distribution are the moat, not the model.
## Biggest risk
Portal automation breaks often (carriers change UIs, add CAPTCHAs or ban bots), and regulators may not accept an AI sending client messages. Mitigation: keep the wedge on messaging and reminders, keep humans on submission, and use official APIs where they exist. (Guess: broker WhatsApp usage is high in India, UK and Australia; verify.)
## Uses founder's existing assets
Reused from UNO: scoped vanaras with locked toolsets, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy, the MCP pipeline (for CRM, calendar and email), voice for call notes, and BYO model key. New work: broker templates, consent tracking, compliance export.
## Scores
market_size: 6
defensibility: 6
feasibility_solo_30k: 8
asset_fit: 9
excitement: 7
