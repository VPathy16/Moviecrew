# Nightshift — overnight AI agents that grind through a freelance developer's client backlog and hand a reviewed result to their phone by morning
Lens: Cloud-first (projects) entry, devices later
## Customer & pain
Solo freelance developers and 2-10 person dev/design/data agencies who juggle 5-15 small client projects (maintenance, bug fixes, dependency upgrades, small features, content updates). They bill hourly or by retainer, and the small tickets eat evenings. They can't leave a coding agent running on a client repo unsupervised because they don't trust it with client credentials, spend, or unreviewed pushes. Clients also expect status updates that nobody has time to write.
## Product
Each client project is a cloud "project room" with its own vanaras: a Fixer (works tickets in a sandbox on a branch), a Tester, a Scribe (client-facing changelog and status email drafts), and a Steward (deadlines, invoices-due reminders). Scoped tools per agent: the Fixer has repo + sandbox but no email; the Scribe has email drafts but no repo write. Agents keep working 24/7 while the laptop is off. Shared memory holds per-client conventions ("Acme hates semicolons, deploys Fridays only"), and agent-to-agent handover moves work along: Fixer -> Tester -> Scribe. Later surfaces: the phone shows a morning digest with approve/reject on each PR and spend rules enforced on-device (approve a $ cloud budget, approve sending the client update); the desktop vanara handles local-only work (design files, client's VPN-only staging, browser checks) and syncs results back into the same project memory. Client secrets are held as reference tokens, so the model never sees raw credentials.
## Wedge (first product, first 10 customers)
A cloud web app plus a thin Android approvals app: connect GitHub, list tickets, and get a morning digest of branches and draft client updates. Sell to 10 freelancers from indie-dev communities and Upwork/Toptal-style groups with a 30-day paid pilot at a low price. Founder dogfoods on his own side repos.
## Enterprise path
Agencies -> consultancies and IT-services firms that need per-client isolation, audit logs, and per-employee teams under company rules (which model, which repos, spend caps). Then internal platform/maintenance teams in companies with many legacy apps. The per-employee team plus company policy layer is the vision's enterprise model.
## Business model & pricing
Per-project-room subscription, roughly $19/month per active client room, with a $99/month agency bundle; usage pass-through or BYO model key (reuses UNO's BYO key). Enterprise: per-seat plus policy/audit add-on. (Prices are guesses.)
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They ship general coding agents tied to their own model and one repo host; they won't build multi-client isolation, model-agnostic BYO keys, client-facing comms with approval gates, or freelancer billing-aware workflows. It is a thin, messy vertical with small ticket sizes at the start.
## Biggest risk
Coding agents (Claude Code, Codex, Copilot agent) get good enough natively at background work and bundle it, leaving Nightshift as a thin wrapper. Also: unit economics if model costs exceed the low price point.
## Uses founder's existing assets
Scoped per-agent tool locking, handover between agents, scheduled background jobs, on-device approvals and spend rules (become the phone approvals app), reference-token privacy for client secrets, MCP pipeline classifying tools by role (connects GitHub, email, invoicing), BYO model key, and voice (spoken morning briefing).
## Scores
market_size: 6
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
