# Locum — an AI vanara that runs your one-person business's back office while you're on the job
Lens: Wedge: a single killer vanara role first

## Customer & pain
Solo tradespeople and independent practitioners (electricians, HVAC, mobile vets, physios, photographers, tutors) in the US/UK/EU/India. They pay about $49/mo. They lose 5-10 hours a week and about 20% of inbound leads because they cannot answer calls or texts while working with their hands. Quotes go out late, invoices sit unchased, and no-shows are unmanaged. Receptionist services cost $300+/mo and know nothing about the business.

## Product
The killer role is "The Chaser": one vanara that owns every open loop between a job and its payment.
- Phone: answers missed calls and texts by voice or SMS, qualifies the lead, offers slots, and confirms. The owner approves or edits quotes from a lock-screen card.
- Cloud: runs 24/7 and chases unpaid invoices, sends reminders and review requests, and reorders recurring work. It keeps working while the phone is off.
- Desktop: later, it fills in the accounting or job software (QuickBooks, Jobber) that has no API, using computer use.
- Shared memory plus agent-to-agent sync: the phone vanara hears "customer wants a heat pump quote" and hands a structured job to the cloud vanara. That vanara drafts the quote from past prices, and the phone vanara asks the owner for a one-tap OK. The owner's price rules live on the device, and customer details reach the model only as reference tokens.

## Wedge (first product, first 10 customers)
Android app: missed-call text-back, then quote drafting, then invoice chasing. Bring-your-own model key keeps costs low. Find the first 10 through UNO's existing users and by visiting local trade forums and Facebook groups. Offer 30 days free, then a flat $39/mo. Success metric: money recovered per month, shown on the home screen.

## Enterprise path
Owners hire helpers, and the same setup becomes a "crew" of 3-50 people, each with their own vanara team under owner-set rules (spend limits, who can quote what). That leads to franchise and field-service SMBs. The sale is bottom-up, and vanara-per-employee licensing follows naturally, with admin policy, audit logs, and shared customer memory across staff.

## Business model & pricing
- Solo plan: $39/mo.
- Crew plan: $25 per seat per month, plus $10/mo per extra vanara role.
- Optional usage-based voice minutes.
- Target: 300 solo users reaching about $12K MRR in year one (guess).
- Later, payment-rail take rate (about 0.3%) on invoices chased.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants will not build vertical quote and invoice workflows for plumbers, or take on the liability of sending customer-facing messages and money requests. Small trade businesses are too fragmented and low-ACV for them to sell to. Device-enforced approvals and reference-token privacy are hard to bolt onto cloud-first assistants. Jobber, ServiceTitan, and Square may add AI, but they are tied to their own data silos and lack cross-surface agents.

## Biggest risk
Trust and reliability. One wrong quote or an abusive dunning message costs a customer relationship. There is also retention risk if field-service incumbents bundle "good enough" AI for free.

## Uses founder's existing assets
- Scoped vanaras with locked tools: separate lead, quote, and invoice roles.
- Handover between agents: phone to cloud to phone.
- Scheduled background jobs: invoice chasing and reminders.
- On-device approvals and spend rules: quote OK, refund and discount limits.
- Reference tokens: customer PII stays away from the model.
- MCP pipeline classified by tool role: plugs into QuickBooks, Stripe, Calendar, and Jobber.
- Voice and BYO key.
- New to build: telephony, a cloud runtime, and iOS.

## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 8
asset_fit: 9
excitement: 7
