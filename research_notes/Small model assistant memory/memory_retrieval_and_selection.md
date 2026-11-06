# Memory retrieval and selection for a ~2B on-device model (Maya / Hanu v4, max 5 notes per turn)

Scope: which memories to give Hanu v4 (Gemma 4 E2B, ~2B, 4-bit, on the phone) each turn. Covers when to retrieve (gating), how to rank (BM25, dense, fusion, recency, importance), how many items a small model can use, how distractors and conflicting items affect small models, and rerankers that fit a phone. Writing/consolidating memories and fine-tuning the model to read notes are out of scope (other researchers cover them). Most primary sources were read as full-text PDFs; numbers are quoted from their tables. Dates are given as (venue/arXiv month).

Product facts used below (from the assignment, not from sources): 5-slot MEMORY NOTES block; gate = EmbeddingGemma similarity to example "about-me" vs "task" requests (top-3 average each); 2 "always-known" core notes take slots first; failure trace had 2 conflicting name notes (Victor/Vijay) plus 2 "unconfirmed guess" notes; "speaker what's my name" lost the gate at margin -0.010; notes on task requests ("check today's gold rate") made the model answer from notes instead of acting. nanoMuse (big cloud model) injects up to 20 memories every turn with no gate.

---

## 1. When to retrieve at all (gating / adaptive retrieval)

### Takeaway
Learned "should I retrieve?" routers are cheap but often inaccurate. A 770M T5 router reached only 54.5% 3-way accuracy, while small supervised classifiers on clear task-type distinctions reach about 95%, and classifiers on the LLM's own hidden states reach about 85-92%. Both kinds of error are expensive for small models: unneeded context wipes out 42-100% of answers a 1.5-7B model already got right. For personal facts, which the model can never know on its own, a missed retrieval is a guaranteed failure. So a binary gate decided by a -0.010 margin is the wrong design: borderline requests should get a small, high-precision set of notes, not none.

