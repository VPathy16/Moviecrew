# GrantHands — a team of on-device AI agents for small NGOs that runs the grant cycle, donor comms and field reporting
Lens: Nonprofits and NGOs
## Customer & pain
Executive directors and program officers at small and mid-size NGOs (5-60 staff, budgets $300K-$10M) in the US, UK, EU, Africa and South Asia. They pay from operating overhead. Pain: staff spend 30-40% of time on funder reporting, grant applications, donor thank-yous and volunteer coordination. Field staff work on phones with poor connectivity. Beneficiary data (health, refugees, abuse survivors) is sensitive, and most NGOs cannot legally or ethically paste it into ChatGPT. Funders each want different report formats.
## Product
- Phone vanara (field staff): voice or text field notes and photos are turned into structured case and activity records, works offline, and beneficiary identifiers are swapped for reference tokens so the AI never sees names. Also handles volunteer scheduling and calls or messages.
- Cloud vanara (programs): drafts grant applications and funder reports 24/7 from the shared memory, tracks deadlines, and chases missing data by messaging staff.
- Desktop vanara (office): fills funder portals, reconciles spreadsheets, and prepares board packs from local files.
- Shared memory + agent sync: a field note on the phone becomes indicator data, which the cloud agent writes into the quarterly report, which the desktop agent submits in the funder's portal. Approvals and spend rules are enforced on the device (e.g. the ED must approve anything sent to a funder).
## Wedge (first product, first 10 customers)
Start with "field notes to funder report": a phone app plus cloud drafter that produces the quarterly narrative and indicator table for one funder template. Get the first 10 from small NGOs in the founder's network, NGO Slack and WhatsApp groups, and Techsoup-style communities. Offer a free pilot for one reporting cycle, then a paid plan.
## Enterprise path
Move from one team to NGO networks and umbrella bodies (federations, consortia, UN implementing-partner lists). Each employee gets their own team under org rules: data-residency, donor-mandated safeguards, audit logs, and role-scoped agents. Sell to international NGOs (INGOs) with hundreds of country staff, and to foundations that mandate the tool for their grantees.
## Business model & pricing
Per-seat SaaS at roughly $15-25 per staff seat per month, with a steep nonprofit discount tier ($5-8) and a free tier for volunteers. Bring your own model key keeps margin high. INGO contracts at $20K-100K a year. (Pricing is a guess.)
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They give nonprofits discounts on generic assistants but will not build per-funder report logic, offline field capture, or tokenised beneficiary privacy for a tiny, low-ARPU market. Their agents are general; the NGO buyer needs scoped agents with approvals and safeguarding rules. They may ship the pieces, so the moat is workflow depth and trust.
## Biggest risk
Low willingness to pay and long, grant-driven procurement cycles; also each funder's format is a long-tail integration burden. Mitigation: sell on hours saved and grant wins, and get funders to sponsor seats.
## Uses founder's existing assets
Reference-token privacy layer (beneficiary data never reaches the model), scoped vanaras with locked tools, handover between agents, scheduled background jobs (deadline chasing), on-device approvals and spend rules, voice, the MCP pipeline (CRM, Drive, funder portals), and BYO model key (NGOs use donated credits).
## Scores
market_size: 6
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
