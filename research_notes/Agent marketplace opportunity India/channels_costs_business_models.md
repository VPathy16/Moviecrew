# Channels, costs, business models and unit economics for AI agents that talk to customers on behalf of small businesses (India first, as of 17 November 2026)

Notes on reading this file:
- Every price carries a date. "List" means the platform's own page; "vendor claim" means a reseller or competitor blog.
- Confidence is given per finding as (High), (Medium) or (Low).
- Exchange rate: Indian press in July 2026 converted $2 to about ₹189, i.e. roughly ₹94.5 per USD ([Business Today, 3 Jul 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/whatsapp-introduces-token-based-pricing-for-ai-agents-from-august-1-540699-2026-07-03)). Meta's INR rate card is not a straight FX conversion of its USD card (₹0.8631 vs $0.0118 implies about ₹73/USD), so do not convert between the two.
- Research stopped at about 38 tool calls. Several sub-questions returned only vendor blogs or nothing; those are listed under Gaps rather than filled in.

## 1. WhatsApp Business Platform (Cloud API) in India: pricing, onboarding, multi-tenant signup, coexistence, AI policy, Meta's own AI agents

### Takeaway
The biggest change for unit economics is recent: since 1 October 2026 free-form replies inside the 24-hour window are no longer free. Each business phone number gets 1,000 free service messages a month, then pays the utility rate (₹0.115 per message in India). A seller-side agent on WhatsApp is still allowed by policy (only general-purpose assistants are barred), but Meta now sells a competing agent inside the WhatsApp Business app, launched in India in May and July 2026.

### Cited Findings

