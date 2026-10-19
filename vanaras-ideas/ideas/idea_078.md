# Sherpa Seat — the personal AI team an employee brings to work, that IT can finally say yes to
Lens: Bottom-up adoption (employees bring their own vanaras to work)

## Customer & pain
Employee-level: knowledge workers (ops, sales, finance, recruiting) already paste work into personal ChatGPT/Claude accounts to get through the day. IT/security is the second buyer: they see "shadow AI", cannot block it without killing productivity, and cannot approve it because agents hold raw credentials and customer data. Today the choice is ban or blind trust.

## Product
Each employee installs Vanaras on their phone (personal daily-life vanara: calendar, reminders, calls) and later a desktop/cloud vanara for work. Work vanaras are scoped agents (Inbox, CRM, Expenses, Docs), each locked to its own tools. Shared memory means the phone vanara knows the 4pm client call moved and the desktop vanara preps the deck; the cloud vanara keeps chasing overnight approvals. Agent-to-agent handover moves work between surfaces. Key trick: a strict personal/work membrane. Work data lives in a work "team" on the device; personal memory never crosses. Reference tokens keep customer PII away from the model. Approvals and spend rules run on-device, so the employee is safe by default. IT later plugs in policy, not a new tool.

## Wedge (first product, first 10 customers)
Free/low-cost "Work Mode" for individuals at small firms: connect Gmail/Slack/CRM via the MCP pipeline, get a morning brief, follow-up chasing, and expense capture on phone. BYO model key keeps my cost near zero. First 10: 10 individual power users (founders' EAs, freelancers, sales reps) from LinkedIn/Reddit/Indie communities, then the small companies they sit in (guess: 2-5 seats each within months).

## Enterprise path
1) Individual paid seats. 2) "Seat count detected" nudge: when 3+ users share a domain, offer an admin console, showing anonymised tool-use, blocked actions, and approval logs. 3) Company-owned work team: SSO, central MCP allowlist, spend limits, data-residency, audit export, offboarding that wipes the work team but leaves the personal one. 4) SOC 2 once ARR justifies (guess: needs ~$150K to pay for it).

## Business model & pricing
Individual $20/mo (BYO key) or $35 with bundled model. Team $30/seat/mo with admin console; Enterprise $50+/seat/mo, annual, with audit and policy. Land-and-expand bottom-up, so CAC is near zero.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell to IT first and the consumer app second; each is tied to its own model and cloud. A model-agnostic, phone-first, device-enforced membrane between personal and work is against their incentives (Microsoft wants Copilot data in M365; Apple avoids third-party agents). Neutrality across models and services is the moat, plus an on-device enforcement design they can't retrofit.

## Biggest risk
Bottom-up needs individuals to pay or be delighted enough to spread; employers may still ban it before the admin console exists, and "BYOD agents with work data" may trip security reviews. Also, Android-only reach at the start (a guess: many office workers use iPhone).

## Uses founder's existing assets
Scoped vanaras and handover (work roles); on-device approvals and spend rules (employee safety, later IT policy); reference tokens (PII never reaches the AI); MCP tool-role classification (central allowlist); scheduled background jobs (overnight chasing); voice (calls on the go); BYO key (low COGS).

## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 8
