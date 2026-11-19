# Blackbox — a flight recorder and audit ledger for every employee's AI agent team
Lens: Agent observability and audit for companies
## Customer & pain
Buyers: CISO, head of internal audit/compliance, and IT leads at 500-5,000 person firms (finance, health, legal, public sector) where staff already use Claude, ChatGPT, Copilot and browser agents. Pain: agents now send email, move files, and spend money, yet the only logs are per-vendor chat transcripts. Nobody can answer "what did Priya's agents do on Tuesday, on whose approval, with what data?" Cloud-side tracing tools (LLM observability) see model calls, not what happened on the phone or desktop.
## Product
Each employee's vanaras (phone, cloud, desktop) write every action to a tamper-evident, hash-chained ledger on the device first, then sync it. Entries record which agent, which scoped tool, what approval rule fired, who approved, spend, and a reference token for the data touched, never the raw personal data. Shared memory means one timeline per person across surfaces, and agent-to-agent handovers ("phone agent passed invoice to desktop agent") appear as a single causal trace. Admins get replay, policy simulation ("would this rule have blocked last month's incidents?"), anomaly alerts, and exportable evidence for auditors (SOC 2, ISO 42001, EU AI Act logging duties).
## Wedge (first product, first 10 customers)
An Android + desktop "audit companion" that wraps MCP tool calls of the employee's existing agents through the UNO pipeline and produces the ledger, with no need to replace their agent. First 10: small regulated shops (boutique wealth managers, clinics groups, law firms, fintech startups doing SOC 2) reached through compliance consultants and auditors, who need agent evidence for the next audit. Flag: assumes MCP tool-call interception is feasible for the third-party agents; a guess.
## Enterprise path
Per-seat pilot with one team, then SSO/SCIM, central policy push (approval and spend rules), SIEM export (Splunk, Sentinel), data residency options, then upsell to full Vanaras teams once the recorder is trusted. Auditor-recognised reports become the sales channel.
## Business model & pricing
$8-15 per employee per month for recorder and reports; $30-60 with managed agents. Compliance evidence packs as annual add-on ($5-20K). Free tier for individuals (personal ledger) drives bottom-up adoption.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor logs only its own agents and is a conflicted witness for its own behaviour. Auditors want a neutral, cross-vendor record. Microsoft will cover Copilot, not Claude on a phone. On-device recording that keeps personal data out of the cloud is structurally hard for cloud-first vendors.
## Biggest risk
Platform access: OS and vendors may restrict interception of other agents' actions, and audit tools sell slowly and depend on standards (AI Act, auditors) still forming. Also a "feature not company" risk if vendors ship good enough native logs.
## Uses founder's existing assets
On-device approvals and spend rules enforcement (become the policy engine); reference-token privacy model (ledger without raw data); service-agnostic MCP pipeline with role classification (the interception and tool taxonomy); scoped agents with handover (the causal trace); scheduled jobs (evidence collection); BYO model key (neutrality).
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 8
excitement: 6
