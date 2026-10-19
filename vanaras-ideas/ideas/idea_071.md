# Dukacrew — a phone-native back-office crew for informal shop owners, paid by their mobile-money float
Lens: Emerging markets outside India (SE Asia, Africa, LatAm)
## Customer & pain
The paying customer is the informal SME owner (kiosk, salon, spare-parts stall, small wholesaler) in Kenya, Nigeria, Indonesia, the Philippines, Brazil. Their business runs on one mid-range Android: WhatsApp orders, M-Pesa/GCash/Pix/OPay payments, a paper debt notebook. Pain: unpaid customer credit (often 20-30% of sales), missed supplier reorders, payments they cannot reconcile against chats, no idea of real profit. No laptop, no accountant, no time. (Figures are guesses.)
## Product
Phone: a small crew of vanaras. Collector chases debtors politely in the local language by message and voice note. Restocker watches sales and drafts supplier reorders. Bookkeeper matches mobile-money SMS/notifications to chats and writes the ledger. Each is scoped to its own tools; spend caps and approvals are enforced on the device (owner taps to approve a reorder, cap per day). Customer phone numbers and balances never reach the model (reference tokens), which matters for trust and local data-protection laws. Cloud: agents keep running overnight, compiling supplier price comparisons and weekly cash reports while the phone is off. Desktop: for the owner's nephew/accountant or a wholesaler, a light web/desktop view of the same ledger and approvals. Shared memory means Collector knows what Restocker just ordered on credit, and handover between agents (a paid debt triggers a restock) works with no human relaying.
## Wedge (first product, first 10 customers)
Collector only: "get paid what you're owed". Works from WhatsApp/SMS notifications, no integration approvals needed. First 10: hand-recruited salon and hardware-shop owners in one Nairobi or Lagos neighbourhood (via a relative or local fixer), with success-fee pricing. Measure recovered shillings per week.
## Enterprise path
Wholesalers, FMCG distributors and microfinance lenders manage hundreds of retailers. They buy a distributor edition: each retailer gets a crew under the distributor's rules (credit limits, approved SKUs), and the distributor gets the reorder pipeline and repayment data. That maps to "every employee gets their own team, under the company's rules", with the retailers as the extended workforce. Later: banks/MNOs as channel partners.
## Business model & pricing
Freemium: free tier with the Collector; $3-5/month for the full crew, paid via airtime/mobile money; 1-2% success fee on recovered debt; distributor SaaS at $0.5-1 per active retailer per month. BYO model key gets swapped for pooled cheap open models to keep unit cost under $0.30 per user per month (guess).
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Low ARPU, local languages and code-mixing, informal workflows, and per-country payment quirks make it unattractive to them. Google and Meta go for horizontal assistants and business-messaging APIs, not on-device spend rules for a kiosk. On-device enforcement and token-based privacy are a poor fit for cloud-first assistants.
## Biggest risk
Low willingness to pay, and distribution: fragmented markets, WhatsApp/Play policy on reading notifications and automating messages, and the risk that mobile-money operators (Safaricom, GCash) bundle something similar.
## Uses founder's existing assets
Scoped vanaras and handover between agents; on-device approvals and spend rules; reference-token privacy; scheduled background jobs; the MCP pipeline (mobile-money and messaging tools classified by role, service-agnostic across countries); voice for voice-note collection and low-literacy users; BYO key (partner/distributor keys).
## Scores
market_size: 8
defensibility: 5
feasibility_solo_30k: 6
asset_fit: 8
excitement: 7
