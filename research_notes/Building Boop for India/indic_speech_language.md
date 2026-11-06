# Speech and language technology for Indian languages (for Boop's voice-first assistant), as of November 2026

All prices were seen on 2026-11-06 unless another date is given. INR prices exclude GST. Where a USD figure is converted to INR, an assumed rate of about ₹88 = $1 is used. That rate is an assumption and was not checked against a source.

## 1. Sarvam AI: STT (Saarika/Saaras), TTS (Bulbul), translation (Mayura/Translate), LLMs, prices, free tier, licences

### Takeaway
Sarvam has the most complete Indian-language voice stack on one bill, and it is cheap:
- Speech-to-text (STT) costs ₹0.49/min pay-as-you-go, streaming or batch.
- Bulbul v4 Flash text-to-speech (TTS) is ₹1–2 per 1K characters, depending on which page you read. Bulbul v3 is ₹3 per 1K.
- Translation is ₹2 per 1K characters.
- Sarvam 105B costs ₹15 input and ₹60 output per 1M tokens.
- New accounts get ₹100 of free credit that does not expire.

Saaras v4 (25 Sep 2026) covers all 22 scheduled languages plus English, with WebSocket streaming and a time to first token (TTFT) under 150 ms. Bulbul v3 covers 11 Indian languages with a first byte under 250 ms. The Sarvam 30B and 105B LLMs are open weights under Apache 2.0. Sarvam has not said that the speech models are open.

