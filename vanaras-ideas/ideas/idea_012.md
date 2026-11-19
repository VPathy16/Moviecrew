# Handoff — every engineer's pocket agent that keeps their PRs, CI and on-call moving when the laptop is closed
Lens: Software engineering teams
## Customer & pain
Engineering managers and staff engineers at 20-300 person software companies. Pain: work stalls in the gaps between surfaces. A CI failure at 6pm, a review comment on the commute, a flaky test, an on-call page while the laptop is shut. Cloud coding agents (Claude Code on the web, Copilot agent) run tasks, but nobody supervises them from a phone, and they don't know what the engineer promised in Slack or a call. Engineers lose hours to context switching and unattended agents idle or drift.
## Product
- Phone: a voice/chat "chief of staff" for an engineer. Morning brief of PRs, CI, tickets; approve or reject agent work with one tap; answer agent questions by voice while walking.
- Cloud: scoped vanaras (Triage, Fixer, Reviewer-prep) work repos 24/7 in sandboxes: reproduce a failing test, draft a fix PR, summarise a review thread, run dependency bumps.
- Desktop: a local vanara handles what only the laptop can do (local env, IDE state, private VPN resources), and resumes an unfinished task from the phone.
- Shared memory and agent-to-agent sync: a decision made in a phone call ("skip the migration this sprint") is written to memory, and the cloud Fixer reads it and stops working on the migration. Handover between surfaces is explicit: the phone agent hands a task to the cloud agent with context and approval limits.
- Every vanara is locked to its own tools; merges, deploys and spend need on-device approval.
## Wedge (first product, first 10 customers)
An Android/iOS app "PR and CI pocket approver": connect GitHub, get a summary of each agent-authored or teammate PR, approve/comment/re-run CI by voice, with spend caps. Bring your own model key. Sell to 10 small teams already using Claude Code or Copilot agent via founder's network and Show HN; price low, free for solo. Target: 10 teams, 50 seats in about 3 months.
## Enterprise path
Per-engineer teams under company policy: central rules on which repos and tools each vanara may touch, approval thresholds, audit log kept on device plus exported to SIEM, reference-token design so source and secrets never reach the model provider unless allowed. SOC 2 later; BYO key or self-hosted model gateway for regulated buyers.
## Business model & pricing
Per seat SaaS: $15/engineer/month for phone plus cloud agents (BYO key, so no inference margin risk); team tier $30 with policy and audit; enterprise custom. Optional pooled compute for cloud sandboxes at cost plus margin. Guess: 100 teams x 15 seats x $25 = about $450K ARR.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor supervises only its own agent and model. Engineers run mixed stacks (Claude Code, Copilot, Cursor, Codex), and a neutral, model-agnostic control layer with on-device approvals is against their incentive to lock in. Also mobile supervision is a side feature for them, not their core surface. Risk that GitHub or Anthropic ships a mobile approver is real (flag: guess).
## Biggest risk
Being a thin feature: vendors add mobile approvals and cross-surface memory to their own agents. Mitigation is neutrality across agents and the policy layer, but it must be proven quickly.
## Uses founder's existing assets
UNO's scoped vanaras, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference tokens (keeping source and secrets from the AI), MCP tool-role classification (GitHub, CI, ticketing), voice, BYO key. New: cloud runtime and desktop agent.
## Scores
market_size: 8
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
