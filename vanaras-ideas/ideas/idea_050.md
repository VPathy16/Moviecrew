# Tether — a standing agent crew that keeps a business traveller's trip alive across phone, cloud and laptop
Lens: Travel for business travellers
## Customer & pain
Frequent business travellers (consultants, sales, field engineers, founders; 30+ trips a year) and the small firms that reimburse them. Pain is not booking; it is the mess around it: a cancelled flight at 11pm, a hotel that moved the room, a client meeting that shifts, an expense report assembled from 40 receipts, a visa or per-diem rule missed. Corporate TMCs (Concur, Navan) handle booking but not disruption and the daily long tail. Assistants who do this cost $60K+ a year.
## Product
A crew of scoped vanaras per traveller. Phone vanara: watches itinerary, flight status, and calendar; calls or messages airlines/hotels by voice on disruption; asks approval by tap before rebooking or spending. Cloud vanara: keeps working while the phone is off, e.g. monitoring fares for rebooking, chasing refunds and credit-card travel claims for weeks, filing tax-residency day counts. Desktop vanara: assembles the expense report from receipts, fills the company portal, updates the client deck's meeting logistics. Shared memory holds preferences, loyalty numbers, approved-spend rules, trip state. Agent-to-agent sync: when the phone vanara sees a delay, it hands to the cloud vanara to rebook and to the desktop one to move the calendar and email the client, all under on-device spend limits, with personal data as reference tokens so the model never sees passport or card numbers.
## Wedge (first product, first 10 customers)
"Disruption Rescue" for Android: forward confirmation emails, and the phone vanara handles delay/cancel events with rebook options and one-tap approval, plus receipts auto-collected into an expense pack. Sell $19/month to 10 consultants and sales reps found in LinkedIn and frequent-flyer communities; a 20-person consultancy is the first team pilot.
## Enterprise path
Company sets travel policy (fare caps, approved hotels, duty of care) once; every employee's crew enforces it on-device with an audit trail. Duty-of-care location alerts for the security team. Integrates with Concur/Navan/Expensify via MCP rather than replacing them. Sell to travel managers and finance ops per seat.
## Business model & pricing
Individual $19/mo (BYO model key lowers cost); team $39/seat/mo with policy console; enterprise $60+/seat with audit and SSO. Optional affiliate/refund-recovery fee (e.g. 10% of recovered claims) as a guess to test.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Assistants from the big players are horizontal and cloud-side; they will not accept liability for spending money or calling airlines, or hold per-company policy enforcement on the device. Travel is a messy long tail of suppliers, and none want to run supplier-by-supplier workflows. Microsoft owns Concur-adjacent territory but sells to procurement, not to the traveller's own pocket.
## Biggest risk
Trust and liability in rebooking with real money, plus supplier APIs being closed (airlines rarely expose rebooking); voice calling may hit reliability limits. Flagged guess: many disruption fixes may still require a human call.
## Uses founder's existing assets
Scoped vanaras with locked tools, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy, service-agnostic MCP pipeline (airline, hotel, calendar, email, expense tools), voice for calling suppliers, BYO model key. New: cloud and desktop surfaces, itinerary parsing.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
