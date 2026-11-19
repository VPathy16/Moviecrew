# Keyhold — a team of AI agents for every small landlord and property manager
Lens: Property management
## Customer & pain
Independent landlords and small property managers (5-150 doors) in the US, UK, India, Gulf and Australia. They juggle tenant WhatsApp/SMS at odd hours, maintenance vendors, rent chasing, lease renewals, compliance dates (gas safety, smoke alarms, deposit protection) and owner statements. Enterprise suites (AppFolio, Buildium) are portals, not doers; the work still lands on the manager's phone. Missed compliance dates and slow repairs cost real money and fines.
## Product
- Phone: a Tenant-Liaison vanara answers tenants by message and voice, triages issues ("boiler out, elderly tenant" = urgent), and a Rent vanara sends reminders. Manager approves anything with spend or legal weight on-device.
- Cloud: a Maintenance vanara runs 24/7: gets three vendor quotes, chases them, books the slot, follows up after the visit. A Compliance vanara tracks certificates and renewal dates per property.
- Desktop: a Books vanara reconciles bank exports, updates spreadsheets, files invoices, prepares owner statements in whatever tools the manager already uses.
- Shared memory holds each property's history (boiler age, tenant quirks, vendor reliability). Agent-to-agent handoff: tenant report becomes work order, then quote, then approval, then invoice, then ledger entry, with no re-typing.
## Wedge (first product, first 10 customers)
"Maintenance Desk": forward tenant WhatsApp/email to Keyhold; it triages, gets quotes, books vendors, and asks the landlord for one-tap approval. Sell to landlords with 10-50 doors via landlord Facebook groups, r/landlord, local landlord associations, and a UNO-style BYO-key install. First 10: recruit from associations with a free 60-day pilot in exchange for case studies.
## Enterprise path
Move up to property management firms (200-5,000 doors): each property manager gets their own team; the company sets spend limits, approval tiers, vendor whitelists, and audit logs. Owner-facing portals and SOC2 later. Sell into firms already using AppFolio/Yardi by acting as the agent layer over their exports and APIs.
## Business model & pricing
Per-door SaaS: about $1.50-3 per door per month, with a minimum of $29/month; usage-based voice minutes; optional 1% markup on vendor jobs booked (guess). Firms: per-manager seat ($99-199) plus per-door fee.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants will not build vertical workflows, vendor networks, or jurisdiction-specific compliance calendars. Landlord-tenant law varies by state and country, and liability for wrong legal notices is unattractive to them. The on-device approval and spend rules are a trust feature that a vertical buyer values.
## Biggest risk
Trust and liability: an agent that mishandles an eviction notice, deposit, or emergency repair. Mitigation: agents never send legal notices without approval, and start with maintenance and reminders. Second risk: incumbents (AppFolio Realm-X, Buildium AI) adding similar features (guess).
## Uses founder's existing assets
Scoped vanaras with locked tools (tenant-facing agent cannot touch the ledger); handover between agents; scheduled background jobs for rent and compliance dates; on-device approvals and spend rules; reference tokens so tenant PII and bank details never reach the model; MCP pipeline for connecting accounting, email, calendar, and vendor tools; voice for urgent tenant calls; BYO model key for cost-conscious landlords.
## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
