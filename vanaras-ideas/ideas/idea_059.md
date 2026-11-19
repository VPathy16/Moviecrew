# Tallywise — a personal team of agents for every data analyst, with a memory of every metric definition you've ever agreed
Lens: Data analysts
## Customer & pain
Individual analysts and small analytics teams (in-house at 50-2,000 person companies, plus freelance/consultancy analysts) who pay from their own or team budget. Pain: 60% of the week is not analysis. It is re-running the Monday report, answering "why did revenue dip?" pings from Slack, reconciling two dashboards that disagree, and rediscovering what "active user" meant last quarter. Tribal knowledge about definitions, quirks and caveats lives in the analyst's head and dies when they leave. Text-to-SQL bots fail because they don't know the analyst's context, and analysts can't send raw customer data to a model.
## Product
- Phone: the analyst's on-call vanara. Overnight, cloud agents run the recurring pulls; at 7am the phone says "Signups down 12% WoW; 80% is one paid channel, tracking broke on Friday. Approve sending a note to the marketing owner?" Voice queries while commuting ("what did we tell finance about churn definition?"). Approvals happen on the phone.
- Cloud: scheduled 24/7 agents (a "Refresh" vanara, an "Anomaly" vanara, a "Stakeholder-questions" vanara) run queries read-only against the warehouse via MCP, build drafts, and keep a log.
- Desktop: a "Workbook" vanara drives Excel, Sheets, Tableau/Looker/Power BI and notebooks through the UI where no API exists, fixing the ugly last mile of decks and spreadsheets.
- Shared memory + handover: a metric ledger (definition, owner, SQL, known caveats, who was told what). Anomaly hands to Refresh, which hands to the desktop agent for the deck, which hands to the phone for approval. Reference tokens mean row-level customer data never reaches the model; agents see schemas, aggregates and tokens, and results are rehydrated on-device or in the customer's own environment.
## Wedge (first product, first 10 customers)
"Monday Report Autopilot": connect warehouse read-only (Snowflake/BigQuery/Postgres) plus Slack; the agent rebuilds one recurring report, explains week-on-week movement, and drafts replies to the stakeholder questions. Sell to 10 freelance and in-house analysts found via analytics Slack communities, LinkedIn and r/dataanalysis. Free 2-week trial, BYO model key.
## Enterprise path
Every analyst gets a team; the metric ledger becomes the team's shared, audited semantic layer. Then extend to finance, ops and PMs as "analyst-adjacent" employees. Admin console: spend caps, tool allowlists per role, approval rules, audit log, SSO, data-residency (agents run in customer VPC). Land via a team of 5 analysts, expand to the business-user seats.
## Business model & pricing
$49/analyst/month Pro (BYO key), $99 with managed models and cloud runtime hours. Team tier $30/seat plus platform fee ($500/mo) for shared ledger and governance. Enterprise: custom, VPC deployment. Guess: ~$12K ARR from 10 users; 200 paying analysts is roughly $120K ARR.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They ship horizontal agents and their own BI copilots (Fabric, Gemini in BigQuery), each locked to their own stack. Analysts live across warehouses, BI tools from many vendors and spreadsheets; a neutral, cross-vendor agent with on-device data privacy and a personal metric memory is not their priority. Note they may add memory features; the ledger's depth is the moat.
## Biggest risk
Trust: one wrong number sent to a stakeholder ends the product. Mitigated by mandatory approvals and showing SQL and lineage, but accuracy on messy real schemas is unproven. Also competition from Julius, Hex Magic, and warehouse-native copilots (flagged from memory; may be outdated).
## Uses founder's existing assets
Scoped vanaras with locked tool sets (read-only SQL vs write vs send); handover between agents; scheduled background jobs; on-device approvals and spend rules; reference-token privacy layer (keeps rows away from the model); MCP pipeline classifying warehouse/BI tools by role (read, write, send); voice; BYO key. New: desktop agent and cloud runtime.
## Scores
market_size: 7
defensibility: 6
feasibility_solo_30k: 7
asset_fit: 8
excitement: 7
