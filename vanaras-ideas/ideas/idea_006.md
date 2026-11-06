# Locum — a small AI care team for every independent clinician, that never lets patient data reach the model
Lens: Healthcare clinics and doctors
## Customer & pain
Owner-doctors and small clinics (1-10 clinicians: GPs, physios, dentists, therapists, dermatologists) pay. They lose 1-2 hours a day to admin: recalls, no-show chasing, referral letters, prior-auth/insurer paperwork, follow-up calls, inbox triage. Ambient scribes exist, but nothing runs the practice's day. Cloud AI is blocked by privacy fear (HIPAA/GDPR/DPDP), so staff paste PHI into chatbots covertly or use nothing.
## Product
Per-clinician team of scoped vanaras. Phone: a Front-desk vanara handles patient messages and calls, reminders and reschedules, and briefs the doctor between patients by voice. Cloud: a Recall/Referral vanara works 24/7 through waitlists, overdue-screening lists and insurer follow-ups, and drafts letters overnight. Desktop: a Records vanara operates the legacy EMR/practice-management app and the insurer portals (computer use) where no API exists. Shared memory holds the care-team context (who is overdue, what the doctor prefers, what was promised to whom); handovers are explicit, e.g. Front-desk to Records to Billing. Patient identifiers are reference tokens: the model plans with "Patient#T41", and the device or clinic-side runtime resolves them only at the tool boundary. Approvals and spend rules: nothing clinical goes out without the doctor's tap; scheduling and reminders are pre-approved.
## Wedge (first product, first 10 customers)
Recall and no-show vanara for solo private practices (physio, dental, dermatology): connects to the calendar plus WhatsApp/SMS and phone, refills empty slots, and reports slots recovered. It needs no EMR integration and can be sold in a week. Find the first 10 through founder-run pilots with clinician friends and specialty Facebook/WhatsApp groups, in one non-Indian market (UK or US independent physio) plus one local for proof. Success metric: recovered revenue per month.
## Enterprise path
Small clinic to multi-site group to clinic network or hospital department. Every clinician and staff member gets a team under the group's policy: central approval rules, audit log of every agent action, tokenisation guarantee as a procurement document, BYO model key or private endpoint. Sell the audit trail and PHI-never-leaves guarantee to compliance officers and DPOs, then add EMR connectors as paid integrations.
## Business model & pricing
Per clinician per month: $99 wedge, $249 full team; groups get volume tiers plus a compliance/audit add-on. Optional usage fees for voice minutes. Guess: a clinic recovering 6 slots/month at $80 pays back 5x.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Microsoft (Nuance/Dragon Copilot) and Epic own the scribe and the big-hospital EMR; they will not serve a 3-doctor physio clinic across dozens of fragmented practice systems. Foundation-model labs avoid liability-heavy vertical ops and prefer platforms. The device-side tokenisation and per-role tool locking is an architecture they would have to unwind to copy.
## Biggest risk
Regulatory and liability exposure (HIPAA BAA, medical-device boundaries, telephony consent laws) plus slow trust-building; one leaked or wrong patient message could end the company. Mitigate by staying administrative, never clinical, in v1.
## Uses founder's existing assets
Scoped vanaras with locked tools and handover; on-device approvals and spend rules; reference-token privacy layer (the core selling point); MCP tool-role classification for calendar/messaging/telephony; scheduled background jobs for recalls; voice; BYO model key. New: cloud runtime, desktop computer-use surface, compliance/audit export.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
