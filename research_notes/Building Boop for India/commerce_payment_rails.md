# Commerce and payment rails an AI agent can use for errands in India (as of November 2026)

Scope note: research done 6 November 2026. "Pilot" means a closed or invite-only programme; "GA" means anyone eligible can sign up. Dates are given for every item; older items are marked with their date. Several 2026 claims rest on single press reports or vendor docs; this is flagged where it applies.

## 1. UPI and AI agents: NPCI initiatives, Reserve Pay, UPI Circle, AutoPay, and what a non-bank app needs

### Takeaway
Agentic UPI exists today only as merchant-specific pilots run through payment aggregators (Razorpay with OpenAI from Oct 2025, with Claude from Feb 2026) on top of UPI Reserve Pay (single-block-multiple-debit) and UPI Circle. NPCI's network-wide "Unified Agent Protocol" (an agent registry plus user-set limits) was due to launch at Global Fintech Fest on 10 Sept 2026 but was put on hold pending RBI clearance, and no relaunch had been reported by early November 2026. A third-party app like Boop can hand off UPI intent links or QR codes that a merchant's aggregator generates without any licence. Initiating payments as a payer app requires TPAP status through a sponsor PSP bank, and collecting money as a merchant intermediary requires RBI payment-aggregator authorisation or a PA partner.

### Cited Findings

