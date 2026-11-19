# Why independent LLM runs converge on the same ideas, and which prompt and sampling levers raise idea variety

Provenance note for the report writer: figures marked **[full text]** were read by me from the paper's own text (PDF extracted locally). Figures marked **[page summary]** came from an automated reading of the arXiv HTML page and should be spot-checked before being quoted as exact. Figures marked **[abstract]** or **[secondary]** come from an abstract page or from press or institutional coverage. Similarity and diversity scores are not comparable across papers: each uses its own embedding model, task and scale.

## 1. What do studies report about duplication and homogeneity in LLM idea generation at scale?

### Takeaway
Every study found that pooled LLM ideas are more alike than pooled human ideas, and that adding more samples from the same prompt mostly adds repeats: one large study kept only 200 unique ideas out of 4,000 (5%), and one-idea-per-independent-session was the least diverse condition of ten tested in the largest 2026 product-idea study. The same clustering appears across different models, so the effect is not specific to one vendor.

### Cited Findings

**Share of unique ideas falls as more are generated**
- Si, Yang and Hashimoto (2024, Claude 3.5 Sonnet) generated 4,000 seed research ideas per topic and found only about 200 non-duplicates (5%), using all-MiniLM-L6-v2 embeddings and a duplicate threshold of cosine 0.8. The share of non-duplicates in each new batch kept falling and the cumulative count of unique ideas flattened. This happened even though each prompt carried 6 demonstration examples, 10 retrieved papers, and the titles of all earlier ideas with an instruction not to repeat them. **[page summary]** — [Si et al. 2024](https://arxiv.org/html/2409.04109)
- Meincke, Mollick and Terwiesch (2024, GPT-4, product ideas for college students under $50) estimated the reachable idea space at about 3,700 unique ideas for the base prompt, with 13.8% of ideas repeats, and about 4,700 for a chain-of-thought prompt, with 11.7% repeats (same 0.8 threshold, about 1,200 ideas generated in one session with earlier ideas kept in context, 5 runs each). **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- In the same paper the most common ideas each appeared 25 to 30 times in a sample of about 1,200 (collapsible laundry hamper 30, portable smoothie maker 30, bedside caddy 25), and the authors note these "often occur early in a completion request", which they attribute to lower entropy at the start of a generation. **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- Terwiesch, Meincke, Girotra, Mollick, Nave and Ulrich (July 2026) measured coverage instead of duplication: as a GPT-4o pool grew from 100 to 1,000 ideas, the mean distance from each of 200 human ideas to its nearest LLM idea fell from 0.546 to 0.478 with no plateau, but the distance for the hardest-to-match human idea fell more slowly (0.762 to 0.711). **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)

