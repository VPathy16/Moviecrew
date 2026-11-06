# Ledgerhand — a compliance-safe agent team for every relationship manager at a wealth firm
Lens: Regulated finance (banks, insurers, wealth managers)
## Customer & pain
Buyer: COO/CCO of independent wealth managers and RIAs (20-300 advisers), later bank private-banking units. Advisers spend ~40% of time on meeting prep, follow-ups, KYC refreshes, suitability notes and CRM entry. They already use WhatsApp, calls and personal phones for client contact, and regulators fine firms for off-channel communications (SEC/FCA/SEBI-style record-keeping actions). Firms ban AI tools because client data would leak into models, so advisers use ChatGPT secretly.
## Product
- Phone vanara: captures client calls/messages on the adviser's phone (recorded, archived), drafts follow-ups, sets reminders (birthdays, maturities, review dates). It acts only through approved tools.
- Cloud vanara: overnight, prepares next-day meeting briefs, KYC refresh packets, and suitability-note drafts. It keeps running when devices are off.
- Desktop vanara: fills the CRM/portfolio-system forms and pulls statements, using computer use in the firm's own apps.
- Shared memory + agent sync: a call on the phone becomes a follow-up task in the cloud and a CRM entry on desktop, with one audit trail. Client identifiers are reference tokens, so the model never sees names or account numbers. Approvals and spend/action limits are enforced on-device, and the compliance officer sets them centrally.
## Wedge (first product, first 10 customers)
"Compliant follow-up": phone app that turns each client call or chat into a compliant, archived note plus a drafted follow-up, with adviser approval. It is sold to small RIAs and family offices (5-30 advisers) that already fear off-channel fines. Reach the first 10 through compliance consultants and adviser-community referrals, with a paid pilot of about $99/adviser/month. Build the Android app first (existing UNO base).
## Enterprise path
Pilot, then a firm-wide policy console (scoped vanaras per role: adviser, assistant, compliance), then SSO/SCIM, on-prem or VPC cloud, BYO model key or firm-approved model, SOC 2, and immutable audit export to the firm's archiving vendor. Then banks' private-banking desks with model-risk documentation.
## Business model & pricing
Per seat SaaS: $100-250/adviser/month, plus a policy/audit platform fee of $1-3K/month per firm. 100 firms x 50 advisers x $150 = $9M ARR. Later: insurers' agent networks.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell horizontal assistants and cannot ship per-firm rule enforcement and liability for one vertical's record-keeping regime. Copilot lives in Microsoft 365 rather than on advisers' personal phones and calls. Firms want a neutral layer with BYO model and on-device data isolation that is not tied to one model vendor. Regulated-vertical services are a slow, low-margin fit for them.
## Biggest risk
Sales cycles and compliance proof: regulators may not accept AI-drafted suitability notes, and firms may demand certifications (SOC 2) a solo founder lacks early. Also call-recording legality varies by country (guess: needs per-jurisdiction consent flows).
## Uses founder's existing assets
Scoped vanaras with locked tools (role separation, e.g. adviser vs compliance); handover between agents (call to task to CRM entry); scheduled background jobs (overnight briefs); on-device approvals and spend rules (the core compliance control); reference-token privacy (no client PII to the AI); MCP pipeline classifying tools by role (plugging into CRMs); voice; BYO model key.
## Scores
market_size: 8
defensibility: 7
feasibility_solo_30k: 6
asset_fit: 9
excitement: 8
