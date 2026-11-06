# Tether — a per-employee agent team on Android Enterprise work profiles that keeps company data on the device
Lens: Vanaras on company-issued devices via MDM

## Customer & pain
Buyer: IT/security lead (with a COO sponsor) at 200-5,000 person companies with field, frontline or regulated staff: clinics, logistics, field-service, real estate, insurance adjusters, construction. They issue managed Android phones (Intune, Workspace ONE, Knox, Google Android Enterprise). Today, staff paste customer data into consumer AI apps (shadow AI), or get no AI at all because CISOs cannot approve tools that send data to a model. Field workers lose hours to admin: job notes, follow-up messages, scheduling, reminders, ticket updates.

## Product
Vanaras ships as a managed app in the Android work profile, pushed and configured by MDM (managed app config, managed Google Play). Each employee gets a small team of scoped vanaras (Scheduler, Field Notes, Customer Follow-up, Expenses), each locked to its own tools. Reference tokens mean names, numbers and records never reach the model; the device resolves them locally. Approvals and spend limits are enforced on-device from an IT-signed policy pushed via MDM. Cloud: the employee's team keeps working after hours (drafts follow-ups, chases tickets) using tokenised data. Desktop: a companion runs the same team on the laptop for browser and file work. Shared memory plus agent-to-agent handover means a voice note on the phone becomes a ticket update, then a customer email drafted on the desktop, without re-explaining anything. IT gets an audit log of every tool call and approval.

## Wedge (first product, first 10 customers)
First product: "Field Notes agent" for Android work profiles. Voice-dictated job notes become structured updates in the company's system through MCP tools, with approval on the device. Sell to 10 small field-service and clinic-group firms (50-300 devices) that already run Intune or Knox. Start with a 30-day pilot on 20 devices, priced flat. Find them through MDM resellers and MSPs, who want an AI upsell.

## Enterprise path
Pilot, then department, then company. Ship the security pack early: MDM app-config schema, SSO (Entra/Google), audit export to SIEM, data-residency statement, BYO model key or the company's own Azure/Bedrock endpoint. Then SOC 2 Type I, then Type II. Add iOS managed apps later. Partner with MSPs as the channel.

## Business model & pricing
Per managed device per month: $12 for the phone team, $25 with cloud and desktop surfaces, and a $5k annual platform fee for the policy console. Model usage is passed through or BYO key. MSP resale margin of 20%.

## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They sell horizontal assistants tied to their own cloud and models. A vendor-neutral, model-agnostic agent layer with on-device enforcement, and reference tokens so data never leaves the device, cuts against their data-hungry model. Microsoft Copilot is Microsoft-365-centric, and mobile frontline work on mixed stacks is low priority for them. (Guess: Google may add work-profile agents in Gemini for Workspace; this is the main threat.)

## Biggest risk
Enterprise sales cycles and security review are slow for a solo founder, and Google or Microsoft may bundle "good enough" managed mobile agents. A vendor-security questionnaire could also stall pilots before SOC 2 exists.

## Uses founder's existing assets
Nearly all of UNO: scoped vanaras, on-device approvals and spend rules, reference-token privacy layer, MCP pipeline with tool classification, handover between agents, scheduled jobs, voice, and BYO model key. New work: MDM managed-config, work-profile packaging, audit log, and admin console.

## Scores
market_size: 8
defensibility: 6
feasibility_solo_30k: 6
asset_fit: 9
excitement: 7
