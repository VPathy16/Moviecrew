# Vanaras Guild — a vetted marketplace of scoped, permission-locked agent roles that install into any team's Vanaras
Lens: Marketplace of vanaras (third-party agent roles)

## Customer & pain
Two payers. (1) Small firms and professionals (bookkeepers, immigration consultants, property managers, clinic admins, freelancers) who want an agent doing a real job, not a generic chatbot. (2) Domain experts (accountants, paralegals, ops veterans) who know a workflow well and want to sell it as a role. Today, agent "stores" (GPT Store, MCP directories) list prompts and tool servers with no guarantee of what an agent can touch. Buyers cannot safely install a stranger's agent next to their bank, email and files. Publishers cannot get paid or protect their playbooks.

## Product
A vanara is a signed package: role prompt and playbook, a declared tool scope (which MCP tools, by role class), spend and approval rules, schedules, and handover contracts (which other vanaras it accepts work from or passes work to). The phone, cloud and desktop runtimes enforce the scope on-device, so a third-party role never sees raw personal data (reference tokens) and cannot exceed its manifest. Shared memory is namespaced per role: a "Rent Collector" vanara reads only the tenant-ledger slice the user grants. Agent-to-agent sync lets a bought role plug into the user's existing team, e.g. the phone Errands vanara hands an invoice to a marketplace "GST Filing" vanara, which runs on cloud overnight and asks for approval on the phone. Publishers see usage and outcomes, never user data.

## Wedge (first product, first 10 customers)
Ship the manifest format, the sandboxed installer in UNO, and 10 hand-built roles for one niche, e.g. freelancer back-office (invoice chaser, expense sorter, tax-deadline watcher, contract renewals). Recruit 5 publishers from freelancer communities and sign 10 users at $9-19/role/month. Founder authors the first roles to prove the format.

## Enterprise path
IT admins get a private guild: an allowlist of vetted roles, policy overrides, audit logs, and internal publishing (teams share roles across employees). Procurement asks "what can this agent touch?" and the manifest answers it. Sell via security-review-friendly documentation, then per-seat.

## Business model & pricing
20-30% take on role subscriptions; certification fee for publishers ($99-499 per review); enterprise private-guild tier per seat ($5-10/user/month) on top. Publishers set their own price (flat or per successful outcome).

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They will build stores, but tied to their own model and cloud, and their permission models are app-level OAuth, not per-role, on-device, model-agnostic scoping across phone, cloud and desktop. Vendor-neutral BYO-model neutrality is hard for them to offer. Risk of them adopting MCP-based skills is real (flag: guess).

## Biggest risk
Two-sided cold start: no publishers without users, no users without roles. Also trust: one malicious role incident could kill the brand.

## Uses founder's existing assets
Scoped agents locked to their own tools (the manifest is that concept made portable), handover between agents (handover contracts), on-device approvals and spend rules (enforcement), reference tokens (data privacy for untrusted publishers), MCP pipeline with role classification (auto-derive and verify a role's scope), scheduled jobs (role schedules), BYO model key (publisher-neutral).

## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 8
