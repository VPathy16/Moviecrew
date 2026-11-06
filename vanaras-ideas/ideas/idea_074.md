# Payroll for Agents — hire a vanara like an employee: fixed monthly salary, hard spend cap, audit trail
Lens: Pricing: per-agent 'salary' model (hire a vanara)
## Customer & pain
Two payers. (1) Individuals/freelancers who fear runaway token bills and unpredictable agent actions. (2) Ops/finance leads at 50-500 person companies rolling out agents to employees: usage-based AI billing is unbudgetable, and nobody can say what each agent cost or achieved. Today: opaque token meters, seat licences that ignore agent work, and no per-agent accountability.
## Product
Each vanara is "hired" with a role, a monthly salary (a hard cap covering model spend plus tool spend), a scope (tools it may touch) and a manager (the human). Phone: hire, approve, and get a weekly "timesheet" of what each agent did and cost. Cloud: agents work 24/7 until their salary budget is used, then stop or ask for a raise. Desktop: same salary pool covers computer-use sessions. Shared memory means an agent's work history is its "CV": promotions (wider scope) are earned by measured approval rates. Agent-to-agent handoffs are internal transfers billed to the receiving agent's cost centre, so finance sees real per-role cost. Spend rules are enforced on-device/at the gateway, not by the model.
## Wedge (first product, first 10 customers)
UNO Android users on BYO key get "salary mode": set a monthly cap per vanara, get a timesheet and a pay-slip-style PDF. Charge nothing extra at first; convert to a managed-key plan where Vanaras resells inference at a flat salary (margin from caching and routing). First 10: solo consultants and small agencies who bill clients and want per-client agent cost lines (export to invoices).
## Enterprise path
Cost-centre mapping (department/project codes), per-employee agent budgets, finance approval workflows, SSO, exportable ledger to accounting/ERP, policy templates ("procurement agent may spend up to X"). Sell to finance/IT as "AI headcount budgeting"; expand from one team to all employees.
## Business model & pricing
Salary tiers per hired vanara: about $9 (intern), $29 (associate), $99 (specialist) per month with included inference and tool spend, hard-capped; overage only by explicit raise. Enterprise: platform fee per employee plus the same salaries pooled. Gross margin from routing to cheaper models and prompt caching (guess: 50-65%). Flag: price points are guesses.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their revenue is usage and seats tied to their own model; a fixed, capped, cross-model salary invites margin compression and cross-vendor neutrality they cannot offer. Model-agnostic cost accounting across vendors is against their incentives, and per-agent hard caps enforced outside the model are unnatural for them.
## Biggest risk
Inference costs are volatile; a flat salary can be underwater on heavy users. Mitigate with hard caps, tiered routing and pausing at limit, but the pricing metaphor may also be seen as gimmick unless the accounting is genuinely useful.
## Uses founder's existing assets
Device-enforced approvals and spend rules (the cap engine), scoped agents with locked tools (roles), handover between agents (internal transfers), scheduled background jobs (24/7 work), reference tokens (privacy in audit logs), BYO key (free entry tier), MCP tool-role classification (per-tool cost accounting).
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
