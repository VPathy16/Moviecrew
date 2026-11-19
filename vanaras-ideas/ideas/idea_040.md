# Tether — a desktop agent for accountants and bookkeepers that does the month-end grind and stays inside the rules
Lens: Desktop-first (Windows/Mac) entry, phone later
## Customer & pain
Small accounting and bookkeeping firms (3-30 staff) in the US/UK/AU. Each month-end, staff spend hours in browsers and desktop apps (QuickBooks Desktop, Xero, bank portals, Excel, client email) chasing documents, reconciling, and re-keying. Cowork-style agents can do it, but firms will not hand client financial data and bank logins to a cloud model, and partners fear an agent that "just clicks".
## Product
Desktop (Windows/Mac) app: scoped vanaras, each locked to its own tools: Chaser (client email and document requests), Reconciler (Excel and ledger app), Filer (portal downloads, statements). Client data and credentials are referenced by tokens, so the model never sees account numbers or logins. Approvals and spend/action rules are enforced on the device: e.g. "never submit, only draft", "read-only on bank portals". Handover: Chaser gets the statement, hands to Reconciler, which hands exceptions to the human. Shared memory holds per-client quirks ("Client X codes fuel as Travel"). Later: the cloud vanara runs scheduled month-end jobs overnight on a hosted VM; the phone vanara pings the partner for approvals and takes voice notes ("chase Acme for March invoices").
## Wedge (first product, first 10 customers)
First product: "Month-end Chaser", a desktop agent that sends document requests, matches replies to a checklist, and files them into the client folder, with an audit log. Sell to 10 solo/small practices via bookkeeping communities (accountant Facebook groups, QuickBooks ProAdvisor forums, Xero meetups), 30-day paid pilot at low price, founder-led onboarding.
## Enterprise path
Firm-wide policy console (which agents, which apps, which approvals), per-staff teams with shared client memory, SSO, audit export for professional-liability insurers. Then expand to mid-size firms, in-house finance teams and other regulated back offices (legal, insurance brokers) using the same policy engine.
## Business model & pricing
Per-seat SaaS, about $59/staff/month (BYO model key optional, cheaper); firm tier $500-2,000/month with policy console and audit. Cloud runs metered on top.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal agents; per-profession rules, client-level memory and on-device approval semantics are a slow, unglamorous vertical. Accountants' distrust of cloud data exposure favours a local, token-based design that a general agent vendor has little reason to build. (Guess: they may ship enterprise controls later, but not vertical workflows.)
## Biggest risk
Desktop automation reliability across many finance apps and portals (UI changes, MFA, captchas), and sales cycles in a conservative profession. Also the risk that Cowork/computer-use quality improves so fast that the vertical layer looks thin.
## Uses founder's existing assets
Scoped agents with locked tools, handover between agents, on-device approvals and spend rules, reference-token privacy layer, MCP pipeline classifying tools by role, scheduled background jobs, voice (phone later), BYO key. New work: Windows/Mac shell, computer-use adapter, and accounting connectors.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 7
excitement: 7
