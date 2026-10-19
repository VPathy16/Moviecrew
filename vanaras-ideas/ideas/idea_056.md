# Campfire Crew — a private team of agents for every marketer, with brand rules enforced on-device
Lens: Marketing teams

## Customer & pain
Heads of marketing / marketing ops at 20-500 person B2B and D2C companies, and small agencies. Marketers already use ChatGPT, Claude and Canva AI with personal accounts, pasting unreleased launch plans, customer lists, pricing and ad budgets into them. Legal and brand teams cannot see or stop it. Campaigns also die in handoffs: the brief lives in a doc, the assets in a drive, the approvals in Slack, the spend in an ad manager. Nobody owns the loop at 2 a.m. when a paid campaign overspends or a post goes out with an unapproved claim.

## Product
Each marketer gets a small team of vanaras, each locked to its own tools:
- Phone: the Approver vanara pings you to approve a post, budget bump or influencer payment, by voice or tap. It lives on the phone because that is where approvals actually happen.
- Cloud: the Campaign vanara runs the calendar, drafts variants, schedules posts and monitors ad pacing 24/7, even when laptops are off.
- Desktop: the Production vanara works in Figma, the CMS, the ad managers and spreadsheets, and assembles the weekly report.
- Shared memory holds brand voice, claims that legal has cleared, past performance and the current campaign state. Agent-to-agent handover means the Campaign vanara hands a draft to the Compliance vanara, which can only read and flag, then to the Approver. Spend caps and "never publish without approval" rules are enforced on the device and cannot be prompt-injected away. Customer lists and CRM fields reach the model only as reference tokens.

## Wedge (first product, first 10 customers)
"Spend Guard + Approvals": an Android app plus MCP connectors for Meta/Google Ads, LinkedIn and a scheduler. It sets per-campaign spend rules, sends voice or tap approvals and pauses ads on anomalies. Sell to 10 small agencies and D2C founders (found via marketing communities, my own network and cold DMs) at a low monthly price. The pitch is "let AI touch your ad accounts safely."

## Enterprise path
Sell per-seat to marketing departments, then use the compliance story (audit log of every agent action, tokenised customer data, approval policies set by a CMO or legal) to get security review passed. Add SSO and central policy packs (regulated claims for finance and health, brand kits) and expand from marketing to sales and comms teams.

## Business model & pricing
Per seat about $40 per month for the phone plus cloud team, $80 with desktop. Agency plan of $300 per month for 10 client workspaces. Enterprise: $30-60 per seat per month with an annual contract plus a policy-pack add-on. BYO model key keeps gross margin high (guess: 80%+).

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They build horizontal assistants and vendor-locked suites (Google Ads AI, Meta Advantage+ optimise for their own platform's spend, not yours). A neutral, cross-platform policy layer that limits their spend is against their interest. Marketing-specific approval and claim workflows are too niche for them.

## Biggest risk
Ad platform API access and connector maintenance; and incumbents (HubSpot, Jasper, Adobe) bolting on agents with similar guardrails. Also, marketers may want creative quality more than governance, so the wedge could feel like a boring safety tool.

## Uses founder's existing assets
Scoped vanaras with locked tools, handover between agents, scheduled background jobs, on-device approvals and spend rules, reference-token privacy, the MCP pipeline classifying tools by role (read, write, spend, publish), voice approvals, BYO model key. New: cloud and desktop surfaces, ad and CMS connectors.

## Scores
market_size: 7
defensibility: 5
feasibility_solo_30k: 7
asset_fit: 9
excitement: 7
