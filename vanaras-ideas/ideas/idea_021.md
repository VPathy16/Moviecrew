# Shiftmate — a pocket team of scoped agents that runs the paperwork, handoffs and follow-ups of a frontline shift
Lens: Frontline workers (retail, logistics, field service)

## Customer & pain
Payer: operations heads at field-service companies (HVAC, elevator, telecom install, utilities contractors) with 50-500 technicians. Their techs live on a phone, not a desktop. Pain today: job notes typed with thumbs at 8pm or never, parts and warranty claims filed late, customer follow-ups missed, shift handoffs by WhatsApp voice note, and back-office staff chasing techs for data. Existing FSM tools (ServiceTitan, Jobber, Salesforce Field Service) are forms the worker must feed; they do not act for the worker.

## Product
Phone (core surface): each tech gets a small team of vanaras, each locked to its own tools. A "Job" vanara listens to a voice debrief after each visit and drafts the report. A "Parts" vanara raises the parts and warranty request. A "Customer" vanara sends the follow-up and books the revisit. A "Shift" vanara summarises the day and hands open items to the next tech. Approvals and spend limits are enforced on the device (e.g. parts under $200 auto-approved, above needs the supervisor's tap). Customer data stays as reference tokens, so the model never sees names or addresses.
Cloud: agents keep working after the tech clocks out: chase supplier ETAs, reconcile invoices, escalate stalled jobs, and run scheduled jobs overnight.
Desktop: the dispatcher's vanara works in the FSM/ERP browser UI (no API needed), entering what the techs' vanaras produced.
Shared memory + agent-to-agent sync: a tech's "Parts" vanara tells the dispatcher's vanara a part is delayed, which reschedules the next visit and notifies the customer vanara, with no human relaying it. Site history (this boiler's quirks) persists across techs.

## Wedge (first product, first 10 customers)
Voice-to-job-report plus auto follow-up on Android (rugged-phone-heavy trades are mostly Android), sold to 10 small HVAC, plumbing, or solar-install firms of 20-60 techs, found via trade groups and LinkedIn. Price it as a pilot per tech; success metric is hours of admin saved per tech per week and days-to-invoice. Founder's UNO build means it is largely ready as an Android app.

## Enterprise path
Per-employee teams under company rules: admin console for spend and approval policy, allowed-tool lists per role, audit log, SSO, BYO model key or company-hosted model, on-device tokenisation for data-residency and works-council comfort. Then integrations with ServiceTitan, SAP Field Service, and Dynamics via the MCP pipeline. Expand from techs to warehouse pickers and retail store staff.

## Business model & pricing
Per-worker per-month: ~$25 for the tech team, ~$60 for dispatcher/supervisor seats with desktop agent. 100 techs is roughly $30K ARR per customer. Usage-based overage for cloud agent hours (guess). Model cost via BYO key or pass-through at margin.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Frontline is low-ARPU, fragmented and vertical-specific, with messy rugged Android fleets and per-trade workflows. Microsoft sells Copilot to desk workers and has Dynamics FSM, but its agents are horizontal and cloud-first. Nobody is building on-device approval enforcement and scoped agents for a worker who never opens a laptop. Model vendors sell the models, not the trade-specific handoff logic.

## Biggest risk
Buyers want it inside their existing FSM system; ServiceTitan or a Salesforce bundle could ship "voice notes to report" and squeeze the wedge. Also field-service sales cycles and fleet device management (MDM) can be slow.

## Uses founder's existing assets
Scoped per-agent tools, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy, MCP tool-role pipeline (for FSM integrations), voice input, BYO model key. Needed new: multi-user shared memory, cloud runtime, admin console, desktop agent.

## Scores
market_size: 8
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
