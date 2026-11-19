# Marginalia — a team of AI agents that carries a teacher's weekly admin so they get their evenings back
Lens: Education (teachers)
## Customer & pain
Payer: individual teachers first (US/UK/AU/India-agnostic, K-12), then schools and districts. Teachers lose roughly 10+ unpaid hours a week to parent emails, grading, lesson prep, IEP/differentiation notes, attendance and incident logs, and substitute plans. Existing AI tools (MagicSchool, Brisk) are generators in a browser tab. They do not remember the class or act across the day. Student data is the blocker: districts ban pasting names into chatbots.
## Product
- Phone: a "Parent Desk" vanara drafts and schedules replies to parent messages, reminders, and permission-slip chases. A "Day" vanara runs morning briefings, duty rosters and quick voice notes ("Maya hit Leo, log it").
- Cloud: a "Prep" vanara builds next week's lesson variants and differentiated worksheets overnight from the syllabus and past notes, and a "Marker" vanara drafts rubric-based feedback on submitted work.
- Desktop: a "Desk" vanara moves data between the school's LMS, gradebook and email that have no API, in the teacher's own browser.
- Shared memory holds class context: who needs scaffolds, what was taught, which parent prefers calls. The phone note "Leo struggled with fractions" becomes tomorrow's cloud-built worksheet and a drafted parent update, via agent-to-agent handover. Student names stay as reference tokens, so no identifiable data reaches the model. Approvals gate every outbound message to parents.
## Wedge (first product, first 10 customers)
Android app, "Parent Desk + Sunday prep". Teachers bring their own model key or use a metered plan. Recruit the first 10 through teacher communities (Reddit r/teachers, teacher Facebook groups, TeachersPayTeachers creators) with a promise: "no student names ever leave your phone". Success is measured in weekly hours saved.
## Enterprise path
Bottom-up teacher adoption, then a school pilot, then district. The district buys admin controls: an approved-tools list, audit logs of every agent action, and data-residency and FERPA/GDPR-style attestations. The on-device tokenisation is the compliance story that gets past district IT and procurement.
## Business model & pricing
Teacher: $12/month, or free with BYO key plus paid cloud runtime. School: $8 per teacher per month with admin console. District: annual contract, $60-100 per teacher per year (guess). Costs are mostly model tokens, which are passed through or bundled.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Google (Classroom/Gemini) and Microsoft (Copilot for Education) will build tools inside their own suites. They will not act across rival LMSs, personal phones and email under teacher-owned approvals. Education is low-ARPU and compliance-heavy, so it is not a priority for the labs. Ed-tech niche incumbents lack a phone and desktop presence.
## Biggest risk
Trust and procurement: one privacy scare or a wrongly sent parent message can end a school relationship, and district sales cycles run 6-18 months. Also, Google could bundle a free "good enough" version (guess).
## Uses founder's existing assets
- Scoped vanaras with locked tools: Parent Desk cannot touch the gradebook.
- Handover between agents: the phone note to cloud worksheet to parent update chain.
- Scheduled background jobs: Sunday prep, morning briefings.
- On-device approvals and spend rules: gating parent messages.
- Reference tokens: student PII never reaches the AI.
- MCP pipeline with tools classified by role: connecting to Google Classroom, Canvas and email.
- Voice and BYO key: voice logging in the corridor and low-cost adoption.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 8
asset_fit: 9
excitement: 7
