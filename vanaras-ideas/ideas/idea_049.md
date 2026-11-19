# Ledgerkeeper — a scoped agent team that runs a household's or micro-business owner's bills, without ever seeing the numbers
Lens: Personal finance and bills
## Customer & pain
Self-employed people and 1-3 person businesses (freelancers, contractors, small clinics, Etsy/Shopify sellers) in the US/UK/EU/India who pay 20-60 recurring bills and invoices a month across cards, bank portals, utilities, SaaS and tax authorities. Pain: missed due dates, forgotten subscriptions, price hikes noticed late, receipts scattered across email/phone/desktop, and no trust in handing bank credentials to an AI.
## Product
Three scoped vanaras, each locked to its own tools. Phone "Bills" agent: reads bill emails/SMS/notifications, sets reminders, asks for approval by push or voice ("Pay $212 to the electricity company? Yes"). Cloud "Watcher" agent: runs 24/7 while the phone is off, checks due dates, detects price changes and duplicate charges, and disputes or cancels via email/MCP. Desktop "Books" agent: does the portal drudgery (downloads statements, files receipts, prepares quarterly tax packs) in the browser. Shared memory holds payees, cadence, and rules; handover: Watcher finds an unexpected charge, hands it to Bills for approval, then to Books for the receipt and ledger entry. Spend rules and approvals are enforced on the device; account numbers and amounts are reference tokens, so the model reasons over "PAYEE_7 / AMOUNT_3 vs usual" and never sees raw personal data.
## Wedge (first product, first 10 customers)
Subscription and bill watchdog on Android: connect email, get a weekly "what changed" digest and approval-gated pay/cancel actions. First 10: freelancers from the founder's network and r/personalfinance-style communities, and 3 bookkeepers who each bring 3 clients. Free 30-day pilot, manual onboarding.
## Enterprise path
Same team per employee for expense claims and corporate card hygiene: each employee's agents chase receipts, categorise, and submit within company policy, with finance setting spend rules that are enforced on-device. Sell to bookkeeping and accounting firms first (they manage many small clients), then SMB finance teams; the privacy-token architecture answers security review.
## Business model & pricing
BYO model key. $12/month individual, $29/month small business (unlimited approvals, tax packs), bookkeeper plan $8 per client seat. Enterprise $10-15 per employee per month plus policy console. Guess: 4% paid conversion from the free tier.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Liability: moving money and disputing charges on behalf of users is a regulated, support-heavy niche. Platform vendors will not build cross-bank, cross-country long-tail bill handling, and a "model never sees your data" guarantee conflicts with their cloud-first assistants. Apple and Google may add wallet-level features but not neutral, model-agnostic agents.
## Biggest risk
Access to payment rails and bank data: without open-banking coverage, screen-scraping portals via the desktop agent is brittle and legally grey; also a single wrongly paid or missed bill destroys trust.
## Uses founder's existing assets
Scoped agents with per-agent tools, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy layer, MCP tool-role classification (payments vs read-only), voice approvals, BYO key. New: cloud runner and desktop browser agent.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
