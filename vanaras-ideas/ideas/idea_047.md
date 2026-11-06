# Huddlr — a meeting team for every employee: prep before, act during, close the loop after
Lens: Meetings (before, during, after) as the core
## Customer & pain
Paid by team leads and heads of client-facing functions (sales, customer success, consulting, recruiting) in 20-500 person firms. Meeting notes tools (Otter, Fireflies, Granola) only transcribe. The pain is what surrounds the meeting: nobody prepares (context scattered across email, CRM, docs), commitments made aloud are never executed, and follow-ups are late or forgotten. Employees also dislike bots joining calls and recording others.
## Product
A trio of vanaras per person, sharing one memory:
- Phone vanara (pre): 30 min before a meeting, sends a one-screen brief (last thread, open promises, who is attending) and takes voice notes on the walk in. Handles reschedules and "running late" messages.
- Desktop vanara (during): no bot in the call. It listens locally to the user's own mic/system audio, and drafts live: the CRM note, the doc being referenced, the follow-up mail. Uses the browser/files with approval.
- Cloud vanara (after): turns commitments into tracked jobs that run 24/7: sends the recap, files the ticket, chases the other side on day 3, updates the CRM, books the next slot.
Shared memory means a promise made in a call is known to the phone agent (reminds you), and the cloud agent (executes it). Agent-to-agent sync lets my vanara hand a task to a colleague's vanara, subject to their approval rules. Personal data stays as reference tokens, so the model sees "CLIENT_1", not names.
## Wedge (first product, first 10 customers)
Post-meeting follow-through for freelance consultants and small agencies: a phone app plus a desktop listener that produces the recap mail, action list and chasers from each call, sent only after one tap approval. Sell to 10 solo consultants/agency founders from founder's network and LinkedIn at $29/mo; measure "promises kept on time".
## Enterprise path
Team plan: shared client memory with permissions, per-role approval and spend rules (enforced on device), audit log of what each vanara did, SSO, then data-residency and on-prem local transcription for regulated firms. Land in one sales team, expand across departments as every employee gets their own trio.
## Business model & pricing
$29 per user/month individual, $59 per seat/month team with admin controls, usage-based add-on for cloud jobs. BYO model key lowers COGS; a managed-key tier gets a margin markup.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each owns one surface and one suite (Copilot in Teams, Gemini in Meet). They are tied to their own meeting platform and are not going to act across rival tools or run bot-less on a competitor's client. Cross-platform, on-device approvals and tokenised privacy are awkward for them to bolt on. Guess: they will ship good summaries; the execution layer across tools is where a neutral player wins.
## Biggest risk
Audio capture consent and law (two-party consent regions), plus platform limits on capturing system audio on Android/iOS. Also commoditisation of summaries by bundled Copilot/Gemini.
## Uses founder's existing assets
Scoped vanaras with locked tools (brief, recap, chaser agents), handover between agents (pre to during to after), scheduled background jobs (chasers, reminders), on-device approvals and spend rules (send-mail gate), reference-token privacy layer, MCP tool-role classification (calendar, mail, CRM connectors), voice, and BYO key. New: desktop listener, cloud runner, meeting-specific memory.
## Scores
market_size: 8
defensibility: 5
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
