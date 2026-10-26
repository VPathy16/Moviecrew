# Pagerhand — a personal team of agents for on-call engineers, from the phone in your pocket to the cloud runbook
Lens: DevOps / on-call engineers
## Customer & pain
The individual on-call engineer (SRE, DevOps, platform dev), who pays personally at first and later through the team budget. Pain: 3am pages, alert fatigue, context lost between the phone (PagerDuty push), the laptop (terminals, dashboards) and Slack. Existing AIOps tools serve the company's incident process, not the person holding the pager. Nobody wants to hand an LLM production credentials, so the AI SRE tools stall in security review.
## Product
Each on-call gets a private team of vanaras.
- Phone: a Triage vanara wakes you with a spoken 30-second brief (what fired, what changed in the last deploy, similar past incidents). It can ack, snooze, or page a teammate by voice, and it answers "is it customer-facing?" from read-only tools.
- Cloud: an Investigator vanara starts working the moment the page lands. It pulls logs, metrics, recent deploys and runbooks through read-only MCP tools, and keeps going while your laptop is closed.
- Desktop: a Hands vanara proposes the fix (kubectl rollback, feature-flag flip, scale-up) as a single approval card. Execution runs on your laptop with your own credentials, and a spend/blast-radius rule set (for example "never touch prod databases") is enforced on-device.
- Shared memory and agent-to-agent sync: the Investigator hands findings to Triage, which briefs you, and Hands then executes what you approved. Afterwards a Scribe drafts the postmortem timeline from the shared memory. Secrets and customer data stay as reference tokens, so the model never sees raw keys.
## Wedge (first product, first 10 customers)
An Android app plus a cloud worker: the "3am brief", a spoken and written page summary from PagerDuty/Opsgenie/Grafana webhooks, read-only. It is free for the first week, then $19/month. The first 10 customers come from SRE communities (r/sre, DevOps Slack groups, Hacker News Show HN), and I would offer the founder's own on-call friends the tool first. BYO model key keeps my costs near zero.
## Enterprise path
Team plan with a shared runbook memory and org-wide guardrail policies (approval tiers per environment, audit log export to SIEM). Then SSO/SCIM, and a self-hosted cloud worker inside the customer VPC. Security review is easier because the model never holds credentials and every action is approved on-device.
## Business model & pricing
$19/user/month individual, $39/user/month team with policies and audit, and enterprise on annual contracts starting around $60/seat. Bring-your-own-key is free of markup, with a managed-model option at cost plus margin.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
It is a vertical of niche workflows built on integrations with PagerDuty, Datadog and Grafana, which the general assistants will not prioritise. Microsoft and Google favour their own clouds' ops tools, while this is cloud-neutral. The phone-to-laptop approval flow with credentials that never leave the device is an architecture choice that runs against how their hosted agents work. (Guess: PagerDuty and Datadog will ship their own AI agents, which is a competitor risk.)
## Biggest risk
Trust. One bad automated action in production ends the product, and PagerDuty/Datadog/incident.io are shipping their own agents for the same moment. Mitigation: read-only by default, and human approval for every write in the first year.
## Uses founder's existing assets
Scoped vanaras with locked tool sets (Triage, Investigator, Hands, Scribe), handover between agents, scheduled and background jobs, on-device approvals and spend/blast-radius rules, reference tokens so secrets never reach the AI, the MCP pipeline that classifies tools by role (read vs write), voice, and BYO model key. The new work is the cloud worker and the desktop executor.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 9
excitement: 8