Pricing model and India rates
- (High) Meta charges per delivered message, by category and recipient country; it does not charge for messages users send to businesses. Template categories are marketing, utility and authentication; non-template categories are service and, since 1 July 2026, "Meta Business Agent" — [Meta developer docs, pricing page, read 17 Nov 2026](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (High) Per-conversation pricing ended on 1 July 2025, when per-message pricing began — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (High) From 1 October 2026 service (free-form) messages are charged after a free tier: "Meta provides every business phone number with a free tier of 1,000 service messages per month." The allowance does not roll over; charging starts at the 1,001st message. Utility templates sent inside an open customer service window, free from 1 July 2025 to 30 September 2026, are also charged from 1 October 2026 — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (High) Meta stops delivering service messages for solution providers or directly integrated businesses with no payment method on file by 30 September 2026 — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (High) Customer service window: a 24-hour timer starts when the user messages or calls; each new user message resets it; outside it only templates can be sent — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (High, with a conflict) Free entry point window: when a user arrives from a Click-to-WhatsApp ad, marketing, utility, authentication and service messages are free. Meta's page now says this window "may remain open for up to 7 days" — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md); a vendor page still describes it as 72 hours — [InstantDM, Oct 2026](https://instantdm.com/blog/whatsapp-business-api-pricing-2026-india-october-update). Meta Business Agent messages stay charged even in this window.
- (Medium-High; the official page does not print INR amounts, they are in downloadable rate cards, so these come from vendor transcriptions that agree with each other) India Meta list rates on the card effective 1 October 2026: marketing ₹0.8631 ($0.0118); utility ₹0.1150 ($0.0014); authentication ₹0.1150; authentication-international ₹2.4971 ($0.0304); service ₹0.1150 after the 1,000 free — [InstantDM, Oct 2026](https://instantdm.com/blog/whatsapp-business-api-pricing-2026-india-october-update); service rate of ₹0.115 corroborated by [Business Today, 3 Jul 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/whatsapp-introduces-token-based-pricing-for-ai-agents-from-august-1-540699-2026-07-03)
- (Medium) India marketing rate rose about 10% on 1 January 2026, from ₹0.7846 to ₹0.8631 — [ecorpit, 2026](https://ecorpit.com/whatsapp-business-api-cost-india-d2c-2026/); Meta confirms a marketing rate change in India on 1 Jan 2026 and further India rate changes on 1 April 2026 without printing amounts — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (High) Conflicting numbers are mostly reseller markups, not different Meta rates: AiSensy shows ₹1.09 marketing and ₹0.145 utility/authentication/service; Interakt ₹0.871 marketing, ₹0.150 utility, ₹0.128 authentication; Wati ₹1.0357 marketing, ₹0.1495 utility — [InstantDM, Oct 2026](https://instantdm.com/blog/whatsapp-business-api-pricing-2026-india-october-update). Other blogs quote utility at ₹0.35, which looks stale — [WebSearch summary of CampaignHQ/ChatDaddy](https://chatdaddy.tech/blog/whatsapp-business-api-india)
- (Medium) Volume discounts apply to utility and authentication only; India utility stays at ₹0.1150 until 25 million delivered messages a month. Service messages get no volume discount — [InstantDM, Oct 2026](https://instantdm.com/blog/whatsapp-business-api-pricing-2026-india-october-update); tiers confirmed in principle by [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (High) INR billing launched 1 January 2026 for India sold-to customers; all messaging accounts must migrate to INR by 31 December 2026, and from 1 January 2027 Meta will not deliver messages from non-INR accounts — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)
- (Medium) 18% GST applies on the provider's invoice — [InstantDM, Oct 2026](https://instantdm.com/blog/whatsapp-business-api-pricing-2026-india-october-update)
- (Medium) Meta may revise rates up to once a quarter — [Business Today, 3 Jul 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/whatsapp-introduces-token-based-pricing-for-ai-agents-from-august-1-540699-2026-07-03)

Solution-provider (BSP) fees in India (all vendor or third-party pages; treat as indicative)
- (Medium) Interakt: Growth ₹2,499/month and Advanced ₹3,499/month plus taxes — [codingclave audit, 2026](https://codingclave.com/blog/interakt-pricing-india-2026)
- (Medium) AiSensy: Pro plan raised about 30% in May 2026 from ₹2,699 to ₹3,499/month with a 5-agent cap — [richautomate, May 2026 (a competitor)](https://richautomate.in/lead-magnets/bsp-switching-kit); Basic at ₹1,500/month — [go4whatsup guide, Sep 2026 (a competitor)](https://www.go4whatsup.com/india/whatsapp-business-api-guide-2026/); AI chat agent add-on ₹1,350/month — [wanotifier comparison, 2026](https://wanotifier.com/?p=6542)
- (Medium) Wati: India range ₹2,499–₹16,999/month — [codingclave audit, 2026](https://codingclave.com/blog/wati-pricing-india-2026)
- (Low) Markups on Meta fees are quoted anywhere from about 2.8% (Wati marketing) to 10–40% or 20–50% — [go4whatsup comparison, 2026](https://go4whatsup.com/blog/aisensy-vs-wati-vs-interakt-pricing-showdown-2026/); [Hyperleap, 2026](https://hyperleap.ai/blog/whatsapp-chatbot-pricing-india-2026)

Onboarding, embedded signup, coexistence, limits
- (High) Embedded Signup is the flow a Tech Provider or Solution Partner embeds so that each client business creates or connects its own WhatsApp Business account under the provider — [Meta docs, onboarding Business app users](https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/onboarding-business-app-users)
- (High) Coexistence (same number on the WhatsApp Business app and the Cloud API) is enabled by adding the `whatsapp_business_app_onboarding` feature to Embedded Signup; the client must be on WhatsApp Business app version 2.24.17 or higher. It converts the client's existing app account rather than creating a new one — [Meta docs](https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/onboarding-business-app-users)
- (High) Tech Providers that are part of a solution can onboard up to 200 new clients in a rolling one-week period; only clients new to the platform count — [Meta docs, multi-partner solutions](https://developers.facebook.com/documentation/business-messaging/whatsapp/solution-providers/multi-partner-solutions/)
- (Medium) Tech Providers must have clients add their own payment method, or share a line of credit with them during onboarding — [WebSearch summary of Meta/mirror docs](https://support.chatarchitect.com/books/meta-whatsapp/chapter/embedded-signup/export/html)
- (High) Messaging limits (for business-initiated template messages) are now set at the business-portfolio level and shared by all numbers in the portfolio; the change began October 2025, with upgrades promised within 6 hours instead of 24 — [Meta docs, messaging limits](https://developers.facebook.com/documentation/business-messaging/whatsapp/messaging-limits)
- (Low, conflicting) Tier values: one vendor says a new unverified portfolio starts at 250 unique recipients per 24 hours and moves to 2,000 after business verification — [AiSensy guide, 2026](https://m.aisensy.com/blog/whatsapp-message-limits-guide/); another says the 2K and 10K tiers are being removed from Q1 2026 in favour of portfolio pacing — [Webex Connect changelog](https://help.webexconnect.io/changelog/whatsapp-supports-business-portfolio-pacing-relaxing-messaging-limit-tiers-and-text-truncation-on-marketing-messages). Not confirmed against Meta's page.

AI chatbot policy
- (High) WhatsApp changed its Business API terms to bar general-purpose AI chatbots; new API users fell under the terms from 15 October 2025 and all existing users from 15 January 2026. The target is developers of "large language models, generative AI platforms, or general-purpose AI assistants" where the assistant is the product — [TechCrunch, 18 Oct 2025](https://techcrunch.com/2025/10/18/whatssapp-changes-its-terms-to-bar-general-purpose-chatbots-from-its-platform/?source_type=web); [Business Standard, Oct 2025](https://www.business-standard.com/technology/tech-news/meta-bans-ai-chatbots-from-whatsapp-business-api-chatgpt-to-shut-down-jan-2026-125102200335_1.html)
- (Medium; this is a vendor's reading, not Meta's text) Still allowed: AI used for a business's own support, sales, bookings, order tracking and notifications, where the bot is "ancillary to a legitimate business service"; a "concierge" assistant is acceptable if focused on support or transactions with human escalation — [respond.io, modified Oct 2026](https://respond.io/blog/whatsapp-chatbot-policy-2026)
- (High) Where regulators forced Meta to keep carrying third-party general assistants, it charges them: from 16 February 2026 "AI Providers" pay per non-template message in such countries (Italy: $0.0691 per message) — [Meta docs, AI Providers pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/ai-providers); [Neowin, 2026](https://www.neowin.net/news/meta-to-begin-charging-for-third-party-ai-chatbots-on-whatsapp-for-some-users/). Italy's competition authority asked Meta to suspend the policy in December 2025; a Brazilian court overturned a preliminary order against it; the EU opened a probe — [WebSearch summary of TechCrunch coverage](https://techcrunch.com/?p=3087325)
- (Medium) From 1 October 2026 a reply handled by a human or by a third-party AI system is billed as a service message — [IBTimes India, 2026](https://www.ibtimes.co.in/whatsapp-business-messages-become-paid-october-1-india-prices-rules-what-changes-906727)

Meta's own AI agents for small businesses in India
- (High) "Business AI" inside the WhatsApp Business app was announced for India on 7 May 2026: answers customers around the clock from the business profile and catalog, recommends products, captures leads, books appointments, hands over to the owner, works in "all native languages in India", needs no code. Set up from Tools → "Your Business AI". Rollout "to all eligible businesses over the coming weeks"; eligibility criteria not published; UPI payments in chat "starting soon"; price not stated — [Meta newsroom, May 2026](https://about.fb.com/news/2026/05/introducing-business-ai-on-whatsapp-for-small-businesses-in-india/)
- (Medium; self-reported by merchants in Meta's post) The Purple Sunset handled 60–70 daily queries and closed 6–7 orders a day through the AI — [Meta newsroom, May 2026](https://about.fb.com/news/2026/05/introducing-business-ai-on-whatsapp-for-small-businesses-in-india/)
- (Medium) "Meta Business Agent" was rolled out for Indian businesses on 7 July 2026 at Meta's Business Summit in Mumbai, with a waitlist — [Zee News, Jul 2026](https://zeenews.india.com/technology/whatsapp-just-got-smarter-meta-launches-ai-business-agent-in-india-here-s-how-it-works-3059886.html)
- (High) Meta Business Agent is billed per token at one global rate of $2.00 per million tokens, with no free messages or volume tiers; Meta estimates about 4–5 US cents per message — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md). A typical message may use up to 25,000 tokens; billing starts 1 August 2026; smaller businesses get the agent through select WhatsApp Business Premium tiers — [Business Today, 3 Jul 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/whatsapp-introduces-token-based-pricing-for-ai-agents-from-august-1-540699-2026-07-03)
- (Medium) India is WhatsApp's largest market with an estimated 850 million users and more than $1 billion a year in business-messaging revenue — [Business Today, 3 Jul 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/whatsapp-introduces-token-based-pricing-for-ai-agents-from-august-1-540699-2026-07-03)
- (Medium) 91% of online adults in India chat with a business weekly (Kantar 2025, cited by Meta) — [Meta newsroom, May 2026](https://about.fb.com/news/2026/05/introducing-business-ai-on-whatsapp-for-small-businesses-in-india/)

### Inferences
- Messaging cost of one inbound sales chat for a third-party agent on WhatsApp: about 10 bot replies × ₹0.115 = roughly ₹1.15, and zero while the seller's number is inside its 1,000 free service messages (about 100 ten-reply chats a month). Because the allowance is per phone number, a platform where each small seller connects their own number (coexistence) gets a free tier per seller; a platform that fronts many sellers through one shared number gets 1,000 free in total and also looks more like a general assistant.
- Meta's own agent at 4–5 US cents per agent message (about ₹4–5) is far more expensive per reply than a third-party agent paying ₹0.115 plus its own model cost on a small model (see section 5). Meta's edge is distribution and zero setup inside the Business app, not price. How "Business AI" in the app is priced for micro-sellers (Premium subscription tiers) is the number that matters and was not found.
- A buyer-side assistant that shops across many sellers on WhatsApp sits close to the banned "general-purpose assistant" definition. A seller-side agent attached to one business's number is squarely in the allowed use. This is a policy risk asymmetry between the two sides of an agent network.
- Platform dependence is high: in 16 months Meta changed pricing model once, added charges for previously free replies, banned a category of bots and launched a first-party competitor.

### Gaps
- Meta's official INR rate card was not opened directly; INR figures rest on vendor transcriptions.
- No reliable source found for typical time to go live, template approval turnaround, display-name review time or the current exact messaging-limit tiers. Vendor blogs conflict.
- Exact wording of the AI Providers clause in Meta's Business Solution Terms was not retrieved; enforcement record since January 2026 against small "concierge" style bots is unknown.
- Pricing and eligibility of WhatsApp Business Premium tiers that include Business AI in India not found.
- A reported Jio Haptik SMB agent "from ₹10,000" appeared only in aggregator headlines ([tecknexus](https://tecknexus.com/jio-haptik-whatsapp-ai-agents-for-smbs-from-₹10000/)); terms unverified.

## 2. Web chat link / QR versus WhatsApp

### Takeaway
Survey evidence that Indians prefer messaging a business over visiting its website is strong, but it is mostly Meta-commissioned, and I found no independent head-to-head data on whether customers will chat on an unfamiliar web page or how link/QR chat pages convert against WhatsApp.

### Cited Findings
- (Medium; Meta-commissioned) A Kantar study found 86% of Indian adults message a business at least once a week against a 66% global average — [BestMediaInfo, Oct 2022](https://bestmediainfo.com/2022/10/86-of-indian-adults-message-a-business-at-least-once-a-week-highest-in-the-world-kantar-survey); more than 70% said they prefer messaging a business to emailing, calling or visiting its website — [Business Standard, Oct 2022](https://business-standard.com/article/technology/over-7-in-10-indians-now-prefer-to-chat-with-businesses-meta-report-122100700432_1.html)
- (Medium) Mobile Ecosystem Forum: Indian mobile users' preferred channel to receive business messages is WhatsApp (45%), then email (41%), SMS (35%), voice calls (33%), Instagram (29%) — [MEF](https://mobileecosystemforum.com/mef_data_post/whatsapp-in-india)
- (Medium) Meta's "Win With Conversations" report says 15 million SMBs on WhatsApp Business drive traffic through click-to-chat ads — [Meta report, 2024](https://about.fb.com/wp-content/uploads/2024/05/Win-With-Conversations-Report_2024.pdf)
- (High) Chats that start from a Click-to-WhatsApp ad get a free messaging window of up to 7 days — [Meta pricing page](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing.md)

### Inferences
- A web chat link or QR has zero per-message platform fee and no policy risk, but gives up the re-contact channel: on the web the seller's agent cannot message the customer later unless it collects a phone number, whereas a WhatsApp thread persists (within template rules and fees).
- A practical hybrid is a web page or QR that opens a WhatsApp deep link to the seller's own number, keeping the conversation in the seller's free tier. Whether to run the agent on the web page itself should be settled by a small split test, since no public data answers it.

### Gaps
- No independent India data found on link-in-bio chat or ordering page conversion versus WhatsApp, on willingness to chat on an unknown web page, or on trust signals. Vendor "98% open rate" style numbers were seen and discarded as unverified.
- Progressive web app and Android instant-app options were not researched within the call budget.

## 3. Voice: cost and regulation of AI voice agents in India

### Takeaway
An AI voice agent in Indian languages costs about ₹3.5–6 per connected minute all-in on Indian platforms in 2026 (list prices), so a three-minute call costs roughly ₹11–18, about ten times a WhatsApp text chat. Disclosed traction of Indian voice-AI startups is enterprise and BFSI, not small business.

### Cited Findings
- (High, list price) Sarvam voice agents: ₹3.50 per minute pay-as-you-go, ₹3.25 (min ₹9,999/month), ₹3.15 (min ₹49,999/month), ₹3.00 (min ₹1,99,999/month), excluding GST. The rate bundles speech recognition, language model and voice: "There is no separate model or token charge." Telephony extra: ₹0.20 per 30-second pulse via Sarvam's carrier, or free if you bring your own; number rental ₹59 per 30 days; unanswered calls not charged — [Sarvam docs, read 17 Nov 2026](https://docs.sarvam.ai/voice-agents/pricing.md)
- (Medium, vendor) Ringg: ₹6 per connected minute in India; number ₹499/month — [Ringg pricing page](https://www.ringg.ai/ai-voice-agent-pricing)
- (Medium, vendor) Market rate cards run ₹2–12 per minute, most commonly ₹3–6; Bolna ₹4–8; Edesy ₹6 with telephony; Vapi $0.05/min platform fee before speech and telephony — [ecorpit, 2026](https://ecorpit.com/ecorpit-ai-voice-agent-development-service-india-2026/); [Edesy, 2026](https://edesy.in/blog/ai-voice-agent-pricing-india-2026.md). One vendor argues effective cost is ₹6–25 per minute after platform fees and connect-rate losses — [Caller.Digital, 2026](https://caller.digital/blog/voice-ai-india-pricing-cost-breakdown)
- (Medium) Telephony: Plivo India rate card lists ₹0.38 per minute inbound and outbound, 30-second pulse, number rental ₹200/month (checked October 2026 by the source) — [Caller.Digital, Oct 2026](https://caller.digital/blog/twilio-alternatives-india-2026). Exotel sells prepaid bundles: ₹9,999 for 5 months (one virtual number, 3 agents, 5,000 credits), ₹19,999 and ₹49,499 for 11 months, plus 18% GST — [CloudTalk, Jun 2026](https://www.cloudtalk.io/blog/exotel-pricing/)
- (Medium) Regulation: TRAI reserves the 1600 series for service and transactional calls by regulated entities (BFSI, government) and the 140 series for promotional calls subject to Do Not Disturb preferences — [Telangana Today, Nov 2026](https://telanganatoday.com/trai-clarifies-rules-for-1600-and-140-number-series-to-prevent-misinformation); the 1601 series is directed for utilities, courier and logistics — [ThePrint](https://theprint.in/economy/trai-directs-use-of-1601-series-for-service-transactional-calls-by-utilities-logistics-cos/3010594/); migration deadlines for RBI, SEBI, PFRDA and IRDAI entities ran 1 January to 15 March 2026 — [Exotel blog](https://exotel.com/blog/1600-phone-number/)
- (Medium) Traction: Bolna raised $6.3M (General Catalyst, Jan 2026), with 50+ BFSI clients — [TechCrunch, 20 Jan 2026](https://techcrunch.com/2026/01/20/bolna-nabs-6-3-million-from-general-catalyst-for-its-india-focused-voice-orchestration-platform/?rand=324). Ringg raised $5.5M then a further $10M, closing Series A at about $15.5M — [Inc42, 2026](https://inc42.com/?p=545709). Gnani.ai raised $10M and claims 30 million voice interactions a day for 200+ enterprises (company claim) — [Outlook Business, 2026](https://www.outlookbusiness.com/corporate/gnaniai-raises-10-mn-in-first-tranche-of-funding-round-led-by-aavishkaar-capital). Smallest.ai raised $13M — [Entrepreneur India](https://india.entrepreneur.com/business-news/smallest-ai-raises-usd-13-mn-in-series-a-funding-led-by-seligman-ventures)

### Inferences
- Inbound answering (a customer calls the seller's virtual number) avoids most of the 140/1600 and DLT complexity, which is aimed at business-initiated calls. Outbound calling by an agent on behalf of a small seller or a consumer is the regulated, riskier direction.
- On Sarvam list prices a three-minute inbound call is about 3 × (₹3.50 + ₹0.40) ≈ ₹11.70 plus ₹59 a month for the number. That is affordable for high-value enquiries (services, made-to-order) but not as a free default for ₹200 orders.

### Gaps
- No TRAI or DoT text found that addresses AI voice agents specifically; no primary regulator document was opened.
- Standalone speech-to-text and text-to-speech prices for Indian languages were not found (Sarvam bundles them).
- No evidence of a voice-AI product with disclosed small-business traction in India. Monthly revenue figures for Bolna appeared only in a search summary and were not verified, so they are omitted.
- Official Exotel and Twilio India per-minute rate cards not retrieved; KYC requirements for virtual numbers not sourced.

## 4. Instagram/Messenger API, Google Business Messages, RCS

### Takeaway
Google Business Messages is dead (31 July 2024). RCS in India got materially more expensive on 1 September 2026 and now reaches iPhones via Jio, but it is priced and built for business-initiated messages. Instagram messaging follows a 24-hour reply window; I found no per-message fee documented for it.

### Cited Findings
- (High) Google Business Messages was discontinued on 31 July 2024; customers can no longer message businesses from Search or Maps listings — [Google developers notice](https://developers.google.com/business-communications/business-messages/resources/release-notes/update-on-gbm?hl=en)
- (High) Instagram/Messenger: a business has 24 hours to respond after a user messages; messages inside that window may be promotional — [Meta Messenger Platform and IG Messaging policy](https://developers.facebook.com/documentation/business-messaging/messenger-platform/policy.md)
- (Low, vendor) Instagram automated messages limited to 200 per hour per account, cut from 5,000 in October 2024 — [keyapi blog](https://www.keyapi.ai/blog/instagram-messaging-api-policy/)
- (High) Jio's RCS business rates from 1 September 2026: marketing ₹0.27–0.30, transactional ₹0.25, OTP ₹0.11–0.16 per message, replacing a flat ₹0.08–0.10 — [Inc42, Sep 2026](https://inc42.com/buzz/jio-introduces-new-rcs-business-messaging-rates-for-iphone-users-in-india/); Jio is the first Indian operator to extend RCS business messaging to iPhones — [Mobile Ecosystem Forum, 14 Sep 2026](https://mobileecosystemforum.com/2026/09/14/jio-bring-rcs-business-messaging-to-iphones-in-india/)
- (Medium, conflicting) MoEngage puts the market move at roughly 6–7 paise to 20–25 paise per marketing message from 1 September 2026 — [MoEngage, 2026](https://www.moengage.com/blog/rcs-and-whatsapp-pricing-changes-2026/); Exotel cites Airtel at about ₹0.11 — [Exotel glossary](https://exotel.com/glossary/rcs-rich-communication-services-messaging/); aggregators quote ₹0.15–0.80 — [CM.com](https://www.cm.com/en-in/blog/rcs-pricing-india/). Rates are set per operator; there is no single India price.

### Inferences
- RCS marketing at ₹0.27–0.30 is still about a third of WhatsApp marketing at ₹0.8631, so it is a cheaper outbound channel, but it does not offer a consumer habit of opening a chat with a small seller. It is not a substitute front door for an inbound seller agent.
- Instagram DMs matter for sellers whose discovery happens on Instagram; the 24-hour window and apparent absence of per-message fees make it cheap for inbound, with rate limits as the constraint.

### Gaps
- No Meta page found stating Instagram Messaging API pricing explicitly; "free" is an absence of evidence of fees, not a confirmed fact.
- No India RCS adoption figures (active users, business senders) found.

## 5. LLM cost per conversation, and what Indian small-business software can charge

### Takeaway
On small models with caching, the model cost of a ten-reply sales chat is well under ₹1; on frontier models it is ₹5–50. Model cost is no longer the binding constraint for text; pricing power is. Published Indian comparables charge ₹1,500–3,500 a month to businesses that already advertise, and listed directories earn about ₹19,000–67,000 per paying business per year.

### Cited Findings
Model list prices (USD per million tokens, read 17 Nov 2026)
- (High) Anthropic: Claude Haiku 5.5 $0.10 input / $0.50 output, cache read $0.01 (prompts up to 100k tokens); Sonnet 5.5 $2 / $10, cache read $0.10; Opus 5.5 $4 / $20, cache read $0.20; Fable 5.2 $8 / $40, cache read $0.20; 5-minute cache writes cost 1.25× input; Batch API gives 50% off — [Anthropic pricing docs](https://platform.claude.com/docs/en/about-claude/pricing)
- (High) Google: gemini-2.5-flash-lite $0.10 / $0.40, cached $0.01; gemini-3.5-flash-lite $0.30 / $2.50, cached $0.03; gemini-3.8-flash $0.75 / $3.75, cached $0.075; gemini-3.1-pro-preview $2 / $12, cached $0.20. The page lists scheduled price increases for some Flash models from 1 January 2027 — [Google AI Studio pricing](https://aistudio.google.com/docs/pricing)
- (Low; third-party trackers that disagree with each other) OpenAI economy tier quoted at $0.20 / $1.20; DeepSeek at $0.14 / $0.28 — [CloudZero, Aug 2026](https://www.cloudzero.com/blog/llm-api-pricing/); [TechSy, Jul 2026](https://techsy.io/en/blog/llm-api-pricing-comparison)
- (High) Benchmark from Meta: its own business agent bills $2 per million tokens and a typical message uses up to 25,000 tokens — [Business Today, 3 Jul 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/whatsapp-introduces-token-based-pricing-for-ai-agents-from-august-1-540699-2026-07-03)

What Indian small businesses pay
- (Medium) WhatsApp tool subscriptions: ₹1,500–3,499/month for AiSensy and Interakt tiers (sources in section 1); AI agent add-on ₹1,350/month at AiSensy — [wanotifier, 2026](https://wanotifier.com/?p=6542)
- (High) IndiaMART: about 2.21–2.22 lakh paying suppliers in FY26; annualised revenue per paying supplier about ₹67,000 — [Quartr Q4 FY26 summary](https://quartr.com/events/indiamart-intermesh-limited-indiamart-q4-25-26_3PjDiEE6); paying supplier count fell about 1,000 in Q3 FY26 after a Silver-tier price increase — [Quartr Q3 FY26](https://quartr.com/events/indiamart-intermesh-limited-indiamart-q3-25-26_3PjDp0Xq)
- (Low-Medium; not checked against the filing) IndiaMART Silver (entry) tier monthly churn of 4–7% — [Whalesbook, 2026](https://www.whalesbook.com/corporate-news/English/tech/IndiaMART-Revenue-Surges-14percent-in-Q4-Amid-Supplier-Base-Decline/69fb49b1d27867b982d4800d)
- (High) Justdial: 631,530 active paid campaigns at end of Q4 FY26; FY26 operating revenue about ₹1,214 crore — [Outlook Business, 2026](https://www.outlookbusiness.com/corporate/just-dial-q4-results-operating-revenue-hits-307-cr-profit-dips-on-treasury-drag); 656,520 paid campaigns in Q2 FY27 — [Investywise, 2026](https://www.investywise.com/?p=121324)
- (Low, consultancy blog) Entry tiers for Indian SMB software sit around ₹999–4,999/month; Indian B2B buyers pay 50–70% less than US/EU for the same product — [upGrowth, Sep 2026](https://upgrowth.in/saas-pricing-packaging-strategy-india-gtm/)
- (Low) Generic SMB software churn benchmark 3–5% a month — [WebSearch summary, aiaccountant blog](https://www.aiaccountant.com/blog/saas-metrics-dashboard-india-edition-681f4)
- (Medium, payment-vendor blog citing NPCI-linked reporting) More than 20 million UPI AutoPay mandates are revoked each month, mostly for insufficient balance at debit time; failure rates on subscription-type debits have reached as high as 90% in some cases — [Cashfree blog](https://www.cashfree.com/blog/saas-payment-failures-india/)

### Inferences
Cost model (my arithmetic, assumptions stated): one sales chat = 8 customer turns, 2 tool calls, so about 10 model calls; fixed prefix (instructions, catalog extract, tool definitions) about 4,500 tokens; history grows to about 2,000 tokens; total about 55,000 input tokens of which about 45,000 are cache hits, and about 1,200 output tokens.

| Model (list price, 17 Nov 2026) | No caching | With caching |
|---|---|---|
| Gemini 2.5 Flash-Lite / Claude Haiku 5.5 | about $0.006 (₹0.6) | about $0.002 (₹0.2) |
| Gemini 3.8 Flash | about $0.046 (₹4.3) | about $0.015 (₹1.5) |
| Claude Sonnet 5.5 | about $0.12 (₹11.5) | about $0.05 (₹4.5) |
| Claude Fable 5.2 | about $0.49 (₹46) | about $0.18 (₹17) |

- Caching cuts cost by roughly 60–70% in this shape because the catalog prefix dominates input. Larger catalogs in context raise both columns in proportion; retrieval of a few items per turn keeps the prefix small.
- Full cost of a WhatsApp text chat on a small model: ₹0.2–0.6 model + ₹0 to ₹1.15 Meta service fees = roughly ₹0.2–1.8. At 300 chats a month per seller that is about ₹60–540, of which Meta fees are the larger part once the free 1,000 messages run out. A ₹199/month plan cannot cover a busy seller on WhatsApp; ₹499–999 can, or a usage cap is needed. On a web chat link the same 300 chats cost ₹60–180.
- Meta's own assumption of up to 25,000 tokens per agent message is roughly four to five times the per-call input in the model above, which suggests either large catalog context or multi-step reasoning per reply; treat my numbers as a lean lower-middle case.
- The businesses that demonstrably pay ₹1,500–5,500 a month (WhatsApp tools, IndiaMART, Justdial) pay for leads and broadcast reach, not for answering. This suggests willingness to pay attaches to new customers delivered, which matters for the choice between subscription and lead/order fees in section 6.
- UPI AutoPay failure and revocation rates mean involuntary churn will be high on small monthly plans; prepaid packs (as Wati's ₹999 one-time pack and Exotel's prepaid bundles do) are a common local answer.

### Gaps
- No verified ARPU, paid conversion or churn data found for Khatabook, Vyapar, Dukaan or similar micro-merchant apps; no evidence either way that ₹199–999/month price points work for an answering agent.
- OpenAI's official price page was not opened; its figures above are third-party and conflicting.
- No measured token logs from a production sales agent were found; the per-conversation model is an estimate.

## 6. Business models in comparable products; marketplace commissions and seller resentment

### Takeaway
Indian marketplaces are moving in two directions at once: goods marketplaces are racing to zero commission on low-priced items, while food delivery and home services still take 8–28% and face organised seller revolt. For AI agents, disclosed models are monthly subscription plus pass-through messaging fees (BSPs), per-minute (voice) and per-token (Meta). I found no disclosed revenue for an Indian AI agent product aimed at small sellers.

### Cited Findings
- (High) Meesho has charged zero commission since 2021 and reached about 37% of India's e-commerce orders by FY25; Flipkart introduced zero commission under ₹1,000 in late 2025 (and made Shopsy commission-free); Amazon India waived referral fees under ₹1,000 from March 2026 across more than 12.5 crore products — [YourStory, Mar 2026](https://yourstory.com/2026/03/amazon-india-expands-zero-referral-fees-125-crore-products-flipkarts-commission-waiver); [Outlook Business](https://www.outlookbusiness.com/corporate/flipkart-rolls-out-zero-commission-policy-for-items-under-1000-shopsy-made-completely-commission-free); [Business Standard, Nov 2025](https://www.business-standard.com/amp/companies/news/flipkart-zero-commission-value-commerce-125111401468_1.html)
- (Low-Medium, seller blogs) Above those thresholds Amazon referral fees are quoted at 5–25% by category; "zero commission" platforms still cost sellers 10–15% through ads and returns — [goNukkad comparison](https://www.gonukkad.com/blog/marketplace-commission-comparison-india)
- (Medium) Food delivery: Swiggy and Zomato charge 8–28% commission plus ads and payment fees (Bengaluru hoteliers' association estimate); more than 1,000 Bengaluru restaurant owners threatened to delist from 15 August 2026 — [The Week, 30 Jul 2026](https://www.theweek.in/news/biz-tech/2026/07/30/wont-take-orders-anymore-why-bengaluru-restaurants-are-threatening-to-boycott-zomato-swiggy.amp.html). The restaurant association's complaint to the competition regulator cites exorbitant commissions, data masking, bundling and price-parity clauses that stop restaurants building their own ordering channels — [Business Standard, Jul 2026](https://www.business-standard.com/industry/news/zomato-price-parity-cci-case-why-nrai-oppose-explained-126071500578_1.html); [Outlook Business](https://www.outlookbusiness.com/equity/nrai-files-anti-competitive-practices-case-against-zomato-swiggy-7951)
- (Medium) Urban Company: partner commissions and fees were 28.3% of service professionals' average gross earnings in 9M FY26 — [Inc42, 2026](https://inc42.com/features/inside-urban-companys-marketplace-model-what-it-keeps-from-every-booking/)
- (Low, conflicting) ONDC: buyer-app fees "near 3%" versus 15–25% at incumbents — [ecorpit, 2026](https://ecorpit.com/ondc-2026-d2c-brand-seller-scale-playbook/); an older primer shows ₹15 buyer finder fee on a ₹500 order and total 5–10% — [Kalaari ONDC primer, 2023](https://kalaari.com/wp-content/uploads/2023/11/ONDC-Primer-%E2%80%93-Final-Full-Report.pdf); ONDC itself planned a network fee of ₹1.5 per transaction — [Inc42](https://inc42.com/buzz/ondc-to-levy-fee-of-inr-1-5-from-next-month)
- (High) Lead/listing subscription model at scale: IndiaMART about ₹67,000 per paying supplier per year; Justdial about 6.3 lakh paid campaigns (sources in section 5)
- (High) AI agent pricing models in market: per-token (Meta Business Agent, $2 per million tokens), per-minute (Sarvam ₹3–3.50; Ringg ₹6), monthly add-on (AiSensy AI agent ₹1,350/month) — sources in sections 1, 3 and 5
- (Medium) Dukaan, an online-store builder for small Indian merchants, replaced 90% of its support staff with an AI chatbot in 2023 and said it was prioritising profitability — [DT Next, 2023](https://www.dtnext.in/news/business/saas-platform-dukaan-hires-ai-chatbot-fires-90-of-support-staff-723630); Khatabook's attempt to monetise its free ledger app through lending was held back by small ticket sizes and unreliable data — [The Morning Context](https://themorningcontext.com/internet/khatabook-cant-lend-enough-to-justify-its-valuation)

### Inferences
- A take rate on orders is commercially and emotionally the hardest model to introduce in India right now: the reference price for selling low-ticket goods online has become 0%, and price-parity and commission disputes are live in food. "No commission, your customer stays yours" is a usable wedge against exactly the grievances in the regulator complaint (data masking, inability to build a direct channel).
- The models with proof of payment by Indian small businesses are (a) fixed subscription for lead flow and (b) prepaid usage. Per-conversation pricing maps cleanly onto Meta's per-message cost and avoids the "commission" label.
- Free ledger and store apps that reached tens of millions of merchants and then struggled to monetise are the cautionary case for "free tool first, monetise later" without a paid action in the loop.

### Gaps
- No disclosed revenue, growth or shutdown found for an Indian startup selling AI sales/support agents specifically to micro and small sellers. Global comparables were not researched within budget.
- Dukaan's later direction (AI support product) and current status could not be verified; aggregator pages calling it "failed 2024" were not relied on.
- Official ONDC fee documentation and Zomato/Swiggy published commission slabs not retrieved; outcome of the August 2026 Bengaluru boycott threat unknown.
- Lead-fee prices per lead for local services (Sulekha, Urban Company style) not found.

## 7. Two-sided cold start, and agent networks where the other party has no agent

### Takeaway
The best-documented route is "come for the tool, stay for the network": give the hard side a product that is useful alone, then connect the users. I could confirm the framework and its standard example only through secondary summaries; primary sources were not opened.

### Cited Findings
- (Medium; secondary summary of Chris Dixon's January 2015 essay) The pattern is to attract users with a single-player tool and later convert them into network participants; OpenTable is the standard case, where the reservation book was useful to a restaurant alone and the network later sent diners — [Rework, single-player mode explainer](https://resources.rework.com/libraries/marketplace-growth/single-player-mode); [chapter summary of Andrew Chen's The Cold Start Problem](https://sachinjain024.github.io/awesome-books-mindmap/cold-start-problem/chapters/chapter-05.html)
- (Medium) Limits: products with no single-player value cannot use this; Dixon notes Facebook and Twitter started networks without a tool and calls that very hard — [Rework](https://resources.rework.com/libraries/marketplace-growth/single-player-mode)
- (Low, practitioner blog) Alternative: pick one side, subsidise or manually fulfil it, and prove the transaction in one geography before scaling — [RaftLabs](https://www.raftlabs.com/blog/two-sided-marketplace-cold-start)
- (Medium) A critique exists that single-player tools often fail to convert into networks ("single-player mode fallacy") — [Product Hunt discussion](https://www.producthunt.com/p/general/the-single-player-mode-fallacy)
- (High) Existing networks an agent can piggyback on in India: WhatsApp Business app accounts via coexistence (section 1), and consumer AI assistants that already place orders through Swiggy's published tool interface (section 8)

### Inferences
- For an agent network, the single-player version is clear: a seller's agent is useful the moment any human customer can reach it by link, QR or the seller's existing WhatsApp number. It needs no buyer-side agent. The reverse is weaker: a buyer's agent is only useful if it can reach sellers who have no agent, which means falling back to messaging or calling humans, the costly and policy-exposed path (sections 1 and 3).
- That asymmetry argues for supply-first: seller agents as a standalone product in one city or category, with agent-to-agent interaction added once density exists. The risk named in the critique applies: sellers may use the tool and never join a network, so the network step needs its own reason (for example, incoming quote requests).
- Meta's free-with-the-app Business AI is a direct competitor for the single-player tool on the seller side, so the standalone tool needs something Meta's does not offer (multi-channel reach, quoting, negotiation rules, portability off WhatsApp).

### Gaps
- Primary sources (Dixon's essay, Chen's book, Lenny Rachitsky's marketplace series) were not fetched; no concrete India cases (for example how local-services or B2B marketplaces seeded supply) were sourced.
- No documented case found of an agent-to-agent commerce network bootstrapping in practice.

## 8. Buyer-side demand: quotes, reorders, concierge, high-friction categories

### Takeaway
There is live infrastructure and stated consumer openness for assistant-led buying in India in 2026, concentrated in food and grocery with large platforms. I found no usage data on consumers asking an assistant to collect quotes from small sellers, and no category-level data on enquiry-to-order friction.

### Cited Findings
- (Medium; consultancy survey, stated intent not behaviour) Accenture Consumer Pulse 2026: 59% of Indian consumers would tell their AI agent which brands to consider; 36% would switch brands if an agent said another was a better fit — [CXOToday, 2026](https://cxotoday.com/media-coverage/consumers-in-india-are-ready-for-ai-agent-led-shopping-and-businesses-must-prepare-for-the-next-frontier-of-commerce/)
- (High) Swiggy lets users order food, groceries and table bookings through ChatGPT, Claude and Gemini via a published tool interface — [YourStory, Jan 2026](https://yourstory.com/2026/01/swiggy-lets-users-order-through-chatgpt-claude-gemini); its tools cover reading past orders and repeat items — [Stellagent analysis](https://stellagent.ai/insights/swiggy-money-mcp-agentic-payment)
- (High) Razorpay and NPCI launched agentic payments on Claude in February 2026, with a pilot covering Zomato, Swiggy and Zepto — [Razorpay newsroom](https://razorpay.com/newsroom/razorpay-npci-launch-agentic-payments-on-claude-powering-zomato-swiggy-zepto-at-the-india-ai-impact-summit/); [Business Today, 18 Feb 2026](https://www.businesstoday.in/technology/news/story/npci-anthropic-test-ai-driven-shopping-pilot-using-upi-payments-516761-2026-02-18)
- (Medium) Payment approval remains a friction point: the agent starts the transaction but the user approves in a UPI app, unless a prepaid wallet balance is used — [Stellagent analysis](https://stellagent.ai/insights/swiggy-money-mcp-agentic-payment)
- (Low; possibly non-India sample) Forrester, December 2025: only 35% of Gen Z and 23% of Gen X had used ChatGPT to search for a product — [build3 blog citing Forrester](https://blog.build3.org/?p=162)
- (High) Proxy for B2B enquiry demand: IndiaMART sustains about 2.2 lakh paying suppliers at about ₹67,000 a year for buyer enquiries (section 5)
- (Medium, merchant self-report) A small seller using Meta's Business AI reported 60–70 daily queries converting to 6–7 orders, i.e. about one order per ten enquiries — [Meta newsroom, May 2026](https://about.fb.com/news/2026/05/introducing-business-ai-on-whatsapp-for-small-businesses-in-india/)

### Inferences
- Evidence of demand is strongest where the catalog is structured and the seller is a large platform (reorder groceries, repeat a meal). That is the opposite end of the market from small sellers of custom goods or local services, where no data was found. The quote-collection use case is therefore unproven, not disproven.
- The sustained spend on IndiaMART and Justdial shows that sellers pay for inbound enquiries in wholesale and local services, which are also the categories where price is not posted and a quote must be requested. These are plausible first categories for a quoting agent, but that is reasoning from seller spend, not from buyer behaviour data.
- A roughly 10% enquiry-to-order rate (one merchant's self-report) implies about ten conversations' cost per order: ₹2–18 on text with a small model, which a fee per order of ₹10–20 or a flat plan could cover; on voice it would be ₹110–180 per order.

### Gaps
- No data found on usage of quote-request features (IndiaMART requirement postings, Justdial, Urban Company), on reorder/subscription rates outside grocery, or on concierge services in India.
- No category-level data on enquiry-to-order friction for made-to-order goods, local services or small-shop wholesale procurement.
- Status of shopping inside ChatGPT is disputed: Indian reports describe live integrations, while a blog citing CNBC (March 2026) says OpenAI ended its checkout feature. Not resolved.
