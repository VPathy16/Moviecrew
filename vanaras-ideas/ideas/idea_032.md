# Switchyard — the model-neutral control plane where every employee's agent team runs under company rules, on any LLM
Lens: Model-neutral layer that works with any LLM
## Customer & pain
Payer: the CIO/CISO and head of AI at 200-5,000 person companies. Today teams buy Copilot for some, ChatGPT Enterprise for others, Claude for engineers, plus shadow BYO keys. Each has its own memory, policy and audit trail. Switching model vendors means losing agent setups and context; spend is unmanageable; personal and customer data flows to whichever vendor the employee picked. (Guess: most mid-size firms already run 2-3 model vendors.)
## Product
Each employee gets a small team of vanaras (scoped agents, each locked to its own tools) on phone, cloud and desktop. Model is a config line per vanara: OpenAI, Anthropic, Google, local or on-prem, swappable without losing anything. Shared memory lives in a company-owned store, not in any vendor's account, and stores reference tokens instead of raw personal data, so the model only sees what policy allows. Agent-to-agent sync: the phone vanara captures a request in a call, hands it to the cloud vanara to work overnight, and the desktop vanara finishes it in the browser or files; every handoff is logged. Device-enforced approvals and spend limits mean policy holds even if a model misbehaves. The MCP role-classification pipeline auto-sorts a company's tools into read/write/spend scopes.
## Wedge (first product, first 10 customers)
Start with a "model portability and policy" Android and desktop app for 20-100 person AI-forward firms (agencies, dev shops, consultancies). It is BYO-key, free for one user, and sold per seat for a team layer: shared memory, per-vanara scopes, approval rules, spend caps, one audit log. Pitch: "Change your LLM vendor in an afternoon and prove what your agents did." Find 10 customers through founder-led outreach to small firms already juggling several subscriptions, plus MCP and agent-builder communities.
## Enterprise path
Small teams, then departments, then SSO/SCIM, a self-hosted memory store in the customer's VPC, SOC 2, a policy-as-code admin console, and a model-routing policy (sensitive data goes to on-prem models, cheap tasks to small models). Land through security and finance, who care about audit and spend, rather than through the AI team.
## Business model & pricing
Per-seat SaaS: about $12/user/month for the team layer, $30-40 for enterprise with audit and VPC. Optional usage-based routing margin is a guess and is not needed at the start. Enterprise ACV is roughly $50-300K at 200-1,000 seats.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor's incentive is to lock memory, agents and workflows to its own model. A neutral layer that makes switching vendors easy works against their business, and none can credibly offer it. Microsoft comes closest through multi-model Copilot but stays inside its own tenant and ecosystem. Neutrality is only credible from a third party, like Okta for identity.
## Biggest risk
Vendors will ship "good enough" memory, agent and admin features and support open standards such as MCP, so neutrality may look like a nice-to-have until a vendor price hike or outage makes it urgent. Another risk is that phone, cloud and desktop together are too much surface for one person to build; if so, ship the policy and memory layer first.
## Uses founder's existing assets
Scoped vanaras and handover between agents (core runtime); on-device approvals and spend rules (policy enforcement); reference tokens keeping personal data from the model (the privacy pitch); the service-agnostic MCP pipeline with role classification (tool onboarding); scheduled background jobs (24/7 cloud work); voice (phone surface); BYO model key (the neutrality already built).
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