**Independent sessions with the same prompt are the worst case**
- In Terwiesch et al. (2026), generating one idea per independent GPT-4o session scored 0.452 on diversity (1 minus mean pairwise cosine similarity; pools of 100), against 0.679 for GPT-4o producing 100 ideas per session and 0.773 for humans. It ranked last of ten conditions. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Deng, Brucks and Toubia (Columbia, 2026; GPT-4o at temperature 1.0; 99 simulated participants each giving 10 fitness-product ideas; ideas hand-coded into a 28-category taxonomy) found that the *first* ideas of independent LLM sessions covered far fewer categories than the first ideas of independent humans (8.71 vs 14.29 accumulated categories; 5.98 vs 8.99 category combinations). For a newer reasoning model the first-idea figure was 4.22 against 14.29 for humans. **[page summary; the model name was rendered as "gpt-5.6-sol", verify]** — [Deng et al. 2026](https://arxiv.org/html/2602.20408)

**Pooled LLM ideas versus human pools**
- Terwiesch et al. (2026) Study 2a: mean pairwise cosine similarity was 0.221 for 200 human ideas and 0.414 for GPT-4 zero-shot ideas (B = 0.193, p < .001); 80 to 90% of the gap remained after all ideas were rephrased by an LLM to remove style differences. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- The same paper re-analysed four earlier studies (five datasets): AI pools were more similar in every comparison, 32 of 32 across alternative measures, with Cohen's d from 0.380 to 5.538. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Meincke et al. (2024): human student pool 0.243 mean cosine similarity; 35 GPT-4 prompt variants ranged from 0.255 to 0.432 (base prompt 0.377). Differences of about 0.01 were significant for pools of 1,000. **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- Wenger and Kenett (2025; 22 LLMs, 102 humans; Alternative Uses, Forward Flow, Divergent Association tasks): individual LLM answers were about as original as human ones, but population-level variability was far lower: 0.459 vs 0.738 (AUT), 0.534 vs 0.835 (FF), 0.665 vs 0.819 (DAT), effect sizes 2.2, 2.0, 1.4. **[page summary]** — [Wenger & Kenett 2025](https://arxiv.org/html/2501.19361)
- Ma, Grandi, McComb and Goucher-Lambert (2024, GPT-4, 4,000 design solutions over five design problems): crowdsourced human solutions scored higher on every diversity metric under every parameter and prompt setting tested. **[full text]** — [Ma et al. 2024](https://codesign.berkeley.edu/pdfs/papers/ma-llmdiverse-jcise.pdf)
- Shur-Ofry et al. (2024, eight models, older generation: GPT-4, GPT-3.5, Claude 1.3, Gemini and others): asked for three influential nineteenth-century figures ten times, models gave on average 4.3 different names out of 30 slots (API models at temperature 0.3); 28 human answers on X contained 25 different names. Entropy was 2.1 to 2.9 for models and 4.6 to 4.7 for humans. **[full text]** — [Shur-Ofry et al. 2024](https://arxiv.org/pdf/2411.02989)

**Repetition within one model and sameness across models, at scale**
- Jiang et al., "Artificial Hivemind" (2025; 26,070 open-ended real user queries; 70+ models): with 50 responses per query at top-p 0.9 and temperature 1.0, average pairwise similarity exceeded 0.8 in 79% of cases. Across *different* models the average pairwise similarity was 71% to 82%. **[page summary]** — [Jiang et al. 2025](https://arxiv.org/html/2510.22954)
- NoveltyBench (Zhang et al. 2025; 20 models, 1,100 prompts, 10 samples each at temperature 1): models generally produced fewer than 3 distinct answers in 10 (GPT-4o: 2.88), fewer than a baseline of eight human writers. **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2504.05228)

**Effects on people who brainstorm with an LLM (related, not the same setup)**
- Doshi and Hauser (Science Advances, 2024): stories by writers given one AI idea were 10.7% more similar to each other than stories written without AI. **[secondary, authors' university]** — [University of Exeter](https://news.exeter.ac.uk/?p=13749)
- Meincke, Nave and Terwiesch (Nature Human Behaviour, 2025): ChatGPT-assisted pools were less diverse in 37 of 45 comparisons across five experiments; in one toy task 94% of ChatGPT-assisted ideas shared overlapping concepts. **[secondary]** — [Wharton Mack Institute](https://mackinstitute.wharton.upenn.edu/2025/new-in-nature-chatgpt-decreases-idea-diversity-in-brainstorming/); [Axios](https://www.axios.com/2025/06/18/ai-chatgpt-research-creativity-brainstorming)
- Anderson, Shah and Kreminski (2024, 36 participants): different users produced less semantically distinct ideas with ChatGPT than with another creativity tool. No numbers on the abstract page. **[abstract]** — [Anderson et al. 2024](https://arxiv.org/abs/2402.01536)

### Inferences
- A team that sends one identical brief to 10 and then 33 agents is running the "independent sessions" design, which the 2026 Wharton study found to be the least diverse way to use a model. Going from 10 to 33 agents should be expected to add repeats of the same dozen themes, in line with the 5% unique rate in Si et al. and the concentrated first ideas in Deng et al.
- Each agent's first and most developed ideas are the model's most probable ones, and those are the same for every agent. The Meincke observation that the commonest ideas appear early in a completion points the same way.
- More volume still helps coverage slowly (the 0.546 to 0.478 result), so scale is not useless, but the cost per new theme rises steeply.

### Gaps
- No study found that measures theme-level collapse for small models run as parallel agents with tools; all figures above are for plain API calls.
- I could not read the figure in Si et al. that plots the non-duplicate share per batch, so the shape of the curve is described from the text only.
- The Nature Human Behaviour and Science Advances figures were taken from institutional and press coverage, not from the papers.

## 2. What is known about the causes?

### Takeaway
The best-supported account has three parts: a model pools everyone's knowledge into one central distribution, so independent samples are not independent the way separate people are; post-training for helpfulness rewards typical answers and narrows that distribution further; and an identical prompt puts every run at the same starting point. Examples in the prompt narrow it a little more.

### Cited Findings

**One shared central distribution ("knowledge partitioning" is missing)**
- Deng et al. (2026) separate two mechanisms. Between sessions, humans each hold different knowledge, while LLM sessions draw from "a more shared, centralized distribution" (first-idea categories 8.71 vs 14.29). Within a session, fixation on earlier ideas was about the same for humans and the default LLM (slope of new categories per idea 1.020 vs 1.023, p = .90). So in the current version of the paper the human advantage sits between sessions, not within them. **[page summary]** — [Deng et al. 2026](https://arxiv.org/html/2602.20408)
- Terwiesch et al. (2026) found that GPT-4 ideas concentrate "in regions of the idea space that are commercially plausible but less novel": the farther a human idea sat from the nearest LLM idea, the lower its purchase intent (B = -0.288, p < .001). **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)

**Post-training (alignment, preference tuning) favours typical outputs**
- Verbalized Sampling (Zhang et al. 2025) attributes mode collapse to "typicality bias" in human preference data: in 6,874 correctness-matched response pairs from HelpSteer, raters preferred the more typical response 51.6 to 60.8% of the time, with a fitted typicality weight of 0.57 ± 0.07 (p < 10⁻¹⁴). **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2510.01171)
- Kirk et al. (2023/2024): RLHF "significantly reduces output diversity compared to SFT across a variety of measures". No numbers on the abstract page. **[abstract]** — [Kirk et al.](https://arxiv.org/abs/2310.06452)
- Murthy, Ullman and Hu (NAACL 2025, ten open models): aligned models showed less conceptual diversity than their instruction-tuned counterparts, and no model reached human population-level variability. **[secondary summary of abstract]** — [Murthy et al.](https://arxiv.org/abs/2411.04427)
- West and Potts (2025): base models "consistently outperform their popular aligned forms" on random-number generation, mixed-strategy games and creative writing; aligned models favour "7" when asked for a random number. **[abstract]** — [West & Potts 2025](https://arxiv.org/abs/2505.00047)
- NoveltyBench: in the OLMo 2 family each alignment stage reduced diversity, and more reasoning effort in OpenAI reasoning models tended to reduce both diversity and utility. **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2504.05228)
- A study on Llama-2 found aligned models have lower token entropy and gravitate to "attractor states" in embedding space. **[secondary summary; small, older-model study]** — [arXiv 2406.05587](https://arxiv.org/abs/2406.05587)

**Shared training data and methods across vendors**
- Artificial Hivemind reports 71 to 82% average similarity between responses from different models, and that among the 50 most similar responses to a query about 8 different models are represented on average. **[page summary]** — [Jiang et al. 2025](https://arxiv.org/html/2510.22954)
- Wenger and Kenett tested whether a shared model family explains the sameness: Llama-family models were no more alike than unrelated models (0.441 vs 0.445, p = .41). **[page summary]** — [Wenger & Kenett 2025](https://arxiv.org/html/2501.19361)

**Identical prompts**
- The independent-sessions result (0.452 vs 0.679) is the direct evidence. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Wan and Kalman (2025/2026) argue the creativity-diversity trade-off "may emerge from uniform deployment practices rather than from an inherent limitation": when 300 plots were generated from 10 different AI personas, human story diversity was preserved relative to a no-AI baseline. No numbers on the abstract page. **[abstract]** — [Wan & Kalman](https://arxiv.org/abs/2504.13868)

**Examples in the prompt**
- Terwiesch et al. (2026): GPT-4 given six high-scoring example ideas produced a less diverse pool than the same model given none (similarity 0.428 vs 0.414; B = 0.014, p = .036), while purchase intent was slightly higher (49.3% vs 46.4%, p = .057). **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Meincke et al. (2024): the "Previous Top Ideas" prompt scored 0.403 against the base prompt's 0.377 (higher is less diverse). **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)

### Inferences
- The cause most relevant to a same-brief swarm is the first one: 33 runs of one model are closer to one person asked 33 times than to 33 people. Levers that work are the ones that give each run a different starting point.
- A long shared brief (background, fixed rules, examples of what not to repeat) is itself a strong common prior. Nothing in the literature tests a 400-word brief specifically, but the few-shot results suggest shared content pulls runs together and does not push them apart.

### Gaps
- The alignment findings are mostly from abstracts; I did not retrieve per-stage numbers.
- No study isolates how much of the collapse is due to shared training data versus alignment versus decoding.
- The example-anchoring effect measured is small (0.014 in similarity) and from a 2023 model. I found no study that measures how strongly ideas copy the *content* of prompt examples in ideation.

## 3. Which levers have been tested and how much did each help?

### Takeaway
The levers with the largest measured gains all vary the starting point between runs or make the model see and work against its own earlier ideas: randomly assigned ordinary personas, randomly assigned functional constraints, a planning step that splits the space into different directions, a draft-then-diversify step, and asking for a set of candidates with probabilities. Temperature, "be creative" wording and famous-person personas give small or unreliable gains. No single-model lever fully reached the human pool in the product-idea studies, except personas combined with chain-of-thought in one study.

### Cited Findings

**Summary of effect sizes from the one study that tested many levers on one scale** (GPT-4o, product ideas, diversity = 1 minus mean pairwise cosine similarity, pools of 100 drawn from 2,000; higher is better) **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)

| Condition | Diversity |
|---|---|
| Humans | 0.773 |
| Composite pool, four vendors | 0.763 |
| Random personas (one of 100 student personas per session) | 0.757 |
| Human picks the problem, model proposes solutions | 0.739 |
| Random functional constraints (one of 20 per session) | 0.735 |
| Chain-of-thought (draft, make different, then describe) | 0.698 |
| Random Shakespeare sonnet placed before the prompt | 0.686 |
| GPT-4o plain, 100 ideas per session, temperature 1 | 0.679 |
| GPT-4o plain, temperature 0.5 / 0 | 0.626 / 0.618 |
| "Make this idea bolder", applied twice to each idea | 0.575 |
| One idea per independent session | 0.452 |

**Temperature and other sampling settings**
- Terwiesch et al. (2026): temperature 0 to 1 moved GPT-4o from 0.618 to 0.679; 0.5 was not significantly different from 0 (p = .247); above 1.0 output was often unstable. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Deng et al. (2026): temperature 1.0 to 1.5 raised categories from 22 to 23 and combinations from 89 to 97 (humans: 28 and 209); 2.0 produced garbled output. **[page summary]** — [Deng et al. 2026](https://arxiv.org/html/2602.20408)
- Artificial Hivemind: even with min-p 0.1 at temperature 2.0, 81% of response pairs were above 0.7 similarity and 61.2% above 0.8. **[page summary]** — [Jiang et al. 2025](https://arxiv.org/html/2510.22954)
- Peeperkorn et al. (ICCC 2024, story generation): temperature is "weakly correlated with novelty" and "moderately correlated with incoherence". No coefficients on the abstract page. **[abstract]** — [Peeperkorn et al. 2024](https://arxiv.org/abs/2405.00492)
- Ma et al. (2024, GPT-4): no monotonic effect of temperature or top-p on diversity; temperature 1 with top-p 1 was best; temperature 2 with top-p 1 was incoherent; prompt changes mattered more than parameters. **[full text]** — [Ma et al. 2024](https://codesign.berkeley.edu/pdfs/papers/ma-llmdiverse-jcise.pdf)
- Shur-Ofry et al. (older models, list questions): raising temperature from 0.3 to 1 increased the number of different answers by roughly 80 to 100% (for example 4.3 to 7.8 of 30). **[full text]** — [Shur-Ofry et al. 2024](https://arxiv.org/pdf/2411.02989)

**Persona or role prompts**
- Random ordinary personas were the best single-model lever in Terwiesch et al. (0.757 vs 0.679). A five-step eccentricity test found no steady gain from stranger personas: near-identical personas were worst, diverse ordinary students best, and outlandish personas (Mars colonist, sentient cloud) significantly worse than ordinary diverse ones (p < .001); eccentric personas moved ideas away from human ideas but they still clustered. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Deng et al. (2026): "ordinary" personas raised category combinations from 89 to 208 (humans 208) and beat curated "creative" personas (164). Personas slightly increased within-session fixation (slope 0.875 vs 1.023, p < .001). **[page summary]** — [Deng et al. 2026](https://arxiv.org/html/2602.20408)
- Meincke et al. (2024), one persona for the whole pool: small and unpredictable. Creative entrepreneur 0.348, Steve Jobs 0.368, base 0.377, "boring person" 0.383, Elon Musk 0.385, plain entrepreneur 0.406. **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- Moon et al. (Sept 2026): personas generated by an evolutionary search for spread raised response diversity on the Alternative Uses Task by 78.8%, originality by 26.1% and flexibility by 49.5% over task-only prompting, with 98.5% validity; they added a further 18.6% diversity on top of a creativity-optimised prompt. **[abstract]** — [Moon et al. 2026](https://arxiv.org/abs/2609.30492)
- Feng, Hélie and Panchal (Design Science, 2025; GPT-4o, Gemini 1.5 Flash, Llama 3.1 8B): five professional personas in five separate prompts gave more diverse concepts than no persona; putting all five personas in one prompt gave the lowest diversity of the three strategies. Results are shown in figures; no numbers in the text. **[full text]** — [Feng et al. 2025](https://doi.org/10.1017/dsj.2025.10037)
- Counter-evidence: in the Terwiesch re-analysis of Boussioux et al. (2024), GPT-4 pools with a random persona were *more* similar than pools without one (0.56 vs 0.465 for single problems; 0.62 vs 0.562 for single solutions). **[full text, table values only]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Wenger and Kenett: a "very creative" system prompt raised LLM population variability from 0.459 to 0.576, still far below the human 0.738. **[page summary]** — [Wenger & Kenett 2025](https://arxiv.org/html/2501.19361)

**Chain-of-thought or stepwise prompts (draft a list, revise for difference, then write up)**
- Meincke et al. (2024): best of 35 prompts, 0.255 against base 0.377 and humans 0.243. Advantage held to about 750 ideas. About 15% of runs skipped the revision step and were discarded. The chain-of-thought runs used a later model (gpt-4-1106-preview) than the base runs. **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- Terwiesch et al. (2026): on GPT-4o the gain was "more modest", 0.698 vs 0.679. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Deng et al. (2026): chain-of-thought raised combinations from 85 to 152 (humans 196) and reduced fixation (slope 1.023 to 1.354); it did not help humans. Personas plus chain-of-thought reached 240 combinations, above humans, and was the top condition for every model tested (263 vs 208 on the newer reasoning model). **[page summary]** — [Deng et al. 2026](https://arxiv.org/html/2602.20408)
- Ma et al. (2024): a critique-and-revise pass gave the largest diversity gain among their prompt methods. **[full text]** — [Ma et al. 2024](https://codesign.berkeley.edu/pdfs/papers/ma-llmdiverse-jcise.pdf)
- Lu et al. (NAACL 2025, code tasks): planning and self-correction raised correctness but slightly lowered divergent scores (-1.16 and -0.37 points). **[page summary]** — [Lu et al. 2025](https://arxiv.org/html/2407.09007)

**Many ideas in one call versus many calls**
- One idea per session 0.452 vs 100 per session 0.679 (GPT-4o). **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Verbalized Sampling paper: a plain list in one call ("Sequence") barely beat single calls on poem diversity (GPT-4.1-mini 9.6 vs 8.4; GPT-4.1 10.6 vs 10.6) but did much better on human-rated joke diversity (2.93 vs 1.83 on a 1 to 4 scale). **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2510.01171)
- NoveltyBench: "in-context regeneration" (earlier answers stay in context, model is asked for a different one) was the most effective strategy and roughly matched human writers; paraphrasing the prompt and a "be creative" system prompt were only marginally effective. No numbers in the text. **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2504.05228)

**Asking for probabilities or a distribution**
- Verbalized Sampling (ask for k responses with their probabilities; 10 models): diversity 1.6 to 2.1 times direct prompting on creative writing; human-evaluated scores up 25.7%; recovers 66.8% of base-model diversity. Poem diversity: GPT-4.1-mini 8.4 direct, 14.8 standard variant, 15.0 with reasoning; GPT-4.1 10.6, 15.2, 25.6. Quality dropped a little for the standard variant (56.5 vs 61.1 on mini; 63.7 vs 68.6 on GPT-4.1). k = 5 was used; larger k adds diversity but lowers quality; asking for low-probability items raises diversity further. **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2510.01171)
- String Seed of Thought (model first writes a random string, then derives its answer from it): on NoveltyBench with DeepSeek-R1, distinct answers rose from 4.70 to 6.19 of 10 (curated set) and 3.39 to 5.25 (real user prompts), ahead of paraphrasing (5.63) and temperature 1.0 (5.57). The authors warn models under about 8B parameters may fail to carry it out. **[page summary]** — [Misaki & Akiba 2025](https://arxiv.org/html/2510.21150v3)

**"Denial" or "already taken" lists and anti-anchoring**
- Si et al. put all earlier idea titles in each prompt and still got 95% duplicates. **[page summary]** — [Si et al. 2024](https://arxiv.org/html/2409.04109)
- Denial prompting (ban a technique used in the previous solution, up to five rounds; GPT-4 on coding problems): share of techniques unseen in human solutions rose from 4.5% to 15.3%, but pass rate fell from 16.1% to 2.1% and constraint-following from 100% to 14.4%; the combined score peaked after one denial and hit zero by four. **[page summary]** — [Lu et al. 2025](https://arxiv.org/html/2407.09007)
- Ibrahim, Azad and Baten (May 2026; GPT-5.4, Claude Sonnet 4.6, Gemini 2.5 Pro; stories, alternative uses, slogans; 150 outputs per cell): showing every regeneration call the same three representative earlier outputs to avoid gave the smallest gain; showing each call its own earlier output plus one or two peers did well but cost 3.71 times the tokens; a plan-first split into five directions with no earlier outputs matched or beat it at 1.61 times the tokens. **[page summary]** — [Ibrahim et al. 2026](https://arxiv.org/html/2605.30150)
- Telling the model the cosine similarity of its existing ideas made things worse (0.432 vs base 0.377). **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)

**Planning the space first (stratification) and a "stand out" line**
- Ibrahim et al. (2026): one planning call proposes five semantic directions and the parallel calls are split evenly across them. With a line asking the answer to stand out from what others would write, mean pairwise distance rose by 0.17 (GPT-5.4), 0.25 (Claude Sonnet 4.6) and 0.13 (Gemini 2.5 Pro) over plain independent calls. It reached the plain baseline's full-pool entropy level after 7.4 outputs on average, against 17.9 for the "stand out" line alone and 23.6 for the shared-anchors method. The "stand out" line alone added 0.04 to 0.06 at about 1.1 times the tokens and did not lower automatic quality scores. Quality was scored by automatic proxies, not people. **[page summary]** — [Ibrahim et al. 2026](https://arxiv.org/html/2605.30150)
- Shur-Ofry et al.: adding "answer from diverse perspectives" raised the number of different answers by about 20 to 60%; combined with temperature 1, by about 150 to 200%. Older models. **[full text]** — [Shur-Ofry et al. 2024](https://arxiv.org/pdf/2411.02989)

**Random seed words or forced stimuli**
- Task-relevant randomness worked (personas 0.757, constraints 0.735); task-irrelevant randomness barely did (random sonnet 0.686 vs 0.679). The authors conclude "the type of introduced heterogeneity matters". **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Agrawal and Goyal (Jan 2026): prepending one random word to list prompts such as "Name 10 Hollywood actors" raised the median count of unique items over 100 runs from 22 to 32 on Gemma 3 4B (30 with a random sentence). The task is recall, not ideation. **[search snippet of the paper's table]** — [Agrawal & Goyal 2026](https://arxiv.org/abs/2601.18053)
- String Seed of Thought also reports that an externally supplied random string improves results, though less than a self-generated one in their biased-sampling test. **[page summary]** — [Misaki & Akiba 2025](https://arxiv.org/html/2510.21150v3)

**Explicit constraints**
- Random functional constraints: 0.735 vs 0.679. On a five-step scale, "extreme but physically possible" constraints (must fit in a walnut shell) were the most diverse of any tier and closest to humans; surreal impossible ones (made of moonlight) lost the gain; mild and practical ones helped least. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- CS4 (2024, mostly 7B-scale models): as the number of story constraints rose to 39, story quality fell for every model. **[secondary summary]** — [Atmakuru et al. 2024](https://arxiv.org/abs/2410.04197)

**Analogies from distant fields**
- Liu, Dubova, Conklin, Harada and Griffiths (2026; humans and seven LLMs designing products from a random source domain): humans reliably benefited; LLMs "showed no overall benefit"; more distant sources gave more original ideas in both, but only the highest-rated LLMs benefited and only from sufficiently remote sources. No numbers on the abstract page. **[abstract]** — [Liu et al. 2026](https://arxiv.org/abs/2603.19087)
- Choi and Song (2026, research ideation): cross-domain retrieval won more novelty comparisons than no retrieval, but showed "no significant difference from a random diverse-seed control". **[abstract]** — [Choi & Song 2026](https://arxiv.org/abs/2605.11532)
- Shen et al. (2026, ten LLMs): models draw analogies from "a narrow set of target domains", and methods that widen them cost quality. **[abstract]** — [Shen et al. 2026](https://arxiv.org/abs/2608.03233)

**Examples in the prompt**
- Six good example ideas: slightly less diverse (0.428 vs 0.414 similarity, p = .036), slightly higher rated (not significant). **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Pasting in a Harvard Business Review article on brainstorming (0.387) or a Stanford design-thinking article (0.392) was slightly worse than the base prompt (0.377). **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)

**Asking for bolder, extreme or bad ideas**
- Applying "make this idea bolder" twice to each idea separately *reduced* diversity (0.575 vs 0.679); ideas converged on the same "novel" features, notably scents. **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Asking the model to revise a whole list so items are "bolder and more different" from each other is the core of the chain-of-thought prompt that helped. **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- Adding "far-fetched" to an expert persona gave "a considerable improvement" in diversity, while plain "You are a design expert" did not; the words "unique" and "diverse" scored slightly below "creative" and "novel". **[full text]** — [Ma et al. 2024](https://codesign.berkeley.edu/pdfs/papers/ma-llmdiverse-jcise.pdf)

**Politeness, tips, threats**
- Tipping 0.374, threat to switch off 0.375, "say please" 0.383, against base 0.377: no meaningful effect. **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)

**Combining levers and selecting afterwards**
- Pools from different prompt strategies overlapped little, so the authors recommend mixing strategies. A programmatic greedy pick (start from one random idea, then repeatedly add the idea that raises similarity least; one set of 100) gave 0.144, far more diverse than any generation prompt or the human pool (0.243). The paper lists this in an appendix table without further analysis. **[full text]** — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)

### Inferences
- Wording that every agent receives identically ("imagine freely", "be creative", a fixed rule list) cannot separate agents from each other; at best it shifts the whole swarm. The measured gains for such wording are small (0.04 to 0.06 in pairwise distance for a "stand out" line; 0.459 to 0.576 for "very creative").
- A single shared "do not repeat these" list is closest to the "same three anchors for everyone" condition, which was the weakest anti-anchoring method. It removes named ideas but leaves every agent at the same next-most-likely ideas.
- The cheapest high-yield change for a swarm is to give each agent a different, task-relevant assignment: a distinct ordinary persona or user, a distinct hard constraint, or a distinct region from a planning call. On the Wharton scale personas were worth about 0.08 and constraints about 0.06, against 0.02 for chain-of-thought and 0.06 for the whole 0-to-1 temperature range. The planning-call result comes from a different study and scale, so it cannot be ranked against these directly.
- Asking each agent for several ideas, with a step that revises the list for difference, should beat one idea per agent. Asking each agent to push one idea "bolder" on its own is likely to backfire.
- Over-generating and then selecting for spread is a legitimate lever and had the largest effect of anything measured, though it was reported only as a side result.

### Gaps
- No controlled study found of "ask for bad ideas first" or "worst idea" prompting for LLMs; only practitioner advice without measurements.
- No study tests random seed *words* for product ideation; evidence is from list recall, a sonnet prefix, and random strings.
- I could not retrieve the Verbalized Sampling ablations on temperature, k and probability thresholds; the paper says the method is orthogonal to decoding settings but I have no numbers.
- Few-shot results in Ma et al. appear only in a figure I could not read.
- Most gains are in embedding distance. Only Verbalized Sampling (human raters), Terwiesch et al. (purchase intent, for the base comparison only) and Ibrahim et al. (automatic proxies) say anything about whether the extra ideas are good. Deng et al. report no quality measure.

## 4. Do smaller models behave differently from larger ones? Does mixing models or providers raise pooled diversity?

### Takeaway
On raw sampling, smaller models in a family often give more distinct answers than larger ones, but lower quality, and they gain less from the prompt methods that need reasoning. Mixing vendors raised pooled diversity to near the human level in the one study that sampled 25 ideas from each of four models, but other work shows different models still share most of their default answers, so mixing helps most when combined with other levers.

### Cited Findings

**Model size**
- NoveltyBench, distinct answers out of 10 (and utility score): Gemma 2 2B 5.66 (4.63), 9B 3.25 (3.93), 27B 3.03 (3.77); Llama 3 1B 6.74 (2.81), 3B 5.10 (3.24), 8B 5.24 (3.76), 70B 2.49 (2.87), 405B 3.20 (3.39). The abstract states that "larger models within a family often exhibit less diversity than their smaller counterparts". **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2504.05228)
- Terwiesch et al. (2026): GPT-3.5 Turbo (0.680) was more diverse than the original GPT-4 (0.585) and equal to GPT-4o (0.679). The reasoning model o3-mini was the least diverse of all (0.495), fixated on desk organisers, while another reasoning model, DeepSeek R1, was near the top (0.752). Diversity was "heterogeneous and not monotonic in release date". **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Verbalized Sampling: gains "are positively correlated with model scale"; larger models gained 1.5 to 2 times more diversity, and less capable models may show a drop in output quality. On poems the mini model still gained (8.4 to 14.8). **[page summary]** — [Zhang et al. 2025](https://arxiv.org/html/2510.01171)
- String Seed of Thought: models under about 8B parameters "may fail to execute these strategies correctly". **[page summary]** — [Misaki & Akiba 2025](https://arxiv.org/html/2510.21150v3)
- Deng et al. (2026): a newer reasoning model was *more* concentrated on first ideas than GPT-4o (4.22 vs 8.71 categories; humans 14.29), which the authors read as a growing deficit in newer models; personas plus chain-of-thought still restored it. **[page summary]** — [Deng et al. 2026](https://arxiv.org/html/2602.20408)
- Haase, Hanel and Pokutta (2025, 14 models): no rise in divergent-thinking scores over 18 to 24 months; the same model with the same prompt ranged from below-average to original; only 0.28% of responses reached the top 10% of human answers. **[secondary summary of abstract]** — [Haase et al. 2025](https://arxiv.org/abs/2504.12320)
- Lu et al. (2025, code): GPT-4 had the highest combined creativity score; Claude 3 Sonnet and Llama 3 70B started close but fell to zero within two rounds of denial; smaller models lagged. **[page summary]** — [Lu et al. 2025](https://arxiv.org/html/2407.09007)

**Mixing models or providers**
- Terwiesch et al. (2026): a balanced pool of 25 ideas each from GPT-4 Turbo, Gemini Pro 2.0, DeepSeek R1 and Claude Sonnet 3.5 scored 0.763, above every single model (best 0.756) and not significantly different from humans at 0.773 (p = .092). **[full text]** — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- Shur-Ofry et al. (older models): at default settings, pooling added almost nothing: 180 answers from six API models contained only 10 different names, and 60 answers from two chat interfaces contained 8, the same as one model alone. With a diversity prompt plus temperature 1, six pooled models gave 58 to 60 different TV series against 25 in 30 human answers. **[full text]** — [Shur-Ofry et al. 2024](https://arxiv.org/pdf/2411.02989)
- Artificial Hivemind: 71 to 82% similarity between different models' responses to open-ended queries. **[page summary]** — [Jiang et al. 2025](https://arxiv.org/html/2510.22954)
- Wenger and Kenett conclude that switching between LLMs would not restore variability, since 22 models from several families were collectively far less varied than humans. **[page summary]** — [Wenger & Kenett 2025](https://arxiv.org/html/2501.19361)

### Inferences
- Small models are not the cause of the collapse; if anything they repeat less per sample. But their extra variety comes with lower quality, and the reasoning-heavy fixes (verbalized probabilities, random-string derivation) are documented to work less well on them. Persona and constraint assignment need no reasoning ability and should transfer; this is my inference, since Feng et al. is the only study that included a small model (Llama 3.1 8B) with personas, and it reports direction only.
- Mixing providers is worth doing, but the four-vendor result (+0.007 over the best single model, +0.08 over GPT-4o) and the older "pooling adds nothing at defaults" result together suggest most of the gain comes from including models that are individually diverse, plus other levers.

### Gaps
- No study compares small and large models on ideation diversity with personas or constraints applied.
- The four-vendor pool has not been tested at swarm scale or with small models.
- No source measures whether "reasoning" or "thinking" modes in current small models reduce diversity the way NoveltyBench found for OpenAI reasoning effort.

## 5. Where is there disagreement or weak evidence?

### Takeaway
The direction of the main finding is not disputed, but its size is, because it depends heavily on how diversity is measured. Personas, chain-of-thought, mixing models and model progress each have at least one study pointing the other way, and almost no study checks whether more diverse ideas are also better ideas.

### Cited Findings
- **Measurement.** Deng et al. argue embedding similarity is sensitive to wording and overstates the human-LLM gap by roughly two to three times compared with hand-coded categories. Terwiesch et al. counter that 80 to 90% of their gap survives rephrasing. Meincke et al. concede cosine similarity "is not perfect" and that it is unclear how it links to human judgments. — [Deng et al. 2026](https://arxiv.org/html/2602.20408); [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553); [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- **Human baselines favour humans.** The human pools are aggregates of many separate people; Meincke et al. say this "is likely to have created a much more diverse idea pool than any human individual or brainstorming team" could. — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- **Personas.** Help strongly when varied per session (0.757; 89 to 208 combinations; +78.8%), help little or unpredictably as one persona for the pool (0.348 to 0.406 around a 0.377 base), and were associated with *less* diversity in the Boussioux data (0.56 vs 0.465). Ordinary personas beat "creative" or outlandish ones in two studies. — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553); [Deng et al. 2026](https://arxiv.org/html/2602.20408); [Moon et al. 2026](https://arxiv.org/abs/2609.30492); [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727)
- **Chain-of-thought.** A large gain in 2024 (0.377 to 0.255, with a model change between conditions), a modest one on GPT-4o in 2026 (0.679 to 0.698), a clear one on categories in Deng et al. (85 to 152), and slight losses for planning and self-correction on code. — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727); [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553); [Deng et al. 2026](https://arxiv.org/html/2602.20408); [Lu et al. 2025](https://arxiv.org/html/2407.09007)
- **Within-session fixation.** The February 2026 version of Deng et al. described LLM fixation as a cause; the November 2026 version reports fixation equal to humans (p = .90) and locates the gap between sessions. The paper's title also changed between versions. — [Deng et al. 2026](https://arxiv.org/html/2602.20408); [earlier abstract](https://arxiv.org/abs/2602.20408?context=cs)
- **Are newer models better?** Terwiesch et al. find most later models more diverse than 2023 GPT-4; Deng et al. find a newer reasoning model more concentrated on first ideas; Haase et al. find no gain in 18 to 24 months; NoveltyBench finds larger models less diverse. — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553); [Deng et al. 2026](https://arxiv.org/html/2602.20408); [Haase et al. 2025](https://arxiv.org/abs/2504.12320); [Zhang et al. 2025](https://arxiv.org/html/2504.05228)
- **Mixing models.** Near-human in one study, close to no gain at defaults in another, and 71 to 82% cross-model similarity in a third. — [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553); [Shur-Ofry et al. 2024](https://arxiv.org/pdf/2411.02989); [Jiang et al. 2025](https://arxiv.org/html/2510.22954)
- **"Bolder".** List-level "make them bolder and more different" helped; idea-by-idea "make it bolder" hurt. — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727); [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- **Distant analogies.** Reliable for humans, no overall benefit for LLMs, and no better than random diverse seeds in research ideation. — [Liu et al. 2026](https://arxiv.org/abs/2603.19087); [Choi & Song 2026](https://arxiv.org/abs/2605.11532)
- **Diversity versus quality.** Denial prompting traded correctness away almost entirely; Verbalized Sampling lost a few quality points in its standard form; more constraints lowered story quality; yet a "stand out" line and stratification did not lower automatic quality scores. Meincke et al. note "diversity can be obtained by sacrificing idea quality" and did not test it. In Terwiesch et al., human ideas far from any LLM idea had lower purchase intent. — [Lu et al. 2025](https://arxiv.org/html/2407.09007); [Zhang et al. 2025](https://arxiv.org/html/2510.01171); [Atmakuru et al. 2024](https://arxiv.org/abs/2410.04197); [Ibrahim et al. 2026](https://arxiv.org/html/2605.30150); [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727); [Terwiesch et al. 2026](https://arxiv.org/pdf/2607.27553)
- **Self-evaluation is weak.** Si et al. found the best LLM judge of ideas reached 53.3% accuracy, below the 56.1% agreement between human reviewers, so a swarm cannot reliably pick its own best ideas. **[page summary]** — [Si et al. 2024](https://arxiv.org/html/2409.04109)
- **Evidence quality.** Most 2026 sources are preprints. Meincke et al. used 10 runs per prompt and warn some results "might be driven by statistical noise" and "might be GPT-4 specific". Shur-Ofry et al. used three questions and a human baseline of about 30 posts on X. Ibrahim et al. used automatic quality proxies. — [Meincke et al. 2024](https://arxiv.org/pdf/2402.01727); [Shur-Ofry et al. 2024](https://arxiv.org/pdf/2411.02989); [Ibrahim et al. 2026](https://arxiv.org/html/2605.30150)

### Inferences
- Any diversity number a team computes for its own sessions should be a category or theme count by hand or by a separate judge, alongside an embedding measure, because the two can differ by a factor of two to three.
- Since the literature mostly optimises spread and rarely checks value, a team should expect some of the added variety to be weak ideas and plan a separate human selection step.
- The lever ranking is most trustworthy where two independent groups agree: per-session ordinary personas (Wharton and Columbia), draft-then-diversify (Wharton and Columbia), temperature as a minor lever (Wharton, Columbia, Berkeley, the Hivemind paper).

### Gaps
- No replication yet of the stratified planning result or the evolutionary-persona result by a second group.
- No study reports confidence intervals for lever effects on small models.
- I found no careful practitioner write-up with measurements that adds to the academic sources; the practitioner material located was opinion without data.