### Cited Findings
**Pricing and plans (seen 2026-11-06)**
- **STT:** real-time and batch are both ₹0.49/min pay-as-you-go. Pro is ₹0.45, Growth ₹0.41 and Business ₹0.38. With diarization the prices are ₹0.59 / 0.54 / 0.50 / 0.47 per minute. Language identification costs ₹0.35 per 1K characters. — [Sarvam API pricing](https://www.sarvam.ai/api-pricing)
- **STT units changed.** STT is now billed per minute, billed per second. The older list price was ₹30/hour, or ₹45/hour with diarization, and Saarika v2.5 is now "legacy". — [Sarvam docs pricing](https://docs.sarvam.ai/api/getting-started/pricing.md); [smallest.ai summary of the older ₹30/hr rate](https://smallest.ai/blog/sarvam-ai-speech-to-text-pricing)
- **The default STT model moved.** A search snippet says the REST and Batch endpoints now default to `saaras:v3`. — [Sarvam changelog](https://docs.sarvam.ai/api/changelog.md)
- **Bulbul v4 Flash TTS (real-time, streaming, WebSocket):**
  - The pricing page lists ₹2.00 / 1.85 / 1.70 / 1.70 per 1K characters (Pay-as-you-go / Pro / Growth / Business).
  - A 50% discount runs until 12 Nov and gives ₹1.00 / 0.925 / 0.85 / 0.80. — [Sarvam API pricing](https://www.sarvam.ai/api-pricing)
  - The docs pricing page lists ₹1.00 / 0.925 / 0.85, so it appears to show the discounted price as the price. — [Sarvam docs pricing](https://docs.sarvam.ai/api/getting-started/pricing.md)
  - The TTS product page says "₹20 per 10K characters, currently ₹10 (50% off until 12 Nov)." — [Sarvam TTS page](https://www.sarvam.ai/text-to-speech)
- **Other TTS prices:** Bulbul v3 is ₹3.00 / 2.85 / 2.70 / 2.60 per 1K characters. Instant voice cloning is ₹2.00 per 1K characters on every tier. — [Sarvam API pricing](https://www.sarvam.ai/api-pricing)
- **Translation and transliteration:**
  - Translate (standard, formal or colloquial) is ₹2.00 / 1.70 / 1.50 / 1.35 per 1K characters.
  - Transliteration is ₹2.00 / 2.00 / 1.80 / 1.70 per 1K characters.
  - Document translation is ₹5 per 1K characters per language.
  - The pricing page does not name "Mayura" or "Sarvam-Translate" any more. It only lists "Translate". — [Sarvam API pricing](https://www.sarvam.ai/api-pricing)
- **LLM prices, per 1M tokens (input / cached input / output):**

  | Model | Input | Cached input | Output | Note |
  |---|---|---|---|---|
  | Sarvam 105B (`sarvam-105b`, also `sarvam-105b-conversations`) | ₹15 | ₹5 | ₹60 | |
  | Sarvam Prism | ₹4 | — | ₹0 | Its purpose is not described |
  | GLM‑5.3 | ₹126 | ₹20 | ₹390 | Third-party model resold by Sarvam |
  | GLM‑5.3 Flash | ₹13.5 | ₹2.5 | ₹45 | Third-party model resold by Sarvam |
  | Gemma 4 31B | ₹35 | ₹10 | ₹90 | Third-party model resold by Sarvam |
  | DeepSeek V4.1 Flash 1017 | ₹25 | ₹0.5 | ₹105 | Third-party; 1,048,576-token context |

  Sources: [Sarvam docs pricing](https://docs.sarvam.ai/api/getting-started/pricing.md); [Sarvam changelog](https://docs.sarvam.ai/api/changelog.md)
- **Sarvam 105B price cut.** Pricing for `sarvam-105b` changed on 10 Oct 2026. A third-party tracker records this as a price cut. — [Sarvam changelog](https://docs.sarvam.ai/api/changelog.md); [usagepricing.com](https://www.usagepricing.com/blueprint/activity/sarvam-ai-2026-10-15-sarvam-105b-price-cut)
- **Free tier and credits:**
  - Each verified user gets ₹100 of credit on signup. It works on every API and never expires.
  - Each payment adds credits 1:1 (₹1,000 buys 1,000 credits), and payments are non-refundable.
  - When credits run out the API returns HTTP 402. A rate-limit hit returns 429.
  - Sources: [Sarvam docs pricing](https://docs.sarvam.ai/api/getting-started/pricing.md); [Sarvam API pricing](https://www.sarvam.ai/api-pricing)
- **Plan fees:** Pay-as-you-go is ₹0 a month, Pro ₹9,999, Growth ₹49,999 and Business ₹1,99,999. Enterprise is custom. — [Sarvam API pricing](https://www.sarvam.ai/api-pricing)
  - Third-party captures say monthly tiers began in Oct 2026 at Pro ₹2,000 / Growth ₹10,000 / Business ₹50,000, and that these were later raised to the current figures. — [PricingSaaS](https://pricingsaas.com/companies/sarvam)
- **Rate limits (Pay-as-you-go / Pro / Growth):**
  - STT REST: 60 / 100 / 4,000 requests per minute. STT WebSocket: 20 / 100 / 100 concurrent connections.
  - TTS REST and HTTP streaming: 60 / 200 / 1,000 requests per minute. TTS WebSocket: 60 / 200 / 1,000 concurrent connections.
  - Sarvam 105B: 60 / 200 / 300 requests per minute.
  - Limits apply per account, not per API key. Opening WebSockets in a fast burst can get them rejected with close code 1003.
  - Source: [Sarvam docs pricing](https://docs.sarvam.ai/api/getting-started/pricing.md)
- **Sarvam's own voice-agent product** is advertised "as low as ₹3 a minute", with models included. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)

**Speech recognition models**
- **Saaras v3:**
  - Native streaming built for low latency, across 22 Indian languages plus English, and better on code-mixed and noisy speech. — [Sarvam Saaras v3 blog](https://www.sarvam.ai/blogs/asr)
  - Sarvam reports about 19% WER on IndicVoices. — [Sarvam Saaras v3 blog](https://www.sarvam.ai/blogs/asr)
- **Saaras v4 (released 25 Sep 2026):**
  - Architecture: an audio encoder plus a 3B-parameter hybrid state-space LLM decoder, trained in-house. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - Claims "SOTA on all 22 Indian languages" plus English. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - 16.03% WER on IndicContextEval in the L5 keyterm-prompting setting. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - Language-identification error is 5.22% across all 22 languages and 2.9% across the top 10. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - WebSocket streaming has a TTFT under 150 ms. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - API output modes are transcribe, translate (straight to English), translit, verbatim and codemix. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - The REST API takes audio under 30 s. The Batch API takes files up to 2 hours, with diarization. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - Competitors (GPT-4o Transcribe, ElevenLabs Scribe v2, Deepgram Nova3) appear only in qualitative examples, not in WER tables. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)
  - Press coverage of the launch. — [MarkTechPost, 26 Sep 2026](https://www.marktechpost.com/2026/09/26/sarvam-ai-releases-saaras-v4-a-speech-to-text-model-for-all-22-indian-languages-and-global-english/)
- **Independent Hindi benchmark (Vaani, ARTPARK-IISc, Sep 2026):** on Vaani Benchmark V1.0, Saaras v3 scored 19.5 / 16.4 / 13.1% WER across three scoring approaches. That is second only to Gemini‑3.1‑Pro (19.0 / 15.6 / 12.3) and ahead of Google Chirp 3 (22.5 / 19.2 / 15.6) and Azure Speech (26.6 / 23.6 / 18.7). — [Vaani Benchmark arXiv 2606.21408](https://arxiv.org/html/2606.21408)

**Text-to-speech models**
- **Bulbul v3:**
  - 11 Indian languages: Hindi, Tamil, Telugu, Bengali, Malayalam, Marathi, Gujarati, Kannada, Punjabi, Odia and Assamese.
  - 35+ voices and 48 kHz full-band audio, plus 8 kHz for telephony.
  - First byte under 250 ms over WebSocket. REST takes up to 2,500 characters per request.
  - Handles Hinglish, Tanglish and similar mixes in one pass. Offers emotion, pace (0.5–2x) and pitch controls.
  - Voice cloning needs a 30–60 s sample and is not on the self-serve free tier.
  - Source: [Sarvam TTS page](https://www.sarvam.ai/text-to-speech)
- **Bulbul v3 listening test (vendor-reported):** in a blind study by Josh Talks at 8 kHz, with 50–70 annotators per language, Bulbul v3 won 77.95% against ElevenLabs Flash v2.5, 43.64% against ElevenLabs v3 Alpha and 40.08% against Cartesia Sonic‑3. — [Sarvam TTS page](https://www.sarvam.ai/text-to-speech)
- **Bulbul v4 timeline:**
  - Bulbul V4 became available in Voice Agents on 6 Oct 2026. — [Sarvam changelog](https://docs.sarvam.ai/api/changelog.md)
  - Bulbul V3 reaches end of life in Voice Agents on 10 Nov 2026 but stays on the TTS API. — [Sarvam changelog](https://docs.sarvam.ai/api/changelog.md)
  - The TTS page gives no language, voice or latency specs for Bulbul v4 or v4 Flash. — [Sarvam TTS page](https://www.sarvam.ai/text-to-speech)

**LLMs and licences**
- **Sarvam‑105B:**
  - Licence: Apache 2.0, with weights on Hugging Face and AIKosh.
  - Mixture-of-experts: 106B total parameters, about 10B active, with a 128K context.
  - Sources: [HF sarvam-105b](https://huggingface.co/sarvamai/sarvam-105b); [Artificial Analysis, Apr 2026](https://artificialanalysis.ai/ja/articles/sarvam-105b-Sarvam-30b-everything-you-need-to-know)
- **Sarvam‑30B:**
  - Licence: Apache 2.0.
  - Mixture-of-experts: 32B total parameters, about 2.4B active, with a 65K context.
  - It is not on the current API price list.
  - Sources: [HF sarvam-30b](https://huggingface.co/sarvamai/sarvam-30b); [Artificial Analysis, Apr 2026](https://artificialanalysis.ai/ja/articles/sarvam-105b-Sarvam-30b-everything-you-need-to-know)
- **Artificial Analysis Intelligence Index:** Sarvam 105B scores 18 and Sarvam 30B scores 12. Both are weaker than peers on agentic coding and on AA‑Omniscience. — [Artificial Analysis](https://artificialanalysis.ai/ja/articles/sarvam-105b-Sarvam-30b-everything-you-need-to-know)
- **Sarvam‑M (2025, built on Mistral Small)** is older. Its card reports 0.75 on MILU‑IN, against 0.59–0.67 for the comparison models. This is vendor-reported. — [Sarvam-M blog](https://www.sarvam.ai/blogs/sarvam-m)

### Inferences
- For Boop, one Sarvam key gives streaming STT, streaming TTS, translation and a cheap Indic-tuned LLM, all billed in INR.
- The free tier is small. ₹100 is roughly 200 minutes of STT alone, or about 70 minutes of full STT+TTS calls. It is enough to try the service, not to run a free tier for users.
- **Bring-your-own-key fit.** Boop is open source and lets users pick their model, so a user-supplied Sarvam key (BYOK) fits the same way OpenRouter does today.
- **Concurrency is the bottleneck on pay-as-you-go.** The cap is 20 concurrent STT WebSockets per account. If Boop proxied all users through one account, it would need the Pro plan (₹9,999/mo, 100 concurrent) or higher.
- **Bulbul v4 Flash prices.** The ₹1.00/1K figure is a promotion that ends 12 Nov 2026. Plan on ₹2.00/1K list from then on.

### Gaps
- No official Bulbul v4 / v4 Flash spec sheet was found: languages, voice count, latency and MOS are all unknown.
- No full per-language WER table for Saaras v4 was found, because the blog's chart values were not in text.
- No statement was found on whether the Saaras or Bulbul weights are open. They appear to be API-only.
- No current page uses the name "Mayura". Its languages and quality compared with the generic "Translate" product are not described on the pricing pages.
- The exact Saaras v4 per-minute price is unclear. The pricing page lists a single "Speech to Text" rate, which presumably covers v3 and v4.

## 2. AI4Bharat (IIT Madras): IndicConformer, IndicTrans2/3, Indic Parler‑TTS, Indic‑Transcribe; quality, licences, size, on-phone feasibility

### Takeaway
AI4Bharat's models are open and commercially usable:
- IndicConformer 600M (MIT) covers 22 languages for speech recognition (ASR), and its Hindi accuracy roughly matches Saaras v3 on an independent benchmark.
- IndicTrans2 (MIT) does translation, with distilled 200M and 320M variants.
- Indic Parler‑TTS (Apache 2.0, 0.9B) covers about 21 languages for TTS.

IndicConformer ships ONNX and quantized exports, so on-device ASR is feasible. Indic Parler‑TTS, at 0.9B parameters in FP32, is a server-class model rather than a phone model.

### Cited Findings
**IndicConformer 600M multilingual**
- Licence: MIT. — [HF IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- Size and coverage: 600M parameters across all 22 scheduled languages (as, bn, brx, doi, gu, hi, kn, kok, ks, mai, ml, mni, mr, ne, or, pa, sa, sat, sd, ta, te, ur). — [HF IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- Architecture: a hybrid CTC + RNNT Conformer. — [HF IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- Exports: ONNX is supported, and the page lists 15 quantized variants. — [HF IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- Access: downloading requires agreeing to share your Hugging Face account information. — [HF IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- The page recommends a newer "Indic-Transcribe" model, described as covering 25 languages with better quality. — [HF IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- On the Vaani Hindi benchmark it scored 20.0 / 16.8 / 13.1% WER, essentially tied with Sarvam Saaras v3 (19.5 / 16.4 / 13.1). It beat Google Chirp 3 (22.5 / 19.2 / 15.6) and Azure (26.6 / 23.6 / 18.7) and was far ahead of Whisper‑large‑v3 (32.8 / 30.0 / 26.4). — [Vaani Benchmark arXiv 2606.21408](https://arxiv.org/html/2606.21408)

**Indic‑Transcribe (2026)**
- 1.2B parameters, covering 26 Indian languages plus English. Built by Mitesh Khapra (IIT Madras), AI4Bharat and BodhanAI. — [Business Today, 18 Aug 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/from-hindi-to-regional-accents-this-new-ai-model-is-built-to-understand-26-indian-languages-549708-2026-08-18)
- It was scheduled to go live via Bodhan.AI on 5 Sep 2026. — [Business Today, 18 Aug 2026](https://www.businesstoday.in/technology/artificial-intelligence/story/from-hindi-to-regional-accents-this-new-ai-model-is-built-to-understand-26-indian-languages-549708-2026-08-18)
- Bodhan's models are described as shipping as open weights and as hosted APIs. — [CareerIndia](https://www.careerindia.com/news/bodhan-ai-open-models-2026-career-paths-indic-speech-translation-ocr-011-65583.html)

**IndicTrans2**
- Licence: the code and model checkpoints are MIT. The training data is CC0 for mined and back-translated data and CC‑BY‑4.0 for BPCC‑Human and the IN22 test sets. — [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2)
- Coverage: 22 scheduled languages.
- Sizes: about 1B parameters for the base models (En‑Indic, Indic‑En, Indic‑Indic). The distilled models are 200M (En‑Indic and Indic‑En) and 320M (Indic‑Indic).
- Inference: CTranslate2 versions exist for efficient inference.
- Updates: RoPE long-context variants with 2,048 tokens were added in Jan 2025.
- Source for this block: [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2)

**IndicTrans3‑beta (Mar 2025)**
- A document-level translation model for 22 languages, available as a Hugging Face Space demo. No licence or size was stated. — [Analytics India Magazine, Mar 2025](https://analyticsindiamag.com/ai-news-updates/ai4bharat-launches-indictrans3-for-22-indic-languages/)

**Indic Parler‑TTS**
- Licence and size: Apache 2.0, with 0.9B parameters in FP32 safetensors. — [HF Indic Parler-TTS](https://huggingface.co/ai4bharat/indic-parler-tts)
- Languages: 21 are officially supported (as, bn, brx, doi, en, gu, hi, kn, kok, mai, ml, mni, mr, ne, or, sa, sat, sd, ta, te, ur). Chhattisgarhi, Kashmiri and Punjabi are supported unofficially.
- Voices: 69 named speakers.
- Quality: AI4Bharat reports a "Native Speaker Score" for the fine-tuned model of 84.79 for Hindi and 75.48 for Tamil.
- Dates: the paper is from Feb 2024 and the collection was updated in Dec 2024.
- The card gives no hardware requirements.
- Source for this block: [HF Indic Parler-TTS](https://huggingface.co/ai4bharat/indic-parler-tts)

### Inferences
- **IndicConformer is the strongest free option for on-device or self-hosted ASR.** Its MIT licence allows commercial use, and its Hindi WER matches Sarvam's API.
- **Phone fit.** An INT8-quantized 600M model would be roughly 0.6 GB of weights. That is plausible on mid-range phones with 6–8 GB of RAM but heavy as an app download, so it would suit an optional downloadable language pack. This is an estimate from the parameter count, not a measured figure.
- **Indic Parler‑TTS is too large for phones.** At 0.9B parameters in FP32 its weights are about 3.6 GB, and it is an autoregressive model, so it is better suited to a self-hosted GPU server than a phone.
- **IndicTrans2 distilled (200M) could translate on-device,** but Boop probably doesn't need a separate translation step if the LLM handles Indic languages directly.

### Gaps
- IndicWhisper / Vistaar: no current model card was fetched, so its licence and accuracy compared with IndicConformer are not confirmed here.
- No measured Android latency, real-time factor or RAM figures for IndicConformer ONNX were found. A Medium write-up on running AI4Bharat models offline on Android returned HTTP 403.
- Indic‑Transcribe: no licence, no benchmarks, and no confirmation that it actually launched on 5 Sep 2026.
- No reliable source was found for AI4Bharat's own hosted inference API or its terms.

## 3. Bhashini (Government of India): APIs, access terms, cost, quality and reliability

### Takeaway
Bhashini (MeitY) offers ASR, translation, TTS and transliteration APIs across 22 languages. Registration is free, and secondary sources describe it as free for developers. However, Bhashini's own API docs say that production use, or any integration that charges end users, requires contacting the Bhashini team for a paid version, and no public price list was found. No reliability or latency data was found.

### Cited Findings
- The official Bhashini API docs say that if a Bhashini Sahyogi, App Mitra or Udyat Mitra user wants to use the APIs on production systems, or is charging end users, they should "reach out to Bhashini team for the paid version of the APIs and exploring Pricing Plans". The page may be about 3 years old. — [Bhashini APIs GitBook](https://bhashini.gitbook.io/bhashini-apis)
- Secondary guides say developers, startups and companies get free API access after registering at bhashini.gov.in. None quotes an official tariff or usage cap. — [schemesinindia.in](https://schemesinindia.in/central/bhashini-digital-india-language-ai-platform)
- **"Bhashini.ai" is a different, commercial company.** Its credit plans cost ₹1,000 to ₹1,00,000 a month, and its trial does not include API keys. It is not the government service. — [Bhashini.ai pricing](https://www.bhashini.ai/pricing)
- ULCA (Universal Language Contribution APIs) is an open-source data and benchmarking platform under MIT, run by the Digital India Bhashini Division. — [ULCA GitHub](https://github.com/bhashini-dibd/ulca)
- The IndiaAI / AIKosh portal lists startups and MSMEs as eligible categories, subject to its criteria and usage terms. — [CitizenNest guide](https://www.citizennest.com/guide/indiaai-compute-aikosha-students-developers-guide)

### Inferences
- **Bhashini is a reasonable free fallback for prototyping** and for rare languages that Sarvam's TTS does not cover. It is risky as Boop's main real-time path, because there is no published uptime, latency or rate-limit information and commercial terms need negotiation.
- **Many Bhashini pipelines are built on AI4Bharat models,** so Boop could get similar quality by self-hosting IndicConformer and IndicTrans2. This is widely reported but was not verified in this session.

### Gaps
- No official 2026 Bhashini tariff, rate limits, uptime figures, streaming latency or quality benchmarks were found.
- The government portal bhashini.gov.in itself was not fetched.

## 4. Big cloud for Indian languages: Google STT/Chirp, Google TTS, Gemini Live, Azure, AWS, ElevenLabs

### Takeaway
Google Cloud is the main option with good coverage and a clear price list:
- STT costs $0.016/min for V2 standard, including Chirp, falling with volume.
- Chirp 3 HD TTS costs $30 per 1M characters, with 1M characters free each month.
- Gemini Flash TTS costs $9 per 1M audio tokens until 31 Dec 2026, then $18.

The Gemini Live API lists only Hindi, Marathi, Tamil, Telugu, Bengali (Bangladesh) and en‑IN among Indian-region languages. Gujarati, Kannada, Malayalam, Punjabi and Urdu are not listed.

On the independent Hindi WER benchmark, Gemini 3.1 Pro is the most accurate system, and Chirp 3 and Azure trail Sarvam and IndicConformer. ElevenLabs Scribe v2 Realtime is the cheapest streaming STT found, at $0.39/hour.

### Cited Findings
**Google Cloud Speech-to-Text**
- V2 "Standard" recognition, which includes `chirp`, costs $0.016/min for the first 500K minutes a month. It then drops to $0.01, $0.008 and $0.004 per minute at 2M+ minutes. — [Google STT pricing](https://cloud.google.com/speech-to-text/pricing)
- Dynamic batch recognition costs $0.003/min. — [Google STT pricing](https://cloud.google.com/speech-to-text/pricing)
- V1 gives 60 free minutes a month, then charges $0.016/min with data logging or $0.024/min without it. — [Google STT pricing](https://cloud.google.com/speech-to-text/pricing)
- Chirp 3 is listed at $0.016/min on OpenRouter. — [OpenRouter Chirp 3](https://openrouter.ai/models/google/chirp-3)
- Chirp 3 scored 22.5 / 19.2 / 15.6% WER on the Vaani Hindi benchmark. — [Vaani arXiv](https://arxiv.org/html/2606.21408)

**Google Cloud TTS**
- Chirp 3 HD voices cost $30 per 1M characters, with 0–1M characters free each month. Instant custom voice costs $60 per 1M. — [Google TTS pricing](https://cloud.google.com/text-to-speech/pricing)
- Legacy voices:
  - Neural2: $16 per 1M characters, 1M free.
  - WaveNet: $4 per 1M, 4M free.
  - Standard: $4 per 1M, 4M free.
  - Studio: $160 per 1M.
  - Source: [Google TTS pricing](https://cloud.google.com/text-to-speech/pricing)
- Gemini TTS:
  - Gemini 3.8 Flash TTS (Preview) costs $0.50 per 1M text input tokens and $9.00 per 1M audio output tokens through 31 Dec 2026, rising to $1.00 / $18.00 from 1 Jan 2027.
  - Gemini 3.8 Flash‑Lite TTS costs $6 per 1M audio tokens, rising to $12.
  - Audio is counted at 25 tokens per second.
  - Source: [Google TTS pricing](https://cloud.google.com/text-to-speech/pricing)

**Gemini Live API**
- **Languages:** the docs name `gemini-3.8-live` and list hi‑IN, mr‑IN, ta‑IN, te‑IN, bn‑BD (Bangladesh) and en‑IN bundled with hi‑IN. Gujarati, Kannada, Malayalam, Punjabi and Urdu are not listed. — [Vertex Live API language docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/configure-language-voice)
- **Language switching:** native-audio models can switch languages mid-conversation, and the language can be restricted through the system prompt. — [Vertex Live API language docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/configure-language-voice)
- **Pricing (third-party sources):** gemini‑3.8‑live costs $3 per 1M audio input tokens (about $0.005/min) and $12 per 1M audio output tokens (about $0.018/min). Text output costs $4.50 per 1M. — [developersdigest](https://www.developersdigest.tech/models/speech/google); [tokenkarma](https://tokenkarma.app/blog/gemini-live-api-pricing-voice-agents-2026/)
- **Deprecations (third-party report, needs checking):** Gemini 3.1 Flash Live Preview and the Gemini 2.5 Flash Native Audio preview shut down in the Gemini Developer API on 17 Nov 2026, and `gemini-live-2.5-flash-native-audio` on Vertex is slated for deprecation on 13 Dec 2026. — [tokenkarma](https://tokenkarma.app/blog/gemini-live-api-pricing-voice-agents-2026/); [Cekura](https://www.cekura.ai/blogs/gemini-live-api-pricing)
- **Consumer Gemini app:** separately from the API, the Gemini app's Live mode was reported (Aug 2026) to be adding Hindi and 8 other Indian languages. — [TheTechOutlook](https://www.thetechoutlook.com/new-release/software-apps/googles-gemini-live-officially-announced-to-support-hindi-and-8-other-indian-languages-to-roll-out-in-the-coming-weeks/)
- **Gemini models on the Vaani Hindi benchmark:** Gemini‑3.1‑Pro was the best system tested (19.0 / 15.6 / 12.3% WER), and Gemini‑3.5‑Flash scored 22.0 / 18.7 / 15.3. — [Vaani arXiv](https://arxiv.org/html/2606.21408)

**Azure Speech**
- Real-time STT costs about $1 per audio hour (≈$0.0167/min), batch about $0.18/hour and fast transcription about $0.36/hour. — [developersdigest Azure](https://www.developersdigest.tech/models/speech/azure); [costbench](https://costbench.com/software/ai-voice-tools/microsoft-speech/)
- Neural TTS is about $15–16 per 1M characters, and Neural HD is about $22–48 per 1M. Sources conflict on these figures. — [makerstack](https://makerstack.co/reviews/azure-ai-speech-review/); [developersdigest Azure](https://www.developersdigest.tech/models/speech/azure)
- The F0 free tier gives 5 hours of STT and 0.5M characters of neural TTS a month. — [makerstack](https://makerstack.co/reviews/azure-ai-speech-review/)
- Azure scored 26.6 / 23.6 / 18.7% WER on the Vaani Hindi benchmark. — [Vaani arXiv](https://arxiv.org/html/2606.21408)

**AWS Transcribe**
- Hindi (hi‑IN) supports batch and streaming. Tamil (ta‑IN) and Telugu (te‑IN) show "batch, streaming*", with a footnote that was not read. en‑IN supports streaming. — [AWS Transcribe languages](https://docs.aws.amazon.com/transcribe/latest/dg/supported-languages.html)

**ElevenLabs**
- Scribe v2 Realtime costs $0.39/hour (about $0.0065/min). Batch Scribe costs $0.22/hour. — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- Scribe v2 Realtime launched in Nov 2025 with sub‑150 ms latency and 90+ languages, including 11 Indian languages (hi, ta, te, ml, bn, gu, kn, or and others). — [CXO Digital Pulse](https://www.cxodigitalpulse.com/elevenlabs-launches-scribe-v2-realtime-for-sub-150-ms-live-transcription-across-90-languages/)
- ElevenLabs reports 93.5% accuracy on FLEURS. A competitor, Soniox, disputes its Hindi and Tamil accuracy. Both claims are vendor material. — [CXO Digital Pulse](https://www.cxodigitalpulse.com/elevenlabs-launches-scribe-v2-realtime-for-sub-150-ms-live-transcription-across-90-languages/); [Soniox vs ElevenLabs (Hindi)](https://soniox.com/compare-stt/soniox-vs-elevenlabs/hindi)

### Inferences
- **Gemini Live alone cannot meet the "Hindi + 4–5 languages" goal.** It covers Hindi, Marathi, Tamil and Telugu, while Bengali is only listed for Bangladesh, and Gujarati, Kannada and Malayalam are missing. A cascade of STT → LLM → TTS is needed for the wider set.
- **Boop's Gemini Live integration should be checked against the reported Nov–Dec 2026 deprecations.** If it targets a 2.5 native-audio or 3.1 Flash Live preview model, it needs a migration.
- **Google's prices** work out to about $0.016/min for STT and about $0.012 for 400 characters of Chirp 3 HD speech. That is roughly 2× Sarvam's cost per minute, and Google's Hindi WER is worse.
- **ElevenLabs Scribe v2 Realtime and Sarvam STT cost about the same per minute.** ElevenLabs is about $0.0065 and Sarvam about $0.0056 (₹0.49 at the assumed rate), so Sarvam is slightly cheaper. There is no independent Indic WER evidence for ElevenLabs.

### Gaps
- No official Google list of Chirp 3 or Chirp 3 HD Indian languages and voices was found.
- No official Azure or AWS price page rendered: Azure figures come from aggregators, and AWS Transcribe and Polly prices were not found. Polly Hindi voices (Kajal / Aditi) were not verified.
- ElevenLabs TTS (Flash v2.5 / v3) per-character API prices for Hindi were not retrieved.
- No independent latency comparison was found across providers for Indian-language streaming.
- How the Gemini Live API bills accumulated session context (text and audio tokens per turn) was not verified.

## 5. On-device Android: built-in recognizer and TTS packs, Gemini Nano, small open models

### Takeaway
Android's on-device recognizer API exists on Android 12+ (API 31) with an availability check. Google's "Speech Recognition & Synthesis" app lists about 21 Indian languages plus en‑IN, but no source confirmed which work offline. Gemini Nano's Indian-language support is undocumented and depends on the device.

The best measured small model is Gemma4‑E2B‑IT (open), at 26.2% WER on Hindi, which is about Azure's level. IndicConformer (ONNX, quantized) is the strongest open option. Whisper‑large‑v3 is clearly weak on Hindi.

### Cited Findings
**Android built-in speech**
- `SpeechRecognizer.createOnDeviceSpeechRecognizer()` fails if `isOnDeviceRecognitionAvailable()` returns false. It is available from API level 31. — [Android SpeechRecognizer reference](https://developer.android.com/reference/android/speech/SpeechRecognizer); [Microsoft .NET Android binding docs](https://learn.microsoft.com/en-us/dotnet/api/android.speech.speechrecognizer.createondevicespeechrecognizer?view=net-android-34.0&viewFallbackFrom=xamarin-android-sdk-12)
- A developer test of Hindi‑English code-switching used EXTRA_LANGUAGE and EXTRA_PREFER_OFFLINE, and reported that Android 14 added multi-language switching. This is anecdotal. — [HackerNoon](https://hackernoon.com/testing-androids-on-device-speech-recognition-with-hindi-english-code-switching)
- **Speech Recognition & Synthesis app (formerly "Speech Services by Google"):**
  - Lists Assamese, Bengali, Bodo, Dogri, Gujarati, Hindi, Kannada, Kashmiri, Konkani, Maithili, Malayalam, Manipuri, Marathi, Odia, Punjabi, Sanskrit, Santali, Sindhi, Tamil, Telugu, Urdu and en‑IN, without saying which work offline.
  - "Users must install voice data for each language."
  - The latest build listed is from Nov 2025, and the app requires Android 8+.
  - Source: [Wikipedia: Speech Recognition & Synthesis](https://en.wikipedia.org/wiki/Speech_Recognition_%26_Synthesis)
- Google's Live Transcribe has offered offline transcription since March 2022, provided the language pack is installed. — [Wikipedia: Live Transcribe](https://en.wikipedia.org/wiki/Live_Transcribe)

**Gemini Nano**
- Language support "may differ depending on the device configuration and the model downloaded". — [ML Kit GenAI overview](https://developers.google.com/ml-kit/genai)
- The Prompt API runs on specific nano‑v2 and nano‑v3 devices and performs best on the Pixel 10, which has nano‑v3. — [Android Gemini Nano docs](https://developer.android.google.cn/ai/gemini-nano?hl=en)
- The Prompt API reached alpha in late 2025. — [InfoQ, Nov 2025](https://www.infoq.com/news/2025/11/android-genai-prompt-api)
- Earlier, summarisation covered only English, Japanese and Korean, and Hindi was not mentioned. — [heise](https://heise.de/-10387851)

**Open models and toolkits**
- On the Vaani Hindi benchmark:
  - Gemma4‑E2B‑IT (open): 26.2 / 23.2 / 19.4% WER.
  - Shrutam‑HindiASR‑1.0 (open): 24.5 / 21.5 / 18.1.
  - OmniASR_LLM_1B: 32.2 / 29.3 / 25.6.
  - Whisper‑large‑v3: 32.8 / 30.0 / 26.4.
  - Source: [Vaani arXiv 2606.21408](https://arxiv.org/html/2606.21408)
- IndicConformer 600M has ONNX and 15 quantized variants under MIT, covering 22 languages (see section 2). — [HF IndicConformer](https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual)
- The Vosk offline toolkit lists Hindi, Telugu and Gujarati among its models. — [Vosk](https://alphacephei.com/vosk/)

### Inferences
- **Practical free tier for Boop.** Use Android's on-device recognizer and TTS where `isOnDeviceRecognitionAvailable()` passes and the voice data is installed, then send the text to the user's cloud LLM. The STT and TTS cost is ₹0. Quality for Tamil, Telugu, Bengali and others must be tested on real devices.
- **Gemma 4 E2B is the most interesting on-device candidate.** It accepts audio, so one on-phone model could do both ASR and simple replies, and its Hindi WER is similar to Azure's. Its phone memory and latency were not measured here.
- **Whisper variants are a poor default for Indic speech.** Whisper‑large‑v3 is the worst system on the Hindi benchmark, and smaller Whisper models would be worse still. This last point is an inference.

### Gaps
- No official list was found of which Indian languages Android's recognizer and TTS support offline in 2026. Device testing is needed.
- No Gemini Nano language table for Hindi or other Indic languages was found.
- No measured phone latency, RAM or battery figures were found for IndicConformer, Gemma 4 E2B or sherpa‑onnx Indic models on mid-range Android phones.

## 6. Indian-language LLM quality: frontier vs Indian models; benchmarks; tokenizer cost penalty

### Takeaway
On the main public benchmark, MILU (2024), frontier models led: GPT‑4o scored about 72–74% and Gemini 1.5 Pro about 67.7%, while small Indian models trailed. Sarvam's newer 30B/105B models claim competitive MILU scores (vendor-reported), but they score low on general intelligence indices.

Indic scripts cost extra tokens:
- On GPT‑4o's tokenizer, Hindi takes about 1.3× as many tokens as English, Bengali about 1.56× and Tamil about 2.6×.
- Sarvam's own tokenizer is more efficient.
- No measured figures exist for Claude or Gemini.

### Cited Findings
**Benchmarks**
- MILU covers 8 domains, 41 subjects and 11 Indic languages. GPT‑4o has the top average, given as 74% in the arXiv HTML and Hugging Face versions and 72% in an earlier version. — [MILU arXiv](https://arxiv.org/html/2411.02538); [HF MILU dataset](https://huggingface.co/datasets/ai4bharat/MILU)
- On MILU, Gemini‑1.5‑Pro scored about 67.7% and Gemini‑1.5‑Flash about 61.6%. Indian models (Krutrim‑spectre‑v2, sarvam‑2b‑v0.5) "perform slightly below their English counterparts of comparable scale". These are 2024 data. — [MILU PDF](https://arxiv.org/pdf/2411.02538)
- Sarvam‑M reports MILU‑IN 0.75 against 0.59–0.67 for its baselines (vendor, 2025). — [Sarvam-M blog](https://www.sarvam.ai/blogs/sarvam-m)
- A third-party overview reports MILU 76.8 for Sarvam‑30B and notes that MILU was dropped from the Sarvam‑105B card. — [ashishkumar.ai](https://ashishkumar.ai/blog/indic-models-benchmark-and-bazaar/)
- An Aug 2026 arXiv paper found that Indian foundation models report strong scores on saturated benchmarks (MMLU, MATH‑500) but rarely take part in newer agentic evaluations. It argues that apparent capability gaps partly reflect gaps in evaluation maturity. Sarvam reports the broadest coverage. — [arXiv 2608.11891](https://arxiv.org/abs/2608.11891)
- Artificial Analysis gives an Intelligence Index of 18 for Sarvam 105B and 12 for Sarvam 30B (Apr 2026). — [Artificial Analysis](https://artificialanalysis.ai/ja/articles/sarvam-105b-Sarvam-30b-everything-you-need-to-know)

**Tokenizer cost**
- Sarvam says existing multilingual models need 4–8 tokens per word for Indic scripts, against about 1.4 for English, and that Sarvam‑1's tokenizer needs 1.4–2.1 (2024). — [Sarvam-1 blog](https://www.sarvam.ai/blogs/sarvam-1)
- Sarvam's 2024 table gives these tokens per word:

  | Tokenizer | English | Hindi | Tamil |
  |---|---|---|---|
  | GPT‑4o | 1.23 | 1.65 | 3.17 |
  | Llama‑3.1 | — | — | 12.39 |
  | Gemma‑2 | — | — | 4.19 |
  | Sarvam‑2B | — | — | 2.17 |

  Source: [Sarvam-1 blog](https://www.sarvam.ai/blogs/sarvam-1)
- An independent arXiv audit (Aug 2026) found Bengali needs 1.56× as many GPT‑4o tokens as English, and up to 4.5× on Qwen2.5 and Mistral tokenizers. Every non-English language carries a premium. — [arXiv 2608.09046](https://arxiv.org/abs/2608.09046)
- A GitHub study measured tokens per whitespace word (Indo-Aryan / Dravidian):

  | Tokenizer | Indo-Aryan | Dravidian |
  |---|---|---|
  | GPT‑4o (o200k) | 3.04 | 3.27 |
  | Sarvam‑30B/105B | 1.93 | 2.56 |
  | Sarvam‑M | 5.43 | 3.99 |

  Source: [indic-tokenizer-study GitHub](https://github.com/jkknikhil-git/indic-tokenizer-study)

### Inferences
- **Frontier models are a safe default for Boop.** Boop already routes to models like Claude via OpenRouter, and on public Indic benchmarks frontier models match or beat Indian models in reasoning.
- **Sarvam 105B is a budget option.** At ₹15 / ₹60 per 1M tokens, plus its tokenizer efficiency on Indic scripts, it is a cheap choice for simple chat in native script. It is not recommended for complex agentic tasks, given its low Artificial Analysis index.
- **Romanised Hinglish (Latin script) avoids most of the token penalty.** Boop could let users speak Hinglish and have the STT output romanised or code-mixed text using Saaras's codemix or translit modes. This is an inference.
- **Budget extra tokens for native-script output.** Plan for about 1.3–1.6× more tokens than English for Hindi and Bengali, and about 2.5–3× for Dravidian languages on GPT‑class tokenizers. Claude's ratio is unknown and should be measured with Anthropic's token-count API.

### Gaps
- No MILU or IndicGenBench scores were found for current Claude, GPT or Gemini models, or for Krutrim's latest models. Krutrim was not researched in depth.
- No published tokens-per-word figures were found for Claude or Gemini tokenizers on Indic scripts.
- No conversational or voice-specific Indic LLM benchmark was found, such as one testing Hinglish chat quality.

## 7. Recommendation inputs: cheapest viable stack for Hindi + 4–5 languages, and cost per minute

### Takeaway
A cascade of streaming STT → the user's chosen LLM → streaming TTS is the only way to cover Hindi plus Tamil, Telugu, Bengali, Marathi and Kannada or Gujarati with natural voices. Gemini Live does not cover that set.

The cheapest cloud cascade is Sarvam for both speech legs, Saaras v4 STT and Bulbul v4 Flash or v3 TTS. It costs about ₹1.0–1.7 per conversation minute for STT and TTS before LLM cost, about $0.012–0.02. A free on-device tier using Android's recognizer and TTS costs ₹0 for speech.

### Cited Findings (price inputs)
- Sarvam STT costs ₹0.49/min. Bulbul v4 Flash costs ₹2.00 per 1K characters (₹1.00 under the promotion to 12 Nov) and Bulbul v3 costs ₹3.00 per 1K. Sarvam 105B costs ₹15 input / ₹60 output per 1M tokens. — [Sarvam API pricing](https://www.sarvam.ai/api-pricing)
- Google STT costs $0.016/min, Chirp 3 HD TTS $30 per 1M characters, and Gemini 3.8 Flash TTS $9 per 1M audio tokens at 25 tokens per second. — [Google STT pricing](https://cloud.google.com/speech-to-text/pricing); [Google TTS pricing](https://cloud.google.com/text-to-speech/pricing)
- Gemini 3.8 Live costs about $0.005/min for audio in and about $0.018/min for audio out (third-party). — [developersdigest](https://www.developersdigest.tech/models/speech/google)
- ElevenLabs Scribe v2 Realtime costs $0.39/hour. — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- Sarvam's managed voice agents are "as low as ₹3 a minute", models included. — [Saaras v4 blog](https://www.sarvam.ai/blogs/introducing-saaras-v4)

### Inferences (worked estimates; the assumptions are mine and are not sourced)

**Assumptions for one minute of conversation**
- About 30 s of user speech and about 30 s of assistant speech.
- About 3 turns.
- About 400 characters of assistant text spoken. Hindi speech runs at roughly 130 words per minute, at about 6 characters per word including spaces, so 30 s is about 400 characters.
- The LLM receives about 6K input tokens (about 2K of context × 3 turns) and returns about 300 output tokens.
- STT is streamed for the whole minute. Gating the microphone with voice-activity detection (VAD) would roughly halve STT cost.

**Estimated cost per conversation minute**

| Stack | STT | TTS | LLM | Total speech cost | Notes |
|---|---|---|---|---|---|
| A. Sarvam STT + Bulbul v4 Flash + user's LLM | ₹0.49 | ₹0.80 at list (₹0.40 promo) | user's LLM | ≈ ₹1.29/min (≈ $0.015) | Covers the 11 Bulbul v3 languages if v4 Flash matches; check the v4 language list |
| A′. Same with Bulbul v3 | ₹0.49 | ₹1.20 | user's LLM | ≈ ₹1.69/min (≈ $0.019) | |
| B. All-Sarvam incl. Sarvam 105B | ₹0.49 | ₹0.80 | 6K × ₹15/M + 300 × ₹60/M ≈ ₹0.11 | ≈ ₹1.40/min all-in (≈ $0.016) | |
| C. Google Chirp 3 STT + Chirp 3 HD TTS | $0.016 | $0.012 | user's LLM | ≈ $0.028/min (≈ ₹2.5) | 1M TTS characters free per month ≈ 2,500 free minutes |
| D. Gemini 3.8 Live speech-to-speech, all-in | $0.005 in | $0.009 out (0.5 min) | included | ≈ $0.014/min (≈ ₹1.2) plus context and text tokens | Only hi/mr/ta/te (+bn‑BD); the LLM is Gemini, not the user's choice |
| E. On-device Android STT + TTS + cloud LLM | ₹0 | ₹0 | user's LLM | ₹0 | Quality and offline availability per language not verified |
| F. Self-hosted IndicConformer + Indic Parler‑TTS on a GPU | — | — | — | GPU hosting cost only (MIT / Apache 2.0) | Adds an ops burden for an open-source project |

**LLM cost with Claude or another frontier model.** The cost is about 6K × input price + 300 × output price per minute. Native-script Hindi inflates tokens by about 1.3×, and Tamil or Telugu by about 2.5–3×, judging from GPT‑4o-class tokenizers. Prompt caching cuts the repeated-context share. Current Claude prices were not checked in this note.

**Latency budget**
- Saaras v4 streaming STT: TTFT under 150 ms.
- Bulbul v3 TTS: first byte under 250 ms.
- The LLM's time to first token comes on top, so a cascade could plausibly reach a reply start under 1 s with a fast LLM.
- This is an inference: there is no end-to-end measurement.

**Suggested tiering for Boop**
1. **Free tier:** Android on-device or default speech plus the user's LLM.
2. **"Natural Indic voice" tier:** a Sarvam key, either the user's own or Boop's, using Saaras v4 and Bulbul, plus the user's LLM.
3. **Gemini Live:** kept for English, Hindi, Marathi, Tamil and Telugu, where users want speech-to-speech.

### Gaps
- No measured end-to-end latency was found for any Indic cascade.
- The characters-per-minute figure for Hindi and Dravidian TTS is assumed, not sourced.
- The Bulbul v4 Flash language list and quality are unknown.
- The USD→INR rate for Nov 2026 was not checked.
- Claude and OpenRouter per-token prices were not retrieved in this note; another research thread should cover them.
