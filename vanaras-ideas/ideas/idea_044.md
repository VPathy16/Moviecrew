# Threadhands — a personal agent team that lives inside your Slack/Teams DMs and follows you to phone and desktop
Lens: Messaging-native (lives in Slack/Teams/WhatsApp as a surface)
## Customer & pain
Buyer: team leads and ops managers at 20-500 person companies who already live in Slack/Teams. Pain: every employee is told to "use AI" but must open a separate app, re-explain context, and paste between tools. Chat is where work is requested, yet agents in chat today are shared, stateless bots (one company-wide bot, no personal memory, broad permissions that IT fears).
## Product
Each employee gets a private DM thread with their own vanara team, one scoped agent per role (Inbox, Calendar, Docs, Tickets, Errands), each locked to its own tools. Chat is the control plane: approvals are tap-buttons in the thread ("Send this reply? Spend EUR 40?"), and the thread is the audit log.
- Phone: same team by voice/WhatsApp; personal reminders, calls, errands. Approvals and spend rules are enforced on the device, and personal data stays as reference tokens so the model never sees raw values.
- Cloud: long jobs (weekly report, ticket triage, monitoring a doc) continue 24/7 when devices are off and report back into the thread.
- Desktop: a small local agent handles files/browser/apps the cloud can't reach; the DM says "handed to your laptop".
Shared memory plus agent-to-agent handover means a request typed in Slack ("get me ready for Thursday's client call") fans out: Calendar agent finds the meeting, Docs agent gathers files on the desktop, phone agent reads the brief aloud in the car. Team-to-team: my Inbox vanara asks your Calendar vanara for a slot, with no humans in the loop.
## Wedge (first product, first 10 customers)
A Slack app, "Approvals-first assistant": personal DM agent connecting Gmail/Calendar/Notion/Jira via MCP with tap-to-approve on every write action. Free for 5 seats; launch through 10 small agencies/consultancies and startups reached via founder network and Slack communities (guess: 2-4 weeks to a working pilot on a BYO key). Android app is the companion that proves the on-device approvals.
## Enterprise path
Per-employee teams under company policy: admin console sets which tools each role-agent may touch, spend caps, retention, and approver chains; SSO/SCIM, audit export from the thread log, data-residency via BYO model key or private endpoint. Reference-token design is the security pitch (model never sees PII). Land through team leads, expand by department, then IT.
## Business model & pricing
Per seat per month: EUR 12 personal-team tier, EUR 25 with cloud+desktop surfaces, enterprise custom with admin/audit. Model cost passed through or BYO key (guess: 60-70% gross margin on hosted).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each ships an agent for its own suite (Copilot, Gemini, Slackbot/Agentforce) and wants you inside its app. A neutral, cross-suite, per-person team spanning Slack AND Teams AND WhatsApp with on-device approvals conflicts with their lock-in. Model vendors sell models and generic agents, not per-role scoped permissioning across surfaces.
## Biggest risk
Platform dependence: Slack/Microsoft can restrict API access, rate-limit or ship a native personal agent; also trust that DM agents are safe enough for real write actions.
## Uses founder's existing assets
Scoped vanaras with locked toolsets; handover between agents; scheduled background jobs; approvals and spend rules (become the tap-buttons); reference-token privacy layer; service-agnostic MCP pipeline (role classification of tools); voice; BYO model key. New: Slack/Teams bot adapter, cloud runner, desktop agent.
## Scores
market_size: 8
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
