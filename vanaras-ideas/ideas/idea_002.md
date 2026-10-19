# Foreman — an AI back-office crew that lives on the owner's phone and runs the business while they're on the job
Lens: Small businesses under 20 people
## Customer & pain
Owner-operators of field-service and appointment businesses with 2-20 staff (HVAC, plumbers, electricians, cleaners, physio/dental/vet clinics, salons, repair shops). The owner is also dispatcher, bookkeeper and receptionist. Pain: missed calls while hands are busy (each lost job is $200-2,000), quotes sent days late, unpaid invoices chased never, evenings lost to admin. They cannot afford an office manager (~$45K/yr) and will not learn another SaaS dashboard. Owner pays, roughly $100-300/month.
## Product
One team of scoped vanaras on the owner's phone, cloud and office PC:
- Phone (Reception vanara): answers/returns missed calls and WhatsApp/SMS, books slots, texts customers "on my way", speaks to the owner by voice ("Two new jobs, one quote waiting, approve?").
- Cloud (Chaser + Scheduler vanaras): run 24/7 - quote follow-ups, invoice reminders on a schedule, rota changes, supplier re-orders - even when the phone is off.
- Desktop (Bookkeeper vanara): drives the legacy stuff with no API - QuickBooks/Xero/Tally desktop, supplier portals, the shop's old booking software - to enter invoices and reconcile.
Shared memory holds customers, price list, job history, and the owner's habits. Agent-to-agent sync: Reception logs a job, hands it to Scheduler, which hands the finished job to Bookkeeper, which hands the overdue invoice to Chaser. Spend and send rules (max discount, no refunds, quote cap) are enforced on-device; customer data goes to the model only as reference tokens.
## Wedge (first product, first 10 customers)
Missed-call-to-booked-job: a vanara that calls/texts back within 60 seconds, qualifies, and books into the owner's calendar, with owner approval by tap. Sell to one trade (e.g. independent HVAC/plumbing) via local trade groups, supplier counters and Facebook groups; price on a free 30-day trial with a "jobs booked" counter. First 10 come from founder's personal network plus 5 cold-visited local shops; run it white-glove.
## Enterprise path
Small firms grow to 20-200 staff; each technician and office person gets their own crew under owner-set rules (approvals, spend limits, tool access). Then multi-location franchises and MSPs/accountants reselling Foreman to their whole client book, which is the bridge to mid-market and full enterprise policy management.
## Business model & pricing
$99/month owner plan (Reception + Chaser), $199 with Desktop Bookkeeper, +$29 per extra staff crew. BYO model key optional at lower tier. Usage-based telephony passed through at cost plus margin. Channel: accountants/bookkeepers earn 20% revenue share. Target 30% gross-margin buffer on call minutes. Guess: ~4% monthly churn typical for SMB.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
SMB tail is high-touch and low-ACV for them; each trade needs its vertical rules, local phone/WhatsApp numbers and legacy-software glue. Horizontal assistants will not enforce per-owner spend and approval rules on-device or sit on a plumber's personal phone. Copilot/Gemini aim at Workspace/365 seats, not owners who run on WhatsApp and Tally.
## Biggest risk
Vertical incumbents (Jobber, ServiceTitan, Housecall Pro) and AI-receptionist startups (many exist, guess) bundle the same missed-call feature; and a wrong action toward a customer (bad quote, rude message) destroys trust. Also telephony/regulatory compliance (call recording, consent) varies by country.
## Uses founder's existing assets
Scoped vanaras with locked tools (Reception, Chaser, Bookkeeper), handover between agents, scheduled background jobs (invoice chasing), on-device approvals and spend rules, reference-token privacy, service-agnostic MCP pipeline (connects to whatever calendar/accounting the shop uses), voice interface, BYO model key. Cloud and desktop surfaces are new build.
## Scores
market_size: 8
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