### Cited Findings
- **Adaptive-RAG (Jeong et al., NAACL 2024).** A T5-Large classifier (770M) routes queries to no retrieval (A), single-step (B) or multi-step (C) retrieval. Labels come automatically from which strategy answered correctly, plus dataset bias. Classifier accuracy is only **54.52%** overall. Per class it is **30.52%** for "No", **66.28%** for "One" and **65.45%** for "Multi". "No" queries were misrouted to single-step about 47% of the time and to multi-step about 22%. — [Adaptive-RAG, arXiv 2403.14403](https://arxiv.org/html/2403.14403)
- **Adaptive-RAG: classifier size barely matters.** 60M gives 53.48% accuracy (QA F1 45.83), 223M gives 53.41% (45.97), 770M gives 54.52% (46.94). — [Adaptive-RAG](https://arxiv.org/html/2403.14403)
- **Adaptive-RAG: cost of routing errors (FLAN-T5-XL reader, averaged F1).**

  | Strategy | F1 | Relative time |
  |---|---|---|
  | Never retrieve | 21.12 | — |
  | Always single-step | 44.31 | 1.00 |
  | Always multi-step | 48.85 | 8.81 |
  | Adaptive-RAG | 46.94 | 3.60 |
  | Adaptive-RAG with an oracle router | 56.28 | 2.11 |

  The gap between the learned and the oracle router (+9.3 F1) is the cost of router mistakes. The paper does not quantify false-negative vs false-positive cost separately. — [Adaptive-RAG](https://arxiv.org/html/2403.14403)
- **"Searching for Best Practices in RAG" (Wang et al., EMNLP 2024; end-to-end generator is a fine-tuned Llama2-7B-Chat).** A BERT-base-multilingual query classifier labels a request "sufficient" (the user gave the information) or "insufficient" (retrieval may be needed) across 15 task types. It scores **Acc 0.95, Precision 0.96, Recall 0.94, F1 0.95**. The paper's text says adding it raised the average score from 0.428 to 0.443 and cut latency from 16.41 to 11.58 s per query. Its Table 11 shows 0.465 to 0.478 and 16.58 to 11.71 s instead; same direction, the paper does not reconcile the two. — [Wang et al. 2024, arXiv 2407.01219](https://arxiv.org/abs/2407.01219)
- **Unified Active Retrieval, UAR (Cheng et al., 2024).** UAR splits "retrieve?" into four binary criteria: intent-aware (the user explicitly wants retrieval), knowledge-aware (needs facts), time-sensitive, and self-aware (the model lacks the knowledge). Each is a small MLP on the frozen LLM's last-layer hidden states, sharing the generation's input encoding, so the extra cost is "negligible". — [UAR, arXiv 2406.12534](https://arxiv.org/abs/2406.12534)
- **UAR accuracy on AR-Bench (Llama2-7B-chat).**

  | Method | Intent | Knowledge | Time | Self | Overall |
  |---|---|---|---|---|---|
  | UAR | 91.88 | 90.38 | 86.69 | 72.32 | 85.32 |
  | FLARE | — | — | — | — | 56.50 |
  | Self-RAG | — | — | — | — | 60.12 |
  | SKR (BERT classifier) | — | — | — | — | 62.14 |

  The self-aware criterion is the hardest. The authors say SKR's BERT classifier underperforms because BERT's knowledge differs from Llama's. — [UAR](https://arxiv.org/abs/2406.12534)
- **UAR: false positives cost points on tasks that need no knowledge (13B).** On DROP and GSM8K, never-retrieve scores 58.76 / 40.64 and always-retrieve 54.16 / 37.68. UAR retrieved on only 3.7% / 0.0% of these and kept near never-retrieve scores. On time-sensitive TAQA/FreshQA, UAR retrieved on 99.6% / 73.3%. — [UAR](https://arxiv.org/abs/2406.12534)
- **FLARE and SKR (as described by UAR).** FLARE decides to retrieve from the model's uncertainty about its generated response. SKR trains a BERT classifier on the model's known and unknown questions. — [UAR](https://arxiv.org/abs/2406.12534)
- **Self-RAG (Asai et al., ICLR 2024).** The generator is trained to emit a "Retrieve" reflection token. Retrieval fires when the normalized probability of Retrieve=Yes passes a threshold δ, and retrieval frequency "dramatically" changes as δ varies. This needs the generator fine-tuned with special tokens (7B/13B in the paper). — [Self-RAG, arXiv 2310.11511](https://arxiv.org/abs/2310.11511)
- **TARG (Nov 2025, revised Apr 2026).** A training-free gate: the base model writes a short draft with no context, and uncertainty in the draft's prefix logits decides retrieval. Signals are entropy, the top-1/top-2 logit margin, and small-N variance. The margin is the recommended default because entropy "compresses" as instruction-tuned models sharpen. TARG cuts retrieval 70-90% vs always-RAG while matching or improving EM/F1. Base model sizes were not visible in the abstract. — [TARG, arXiv 2511.09803](https://arxiv.org/abs/2511.09803)
- **Comparison of 35 adaptive-retrieval methods (Moskvoretskii et al., Feb 2025; LLaMA 3.1-8B-instruct).** Simple uncertainty-estimation methods beat complex adaptive pipelines (FLARE, DRAGIN, Adaptive-RAG, SeaKR and others) on single-hop QA, match them on multi-hop, and use fewer than one retriever call and at most two LM calls per question. Most adaptive methods identify self-knowledge at near-random levels, and an "ideal" estimator still shows a large gap. — [Moskvoretskii et al., arXiv 2501.12835](https://arxiv.org/abs/2501.12835)
- **Context harms small models even when relevant (Pandey, Mar 2026; SmolLM2-360M and Qwen2.5-1.5B/3B/7B, all 4-bit).** Adding retrieval "destroys 42–100% of previously correct parametric answers".
  - On questions the model already answered correctly, noisy dense retrieval cost 64.0 pp (1.5B), 53.6 pp (3B) and 51.2 pp (7B). Oracle retrieval still cost 57.0, 45.6 and 41.6 pp.
  - For models of 3B and below, oracle vs noisy harm was not significantly different (p=0.26 at 1.5B, p=0.07 at 3B). The presence of context, not its quality, drives the distraction. At 7B the difference was significant (p=0.003).
  - On questions the model did not know, oracle-context EM was only 10.0% (1.5B), 12.8% (3B) and 14.6% (7B).
  - Net EM from noisy retrieval was negative at every size (−1.3 to −2.9 points). The authors recommend adaptive retrieval and RAFT-style training.
  - Caveats: single-author preprint; Wikipedia QA, not personal memory. — [Pandey 2026, arXiv 2603.11513](https://arxiv.org/html/2603.11513)
- **Yoran et al. (ICLR 2024; Llama-2-13B).** Even top-1 Google Search context hurt accuracy on StrategyQA and Fermi. An NLI filter (BART-large, 407M, trained on MNLI) prevents the drops but "also discard[s] relevant passages". About 1,000 training examples mixing relevant and irrelevant contexts made the model robust. — [Yoran et al., arXiv 2310.01558](https://arxiv.org/abs/2310.01558)
- **EmbeddingGemma uses separate prompts for each task.** Classification uses the symmetric prompt `task: classification | query: {content}`. Search queries use `task: search result | query: {content}`, and documents use `title: {title|none} | text: {content}`. `sentence similarity` is "not intended for retrieval". EmbeddingGemma 2 keeps the same scheme. — [EmbeddingGemma model card](https://huggingface.co/google/embeddinggemma-300m); [EmbeddingGemma 2 model card](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2)

### Inferences
- **For about-me requests, a gate false negative is fatal.** The "self-aware" criterion that most adaptive-retrieval work models (does the LLM already know the answer?) is trivially "no" for personal facts: Hanu cannot know the user's name from its weights. So for "what's my name", a false negative leaves a wrong or invented answer. That is the trace failure.
- **For task requests, a false positive is also costly.** Maya's own measurement (notes made the model answer instead of acting) matches UAR's DROP/GSM8K drops and the 2603.11513 result that context "overturns" answers small models already had right. Costs are asymmetric by request type, so a single threshold at margin 0 is poorly placed.
- **Use three zones instead of a yes/no decision.**
  - Confident about-me: give notes.
  - Confident task: give no free notes, except notes that pass a strict per-note match (for example, a contact note for "call my wife").
  - Uncertain band (for example |margin| < 0.05; tune on the eval set): give only the 1-2 notes whose own relevance clears a high absolute floor, never fill all 5.

  This turns the request-level gate into a per-note relevance decision, which is what Mem0's absolute relevance threshold does (Section 2).
- **Classifier options, cheapest first.**
  1. A logistic-regression or linear head on EmbeddingGemma vectors using the `task: classification` prompt, trained on a few hundred labelled Maya requests. The BERT task-type classifier at 0.95 F1 suggests a supervised head does far better than top-3-average kNN with few examples. This is an inference: no source tested kNN-average gates.
  2. A UAR-style probe on Hanu's own prefill hidden state. This needs the runtime to expose hidden states.
  3. Cheap lexical overrides for first-person attribute requests ("my name", "my wife", "my birthday", "who am I"), similar to UAR's "intent-aware" criterion.

  TARG/uncertainty gating needs a draft generation from Hanu (extra latency) and targets parametric knowledge, so it fits personal memory poorly.
- **"About me" vs "task" is not a clean split.** Many tasks need memory: "call my wife", "order my usual". Gating per note by relevance, not per request, handles these. Adaptive-RAG shows learned routers lean toward retrieving (47% + 22% of "No" queries were sent to retrieval), so expect the same bias in a learned gate.
- **Check the embedding prompts.** If the gate and retrieval use the same EmbeddingGemma prompt (or `sentence similarity` for retrieval), the model card says that is not the intended use. The gate should use `classification` or symmetric prompts, and note retrieval should use the asymmetric query/document prompts.

### Gaps
- I found no published study of gating for personal-memory assistants specifically (about-me vs task) or of embedding-kNN gate accuracy. All the gating numbers above come from open-domain QA or task-type benchmarks.
- No source separately quantifies false-negative vs false-positive cost for personal-fact questions. The asymmetry above is inferred.
- TARG's model sizes and per-dataset numbers were not checked (abstract only).

---

## 2. How to rank: BM25, dense, hybrid fusion, recency, importance, query expansion (LongMemEval / LoCoMo findings)

### Takeaway
- **Dense beats BM25 on personal chat memory.** On LongMemEval, dense retrievers beat BM25 by about 9-19 points of Recall@5.
- **Adding extracted user facts to the index key is the most reliable single gain** (+9.4% recall, +5.4% QA accuracy on average). Building separate fact keys and merging by rank is clearly worse.
- **Hybrid lexical + dense helps modestly.** A tuned convex combination of normalized scores beats RRF, and RRF is sensitive to its constant.
- **Recency and importance weighting (Generative Agents) is unvalidated for QA accuracy.**
- **LLM query expansion only helps with a strong LLM;** Llama-8B expansion gave no gain.
- **For small readers, fewer high-precision items win.** LoCoMo's best setting was the top 5 observations; 10, 25 and 50 were worse even though recall rose.

### Cited Findings
- **LongMemEval (Wu et al., ICLR 2025): retriever comparison (Table 9, Recall@5).**

  | Retriever | Session, K=V | Round, K=V |
  |---|---|---|
  | BM25 | 0.634 | 0.472 |
  | Contriever | 0.723 | 0.589 |
  | Stella V5 1.5B | 0.720 | 0.660 |

  "Both dense retrieval embeddings have significantly higher performance than the BM25 sparse retrieval method." Larger embedding models were excluded as "unrealistic" for latency. — [LongMemEval, arXiv 2410.10813](https://arxiv.org/abs/2410.10813)
- **LongMemEval: fact-augmented keys.** Indexing each item under its text plus extracted user facts (K = V + fact) helps every retriever.
  - Round-level BM25 Recall@5 rises from 0.472 to 0.554.
  - With Stella on the main benchmark, round Recall@5 rises from 0.582 to 0.644, and session Recall@10 from 0.783 to 0.862.
  - The paper reports an average +9.4% recall@k and +5.4% final accuracy.
  - Keys built from summaries or keyphrases alone gave little or inconsistent gain.

  Table 9 and Table 10 give different K=V baselines for Stella round (0.660 vs 0.582). These appear to be different benchmark variants; the paper does not reconcile them. — [LongMemEval](https://arxiv.org/abs/2410.10813)
- **LongMemEval: rank merging is clearly worse than key merging (Appendix E.3, Table 10, round values).** Retrieving fact keys as separate entries and merging by rank dropped Recall@5 to 0.478, vs 0.644 for merged keys and 0.582 for no expansion. Llama 3.1 8B top-5 QA was 0.458 for rank merging, 0.566 for key merging and 0.518 for no expansion. The authors blame the index growing m+1 times. — [LongMemEval](https://arxiv.org/abs/2410.10813)
- **LongMemEval: time-aware query expansion.**
  - Restricting retrieval to an inferred time range raised temporal-question Recall@5 (session, K=V+fact) from 0.684 to 0.722 with GPT-4o doing the expansion.
  - With Llama 3.1 8B doing the expansion it was 0.677, no gain. The paper says the 8B model "often hallucinat[es]" or misses temporal cues.
  - Retrieved items are "always sorted by their timestamp" before reading, to help temporal consistency. — [LongMemEval](https://arxiv.org/abs/2410.10813)
- **LongMemEval: granularity.** Rounds (one user message plus reply) beat sessions as the value unit for GPT-4o. With Llama 3.1 8B as reader the two are similar. Replacing values with summaries or facts loses information except for multi-session reasoning. — [LongMemEval](https://arxiv.org/html/2410.10813)
- **LoCoMo (Maharana et al., ACL 2024; DRAGON retriever, gpt-3.5-turbo-16k reader; Table 3).** Units were "observations" (assertions about speakers).

  | Top-k | Overall F1 | Recall@k | Adversarial F1 |
  |---|---|---|---|
  | 5 | 41.4 | 49.6 | 44.7 |
  | 10 | 38.8 | — | — |
  | 25 | 38.0 | — | 27.7 |
  | 50 | 37.8 | 71.1 | 27.7 |

  - Session summaries reached Recall@10 of 90.7 but only 31.5 F1.
  - The authors: "it is important to reduce the signal-to-noise (SNR) ratio in retrieved contexts". They also note that improper context from inaccurate retrieval can make open-domain answers worse. — [LoCoMo, arXiv 2402.17753](https://arxiv.org/abs/2402.17753)
- **Hybrid fusion analysis (Bruch, Gai, Ingber; ACM TOIS 2023).**
  - A convex combination (CC) of normalized lexical and semantic scores "outperforms RRF in in-domain and out-of-domain settings".
  - RRF "is sensitive to its parameters", contrary to earlier claims (default η = 60).
  - CC is "extremely sample-efficient, requiring just a handful of labeled" queries to tune α.
  - Choice of score normalization matters little for CC. — [Bruch et al., arXiv 2210.11934](https://arxiv.org/abs/2210.11934)
- **"Best Practices in RAG" (2024; end-to-end generator is a fine-tuned Llama2-7B-Chat).**
  - Score = α·sparse + dense with normalized scores; α = 0.3 was best of 0.1-0.9.
  - Hybrid retrieval averaged 0.477 vs 0.428 for dense only, at the same latency (1.45 vs 1.44 s).
  - HyDE + Hybrid reached 0.478 but took 11.71 s per query, so "Hybrid" is recommended for efficiency. — [Wang et al., arXiv 2407.01219](https://arxiv.org/abs/2407.01219)
- **Generative Agents (Park et al., UIST 2023).**
  - Retrieval score = α_recency·recency + α_importance·importance + α_relevance·relevance, each min-max normalized to [0,1], with all α = 1.
  - Recency is exponential decay with factor 0.995 per sandbox game-hour since the memory was last retrieved.
  - Importance is an LLM rating from 1 to 10 at write time (cleaning a room = 2, asking a crush out = 8).
  - Relevance is embedding cosine.
  - Top memories are added "as long as they fit" the context window.
  - Ablations removed whole memory components (full TrueSkill 29.89 vs no memory 21.21), not the scoring weights. — [Generative Agents, arXiv 2304.03442](https://arxiv.org/html/2304.03442v2)
- **Mem0 (Apr 2025).** The graph variant returns "only those [triplets] that exceed a configurable relevance threshold, ranked in order of decreasing similarity", an absolute floor rather than a fixed k. It combines entity-anchored lookup with whole-query dense matching. Outdated relations are marked invalid rather than deleted. — [Mem0, arXiv 2504.19413](https://arxiv.org/abs/2504.19413)
- **SeCom (ICLR 2025).** Applying a prompt-compression model (LLMLingua-2) to memory units as "denoising" consistently improved retrieval recall at compression rates above 50%, with both BM25 and MPNet retrievers. — [SeCom, arXiv 2502.05589](https://arxiv.org/abs/2502.05589)
- **EmbeddingGemma (v1, Sept 2025; 308M).**

  | Setting | MTEB English v2 |
  |---|---|
  | 768d | 69.67 |
  | 256d | 68.37 |
  | 128d | 66.66 |
  | Q4_0, 768d | 69.31 |
  | Q8_0, 768d | 69.49 |

  Max context is 2048 tokens. It runs in under 200 MB RAM when quantized. — [EmbeddingGemma model card](https://huggingface.co/google/embeddinggemma-300m); [Google Developers Blog](https://developers.googleblog.com/en/introducing-embeddinggemma/)
- **EmbeddingGemma 2 (model card updated 2026-10-06).** 740M total, made up of a 270M text backbone plus optional vision and audio encoders; 8,192-token context.

  | Dimensions | Multilingual v2 | English v2 | Code v1 |
  |---|---|---|---|
  | 768d | 61.36 | 68.46 | 78.68 |
  | 512d | — | 68.41 | — |
  | 256d | — | 67.78 | — |
  | 128d | — | 65.68 | — |

  English v2 is slightly below v1's 69.67. No text-retrieval subset and no quantized scores are reported. — [EmbeddingGemma 2 model card](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2)

### Inferences
- **Ranking cannot fix the Victor/Vijay trace.** Two "my name is X" notes are near-identical in embedding and BM25 space. Both will rank high for "what's my name", so they must be resolved by dedupe/conflict rules (Section 4), not by better ranking.
- **Recommended phone pipeline.**
  1. Score every note with EmbeddingGemma cosine using asymmetric prompts (cache note vectors; 256d costs about 1.3 MTEB points vs 768d on v1).
  2. Compute a BM25/IDF score over note text plus extracted entity/fact keys.
  3. Fuse with a tuned convex combination (α on the BM25 side, start near 0.3 per Wang et al.) rather than RRF, tuning α on Maya's eval set. RRF has no absolute score, so it cannot support a relevance floor; a convex combination of normalized scores can.
  4. Apply an absolute floor and return a variable 0-5 notes.
- **Index notes under extracted keys** (for example "user name; called; identity") merged into the same embedding text: LongMemEval's key merging, not separate rank-merged entries. This is a cheap write-side step that helps short, oddly phrased requests like "speaker what's my name".
- **Recency should be a tie-breaker inside a conflict cluster** (newest confirmed wins), not a filler. nanoMuse's "fill with most recent" works for a big cloud model but contradicts LoCoMo/LongMemEval evidence for small readers (Section 3). Importance scores could bias which core notes are eligible, but there is no QA evidence for importance weighting.
- **Skip LLM-based query expansion and HyDE on the phone:** an 8B expander gave no gain on LongMemEval, and HyDE costs about 8x latency. If needed, use rule-based expansion for date words ("yesterday", "last week") to filter by timestamp.
- **Treat EmbeddingGemma 2 as an unproven upgrade for retrieval:** English MTEB is slightly lower than v1's and no retrieval subset is published. Measure Recall@5 on Maya's own notes before trusting it.

### Gaps
- I found no study that directly measures recency or importance weighting on QA accuracy in personal memory benchmarks.
- I found no published LongMemEval/LoCoMo number for BM25+dense hybrid with RRF vs convex combination on personal memory.
- No EmbeddingGemma (v1 or v2) results on LongMemEval or LoCoMo were found. The parent project has an internal "LongMemEval retrieval baseline" task that may hold this.

---

## 3. How many items a small model can use, distractor sensitivity, and ordering

### Takeaway
Small models gain little from more retrieved items and lose a lot from hard distractors. Hard distractors are irrelevant items that look most like the answer, such as a second, wrong name note.
- Llama-3.1-8B gained only +0.6 QA points going from 5 to 10 memory items on LongMemEval, while GPT-4o gained +6.3.
- LoCoMo F1 peaked at 5 retrieved observations.
- One hard distractor next to the gold passage costs 3B models 11-12 points; weak distractors cost 3B models 3-5 points but 7-8B models only 0.5-2.6.

With 5 notes of about 20 tokens each, Maya is far below any length limit (Llama-8B degrades past about 3k retrieved tokens). The binding constraint is the share of distractors, not token count. Ordering effects exist (best item nearest the question wins slightly) but are small at k ≤ 5.

### Cited Findings
- **LongMemEval: small readers saturate early.**
  - Llama 3.1 8B's performance "drops sharply beyond 3k retrieved tokens", while GPT-4o "continues to improve even with over 20k retrieved tokens".
  - With fact-augmented round keys, QA at top-5 vs top-10 was 0.566 vs 0.572 for Llama 3.1 8B, 0.638 vs 0.682 for Llama 3.1 70B, and 0.657 vs 0.720 for GPT-4o.
  - Long-context (no retrieval) Llama 8B fell from 0.710 with oracle sessions to 0.454 with the full history. — [LongMemEval](https://arxiv.org/abs/2410.10813)
- **LoCoMo.** Top-5 observations gave the best F1 (41.4); top-10/25/50 gave 38.8/38.0/37.8. Adversarial-question F1 fell from 44.7 to 27.7 as k grew. — [LoCoMo](https://arxiv.org/abs/2402.17753)
- **"Long-Context LLMs Meet RAG" (Jin et al., ICLR 2025; Gemma-7B-Chat, Gemma-2-9B-Chat, Mistral-Nemo-12B, Gemini-1.5-Pro).**
  - Accuracy follows an inverted U as passages are added: it rises, then drops or plateaus.
  - The decline is sharper with the strong e5 retriever than with BM25, because negatives from stronger retrievers are harder (harm ranking e5 > Contriever > BM25 > random).
  - Placing top-scored passages at both ends of the context gives "negligible" gains with small retrieval sets and consistent gains with many. — [Jin et al., arXiv 2410.05983](https://arxiv.org/html/2410.05983)
- **"The Distracting Effect" (Amiraz, Cuconasu et al., ACL 2025).** Accuracy on NQ with gold only, gold + weak distractor, and gold + hard distractor (averaged over both orders):

  | Model | Gold only | + weak | + hard |
  |---|---|---|---|
  | Llama-3.2-3B | 82.6 | 79.4 | 71.5 |
  | Qwen-2.5-3B | 80.9 | 75.5 | 69.4 |
  | Falcon-3-3B | 78.5 | 74.1 | 67.1 |
  | Llama-3.1-8B | 80.6 | 80.1 | 73.9 |
  | Qwen-2.5-7B | 82.4 | 80.4 | 73.7 |
  | Falcon-3-7B | 84.1 | 81.5 | 73.3 |
  | Llama-3.3-70B | 81.1 | 80.1 | 75.2 |

  - Hard distractors cost 6-11 points "even for larger LLMs".
  - Higher-ranked irrelevant passages are more distracting.
  - Adding a reranker increases the average distracting effect of the irrelevant passages that remain in the top 5.
  - Fine-tuning with hard distractors gave up to +7.5% accuracy. — [Amiraz et al., ACL 2025](https://aclanthology.org/2025.acl-long.892.pdf)
- **"The Power of Noise" (Cuconasu et al., SIGIR 2024; Llama2-7B, Falcon-7B, Phi-2 2.7B, MPT-7B).**
  - Adding a single distracting document cut accuracy by up to 0.24 (−25%); more distractors cut it by up to 0.38 (−67%).
  - Accuracy is highest when the gold document is nearest the query, lower when furthest, and lowest in the middle.
  - Counter-intuitively, adding random documents improved accuracy by up to 35%. I did not see this replicated in the other sources here, so treat it with caution. — [Cuconasu et al., arXiv 2401.14887](https://arxiv.org/abs/2401.14887)
- **"Lost in the Middle" (Liu et al., TACL 2024).** Accuracy is U-shaped by position of the relevant document. With 20-30 documents, GPT-3.5-Turbo with the answer mid-context scored below its closed-book 56.1% (oracle: 88.3%). Using 50 instead of 20 retrieved documents improved GPT-3.5-Turbo by only about 1.5% (Claude-1.3 about 1%). Models tested were 13B and larger or API models. — [Liu et al., arXiv 2307.03172](https://arxiv.org/abs/2307.03172)
- **Ordering at small k ("Best Practices", fine-tuned Llama2-7B-Chat generator).** Repacking in ascending relevance, so the best item is last and nearest the query, scored 0.483 on average. "Sides" scored 0.478 and descending order ("forward") 0.474. The authors: "positioning more relevant context closer to the query leads to optimal outcomes." — [Wang et al., arXiv 2407.01219](https://arxiv.org/abs/2407.01219)
- **Multi-domain RAG (2025; Llama-3.2-1B, Llama-3-8B, Mistral-7B).** The 1B model "is more sensitive to noise" than the 7-8B models when distractors are added. Even with oracle documents there remains a 20-30% gap to perfect answers. — [arXiv 2504.02411](https://arxiv.org/pdf/2504.02411)
- **Context presence vs quality at small scale.** For models of 3B and below, oracle and noisy context caused statistically similar damage to known answers. — [Pandey 2026, arXiv 2603.11513](https://arxiv.org/html/2603.11513)

### Inferences
- **For a 2B model, 5 slots are an upper limit, not a target.** The evidence (LoCoMo peak at 5; 8B gaining 0.6 points from 5 to 10; 3B models losing 3-12 points per added distractor) supports "fewer, high-precision notes".
  - For a factual about-me question, 1-2 correct notes likely beat 5 mixed ones.
  - The trace (2 core + 2 guesses + 1 conflicting name note) is close to the worst case described by Amiraz et al.: same-topic wrong answers in the top ranks.
- **The 2 reserved core-note slots are distractors whenever they are off-topic.** Better: let core notes compete in the ranking with a boost, or include them only when the request is about-me, instead of reserving slots unconditionally.
- **nanoMuse's 20-memory design depends on a large model.** GPT-4o keeps improving past 20k tokens; 1-8B readers do not. It should not be copied to Hanu.
- **Ordering.** Put the most relevant note adjacent to the user's request: last in the MEMORY NOTES block if the block precedes the request. The measured effect at small k is about 0.5-1 point, so match whatever order Hanu v4 saw during fine-tuning first. A mismatch with training is probably the bigger risk (not measured here).
- **The best notes to drop are the ones that look most relevant but are wrong:** a stale or conflicting note of the same type as the question. Rerankers and stronger retrievers make the surviving wrong items more dangerous, not less.

### Gaps
- I found no study measuring a top-k curve for a ~2B model (Gemma E2B class) on personal-memory notes specifically. The closest evidence is 1-3B open-domain QA and 8B on LongMemEval.
- No source tested ordering effects inside a fine-tuned fixed-format notes block. Effects for Hanu v4 depend on its training data order (covered by other researchers).

---

## 4. Handling conflicting or low-confidence items at retrieval time

### Takeaway
Models (large and small) tend to adopt whatever the context says, overriding correct knowledge more than 60% of the time. With conflicting items they favour the answer with more supporting copies. Hedged "may/possibly" statements of a wrong answer are among the most distracting item types.

So: deduplicate and resolve conflicts before injection (one note per attribute, newest confirmed wins), and drop tentative or unconfirmed notes from the 5 slots rather than marking them. Credibility tags only help models trained to read them.

### Cited Findings
- **ClashEval (Wu, Wu, Zou, NeurIPS 2024 Datasets and Benchmarks; 1,294 questions).**
  - LLMs adopt incorrect retrieved content, "overriding their own correct prior knowledge over 60% of the time".
  - The more unrealistic the perturbation, the less likely it is adopted. The less confident the model's prior (by token probability), the more likely it adopts the context.
  - Best model: Claude Opus with accuracy 74.3%, context bias 15.7%, prior bias 2.1%. Llama-3-8B had lower accuracy partly from answering with neither. — [ClashEval, arXiv 2404.10198](https://arxiv.org/abs/2404.10198)
- **RAMDocs / MADAM-RAG (Wang, Prasad, Stengel-Eskin, Bansal, COLM 2025).**
  - Baselines get worse as supporting evidence becomes imbalanced: up to 8% drop for a concatenated prompt as one answer gains 1→3 supporting documents. LLMs "tend to follow the more attested interpretation".
  - The best baseline (Llama3.3-70B) reaches only 32.60 EM on RAMDocs.
  - The fix (multi-agent debate with an aggregator) needs several LLM calls per query, which is not phone-feasible. Models evaluated were 70B-class and GPT-4o-mini. — [MADAM-RAG, arXiv 2504.13079](https://arxiv.org/abs/2504.13079)
- **The Distracting Effect: hedged wrong answers are highly distracting.**
  - The "modal statement" type is defined as "a passage providing a wrong answer following a disclaimer that the statement is not certain" (for example "The Pyramids may have been built via...").
  - G_modal was "on average the most promising" of the four generated distractor types (generated statements that sound plausible but are wrong).
  - Retrieved hard negatives (R_st) were comparable or stronger. — [Amiraz et al., ACL 2025](https://aclanthology.org/2025.acl-long.892.pdf)
- **LongMemEval.** The benchmark has a "Knowledge Updates" category: recognizing changes in the user's information over time. The retrieved items are sorted by timestamp before reading. Chain-of-Note plus JSON-formatted items "consistently" helped readers of varying ability. — [LongMemEval](https://arxiv.org/abs/2410.10813)
- **Credibility-aware generation, CAG (Pan et al., 2024).** Each document gets a credibility level (high/medium/low) derived from relevance, timeliness (time between query and document) and source reliability. Models fine-tuned to use these labels "significantly outperform" other RAG models and "exhibit robustness despite the increasing noise". This requires fine-tuning (LLaMA-2-7B/13B, Mistral-7B and others evaluated). — [CAG, arXiv 2404.06809](https://arxiv.org/abs/2404.06809)
- **Mem0.** Conflicting or outdated relations are marked invalid rather than physically removed, so they stay available for temporal reasoning but are not served as current facts. — [Mem0, arXiv 2504.19413](https://arxiv.org/abs/2504.19413)

### Inferences
- **Deduplicate before injection.** Duplicates act as votes (RAMDocs majority effect). Group candidates by attribute (name, spouse, home city, and so on) or by note-to-note cosine above a high threshold, and inject at most one note per attribute.
  - Within a group, choose by: user-confirmed > inferred, then newest timestamp, then retrieval score.
  - This alone would have removed one of the Victor/Vijay notes.
- **Drop tentative or unconfirmed notes from the 5 slots on factual questions.** The modal-statement result suggests that "unconfirmed guess: maybe X" is a strong distractor, not a safe hedge. If a guess is the only candidate for the asked attribute, the planner is better served by having no note and asking or confirming. This is an inference; no source measured hedge tags on personal notes.
- **Marking uncertainty in the note text is unlikely to help unless Hanu was trained on such markers.** CAG's gains come from fine-tuning, and a 2B model was trained on a fixed 1-5-line block. Flag for the fine-tuning researchers rather than adding markers at retrieval time.
- **Prefer newest only for attributes that change** (address, job, preferences). For identity facts (name), a contradiction more likely means a transcription or extraction error, for example ASR hearing "Victor" for "Vijay". Prefer the user-confirmed or most-repeated-by-user value and flag the conflict for a confirmation turn instead of silently choosing.
- **Showing notes in a stable order with dates** (LongMemEval sorts by timestamp) is a cheap aid if Hanu's training format allows a date field. Otherwise keep the trained format.

### Gaps
- I found no study measuring how a 1-3B model resolves two directly contradictory personal-fact notes (A vs B) in context. ClashEval and RAMDocs used 8B-70B and API models.
- No source measured "drop tentative items" vs "tag tentative items" for small models without fine-tuning.

---

## 5. Reranking options that fit a phone

### Takeaway
- **Small cross-encoders give large first-stage ranking gains on paper:** MiniLM-L6 (about 22M parameters) reaches MS MARCO MRR@10 39.0, about the same as the 12-layer version. But end-to-end QA gains from adding a reranker were small, about +0.8 points with a 7B generator.
- **Rerankers can make surviving wrong items more distracting.**
- **The cheapest effective phone tools are an absolute score floor, attribute-level dedupe/MMR over EmbeddingGemma vectors, and rule filters** (drop tentative, stale or off-topic items).
- **A tiny learned embedding adapter (RMM) is a promising on-device reranker if training signal exists.** LLM rerankers (RankLLaMA 7B) and multi-agent methods need a server.

### Cited Findings
- **Sentence-Transformers MS MARCO cross-encoders.**

  | Model | TREC DL19 NDCG@10 | MS MARCO MRR@10 | Docs/s |
  |---|---|---|---|
  | TinyBERT-L2-v2 | 69.84 | 32.56 | 9000 |
  | MiniLM-L2-v2 | 71.01 | 34.85 | 4100 |
  | MiniLM-L4-v2 | 73.04 | 37.70 | 2500 |
  | MiniLM-L6-v2 | 74.30 | 39.01 | 1800 |
  | MiniLM-L12-v2 | 74.31 | 39.02 | 960 |

  Throughput hardware is not stated on the page (likely a GPU), so phone CPU speed is unknown. — [SBERT pretrained cross-encoders](https://www.sbert.net/docs/cross_encoder/pretrained_models.html)
- **Reranker comparison ("Best Practices"; MS MARCO dev, reranking BM25 top-1000).**

  | Reranker | Parameters | MRR@10 | Latency per query |
  |---|---|---|---|
  | BM25 (no rerank) | — | 11.65 | — |
  | monoT5 | 220M | 31.78 | 4.5 s |
  | monoBERT | 340M | 31.69 | 15.8 s |
  | RankLLaMA | 7B | 32.35 | 82.4 s |
  | TILDEv2 | 110M | 27.83 | 0.02 s |

  End-to-end with the fine-tuned Llama2-7B-Chat generator, the average score was 0.470 without reranking, 0.478 with monoT5 and 0.476 with TILDEv2. — [Wang et al., arXiv 2407.01219](https://arxiv.org/abs/2407.01219)
- **Multi-domain RAG (2025).** Second-stage reranking improves performance in most cases, "similar both for the small model (Llama3.2-1B) and larger models". — [arXiv 2504.02411](https://arxiv.org/pdf/2504.02411)
- **The Distracting Effect.** Reranking (bge-reranker-v2-m3) "consistently increases the average distracting effect" of irrelevant passages remaining in the top 5. — [Amiraz et al., ACL 2025](https://aclanthology.org/2025.acl-long.892.pdf)
- **Reflective Memory Management, RMM (Tan et al., Google Cloud AI Research; ACL 2025).**
  - The reranker is a linear layer with a residual connection on the query and memory embeddings (q′ = q + W_q q, m′ = m + W_m m), scored by dot product. It picks the top M of the retriever's top K with Gumbel sampling.
  - It is trained online with REINFORCE, using which memories the reader LLM cited as the reward.
  - Results: 58.8% Recall@5 on LongMemEval with retrospective reflection plus the reranker, 60.4% for full RMM; ">10% accuracy improvement over the baseline without memory management".
  - Fine-tuning the retriever instead of adding the reranker did worse.
  - Their reader was Gemini-1.5-Flash and the retriever Contriever. — [RMM, arXiv 2503.08026](https://arxiv.org/abs/2503.08026)
- **NLI filter (Yoran et al.).** A 407M BART-large NLI model filtering irrelevant passages prevents accuracy drops but also discards relevant passages. — [Yoran et al., arXiv 2310.01558](https://arxiv.org/abs/2310.01558)
- **Maximal Marginal Relevance (Carbonell & Goldstein, SIGIR 1998).** MMR picks the next item by λ·Sim(item, query) − (1−λ)·max Sim(item, already-selected), trading relevance against redundancy. — [Carbonell & Goldstein 1998](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)
- **Absolute relevance thresholds in production memory.** Mem0's graph variant returns only items above a configurable threshold. — [Mem0](https://arxiv.org/abs/2504.19413)

### Inferences
- **Phone-feasible reranking stack, cheapest first.**
  1. **Rule filters:** drop tentative or unconfirmed notes, notes superseded within an attribute group, and notes below an absolute fused-score floor.
  2. **Attribute dedupe or MMR on cached EmbeddingGemma note vectors.** No extra model is needed; λ around 0.7 is a common starting point (not sourced).
  3. **Optional:** a MiniLM-L6 cross-encoder (about 22M parameters, int8) scoring the top 10-20 candidates of 10-30 tokens each. That is about 20 short pairs per turn, likely tens of milliseconds on a phone CPU (unmeasured).
  4. **Optional:** an RMM-style 768×768 residual adapter on query and note embeddings, trained offline on Maya's labelled turns or online from which notes Hanu's plan actually used.
- **Prefer a floor plus dedupe to more reranking.** Amiraz et al. show rerankers promote the most convincing wrong items, so a reranker without a floor and dedupe can make Maya's failure mode worse.
- **Flag as needing a server or too heavy for per-turn phone use:** RankLLaMA (7B), monoBERT and bge-reranker-v2-m3-class (about 340-570M) cross-encoders over many candidates, MADAM-RAG debate, LLM query expansion and HyDE, and Hanu itself as a listwise reranker (an extra generation pass on a 2B model adds latency).

### Gaps
- I found no measurements of cross-encoder latency on Android CPU or NPU, and no EmbeddingGemma-based reranker numbers.
- I found no measured gains for MMR or dedupe on personal-memory QA. The benefit is inferred from the RAMDocs majority effect and the distractor studies.
- I found no evidence on whether a cross-encoder trained on web passages (MS MARCO) ranks short first-person notes ("User's name is Vijay") well. Maya should test it on its own eval set.