**ChatGPT pilot (Oct 2025), a pilot**
- NPCI, Razorpay and OpenAI announced "Agentic Payments" on 9 Oct 2025 to test whether AI agents holding payment credentials can complete transactions for users in a safe, user-controlled way. — [Business Today, 9 Oct 2025](https://www.businesstoday.in/tech-today/news/story/razorpay-npci-openai-launch-pilot-for-agentic-payments-where-ai-powered-shopping-meets-upi-497545-2025-10-09); [Razorpay newsroom](https://razorpay.com/newsroom/razorpay-npci-and-openai-come-together-to-launch-agentic-payments-ushering-in-ai-driven-commerce-at-national-scale/)
- The banking partners are Axis Bank and Airtel Payments Bank. The pilot uses UPI Circle (extended authorisation) and UPI Reserve Pay (funds blocking). BigBasket was among the first merchants, and TechCrunch also named Vi (Vodafone Idea) mobile recharges. — [Onmanorama, 9 Oct 2025](https://www.onmanorama.com/news/business/2025/10/09/npci-razorpay-openai-chatgpt-payments.html); [Storyboard18](https://www.storyboard18.com/digital/chatgpt-integrates-upi-payments-in-india-through-bigbasket-pilot-82421.htm); [TechCrunch](https://techcrunch.com/?p=3055954)
- Razorpay told TechCrunch the pilot would roll out nationwide and become widely available "in the coming months". This is a company claim, and I could not verify GA status. — [TechCrunch](https://techcrunch.com/?p=3055954)

**Claude pilot (Feb 2026), a pilot**
- Razorpay and NPCI launched Agentic Payments on Claude on 20 Feb 2026 at the India AI Impact Summit, with Zomato, Swiggy and Zepto as launch merchants. Razorpay's blog says it is "currently in a pilot phase with a select group of users". — [Razorpay blog, 20 Feb 2026](https://razorpay.com/blog/agentic-payments-and-npci/); [Business Today, 20 Feb 2026](https://www.businesstoday.in/technology/news/story/razorpay-npci-launch-agentic-payments-on-anthropics-claude-zomato-swiggy-zepto-go-live-517307-2026-02-20); [Entrackr](https://entrackr.com/snippets/razorpay-and-npci-bring-agentic-payments-to-claude-at-india-ai-impact-summit-11138579)
- The mechanism is "built on UPI Reserve Pay". The user gives a one-time, consent-based authorisation that sets a spending limit for a merchant. Within that limit the agent can transact without repeated PIN prompts, and the user can revoke consent instantly. The only access route is an early-access sign-up form; there is no published developer onboarding, and the blog does not say whether other agents can integrate. — [Razorpay blog](https://razorpay.com/blog/agentic-payments-and-npci/)
- One secondary source says Razorpay was piloting with 15–20 merchants, and that Cashfree and PayU also "shipped agentic payments on LLM surfaces" in Feb 2026. — [Stellagent analysis](https://stellagent.ai/insights/india-agentic-commerce-fintech-payment) (secondary, unverified)

**Unified Agent Protocol (UAP): announced, then on hold**
- Reuters (via Inc42, 1 Sept 2026) reported that NPCI planned to unveil a "Unified Agent Protocol" at GFF 2026. It would let AI agents make small-value payments without per-transaction approval, building on UPI Circle and Reserve Pay. Users would set rules on when and how much agents can pay. The first targets were low-value, high-frequency purchases such as groceries, and merchants would get infrastructure to integrate directly. NPCI declined to comment. — [Inc42, 1 Sept 2026](https://inc42.com/buzz/npci-to-launch-agentic-payments-on-upi-report/)
- Reuters also reported that an NPCI-run registry would vet and monitor AI agents making payments. — [CIO.inc](https://www.cio.inc/india-readies-upi-to-support-payments-initiated-by-ai-agents-a-32777); [Outlook Business](https://www.outlookbusiness.com/news/india-plans-ai-powered-upi-payments-framework-through-unified-agent-protocol)
- Business Standard (11 Sept 2026) reported that NPCI temporarily put the UAP launch on hold while it awaits RBI clearance and builds safeguards. The launch had been planned for 10–11 Sept, and NPCI is expected to address concerns "over the next few months" before seeking approval again. — [Business Standard, 11 Sept 2026](https://www.business-standard.com/finance/news/upi-s-ai-protocol-temporarily-on-hold-as-npci-builds-safeguards-126091101413_1.html) (paywalled; details via search snippet and [rango.design GFF roundup](https://rango.design/articles/global-fintech-fest-2026-launches))
- On 10 Sept 2026, NPCI chairman Ajay Kumar Choudhary said NPCI is "examining the protocols that may be required to identify and authorise digital agents". Per the GFF roundup's paraphrase, he added that AI may recommend a payment but authentication and settlement must follow fixed, auditable rules. — [rango.design](https://rango.design/articles/global-fintech-fest-2026-launches); [theroberthu.com](https://theroberthu.com/blog/npci-upi-ai-agent-authorization)
- Conflict: a ShareWire post (9 Sept 2026) describes the UAP as formally presented and live. Later reporting contradicts it, and one analysis notes the claim rests on a single report, with no published spec, NPCI circular or RBI notification. — [ShareWire](https://www.sharewire.net/blog/npci-unified-agent-protocol-upi-agentic-payments-gff-2026/) vs. [kryptonforge.in analysis](https://kryptonforge.in/blog/2026-07-10-upi-unified-agent-protocol-agentic-payments)
- No liability framework for agent errors has been published. Commentary notes that UPI dispute resolution assumes a human approving each payment. — [Rotavision](https://www.rotavision.com/blog/agentic-payments-upi-ap2-accountability/)

**Other GFF 2026 agentic launches (8–11 Sept 2026, reported by MediaNama via a roundup)**
- Amazon Pay launched a "smart wallet" that lets AI agents make UPI payments for a user, with biometric authentication. Agentic payments went live first for flight booking. — [rango.design](https://rango.design/articles/global-fintech-fest-2026-launches)
- Pine Labs and L&T Finance launched agentic commerce in the PLANET app using Pine Labs' P3P protocol. The first use case is an agent booking flights within a user-set spending limit. — [rango.design](https://rango.design/articles/global-fintech-fest-2026-launches); [Inc42](https://inc42.com/buzz/npci-to-launch-agentic-payments-on-upi-report/) (P3P launched earlier in 2026)
- NPCI launched AiNxt (an open-source agentic AI platform) and AtOM (orchestration with signed audit trails for UPI partner onboarding). The RBI Governor launched MyUPI, a consolidated view of UPI transactions and AutoPay mandates across apps, running on NPCI's FiMI language model. — [rango.design](https://rango.design/articles/global-fintech-fest-2026-launches)

**UPI Reserve Pay (single-block-multiple-debit, SBMD)**
- The RBI announced SBMD for UPI in December 2022. — [Inc42](https://inc42.com/buzz/upi-to-soon-have-single-block-and-multiple-debits-functionality-rbi)
- NPCI OC No. 228/2025-26 (8 Oct 2025) reportedly renamed SBMD "UPI Reserve Pay" and extended it to all UPI funding sources (savings, current, OD, RuPay credit card, credit lines). I saw this only in a third-party summary of NPCI circulars. — [NPCI circular index summary](https://javajack.github.io/broking-kyc/reference/circulars/npci/); [NPCI circulars](https://npci.org.in/what-we-do/upi/circular)
- Pine Labs docs state that NPCI caps the Reserve Pay mandate at ₹10,000 and that no pre-debit notification is required. Bank coverage has changed over time, starting with ICICI and Axis and later adding SBI, Kotak, IDFC and others. — [Pine Labs Reserve Pay](https://www.pinelabs.com/docs/online-payments/upi-reserve-pay); [Pine Labs FAQs](https://www.pinelabs.com/docs/online-payments/upi-reserve-pay/faqs)
- Under Cashfree's implementation, the merchant blocks a maximum amount once and then debits it partially or several times until the limit is used up or the mandate expires. Unused funds are released through a cancel action; pause is not supported. — [Cashfree docs](https://www.cashfree.com/docs/payments/upi-reserve-pay/upi-reserve-pay)
- Reserve Pay is set up on the merchant side through a payment gateway (the mandate is created against the merchant). Setu, Cashfree, Pine Labs and Razorpay document it as a merchant PG feature. — [Setu UMAP Reserve](https://docs.setu.co/payments/umap/mandates/reserve); [Cashfree](https://www.cashfree.com/docs/payments/upi-reserve-pay/reserve-pay)

**UPI Circle (delegated payments)**
- Full delegation lets a primary user authorise a secondary user up to ₹15,000 a month per delegation, with a ₹5,000 per-transaction cap and a ₹5,000 limit in the first 24 hours. Under partial delegation the primary approves each payment with their PIN. — [Razorpay guide](https://razorpay.com/blog/what-is-upi-circle/); [Outlook Money](https://www.outlookmoney.com/retirement/news/ncpis-new-upi-circle-know-how-this-feature-eases-online-payment-for-you); [Ujjivan SFB](https://www.ujjivansfb.bank.in/banking-blogs/banking-services/upi-circle-delegated-payments-how-it-works-limits)
- Conflict: one Paytm explainer says NPCI has not published a separate fixed limit for delegation. Support across UPI apps is uneven; it is BHIM-first, and others were still testing. — [Paytm](https://paytm.com/blog/payments/upi/what-is-upi-circle-transaction-limits); [Suryoday Bank](https://suryoday.bank.in/blogs/upi-circle/)

**UPI AutoPay**
- Razorpay docs say NPCI Circular OC-163/OC-163A makes AutoPay mandates interoperable: a mandate updates automatically when the customer changes UPI app, without re-registration. Compliance starts July 2026. Other sources cite OC-223 (7 Oct 2025), so the circular numbering is unresolved. — [Razorpay AutoPay interoperability docs](https://razorpay.com/docs/payments/recurring-payments/autopay-interoperability); [Inc42](https://inc42.com/buzz/npci-to-let-users-port-upi-autopay-mandates-across-apps-report/)
- RBI e-mandate limits for AutoPay are covered in section 2.

**What a non-bank app needs**
- To be a TPAP (a payer-side UPI app like GPay or PhonePe), an app must be sponsored by a PSP bank that raises the onboarding request to NPCI, pass NPCI review and sandbox testing, sign agreements with NPCI and the bank, and keep UPI data in India. NPCI lists no fixed fee, but banks may charge evaluation and integration fees. — [Razorpay TPAP guide](https://razorpay.com/blog/tpap-integration-go-ahead-requirements-process-benefits-guide/); [NPCI roles and responsibilities](https://www.npci.org.in/what-we-do/upi/roles-responsibilities); [IndusInd R&R PDF](https://bank.indusind.com/content/dam/indusind-corporate/Other/UPI-R&R-of-NPCI-PSP-TPAPs.pdf)
- To collect or route funds for merchants, an entity needs RBI payment-aggregator authorisation. Section 2 covers net worth and onboarding rules.

### Inferences
- Boop's current flow (a Swiggy-generated UPI intent or QR that the user approves with their PIN in their own UPI app) puts Boop outside every licence category. Swiggy and its aggregator are the payee side, and the user's TPAP is the payer side. This is the lowest-risk pattern and matches how Swiggy's own MCP works (see section 6).
- "Pay without asking each time" in India currently means a merchant-side Reserve Pay mandate (under ₹10,000) created through that merchant's aggregator, inside a pilot. Boop cannot create such mandates on its own. It would need either a merchant that exposes Reserve Pay through its MCP (Zepto documents this, see section 6) or a partnership with Razorpay, Cashfree or Pine Labs.
- If the UAP ships, it is the most likely route for an independent agent (Boop) to register and get user-delegated spending limits across merchants. Until NPCI publishes a spec and the RBI clears it, Boop should design for a human PIN on every payment, with Reserve Pay as an optional, merchant-specific add-on.
- Becoming a TPAP is not realistic for an open-source assistant: it needs a sponsor bank, NPCI audits and data localisation, and it is the role GPay and PhonePe hold.

### Gaps
- No NPCI primary circular for the UAP, and no RBI decision on it, was found as of early November 2026.
- No official NPCI circular text for UPI Circle limits or the ₹10,000 Reserve Pay cap was retrieved; both rest on PSP and bank docs.
- Whether the ChatGPT and Claude agentic payment pilots moved to GA, and whether non-OpenAI/Anthropic agents can use Razorpay's agentic flow, is undocumented.

## 2. RBI rules relevant to AI-agent-initiated payments

### Takeaway
As of November 2026 the RBI has issued no circular specific to AI agents in payments. The binding rules are general. The Authentication Directions (25 Sept 2025, in force 1 April 2026) require two factors, one of them dynamic, for every digital payment unless exempt. The Digital Payments E-mandate Framework 2026 (21 April 2026) allows recurring debits without additional authentication up to ₹15,000, or ₹1 lakh for insurance, mutual funds and credit-card bills, after a one-time authenticated registration, with 24-hour pre-debit notices. The PA Directions (15 Sept 2025) govern anyone holding merchant funds. RBI leadership's public line is that accountability stays with the regulated entity: "you cannot outsource the consequence".

### Cited Findings
- **Authentication Directions:** The Authentication Mechanisms for Digital Payment Transactions Directions, 2025 (RBI/2025-26/79, 25 Sept 2025) take effect on 1 April 2026. They require at least two factors of authentication, one of them dynamic and unique to the transaction, except for explicit exemptions. Issuers may adopt risk-based authentication but are not required to. Cross-border card-not-present obligations fall due on 1 Oct 2026. — [Probe42 summary](https://resources.probe42.in/regulatory-updates/rbi-circulars/authentication-mechanisms-digital-payment-transactions-2025/); [Veritect](https://veritect.ai/digital-data-ai-law/rbi-authentication-mechanisms-digital-payments-2025); [ecorpit](https://ecorpit.com/ecorpit-rbi-afa-authentication-retrofit-service-india-2026/)
- **E-mandate Framework 2026:** The Digital Payments E-mandate Framework, 2026 was notified on 21 April 2026. It consolidates the rules for recurring payments on cards, PPIs and UPI.
  - Recurring debits up to ₹15,000 per transaction can run without AFA once the mandate is registered with AFA, and debits above that need AFA.
  - Insurance premiums, mutual fund subscriptions and credit-card bill payments can run without AFA up to ₹1,00,000 per transaction.
  - Banks must send a pre-debit notice at least 24 hours ahead with merchant, amount and date, and the user can opt out.
  - Every mandate must state a validity period, and the user can pause, modify or cancel it, with authentication.
  — [Saraf & Partners](https://sarafpartners.com/rbi-publishes-the-digital-payments-e-mandate-framework-2026/); [LexOrbis](https://www.lexorbis.com/rbis-digital-payments-e-mandate-framework-2026-consolidated-directions-for-recurring-digital-transactions/); [Business Today, 22 Apr 2026](https://www.businesstoday.in/personal-finance/banking/story/now-control-your-auto-debit-payments-rbis-new-rules-explained-526860-2026-04-22)
- The ₹15,000 general e-mandate limit has applied since 2022, and the ₹1 lakh limit for MF, insurance and credit-card bills since Dec 2023. — [Khaitan & Co](https://www.khaitanco.com/thought-leaderships/RBI-enhances-transaction-limits-for-processing-of-e-mandates-for-recurring-transactions:-from-INR-5000-to-INR-15000); [Business Standard, Dec 2023](https://business-standard.com/finance/news/automatic-payment-limit-through-upi-raised-to-rs-1-lakh-says-rbi-123121201097_1.html)
- **PA Directions:** The RBI (Regulation of Payment Aggregators) Directions, 2025 were issued on 15 Sept 2025 and supersede the 2020–21 guidelines.
  - Three categories: PA-Physical, PA-Online and PA-Cross Border.
  - Non-banks need RBI authorisation through the Pravaah portal.
  - Net worth must be ₹15 crore at application and ₹25 crore by the end of the third financial year after authorisation.
  - Merchant onboarding requires KYC, including CKYCR retrieval, with escrow and settlement rules.
  — [Outlook Business](https://www.outlookbusiness.com/news/rbi-issues-new-master-directions-for-payment-aggregators-rules-take-effect-immediately); [Mondaq analysis](https://www.mondaq.com/india/financial-services/1689480/an-analysis-of-the-reserve-bank-of-indias-master-direction-on-regulation-of-payment-aggregators-2025); [Inc42](https://inc42.com/buzz/rbi-issues-new-master-directions-for-payment-aggregators)
- **No agent-specific RBI rule:** The Aapti Institute says India's agentic payments oversight is a "nascent AI governance layer" that is principles-based and draws on the RBI's FREE-AI framework, and that India lacks a comprehensive regulatory framework for agentic commerce. — [Aapti Institute](https://aapti.in/blog/from-prompts-to-payments-the-rise-of-agentic-ai-in-payments/)
- **FREE-AI:** The RBI's FREE-AI committee report (13 Aug 2025) places accountability on the regulated entities that deploy AI. — [RBI FREE-AI report PDF](https://rbidocs.rbi.org.in/rdocs/PublicationReport/Pdfs/FREEAIR130820250A24FF2D4578453F824C72ED9F5D5851.PDF); [search summary](https://www.zeebiz.com/personal-finance/banking/news-rbi-governor-sanjay-malhotra-s-big-ai-warning-careless-use-could-fuel-financial-instability-400299)
- **Governor Malhotra (FIBAC, around Aug 2026):** Banks keep ultimate responsibility for AI-driven decisions and cannot shift blame to vendors or algorithms. He called for meaningful human oversight where errors cause material harm and announced a Digital Payment Intelligence Platform for fraud detection. — [Curiouscats](https://curiouscats.ai/artificial-intelligence/rbi-governor-sanjay-malhotra-says-ai-can-do-for-lending-what-upi-did-for); [Analytics Insight](https://www.analyticsinsight.net/news/rbi-urges-banks-to-use-ai-for-loans-while-keeping-human-oversight); [The420.in](https://the420.in/rbi-digital-payment-intelligence-platform-ai-fraud-detection-banks/)
- **Deputy Governors at GFF 2026:** Deputy Governor Rohit Jain (9 Sept 2026): "an institution may outsource the computation, but it cannot outsource the consequence." Deputy Governor S.C. Murmu (11 Sept 2026): technology "can distribute a service, but it cannot distribute responsibility." — [rango.design, citing RBI speeches](https://rango.design/articles/global-fintech-fest-2026-launches)
- **Regulatory gate on UAP:** RBI clearance is the stated gate for NPCI's UAP, per the 11 Sept 2026 Business Standard report. — [Business Standard](https://www.business-standard.com/finance/news/upi-s-ai-protocol-temporarily-on-hold-as-npci-builds-safeguards-126091101413_1.html)

### Inferences
- Per-payment human authentication (UPI PIN) is the default the RBI framework assumes. "Agent pays without asking" fits only inside an exempt or pre-authorised construct: an e-mandate under ₹15,000, a Reserve Pay block, or UPI Circle delegation. Each of these was authenticated once by the user, at the bank or TPAP, not by the agent.
- Because liability sits with regulated entities, banks and PAs will push risk controls (spending caps, merchant allowlists, revocation) onto agent platforms through contracts. Boop should expect partner terms, not RBI rules, to be the binding constraint.
- Boop should not hold, route or settle funds. Doing so would trigger PA authorisation (₹15 crore net worth), which an open-source project cannot meet.

### Gaps
- No RBI circular, discussion paper or FAQ on AI agents in payments was found. If one exists, it would be on rbi.org.in, which I did not search directly.
- The RBI's specific concerns behind the UAP hold have not been published.

## 3. BBPS (Bharat Connect) for bills and recharges

### Takeaway
BBPS, rebranded Bharat Connect and run by NPCI Bharat BillPay Ltd (NBBL), lists more than 20,000 billers. These cover electricity, water, gas, LPG, telecom postpaid, DTH, FASTag, credit cards, loan EMIs, insurance, education, municipal taxes and, voluntarily, mobile prepaid. A non-bank app joins as an Agent Institution under a bank's operating unit (COU/BOU) through an aggregator such as Setu, Cashfree, PayU or Pine Labs, which handles NBBL certification. Setu quotes a 2–3 week go-live. Pricing (interchange and customer convenience fee caps) is set by NPCI per category, and aggregator fees are not public. Setu has shipped an agentic bill-payment MCP inside ChatGPT and Claude (Dec 2025), so the pattern works, but it pays over UPI first and only then posts the BBPS transaction.

### Cited Findings
- Bharat Connect, formerly Bharat BillPay, is the BBPS platform conceived by the RBI and operated by NBBL; the rebrand was announced at GFF 2024. NBBL's deck cites 22,400+ billers, 5 lakh+ active agents and a 1 billion transactions-a-month ambition. — [Wikipedia: Bharat Connect](https://en.wikipedia.org/wiki/Bharat_Connect); [Bharat Connect overview deck](https://www.bharat-connect.com/strapi/uploads/Bharat_Connect_Overview_Deck_for_website_29c4340e4a.pdf)
- **Categories:** Setu's support page lists 17 categories live on BBPS as of Aug 2020, including utilities, telecom postpaid, DTH, gas cylinders, FASTag, loan repayment, credit cards, insurance, education fees and municipal taxes. NPCI sets guidelines and pricing per category. (Dated Aug 2020; more categories have been added since.) — [Setu support](https://support.setu.co/support/solutions/articles/81000382821-who-is-eligible-for-bbps-)
- The RBI allowed mobile prepaid recharges as a BBPS biller category on a voluntary basis. — [RBI notification PDF](https://rbidocs.rbi.org.in/rdocs/notification/PDFs/NT5405CBB38838F241998F180B0130030461.PDF) (via search snippet)
- Newer categories include Forex Retail (NBBL deck) and Postal Life Insurance premiums (April 2026). — [Bharat Connect deck](https://www.bharat-connect.com/strapi/uploads/Bharat_Connect_Overview_Deck_for_website_29c4340e4a.pdf); [Lokmat Times/ANI](https://www.lokmattimes.com/business/pli-onboarded-on-bharat-connect-digital-premium-payments-expand-to-over-125-crore-policyholders/amp/)
- **Integration path:** Setu BillPay registers the platform as an agent on BBPS, and "all approvals are done by Setu, our bank partner and BBPS". The steps are API keys, NPCI screen approval, test cases, then production credentials. — [Setu API integration docs](https://docs.setu.co/payments/billpay/api-integration)
- Non-bank platforms typically join as Agent Institutions on an existing COU, while banks build their own COU. Setu cites a 2–3 week average go-live for Agent Institutions and 20,000+ billers through one API. — [Setu BBPS COU page](https://setu.co/payments/bbps/cou/)
- Cashfree (with BBPS COU certification), PayU (Connect Agent API) and Pine Labs offer comparable BBPS stacks. — [Cashfree blog](https://www.cashfree.com/blog/cashfree-now-offers-a-complete-bbps-stack-with-bbps-cou-certification/); [PayU docs](https://docs.payu.in/docs/connect-agent-api-integration); [Pine Labs](https://www.pinelabs.com/fintech-infrastructure/bbps)
- **Costs:** The customer convenience fee (CCF) is regulated by NPCI. Agents may charge up to a cap or less, or nothing. Interchange and CCF are set in NPCI pricing circulars (for example NPCI/2022-23/BBPS/012 for FASTag). — [RBL Bank BBPS FAQ](https://www.rblbank.com/wholesale-banking/products-and-services/transaction-banking/digital-banking/bbps); [BC-Bharat FASTag advisory, 2023](https://bharat-connect.com/pdfs/circulars/2023/Advisory-on-Fastag-Recharge-Transactions.pdf); [Setu CCF guide](https://docs.setu.co/payments/billpay/api-integration/customer-convenience-fee)
- An unverified distributor schedule lists a 1.5% commission on Airtel recharges. — [Scribd](https://www.scribd.com/document/866829293/pdf) (unverified)
- **Agentic bill payments:** Setu, a Pine Labs subsidiary, launched "agentic bill payments" inside Claude and ChatGPT around 9–10 Dec 2025, with chat and voice and user-defined limits. — [Business Today, 10 Dec 2025](https://www.businesstoday.in/markets/stocks/story/pine-labs-shares-in-focus-after-unit-launches-agentic-ai-bill-payment-system-key-details-505923-2025-12-10); [Crowdfund Insider](https://www.crowdfundinsider.com/2025/12/256330-fintech-setu-introduces-agentic-bill-payments-experience-via-chatgpt-and-claude/); [Setu product page](https://setu.co/real-time-payments/bbps/agentic-bill-payments)
- **Setu's bill-payment MCP (16 Dec 2025):** It exposes four tools: list billers on Bharat Connect, fetch the bill amount from customer details, initiate payment, and check status. Payment runs over UPI first, and the BBPS transaction is created only after UPI succeeds. The user is redirected to a Setu page to authenticate rather than entering an OTP in chat. Access is by early-access sign-up, and whether third-party agents can connect is not stated. — [Setu engineering blog](https://setu.co/blog/Setu-Bill-Payments-MCP)

### Inferences
- BBPS is the cleanest "errand" rail after food and grocery. It has one integration for electricity, DTH, FASTag, postpaid, LPG, credit cards and (often) prepaid recharges, and bill fetch (amount and due date) suits reminders well.
- For Boop, the realistic options are (a) connecting to Setu's MCP as a client if Setu opens it to third-party agents, or (b) a hosted Boop entity becoming an Agent Institution through Setu, Cashfree or PayU. Option (b) needs a legal entity, KYC and an aggregator contract, which may sit awkwardly with a purely open-source, user-hosted model.
- Prepaid mobile recharge on BBPS is voluntary for operators, so coverage may be partial. Telco or recharge-aggregator APIs may still be needed.

### Gaps
- Current NPCI/NBBL CCF caps and interchange for each category in 2026, and Setu, Cashfree and PayU agent pricing, are not public.
- Whether Setu's MCP accepts arbitrary third-party MCP clients is not documented.
- A full 2026 Bharat Connect category list (including the status of prepaid recharge by operator) was not retrieved.

## 4. ONDC: can an AI agent be or use a buyer app?

### Takeaway
ONDC explicitly allows a buyer network participant (BAP) to be "a voice assistant, chatbot, or any interface" that meets the buyer-app feature requirements, so an AI agent can in principle be a buyer app. Joining as a BAP, however, means registering a business in the ONDC registry and taking on full order, payment and grievance obligations. AI and voice buyer agents exist (Mystore Genie, Gupshup's WhatsApp buyer app, ONDC's Saarthi reference app with Bhashini). I found no official ONDC programme for AI agents or ONDC MCP endpoint, and analysts note that global agent protocols (ACP, AP2, UCP) do not yet reach ONDC.

### Cited Findings
- **Who can be a buyer app:** "Any business with a strong customer base can join ONDC as a buyer network participant." A buyer NP can use an existing app, a white-labelled app, a voice assistant, a chatbot or any interface that integrates with the network and meets the feature requirements. — [ONDC buyer NP page](https://www.ondc.org/pages/buyer-network-participants.html)
- **Required capabilities:**
  - parse search into structured fields and search the network
  - rank results
  - show ratings, reviews and specifications
  - support a multi-seller cart
  - offer a choice of delivery option
  - provide unified checkout and payment initiation
  - confirm the order with the seller and give the buyer an order ID
  Onboarding goes through portal.ondc.org, with a Payment Assurance Program and complaints obligations. — [ONDC buyer NP page](https://www.ondc.org/pages/buyer-network-participants.html)
- **Saarthi:** ONDC's reference app that lets businesses build their own buyer-side apps using Bhashini (the government language AI). Launch date not confirmed. — [Wikipedia: Bhashini](https://en.wikipedia.org/wiki/Bhashini)
- **Mystore Genie (June 2025):** An AI agent on Google Cloud for ONDC buyer journeys, with voice commands for add-to-cart, address change and ordering. — [PR Newswire](https://www.prnewswire.com/in/news-releases/mystore-unveils-mystore-genie-an-ai-agent-built-on-google-cloud-to-supercharge-ondc-network-buyer-journeys-302471365.html)
- **Gupshup (mid-2024, beta):** Launched what it called India's first conversational ONDC buyer app on WhatsApp, starting with food, with RCS and voice "coming soon". — [Gupshup press release](https://www.gupshup.ai/resources/press-releases/gupshup-announces-indias-first-conversational-buyer-app-for-ondc/)
- **Protocol gap:** A 2025–26 analysis says AP2, ACP and UCP connect AI shopping agents to closed checkouts, not yet to ONDC, so ONDC-only MSMEs are invisible to outside agents. — [Raveneye Global](https://raveneyeglobal.com/insights/articles/perplexity-agentic-checkout-meets-ondc-only-msme/)
- **Buyer-app fees:** Unofficial; reports put commissions near 3–4%, with the buyer-app fee built into the declared price. — [echai.ventures](https://echai.ventures/d2c/d2c-ondc/ondc-costs-margins-vs-amazon-flipkart); [Bajaj Finserv, Mar 2026](https://www.bajajfinserv.in/open-network-for-digital-commerce-ondc)
- **Official programmes:** A search for an official ONDC AI-agent programme, MCP integration or agent certification returned only blogs. — [Deepak Bagada blog](https://deepakbagada.in/journal/ondc-ai-agents-agentic-commerce-bharat-2026) (personal analysis)

### Inferences
- Boop has two ONDC paths. (1) It becomes a BAP itself, which requires a registered legal entity, Beckn protocol implementation, payment collection (an RBI-authorised PA partner), grievance officer and settlement duties; this is heavy for an open-source app. (2) It drives an existing buyer app that exposes an API or MCP; none was found. Path 2 depends on a buyer app (Paytm, Magicpin, Mystore, etc.) publishing an agent interface.
- Because ONDC already accepts chatbot and voice buyer interfaces, a Boop-run hosted entity could plausibly certify as a BAP later. It would be the first fully open-source agent buyer app, but that is a long-horizon option.

### Gaps
- No official ONDC 2026 statement on AI agents, MCP or agent buyer apps was found.
- Current BAP onboarding cost, certification timeline and the fee schedule were not found on ondc.org.

## 5. IRCTC trains and other travel (bus, flights)

### Takeaway
Train booking is the most restricted rail. Only IRCTC itself and its authorised B2C partners (for example ixigo, ConfirmTkt, MakeMyTrip, Paytm) can sell tickets online. Running an unauthorised business of "procuring and supplying" tickets is a criminal offence under Section 143 of the Railways Act, and IRCTC has layered on Aadhaar authentication and agent time-bans to fight bots. For an assistant, the safe pattern is a hand-off to an authorised partner's app or ChatGPT app (ixigo has one since April 2026) or the user's own IRCTC session, never automated booking. No public bus (redBus) or flight API or MCP for third-party agents was found, though OTAs are building ChatGPT apps and agentic flight booking launched at GFF 2026 inside Amazon Pay and Pine Labs/L&T apps.

### Cited Findings
- **Tatkal Aadhaar rules:** From 1 July 2025, online Tatkal booking requires an Aadhaar-authenticated IRCTC account, and from 15 July 2025 Aadhaar OTP authentication is required, including at counters and through authorised agents, with the OTP sent to the user's mobile. Authorised agents cannot book opening-day Tatkal in the first 30 minutes (AC 10:00–10:30, non-AC 11:00–11:30). — [DD News](https://ddnews.gov.in/en/indian-railways-introduces-aadhaar-authentication-for-tatkal-bookings-from-july-1/); [News on AIR, 12 June 2025](https://www.newsonair.gov.in/railways-announces-new-rules-for-tatkal-tickets-aadhaar-based-otp-authentication-must-from-july-1)
- **General reservation:** From 1 Oct 2025, only Aadhaar-authenticated users can book general reserved tickets online in the first 15 minutes after booking opens. The existing 10-minute opening-day restriction on authorised agents is unchanged, and the stated aim is to stop bulk booking by bots and touts. — [DT Next](https://www.dtnext.in/news/national/only-aadhaar-authenticated-users-can-book-online-general-tickets-in-first-15-mins-from-oct-1-railways-846693); [SCC Online, 16 Sept 2025](https://www.scconline.com/blog/post/2025/09/16/aadhaar-mandatory-irctc-ticket-booking-october-2025/)
- An unverified single source says that since 12 Jan 2026 opening-day ARP bookings online from 08:00 to midnight are limited to Aadhaar-authenticated users. — [aaptaxlaw](https://www.aaptaxlaw.com/IRCTC/Tatkal-Ticket-Booking-IRCTC-Charges-Indian-Railway-Tatkal-Ticket-booking-Timing.html) (unverified)
- **Section 143 case law:** Section 143 penalises the unauthorised carrying on of the business of procuring and supplying railway tickets.
  - The Supreme Court restored prosecutions against unauthorised online sellers who misused the IRCTC site.
  - A 2026 Madhya Pradesh High Court ruling held that an authorised agent using a personal ID is a rule breach, not a Section 143 offence.
  - The Karnataka High Court quashed proceedings against the developer of the "Tatkalforsure" tool for lack of evidence of procurement or supply.
  — [LiveLaw (SC)](https://www.livelaw.in/amp/supreme-court/unauthorised-sale-of-railway-tickets-online-offence-supreme-court-restores-cases-for-fraudulent-irctc-site-use-280492); [LiveLaw (MP HC)](https://www.livelaw.in/amp/high-court/madhya-pradesh-high-court/authorised-irctc-agent-using-personal-id-booking-ticket-not-section-143-railways-act-offence-547118); [Verdictum (Karnataka HC)](https://verdictum.in/court-updates/high-courts/karnataka-high-court-gaurav-dahake-v-union-of-india-proceedings-section143-railways-act-software-developer-tatkalforsure-1550554)
- In an earlier case (date not confirmed), a developer of a faster-than-IRCTC booking app was arrested. — [Inc42](https://inc42.com/buzz/iit-grads-faster-rail-ticket-booking-app-puts-him-behind-bars)
- **Authorised partners:** ixigo and ConfirmTkt are official IRCTC B2C ticketing partners (2021 reports), and users book with their own IRCTC user ID through ixigo. — [Inc42, Feb 2021](https://inc42.com/buzz/ixigo-acquires-confirmtkt-to-fulfill-post-covid-train-travel-demand); [ixigo trains](https://ixigo.com/trains)
- **IRCTC agent registration:** Becoming a retail agent is done through IRCTC's agent channel. A vendor page quotes ₹3,000 including GST and OTP login (vendor page, not official). — [sionline](https://sionline.co.in/irctc-agent-registration)
- **OTA and AI deals:** MakeMyTrip and ixigo each announced OpenAI partnerships on 18 Feb 2026. MakeMyTrip's is an API deal powering its in-app assistant Myra, not a public agent API. — [Skift, 18 Feb 2026](https://skift.com/2026/02/18/indian-otas-strike-deals-with-openai/); [PhocusWire](https://www.phocuswire.com/makemytrip-ixigo-openai-expand-ai-capabilities)
- ixigo launched native apps inside ChatGPT covering Flights, Hotels, AbhiBus and ConfirmTkt, with booking that redirects to ixigo (reported 30 Apr 2026). It also launched an "AI-native" app with agentic booking features. — [Pulse](https://www.pulse.bot/transportation/news/ixigo-launches-native-travel-apps-on-chatgpt-b77e2a83-d8f3-45fa-9df5-c992f7ad63d3/); [Autocar Pro](https://www.autocarpro.in/news/ixigo-unveils-ai-native-app-with-multimodal-travel-assistant-and-agentic-booking-features-132570)
- **Bus:** A third-party scan scored redBus 22/100 for agent readiness and found no API or MCP endpoint. In May 2026 ixigo partnered with Uber and redBus to book cabs and buses inside its trains app. — [StartupHub agent-ready index](https://www.startuphub.ai/agent-ready-index/redbus); [newsbytes](https://newsbytesapp.com/news/business/makemytrip-ixigo-and-yatra-make-ai-central-to-indian-travel/tldr)
- **Flights:** Agentic flight booking with user spending limits went live at GFF 2026 inside Amazon Pay and Pine Labs/L&T Finance PLANET, and Swiggy MCP also has a "Scenes" server for event tickets (section 6). — [rango.design](https://rango.design/articles/global-fintech-fest-2026-launches)

### Inferences
- Boop should not automate IRCTC logins or bookings. Aadhaar OTP on Tatkal, the bot-focused 15-minute window and Section 143 exposure for anything resembling a ticket-procurement service make this high-risk. Safe options are deep links into IRCTC Rail Connect or an authorised partner (ixigo/ConfirmTkt), with the user completing OTP and payment, or a commercial tie-up with an authorised partner.
- For flights and bus, B2B travel APIs (consolidators such as TBO) exist commercially, but they require agency registration (IATA/agency KYC) and are not designed for consumer agents. The near-term path is the OTAs' own LLM apps (ixigo in ChatGPT) or MCPs if they open them.

### Gaps
- No official IRCTC policy on AI agents or third-party automation was found, and the IRCTC terms of use were not fetched directly.
- No current, official list of IRCTC authorised B2C partners (2026) was retrieved.
- No public redBus, MakeMyTrip or ixigo partner API or MCP for third-party agents was found, and B2B flight API terms and costs were not researched.

## 6. Quick commerce and food: Swiggy, Zomato, Zepto, Blinkit, BigBasket, Flipkart Minutes

### Takeaway
Swiggy is the only food or quick-commerce player with a formal third-party builder programme. Builders Club (announced 23 Apr 2026) is invite-based and application-reviewed: build locally on localhost, get staging during review, and get production after 48 hours of green staging. It now supports in-chat UPI (intent or QR), Swiggy Money and COD. Its GitHub manifest still says "third-party app development is not permitted at this time", which conflicts with the Builders Club docs. Zepto has an official consumer MCP that allowlists localhost redirects and supports UPI links and UPI Reserve Pay, but its third-party app policy is unstated. Zomato's MCP is personal-use only and explicitly bars third-party apps (unchanged as of a Sept 2026 GitHub issue). Blinkit and Flipkart Minutes have no official MCP. BigBasket is live inside ChatGPT with UPI, but no public MCP for outside agents was found.

### Cited Findings

**Swiggy**
- **Launch (27 Jan 2026):** Swiggy launched MCP servers for Food, Instamart and Dineout for ChatGPT, Claude and Gemini, and calls Instamart the first quick-commerce MCP, with 40,000+ SKUs. At launch, COD was the only payment option. — [YourStory, Jan 2026](https://yourstory.com/2026/01/swiggy-lets-users-order-through-chatgpt-claude-gemini); [Inc42](https://inc42.com/?p=546455); [Swiggy corporate](https://www.swiggy.com/corporate/?p=16731)
- **Builders Club (23 Apr 2026, press release):** 3 MCP servers and 18+ tools, live API access with "generous rate limits", engineering support, co-branding and growth partnerships. It is built on AWS Bedrock/AgentCore, open to developers, startups and enterprises, and invite-led. — [Swiggy press release, 23 Apr 2026](https://www.swiggy.com/corporate/press-release/swiggy-to-launch-builders-club-giving-developers-and-enterprises-access-to-its-ai-commerce-stack/)
- **Current docs:** Four servers with 62 tools: Food (20), Instamart (16), Dineout (11) and Scenes (15, events and tickets). The protocol is MCP over streamable HTTP with OAuth 2.1 and PKCE. There are consumer, developer (self-serve to staging) and enterprise (delegated multi-tenant OAuth, custom rate limits, SLA) paths, and "no access approval is needed until production". — [Swiggy Builders docs](https://mcp.swiggy.com/builders/docs/)
- **Access and onboarding:**
  - Swiggy MCP is "invite-based in v1" and every application is reviewed. Applicants submit a video of a working flow.
  - Review criteria: a concrete use case with real users, alignment with the consumer experience, technical readiness (OAuth, 401/429 handling, safe retries), traffic estimates and a security baseline.
  - Staging runs at mcp-staging.swiggy.com with seeded data. Production comes after 48+ hours green on staging. Platform operators and enterprises take 4+ weeks because of per-partner commercial terms.
  - Redirect URIs must be HTTPS exact-match, localhost is allowed for development, and platform schemes such as alexa:// are allowed case-by-case. Clients self-register through Dynamic Client Registration.
  - Obligations include 7 days' notice before major traffic events and honouring Retry-After.
  - Credentials can be revoked without notice for abuse, scraping or bulk catalogue export.
  - Contact: builders@swiggy.in.
  — [Swiggy Access & onboarding](https://mcp.swiggy.com/builders/docs/operate/access/)
- **Conflicting GitHub manifest:** The manifest says, verbatim, "Third-party app development is not permitted at this time due to ongoing security reviews and compliance requirements". It lists Food and Instamart as COD only and Dineout as free bookings only, says COD orders placed through MCP cannot be cancelled, and asks users to keep the Swiggy app closed during use. Its redirect allowlist covers Claude, ChatGPT, VS Code, Postman, localhost and 127.0.0.1. — [Swiggy MCP manifest (GitHub)](https://github.com/Swiggy/swiggy-mcp-server-manifest)
- A GitHub issue from a company (Elaichi) asking to be whitelisted as an OAuth client shows the "not supported for Swiggy MCP sign-in yet" block. — [Issue #135](https://github.com/Swiggy/swiggy-mcp-server-manifest/issues/135)
- **Payments (docs, July 2026):** In-chat UPI works across Food, Instamart and Dineout.
  - On mobile the user picks a UPI app (GPay, PhonePe, Paytm) through intent; on desktop a QR code is shown.
  - No VPA or collect request is used.
  - `check_payment_status` is a long-poll of about 19 seconds, and `confirm_order` runs only after success. The order becomes PLACED only after payment succeeds.
  - If UPI is unavailable for a cart, payment falls back to cash.
  - Reserve Pay and agentic auto-pay are not mentioned.
  — [Swiggy UPI payments blog](https://mcp.swiggy.com/builders/blog/2026-07-10-mcp-payments-upi.md); [llms.txt index](https://mcp.swiggy.com/builders/llms.txt)
- Swiggy Money (wallet) became available for Food and Instamart MCP orders (blog dated 30 Sept 2026). Each server exposes `get_payment_options`. — [Swiggy llms.txt index](https://mcp.swiggy.com/builders/llms.txt)
- **Data and compliance:**
  - Swiggy is the Data Fiduciary and the integration is a Data Processor under DPDP. All tool arguments and responses, including addresses, carts and order status, count as PII.
  - Integrations may use Swiggy-originated data only for the user's immediate task. Analytics, ads or model training need explicit consent plus a DPA.
  - Identifiers must be hashed at rest, and integrations should log only session IDs, not full bodies.
  - Processing MCP responses outside India requires a signed DPA before production, SCCs or equivalent, and minimal cross-border fields.
  — [Swiggy Data & compliance](https://mcp.swiggy.com/builders/docs/operate/data-and-compliance.md)

**Zomato**
- The official manifest says Zomato is "not allowing any third party apps to be built on top of Zomato MCP right now" for security and legal reasons. It calls the server "only for testing purposes" with all liability disclaimed. Developer access is personal-use only via a forms.eternal.com request. The redirect allowlist covers only Claude, ChatGPT, VS Code and Postman, with no localhost. Payment is by QR code. — [Zomato MCP manifest (GitHub)](https://github.com/Zomato/mcp-server-manifest)
- A GitHub issue opened on 26 Sept 2026 by a developer seeking a multi-user agent pilot confirms that access is still personal-use only. — [Zomato issue #73](https://github.com/Zomato/mcp-server-manifest/issues/73)
- Zomato is nevertheless a Razorpay agentic-payments partner on Claude (Feb 2026 pilot). — [Razorpay blog](https://razorpay.com/blog/agentic-payments-and-npci/)

**Zepto**
- The official MCP is at `https://mcp.zepto.co.in/mcp`, with OAuth by Indian mobile and OTP.
  - Tools: catalogue search, cart, order placement and order history.
  - Redirect allowlist: Claude, VS Code, Postman, localhost/127.0.0.1; other URIs on request through GitHub issues. ChatGPT is in beta.
  - Payments: COD, UPI through an in-conversation payment link, cards, Zepto Cash, and UPI Reserve Pay ("reserves the amount via UPI (powered by NPCI and Razorpay) and charges it on fulfillment").
  - Orders are real.
  - The README does not state a third-party app policy.
  — [Zepto MCP repo](https://github.com/zeptonow/mcp); [Tru Commerce review, 23 Sept 2026](https://trucommerce.ai/insights/india-quick-commerce-agentic-mcp)

**Blinkit, BigBasket, Flipkart Minutes**
- **Blinkit:** No company-published MCP endpoint was verified as of 23 Sept 2026; only unofficial community wrappers exist. — [Tru Commerce](https://trucommerce.ai/insights/india-quick-commerce-agentic-mcp)
- **BigBasket:** The first ChatGPT agentic payments merchant (Oct 2025 pilot). April 2026 reports say BigBasket is live on ChatGPT with its catalogue, inventory and cart exposed via MCP and UPI through Razorpay. No public MCP for third-party agents was found. — [Storyboard18, Oct 2025](https://www.storyboard18.com/digital/chatgpt-integrates-upi-payments-in-india-through-bigbasket-pilot-82421.htm); [Stellagent](https://stellagent.ai/insights/india-agentic-commerce-fintech-payment) (secondary)
- **Flipkart and Flipkart Minutes:** Flipkart's AI storefront is "under construction". A March 2026 headline reports Google's Universal Commerce Protocol debuting in India with Flipkart. Only third-party, read-only scrapers exist for Flipkart Minutes. — [Stellagent](https://stellagent.ai/insights/india-agentic-commerce-fintech-payment) (secondary); [Apify Flipkart Minutes actor](https://apify.com/ikmal_suzali_atr/flipkart-minutes-catalog/api/mcp)

### Inferences
- Boop already fits Swiggy's intended pattern (MCP plus UPI intent hand-off). The binding questions are Builders Club approval for a consumer Android client, how an Android app's redirect URI is handled (HTTPS app links versus a custom scheme, which Swiggy allows only case-by-case), and DPDP: if Boop routes Swiggy responses to an LLM API hosted outside India, Swiggy's docs require a signed DPA before production.
- Open-source and bring-your-own-key designs, where each user runs their own client, may be treatable as the "consumer" path (like Claude Desktop connecting directly). But Swiggy approves integrations, not users, so Boop should apply as a developer integration and confirm in writing.
- Zepto is the strongest second integration: an official MCP, a localhost redirect already allowlisted, and the only one documenting UPI Reserve Pay. Boop should still confirm Zepto's third-party policy by GitHub issue or email before shipping.
- Zomato is off-limits for a distributed third-party app until it changes its stated policy. Scraping or unofficial wrappers for Blinkit or Flipkart Minutes carry terms-of-service and account-ban risk and should be avoided.

### Gaps
- Swiggy's actual rate-limit numbers, commercial terms and stance on open-source clients redistributed to many users were not documented publicly.
- Zepto's policy on third-party apps (as opposed to personal connections) is not stated.
- Whether BigBasket, Blinkit (Eternal) or Flipkart offer any partner MCP or API programme for agents is unknown; no official pages were found.

## 7. Account Aggregator (finance tasks) and DigiLocker

### Takeaway
Account Aggregator data can be pulled only by a Financial Information User (FIU) regulated by the RBI, SEBI, IRDAI or PFRDA. An unregulated assistant like Boop would need a licensed partner acting as FIU, at vendor-quoted costs of roughly ₹2.5–₹25 per fetch. Sahamati, recognised by the RBI as the AA self-regulatory organisation in June 2026, has published a draft framework for AI agents in AA, which is not yet binding. DigiLocker requester access requires approved Partner Organisation status (SOP June 2024). MeitY has announced a planned DigiLocker AI agent (Nov 2025) but no MCP or open agent API.

### Cited Findings
- **FIU eligibility:** Only entities registered and regulated by the RBI, SEBI, IRDAI or PFRDA can act as FIPs or FIUs. A non-licensed startup must get a licence or partner with a regulated entity acting as FIU. The FIU signs agreements with AAs, builds to ReBIT specs and is advised to get a Sahamati-empanelled audit before go-live. — [Sahamati: how to join](https://sahamati.org.in/?p=3007); [HyperVerge](https://hyperverge.co/blog/best-account-aggregators/)
- **Pricing (vendor quotes, indicative):** Perfios lists ₹20 per fetch top-up (minimum 200 transactions), and another source cites ₹5–₹25 per bank statement. A third-party comparison gives Finvu ranges of ₹3–₹6 per account and about ₹2.50 per fetch, excluding GST. Sahamati says FIP charges are not yet set. — [Perfios FIU-lite](https://perfios.ai/in/products/fiu-lite/); [productgrowth.in](https://productgrowth.in/tools/banking-api/finvu/)
- **Sahamati as SRO:** The RBI recognised Sahamati as the AA ecosystem's SRO (reported as 5 June 2026), and Sahamati raised ₹50 crore from banks, NBFCs and fintechs. — [ecorpit](https://ecorpit.com/account-aggregator-integration-fintech-builders-2026/); [Pulse](https://www.pulse.bot/banking/news/rbi-names-sahamati-sro-cementing-governance-of-indias-account-aggregator-network-4f8c011e-1492-4960-a294-c8ec40885b22/)
- **AI-agent framework (draft):** Sahamati Labs published "A Framework for AI Agents in the Account Aggregator Ecosystem", built on four questions: who authorised the agent, who the agent is, what it did, and whether it stayed in scope. It is a draft for ecosystem feedback. — [Sahamati](https://sahamati.org.in/?p=1273516); [Sahamati newsletter, June 2026](https://sahamati.org.in/varta-the-sahamati-newsletter-june-2026/)
- **2026 deadlines:** PAN and date of birth for account discovery are mandatory for RBI-regulated FIPs by 31 Oct 2026, and a DPDP consent-manager deadline falls in Nov 2026. — [ecorpit](https://ecorpit.com/account-aggregator-integration-fintech-builders-2026/)
- **DigiLocker partner SOP (5 June 2024):** NeGD/MeitY's partner onboarding SOP sets eligibility for Partner Organisations. Steps are identification, evaluation, verification, agreement or ToS, integration, testing and launch. Partners need official-domain email, and a weekly committee approves applications. — [API Setu Partners SOP PDF](https://cf-media.api-setu.in/resources/Partners-SOP.pdf)
- Vendors conflict on whether non-regulated entities can be requesters. Commercial KYC vendors (Cashfree, Surepass, HyperVerge) resell DigiLocker pulls with user consent. — [didit.me](https://didit.me/blog/digilocker-api/); [Cashfree DigiLocker](https://cashfree.com/digilocker-api)
- **Planned DigiLocker AI agent (Nov 2025):** MeitY announced an AI agent for DigiLocker that would interpret commands and call DigiLocker APIs, designed so outside developers could plug it into their apps, with human approval for irreversible actions. No launch date was given. — [NewsBytes](https://www.newsbytesapp.com/news/science/digilocker-to-get-ai-assistant-for-automated-document-verification/story); [Free Press Journal](https://www.freepressjournal.in/amp/business/ministry-of-electronics-it-announces-plans-for-ai-based-ekyc-global-credential-verification-in-the-digilocker-platform)
- A third-party DigiLocker MCP connector exists (Boomi), using API-key authentication. — [Boomi docs](https://help.boomi.com/docs/Atomsphere/Connect/MCPConnectors/digitallocker-gov-in-authpartner)

### Inferences
- For spend tracking, AA is overkill and licence-gated for Boop. Cheaper legitimate options are on-device parsing of bank and UPI SMS or notifications (Boop already has notification-triggered jobs), user-exported statements, or partnering with a licensed FIU for an opt-in "connect bank" feature. NPCI's MyUPI (Sept 2026) may become a user-facing source of a consolidated UPI and AutoPay view, but no API was announced.
- DigiLocker is best used as a user-driven hand-off: the user opens DigiLocker and shares a document. Becoming a requester needs Partner Organisation approval and (per vendors) often regulated-entity status.

### Gaps
- Whether the RBI or Sahamati will allow an "agent acting for the user" (as opposed to an FIU) to receive AA data is unresolved; the framework is only a draft.
- No 2026 DigiLocker requester eligibility or fee schedule was found, and the launch status of MeitY's DigiLocker AI agent is unknown.
