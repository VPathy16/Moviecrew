# Threadhand — a team of agents that lives in your inbox and works by email
Lens: Email-native (inbox as the main surface)
## Customer & pain
Small professional-services firms (5-50 people: accountants, immigration and boutique law, architects, insurance brokers, recruiters, agencies). Their work runs on email threads with clients, attachments and deadlines. Staff lose hours a day chasing documents, re-keying data, following up and filing. They will not adopt a new app, and clients will not either. Firm owners pay.
## Product
Each employee gets a team of vanaras that are addressable as email identities (cc a vanara like a colleague: "cc: chase@firm.threadhand.com"). No new UI; approvals are one-tap replies to a digest email.
- Phone: the founder's UNO-style vanaras handle voice/quick approvals ("approve the reminder to Mr. Rao?") and calls to clients; the phone is the approval remote.
- Cloud: a Chaser vanara runs 24/7 on threads: tracks who owes what, nudges clients, drafts replies, books meetings, and files attachments into the case folder.
- Desktop: a Filer vanara uses the local browser and apps (tax portal, practice-management tool) to enter the data from the email attachments, since most niche tools have no API.
- Shared memory holds the case state per client (deadlines, missing documents, tone preferences). Agent-to-agent handover: Chaser detects the client sent a P&L, hands to Filer on desktop, Filer returns a receipt, Chaser replies to the client. Personal data stays as reference tokens, so the model sees "CLIENT_17", not names or IDs.
## Wedge (first product, first 10 customers)
"Document chaser" for tax/bookkeeping practices: cc the vanara on an engagement thread; it chases missing documents, classifies attachments, and posts a weekly status digest. Works with Gmail/Outlook via delegated access, no install. First 10 come from founder's network plus accounting-community forums; a 30-day pilot on one busy season's backlog. (Guess: pain is highest in tax-season peaks.)
## Enterprise path
Move from firm-level to larger firms and in-house teams: per-employee teams, SSO, org-wide rules (which agent may email external parties, spend limits, redaction), audit log of every sent message, data residency, BYO model key for regulated firms. Because rules are enforced on the device/tenant, compliance sign-off is easier.
## Business model & pricing
Per-seat SaaS: $39/user/month for the email team, $99 with the desktop Filer. Usage-based overage above a message cap; BYO model key cuts the price. Target ARPA around $600-2,000/month per firm.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Copilot and Gemini in Gmail are horizontal, single-user drafting helpers built around their own suite; they will not chase niche vertical workflows, cross-mailbox case memory, or desktop entry into obscure portals, and they avoid the liability of sending autonomously to clients. Multi-provider mailbox neutrality (Gmail plus Outlook plus IMAP) is against their interest.
## Biggest risk
Trust and deliverability: an agent emailing clients wrongly is a firm-reputation event, and Google/Microsoft can tighten API access or spam-filter agent-originated mail. Mitigated by approval-before-send defaults, but that slows the magic.
## Uses founder's existing assets
Scoped vanaras with locked tool sets (Chaser can email but not file; Filer can file but not email); handover between agents; scheduled background jobs (follow-up cadences); approvals and spend rules on the device; reference-token privacy layer; MCP pipeline for Gmail/Outlook/calendar/portals; voice for phone approvals; BYO key. New: desktop agent and the cloud runtime.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
