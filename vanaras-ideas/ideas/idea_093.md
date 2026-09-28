# Carebench — a team of agents that runs the paperwork of chronic illness for the patient and their family
Lens: Wedge: health and wellness coordination

## Customer & pain
Payer: people managing a chronic condition (type 2 diabetes, MS, IBD, cancer survivorship) or a parent's care, plus later employers via benefits. Pain: 6-12 providers, refill calls, prior authorisations, lab results in five portals, insurance appeals, appointment juggling, symptom logs nobody reads. Patients become unpaid project managers. Nothing owns the whole loop, and health data is too sensitive for people to paste into a chatbot.

## Product
- Phone: a "Refill vanara", "Appointments vanara" and "Log vanara" handle reminders, calls, symptom check-ins by voice, and pharmacy or clinic messaging. Each is locked to its own tools. Anything that spends money or sends records needs on-device approval.
- Cloud: a "Claims vanara" works 24/7 on long jobs: chasing a prior auth, tracking an appeal deadline, assembling a pre-visit brief from the log.
- Desktop: a "Portal vanara" logs into insurer and hospital portals, downloads EOBs and lab PDFs, and files them.
- Shared memory + agent sync: a symptom logged on the phone reaches the cloud agent, which drafts the appeal or visit summary. The desktop agent fetches the missing lab. Handover is explicit and auditable.
- Privacy: reference tokens mean the model sees "MEDICATION_3", not names, diagnoses or member IDs. BYO model key keeps the data out of our vendor bill and liability.

## Wedge (first product, first 10 customers)
Android app for people on injectable or specialty drugs (GLP-1s, MS and IBD biologics), where refills, prior auth renewals and cold-chain pharmacy calls are constant. Wedge feature: "Never lose a refill" (auto-tracked supply, pharmacy call and prior-auth reminders). First 10 users come from patient subreddits and Discord groups, and from 2-3 patient-advocacy nonprofits. Charge $15/month from day one. Start in the US (guess: highest paperwork pain), with a UK/EU variant later.

## Enterprise path
Employer benefits and navigation: each employee with a chronic condition gets a private team, and the employer sees only aggregate outcomes (guess: the "no PHI to employer" design is the selling point). Sell through benefits consultants and care-navigation resellers. Later, specialty pharmacies and digital-health clinics white-label it for their patients. SOC 2 and a HIPAA business associate agreement are needed for this stage.

## Business model & pricing
Consumer: $15/month, $25 family plan (care for a parent). Enterprise: $6-10 per enrolled member per month (guess, priced against navigation vendors). Optional add-on for clinics: $1-2K/month per practice for a patient-facing intake agent.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Health liability, HIPAA exposure and per-payer integration grind are unattractive as a horizontal product. Apple and OpenAI ship health summaries, but not multi-week autonomous work across insurer portals with per-action approval. A neutral BYO-key player that never sees PHI can serve employers who distrust the platforms. (Flag: OpenAI and Apple health pushes are moving fast; this moat may narrow.)

## Biggest risk
Trust and regulation: an agent calling pharmacies or filing appeals on someone's behalf invites HIPAA, state-law and error-liability problems. Portal automation is also brittle, and insurers block bots.

## Uses founder's existing assets
- Scoped vanaras with locked tools and handover: refill, claims and portal agents.
- On-device approvals and spend rules: gate every send, call or payment.
- Reference tokens: PHI never reaches the model.
- Scheduled background jobs: refill and appeal deadline tracking.
- MCP role classification: plugs into pharmacy, calendar and patient-portal tools.
- Voice: pharmacy and clinic calls, symptom check-ins.
- BYO model key.

## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 8
