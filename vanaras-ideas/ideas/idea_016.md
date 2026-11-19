# Bidcrew — a personal team of agents that wins, delivers and gets paid on freelance marketplaces
Lens: Freelancers on marketplaces
## Customer & pain
Full-time freelancers and small solo studios on Upwork, Fiverr, Toptal-style and regional marketplaces (designers, developers, translators, video editors, VAs). They pay for themselves. Pain: 30-40% of time goes to non-billable work: scanning job feeds, writing proposals, chasing clients, scoping, timesheets, invoicing, chasing late payments. Client messages arrive on 4 platforms plus WhatsApp; nothing remembers context across them, and marketplace rules (no off-platform contact, fee limits) are easy to break.
## Product
- Phone: a scout vanara triages new jobs against the freelancer's rates and skills, drafts proposals, and asks approval by voice or tap. A client-comms vanara drafts replies and reminders, holding client details as reference tokens so the model never sees them.
- Cloud: a delivery vanara works on the project 24/7 (first drafts, code branches, translations, asset prep) while the phone is off, and posts results for review.
- Desktop: a packaging vanara handles files, exports, uploads to the marketplace, timesheet screenshots and invoice generation in the browser and apps.
- Shared memory holds per-client style, past feedback, rates, and scope history. Handover: the scout wins a job, hands the brief to delivery, which hands the result to packaging, which hands the invoice to the collections vanara. Spend and approval rules (never bid below X, never send without OK) are enforced on device.
## Wedge (first product, first 10 customers)
Proposal-and-triage on Android: connect job feed alerts (email/RSS/MCP), get ranked jobs and one-tap drafted proposals in the freelancer's voice. Recruit 10 from freelancer subreddits, Discord groups and indie communities; free for 2 weeks, then a subscription. Metric: proposals sent per week and win rate versus their baseline.
## Enterprise path
Agencies and staffing/EOR firms managing 20-500 freelancers get a team-of-teams: each contractor has their own vanaras under agency policy (rates floor, client data boundaries, approval rules), with audit logs. Later, enterprises with contingent workforces buy it to run vendor pools; it slots into the "every employee gets a team" story.
## Business model & pricing
$29/month solo (BYO model key lowers cost), $79/month "studio" with cloud runs. Agency: $15-25 per contractor per month plus policy console. Optional 0.5% on invoices collected (guess).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Horizontal assistants will not build marketplace-specific, policy-aware, multi-surface workflows for a niche; marketplaces themselves (Upwork's Uma-style agents) serve the platform's interest, not the freelancer's cross-platform interest. Neutrality across marketplaces is the moat.
## Biggest risk
Marketplace terms of service and anti-automation: platforms may ban bots that auto-bid or scrape. Mitigation: human-in-the-loop sends, no scraping (use email alerts and official APIs), but access can still be restricted. Also, freelancers churn as they find steady clients (guess).
## Uses founder's existing assets
Scoped vanaras and handover (scout to delivery to invoicing), scheduled background jobs (feed checks, payment chasers), on-device approvals and spend rules, reference-token privacy for client data, MCP tool pipeline (invoicing, email, calendar, storage), voice approvals, BYO key.
## Scores
market_size: 6
defensibility: 5
feasibility_solo_30k: 8
asset_fit: 8
excitement: 6
