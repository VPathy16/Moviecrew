# Kinfolk — a paid agent team for the family that coordinates an aging parent's care
Lens: Elder care and caregivers
## Customer & pain
The payer is the "sandwich-generation" adult child (40-60), often long-distance, or the siblings who split the load. Care is a second unpaid job: pharmacy refills, appointment booking and transport, insurer/Medicare-style paperwork, home-aide scheduling, bills, and "did Mom take her pills?" calls. Information sits in one sibling's head, WhatsApp threads and paper folders; nothing runs when the coordinator is at work or asleep.
## Product
- Phone: the caregiver's daily-life team (reminders, calls to clinics and pharmacies, errands). A lite phone surface for the parent: voice-first, one big button, agents phone or message them to confirm meds and appointments.
- Cloud: a standing "care case" project that works 24/7: chases refills, watches claims and bills, prepares the appointment brief, drafts appeals.
- Desktop: fills portals and forms, downloads statements, files reimbursements.
- Shared memory: one care record (meds, doctors, preferences, insurer IDs) that every sibling's team reads, with per-person permissions. A change made by one sibling's agent, such as a new dose, propagates to the others and to the parent's reminders. Agent-to-agent handover: the phone agent hears "dizzy since Tuesday", the cloud agent drafts a doctor note and books a slot, the desktop agent files the transport claim.
- Reference tokens keep health identifiers and account numbers out of the model. Spend rules cap what agents can pay without approval.
## Wedge (first product, first 10 customers)
Medication and appointment loop for one parent: voice check-ins on the parent's phone plus a shared sibling digest and refill chasing. Sell to 10 caregivers from local caregiver groups, Facebook/Reddit caregiver communities and an eldercare-focused geriatric care manager or two, who resell to their clients. Android first, using the existing UNO stack.
## Enterprise path
Employers pay for caregiver-support benefits (a large share of the workforce has caregiving duties; flag: my estimate). Sell through benefits platforms and the same per-employee-team model in the vision: each employee gets a care-coordination team under company policy, with the employer never seeing health data. Later: home-care agencies and geriatric care managers use it as their coordination layer.
## Business model & pricing
Consumer family plan of about $29/month per care recipient, with unlimited sibling seats (guess); BYO model key discount. B2B2C benefits at about $6-10 per employee per month. Care-manager/agency seats at $99+ per month.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Multi-party, multi-device care with permissions across siblings and a parent who is not a tech user is a niche with liability (health, consent, POA) that horizontal assistants avoid. Their agents are single-user; this needs a shared family record and on-device approval rules. Health-adjacent compliance and phone-call-to-clinic operations are unglamorous work.
## Biggest risk
Trust and safety: a missed or wrong medication reminder has real harm, and health-data regulation (HIPAA-adjacent, GDPR) can apply once you touch clinicians. Mitigate by starting with reminders and coordination only, never medical advice, and human-confirmed actions.
## Uses founder's existing assets
Scoped vanaras with locked tools (med agent vs finance agent), handover between agents, scheduled background jobs (daily check-ins, refill watchers), on-device approvals and spend rules, reference tokens keeping health data from the AI, voice, MCP pipeline for pharmacy/insurer/calendar tools, BYO key.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 8
