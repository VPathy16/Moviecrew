# Ledgerlore — a portable, permissioned memory vault that every agent a person or team uses reads from and writes to
Lens: Agent memory as the core product (shared memory layer)
## Customer & pain
Buyers: heads of IT/AI platform at 200-5,000 person companies, and power users (consultants, founders) paying personally. Pain: every agent (ChatGPT, Claude, Copilot, Cursor, internal bots) keeps its own siloed, unauditable memory. Users re-explain context, memory leaks across clients/projects, and nobody can answer "what does the AI know about me/this customer, and who told it?" or delete it on request.
## Product
A memory vault with typed entries (facts, preferences, decisions, project state, commitments), each carrying provenance, sensitivity class, owner and expiry. Phone vanara captures daily-life memory (calls, messages, reminders); cloud vanara consolidates, dedupes, and resolves conflicts overnight and keeps projects' state; desktop vanara records work context (files, browser, apps) as memory candidates. Any third-party agent connects via MCP and receives only the slice its scope allows. Agent-to-agent sync: when one agent writes a commitment ("send quote Friday"), the vault notifies the agent on the surface that can act, and logs the handoff. Personal data is exposed to models as reference tokens, so the vault, not the model, holds raw values. Users see a "memory ledger": what was learned, from where, edit/forget with one tap.
## Wedge (first product, first 10 customers)
Free-to-start Android + MCP server: "one memory for all your AI apps", starting with Claude, ChatGPT and Cursor via MCP. Target power users and 10 small consultancies/agencies who need client-separated memory (per-client vault, no cross-leak). Paid tier for client separation and export. First 10: consultants and boutique agencies reached through founder communities and MCP forums.
## Enterprise path
Per-employee vaults under company policy: retention rules, PII classes, legal hold, audit export, SSO/SCIM, regional data residency, and a shared team vault with role-based access. Sold as compliance infrastructure for "AI memory governance" (GDPR erasure, discovery). Then offer the full Vanaras team on top.
## Business model & pricing
Individual $12/mo; teams $20/seat/mo; enterprise $40+/seat/mo with audit and residency. Usage-based add-on for consolidation compute (BYO model key keeps COGS low). Guess: 70%+ gross margin.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Each vendor's memory is a lock-in moat; none will make it portable or write into competitors' agents. A neutral vault that enterprises trust to sit across vendors is structurally unattractive for any one of them to build. Risk they ship a standard (MCP memory spec) is real, but neutrality and on-device policy enforcement remain.
## Biggest risk
Memory quality: if consolidation is wrong or stale, trust collapses; and vendors may expose memory APIs that commoditise the storage layer. Also cold-start: value only appears once several agents are connected.
## Uses founder's existing assets
Reference-token privacy layer (personal data never reaches AI); scoped vanaras as per-scope memory readers; approvals and spend rules reused as write/share approvals; MCP pipeline classifying tools by role for the connector gateway; scheduled background jobs for nightly consolidation; handover between agents for cross-surface commitments; BYO key; voice and phone capture from UNO.
## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 8
excitement: 8
