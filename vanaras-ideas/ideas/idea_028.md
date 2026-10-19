# Tendril — a team of agents that runs the admin of disability, across phone, cloud and desktop
Lens: People with disabilities (accessibility-first)
## Customer & pain
Payer: the person or their family (prosumer), then employers and disability-services providers. Living with a disability generates enormous invisible admin: benefit renewals, insurer appeals, appointment chasing, equipment repairs, access requests, reasonable-adjustment paperwork at work. It falls hardest on people for whom phone calls, dense forms, small UI and long waits are the barrier. Existing assistants are built for the average user, are not reliable under approval rules, and expose sensitive health data to a model.
## Product
Phone: voice-first and switch/eye-control friendly; the person speaks or messages, a "caller" vanara phones providers, a "reader" vanara explains letters aloud. Cloud: a "case" vanara owns long-running matters (benefit appeal, insurer dispute, wheelchair repair) 24/7, tracking deadlines and portal statuses. Desktop: a "forms" vanara drives the browser and desktop apps to fill portals, PDFs and workplace HR systems, pausing for approval. Shared memory holds the person's access needs, medical timeline and case history once, so they never re-explain their condition; agent-to-agent handoff moves a case from call to form to appeal letter. Health identifiers stay as reference tokens, so the model never sees raw diagnoses or IDs. Spend and send rules are enforced on the device.
## Wedge (first product, first 10 customers)
Android app "Appeals and renewals": upload a denial or renewal letter, the agents explain it, draft the response, gather evidence, make the phone calls, and track deadlines. Launch with the US (Medicaid/SSI redetermination, insurance denials) or UK/EU equivalents (flag: choose one jurisdiction). First 10 from disability advocacy groups, spinal-injury and MS communities, and caregivers' forums; free case triage, paid tracking.
## Enterprise path
Sell to employers as an accessibility layer: each employee with a disability gets a private team that handles adjustment requests, assistive-tech setup and accommodations paperwork, with HR seeing only what the employee approves. Then disability-services providers, vocational rehab agencies, and insurers running case-management for claimants. Compliance (ADA, EAA in the EU, Equality Act) gives budget owners.
## Business model & pricing
Consumer: $15-25/month, BYO model key discount. Caregiver/family plan $35. Employer: $12-20 per employee-with-accommodation per month plus a per-seat baseline; providers: $50-100 per caseworker seat. Guess: gross margins high because heavy model use is BYO or metered.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They ship horizontal assistants and accessibility features at the OS level, but will not take liability for sensitive casework, make calls on a person's behalf into benefit bureaucracies, or build jurisdiction-specific appeal playbooks. The niche is too small and legally risky for them, yet large enough for a focused company.
## Biggest risk
Trust and harm: a wrong appeal, a missed deadline, or misread medical letter has serious consequences, and vulnerable users need reliability and human backup. Also jurisdictional fragmentation of rules.
## Uses founder's existing assets
Scoped vanaras with locked tools (caller, reader, forms), handover between agents, scheduled background jobs for deadline tracking, on-device approvals and spend rules, reference tokens keeping health data from the AI, the MCP tool pipeline for portals and email, voice, and BYO model key.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 8
