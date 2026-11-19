# Evolutionary, quality-diversity and open-ended search with LLMs, applied to natural-language ideas

Notes compiled November 2026. Findings dated 2024 or earlier are marked "older". Each finding says whether it was shown on code or other automatically scored tasks ("scored") or on open-ended text judged by a model or by people ("text"). Most sources were read through their arXiv HTML pages; where only an abstract, a search snippet or a secondary write-up was read, the finding says so.

## 1. Quality-diversity: how do MAP-Elites and its LLM versions work, how are diversity axes chosen for text, how many cells are practical, and what gains over plain sampling were reported?

### Takeaway
MAP-Elites keeps the single best item in each cell of a grid whose axes the user chooses; the LLM versions (QDAIF, Rainbow Teaming) use a model to rewrite text, to judge its quality and to say which cell it belongs in. Published text grids are small and hand-designed (20 to 100 cells), and gains over plain sampling are large on automatic coverage and diversity measures but small on human-rated quality in the one study that used human raters.

### Cited Findings

**The base algorithm (older, 2015)**
- MAP-Elites lets the user pick the "dimensions of variation" and returns a map of high-performing solutions across that space instead of one best answer. The authors claim it gives "a large diversity of high-performing, yet qualitatively different solutions" and also tends to find a better single solution than plain optimisation (scored; robotics and similar tasks). — [Mouret and Clune 2015, arXiv 1504.04909](https://arxiv.org/abs/1504.04909)
- The insertion rule, as restated in QDAIF: a new solution enters the archive if its cell is empty or if it beats the current occupant on quality. — [QDAIF, arXiv 2310.13032](https://arxiv.org/html/2310.13032)

**First LLM version, on code (older, 2022)**
- Evolution through Large Models (ELM) used a code LLM as the mutation operator inside MAP-Elites and generated "hundreds of thousands of functional examples of Python programs" for walking robots in the Sodarace domain (scored). — [Lehman et al. 2022, arXiv 2206.08896](https://arxiv.org/abs/2206.08896)

**QDAIF: quality-diversity through AI feedback (older, October 2023; text)**
- Loop: start from three hand-chosen seed texts per domain, picked to span the diversity axis; pick a random existing solution from the archive; mutate it with an LLM; have an LLM score the new text's quality and its diversity attribute; insert under the MAP-Elites rule. — [QDAIF](https://arxiv.org/html/2310.13032)
- Mutation operators: "LMX-Near" builds a few-shot prompt from existing archive texts (beginning "Here is a random example of") and takes the model's continuation as the child. For poetry, "LMX-rewrite" asks the model to write a new poem inspired by the parent with a different genre and tone, and "LMX-guided" adds a randomly chosen target genre and tone to that prompt. — [QDAIF](https://arxiv.org/html/2310.13032)
- Judging: quality comes from a yes/no question to the model (is this text high-quality or on-topic), scored by the relative log-probability of the answers. The diversity attribute comes from asking the model to label the text (for example positive or negative), again using label log-probabilities. In poetry, GPT-4 rated quality 1 to 10 ("Rate the quality of the above poem on a scale from 1 to 10") and picked one of five genres. — [QDAIF](https://arxiv.org/html/2310.13032)
- Axes and cells: opinions on eating vegetables, axis sentiment, 1D archive with 20 bins; short stories with genre (romance to horror) or ending (happy to tragic) as 1D archives, and genre by ending as a 2D archive (maximum QD score 100); poetry with 5 genres (haiku, sonnet, ballad, limerick, hymn) by 5 tones (happy, dark, mysterious, romantic, reflective), 25 cells. Bins on the logit-based axes are non-uniform, denser towards the ends, because model logits do not change linearly with the perceived attribute. — [QDAIF](https://arxiv.org/html/2310.13032)
- Scale: 2,000 iterations for opinions and stories (5 random seeds); 200 iterations for poetry. A 13B open model did the mutation by default; poetry used GPT-4. — [QDAIF](https://arxiv.org/html/2310.13032)
- Automatic results: QDAIF "significantly outperforms" four baselines (fixed few-shot prompt, shuffled few-shot prompt, random search, and LMX optimising quality only) on QD score in opinions and stories. Poetry QD scores: QDAIF 130 (CI 118 to 145), random poems 76 (CI 67 to 85), rewriting from a fixed seed 99 (CI 72 to 117). — [QDAIF](https://arxiv.org/html/2310.13032)
- Human results (6 annotators, 280 annotations): human-rated QD score was 0.772 for QDAIF against 0.767 for the fixed few-shot baseline, 0.696 shuffled few-shot, 0.606 random search and 0.650 quality-only evolution. Average human quality rating was higher for fixed few-shot (4.133) than for QDAIF (3.900). — [QDAIF](https://arxiv.org/html/2310.13032)
- Targeting matters: untargeted LMX-rewrite failed to fill some poetry cells (limericks, for example); assigning a random target genre and tone filled them. — [QDAIF](https://arxiv.org/html/2310.13032)
- Limits stated by the authors: the axes must be specified in advance and attributes that are not on an axis are not explored (in a "hero spy vs. hero politician" setup many stories ignored the characters' interaction); they propose letting LLMs suggest axes as future work. — [QDAIF](https://arxiv.org/html/2310.13032)

**Rainbow Teaming (older, February 2024; text prompts scored by an LLM judge)**
- Loop: sample a parent prompt uniformly from the archive; sample a target cell with probability biased towards low-fitness cells; the mutator LLM applies one mutation per axis (first risk category, then attack style); discard the candidate if it is too similar to its parent; get the target model's response; a judge LLM compares that response with the response of the cell's current occupant, and the winner keeps the cell. — [Rainbow Teaming, arXiv 2402.16822](https://arxiv.org/html/2402.16822)
- Axes and cells: two categorical axes of 10 values each (risk category by attack style, 100 cells) for safety; topic by interrogative word by question length (3D) for question answering; 10 attack tactics by 10 prompt-length bins for cybersecurity. Main runs used 2,000 iterations with batch sizes of 16 to 64. — [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- Gain over a no-archive baseline ("No Stepping Stones", which regenerates from scratch each time) in question answering: mean fitness 0.91 vs 0.79, coverage 0.97 vs 0.90, self-BLEU 0.50 vs 0.60 (lower means more varied). — [Rainbow Teaming](https://arxiv.org/html/2402.16822)

**Grid-free variants for ideas (2026; text)**
- IDEAgent (July 2026) frames research ideation as quality-diversity search but deliberately avoids a grid: it "leave[s] idea generation unconstrained" and has an LLM "Diversity Judge" compare a compressed signature of each idea (problem, mechanism, value added, assumptions, expected effect) with the archive. It keeps an active archive of 10, a repair queue, a historical archive and a "rejected-pattern memory". — [IDEAgent, arXiv 2607.22375](https://arxiv.org/html/2607.22375)
- IDEAgent's "Yield" counts the largest set of ideas that all pass quality thresholds and are pairwise distinct, so near-identical good ideas count once. Against the best baseline it reports 1.094 vs 0.281 at the stricter threshold (3.89 times) and 2.312 vs 1.156 at the looser one, across 32 computer-science topics; two human raters preferred its ideas in 69.6% of 25 pairs. — [IDEAgent](https://arxiv.org/html/2607.22375)
- EvoGens (May 2026) uses embedding clusters as niches instead of named axes: ideas are embedded, clustered with k-means (k = 30), and the top-scoring idea in each cluster is kept. — [EvoGens, arXiv 2605.30961](https://arxiv.org/html/2605.30961v1)

**A caution on fixed grids**
- In a November 2025 comparison on evolving image prompts, the authors' re-run of QDAIF scored a Vendi diversity of 1.80 against 3.60 for their novelty-search method and 3.29 for Lluminate (text prompts rendered as images; diversity measured on images). — [Wander, arXiv 2511.00686](https://arxiv.org/html/2511.00686v1)

### Inferences
- The published text archives imply a budget of roughly 8 to 20 candidates per cell (200 iterations for 25 poetry cells with a strong model; 2,000 iterations for 100 cells with weaker models). A 5 by 5 grid therefore needs on the order of 200 candidates, or about six rounds of 30 to 35 agents.
- For a hand-run version, categorical axes with 4 to 6 named values each (as in QDAIF poetry and Rainbow Teaming) are the practical choice: a judging agent can assign a label without access to model logits, and the coordinator can read the grid.
- Each generating agent should be told which cell to aim for. Both QDAIF (LMX-guided) and Rainbow Teaming (target descriptor sampling) found that untargeted mutation leaves cells empty.
- Variety only appears along the axes chosen. The team's "dozen themes" is itself a candidate axis; a second axis should be something the single brief never varied (for example who the idea is for, or how it works). This suggestion is mine, not from a source.
- The human study in QDAIF suggests the method's main benefit is coverage (ideas in places plain sampling does not reach), not higher average quality per idea.

### Gaps
- I found no quality-diversity study on product concepts, feature ideas or names. Published text evidence covers opinions, short stories, poems, adversarial prompts, image prompts and research ideas.
- QDAIF's full prompts and batch size are in appendices beyond the portion of the page that was read.
- No source tested whether axes proposed by an LLM work as well as hand-chosen ones; QDAIF lists it as future work.
- No text-domain archive larger than about 100 cells was found, so the practical upper limit is not established.

## 2. LLM-driven evolution: how do systems that use a model as the mutation and crossover operator work, which parts transfer to natural-language ideas, and which depend on an automatic scorer?

### Takeaway
The common loop is: keep a scored population, show the model one or more parents (often with their scores and feedback), ask for a changed or combined child, score it, and keep the best while protecting variety. The headline results (FunSearch, AlphaEvolve, ShinkaEvolve, Mind Evolution, Promptbreeder) all rely on an automatic scorer; the versions that work on unscored text (AI co-scientist, AlphaWrite, EvoGens, IDEAgent) replace it with pairwise LLM judging, review gates and deduplication, and their gains are mostly measured by other LLM judges.

### Cited Findings

**Operators**
- Language Model Crossover (older, February 2023): build a few-shot prompt from "a few text-based genotypes" and parse the model's output as the offspring. Tested on binary strings, sentences, equations, text-to-image prompts and Python code. — [Meyerson et al., arXiv 2302.12170](https://arxiv.org/abs/2302.12170)
- A 2024 survey (older) sorts the field into "LLM-enhanced EA" and "EA-enhanced LLM", plus integrated uses in "code generation, software engineering, neural architecture search, and various generation tasks". — [Wu et al., arXiv 2401.10034](https://arxiv.org/abs/2401.10034)

**Program-search systems (scored)**
- FunSearch (older, published in Nature, December 2023): a programs database stores scored programs; samplers build a prompt from k = 2 programs drawn from one island, sorted by score and labelled as successive versions, and ask the model to write the next version; evaluators run and score the result. Two programs in the prompt beat one, "with diminishing returns beyond that". Total samples were "on the order of 10^6", with 15 samplers and 150 CPU evaluators in a typical run. — [FunSearch, Nature (PMC copy)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10794145/)
- FunSearch states it works best when an efficient evaluator exists, the score is "rich" (graded, not pass/fail), and a skeleton isolates the part to evolve. Only 4 of 140 experiments reached the record cap set of size 512. — [FunSearch](https://pmc.ncbi.nlm.nih.gov/articles/PMC10794145/)
- AlphaEvolve (June 2025): prompts contain earlier programs with their scores, problem context, rendered evaluation results and co-evolved "meta-prompt" instructions; an ensemble of a fast and a strong model proposes diffs; the database is "a combination of the MAP elites algorithm and island-based population models". It needs "thousands of LLM samples" where FunSearch needed "millions". Results include a rank-48 algorithm for 4 by 4 complex matrix multiplication and, on over 50 open maths problems, matching the best known result in about 75% of cases and improving it in about 20%. — [AlphaEvolve, arXiv 2506.13131](https://arxiv.org/html/2506.13131)
- AlphaEvolve's stated main limitation is the need for an automated evaluator. It allows separate LLM calls to grade properties that are hard to code (such as simplicity), and says LLM evaluation of ideas is possible but was not its focus. — [AlphaEvolve](https://arxiv.org/html/2506.13131)
- ShinkaEvolve (September 2025): parents are sampled with weights that combine fitness with a bonus for having few children so far; mutations are diff edits, full rewrites and crossover (probabilities 0.45, 0.45, 0.1 in one configuration); a "meta-scratchpad" periodically summarises recent evaluations into recommendations appended to the mutation prompt; a bandit picks which LLM to call. It reports a new best circle-packing result "using only 150 samples". Its listed limitation is restriction to "well-defined numerical objectives". — [ShinkaEvolve, arXiv 2509.19349](https://arxiv.org/html/2509.19349)
- OpenEvolve, the open-source implementation of this family, describes itself as using "LLMs to mutate programs and evolves them with MAP-Elites and island populations", with evaluator errors and output fed into the next prompt; its examples include evolving prompts instead of code. — [OpenEvolve README](https://github.com/algorithmicsuperintelligence/openevolve)

**Prompt evolution (text genome, scored on a dataset)**
- Promptbreeder (older, September 2023): a population of 50 units, each holding task-prompts and its own mutation-prompt, run for 20 to 30 generations; selection is a binary tournament in which the fitter unit's mutant overwrites the loser; fitness is accuracy on 100 sampled training questions. Nine operators in five classes, including generating from a "thinking style", continuing a list of the current population, mutating the mutation-prompts themselves, and crossover (10% probability). — [Promptbreeder, arXiv 2309.16797](https://arxiv.org/html/2309.16797)
- Examples of its text: thinking style "How could I devise an experiment to help solve that problem?"; mutation-prompt "Modify the following instruction creatively, giving some advice on how to solve it:". The authors withheld fitness values from the model because it "did not appear to understand" them in preliminary tests. — [Promptbreeder](https://arxiv.org/html/2309.16797)

**Natural-language answers with a programmatic checker (scored)**
- Mind Evolution (January 2025): evolves natural-language plans. A critic role analyses each candidate plus the evaluator's written feedback, an author role writes a refined version; parents are picked by a softmax over fitness; four islands exchange their top solutions. Default: 10 generations, 4 islands, 5 conversations of 4 turns each, 800 candidates at most. — [Mind Evolution, arXiv 2501.09891](https://arxiv.org/html/2501.09891)
- Results with a small model (Gemini 1.5 Flash), validation success: TravelPlanner 95.6% against 55.6% for best-of-N and 82.8% for sequential revision; Trip Planning 96.2% against 77.2% and 74.4%. Cost per problem was 168 to 406 LLM calls and US$0.17 to US$0.52. — [Mind Evolution](https://arxiv.org/html/2501.09891)
- The critic step and the written feedback were the most important components: the most-ablated configuration reached 46.1% on TravelPlanner against 95.6% for the full system. The authors name reliance on a programmatic evaluator as the main limitation and leave LLM evaluators to future work. — [Mind Evolution](https://arxiv.org/html/2501.09891)

**Open-ended text with no automatic scorer (text)**
- AI co-scientist (February 2025, later revised): Generation, Reflection, Ranking, Evolution, Proximity and Meta-review agents under a Supervisor. Each new hypothesis starts at Elo 1200. Top-ranked hypotheses are compared pairwise through multi-turn simulated debates, lower-ranked ones through single-turn comparisons; matches favour pairs that are similar (from the Proximity agent's graph) and hypotheses that are new or highly ranked. — [Gottweis et al., arXiv 2502.18864](https://arxiv.org/pdf/2502.18864)
- Its Evolution agent uses: grounding in retrieved literature; coherence, practicality and feasibility improvement; inspiration from one or more top hypotheses; combination of the best aspects of several; simplification; and "out-of-box thinking" that moves away from a subset of hypotheses. It "generates new hypotheses; it doesn't modify or replace existing ones", so every change must win its place in the tournament. — [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- The Meta-review agent summarises recurring patterns from reviews and debates into feedback that is "simply appended to [the agents'] prompts in the next iteration". — [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- Evidence: across 203 research goals, best and top-10 Elo rose steadily over ten time buckets with no observed saturation; picking the highest-Elo answer gave 78.4% top-1 accuracy on GPQA diamond; the Evolution agent raised GPQA precision from 70.9% to 75.4%. On 11 goals, experts gave an average preference rank of 2.36 (best of four systems), novelty 3.64 and impact 3.09 out of 5. The paper notes Elo "is auto-evaluated and not based on independent ground truth" and that the expert study was small. — [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- AlphaWrite (June 2025): generate a varied first population of stories (different author styles and themes), rank by pairwise LLM judging with a rubric and Elo, let top stories spawn variants, replace weak ones, repeat. With Llama 3.1 8B, evolved stories were preferred 72% of the time over single-shot stories and 62% over sequential prompting, as judged by an LLM. The authors warn of prompt bias and "creative convergence". Read through a news write-up, not the original post. — [InfoQ on AlphaWrite](https://www.infoq.com/news/2025/06/alphawrite)
- The related open-source repository's example configuration: 10 initial stories, initial Elo 1500, K-factor 32, 50 tournament rounds, keep the top 3, 2 variants per kept story, originals retained, 5 iterations; variety seeded through "mission sets" and "author styles". — [AlphaEvolveWriting README](https://github.com/tamassimonds/AlphaEvolveWriting)
- EvoGens (May 2026): ideas have five fields (title, motivation, description, method, rationale). Mutation strength depends on rank: the top tier gets conservative mutation (closely related literature), the middle tier explorative, the bottom tier radical (semantically distant directions), at temperatures 0.6, 0.8 and 1.0. Crossover pairs the top idea of each embedding cluster with the most distant other parent. Population cap 40, 3 iterations, up to 110 new ideas per iteration. — [EvoGens](https://arxiv.org/html/2605.30961v1)
- EvoGens results against earlier idea generators: novelty 0.40 (best baseline 0.10), diversity 0.55 (baselines 0.17 to 0.42), relative quality 0.21 (best baseline 0.24). Without rank-based mutation novelty fell to 0.06; without crossover to 0.25. No human evaluation; the authors call the scores "heuristic proxies". — [EvoGens](https://arxiv.org/html/2605.30961v1)
- Nova (older, October 2024): 15 seed ideas, each expanded into 10 and cut back to 3 by self-reflection, for 3 rounds (405 ideas), then clustered into 100. Over 80% of its ideas were unique in its comparison; the abstract claims 3.4 times more unique novel ideas than without planning. — [Nova, arXiv 2410.14255](https://arxiv.org/html/2410.14255)
- IDEAgent (July 2026): variation is limited to at most one repair and two refinements per seed, driven by a Critic that turns failed checks into targeted feedback. Repair was needed in 30 of 320 lineages and succeeded in 28; 182 lineages were refined and the refined version replaced the original in 83% of cases. — [IDEAgent](https://arxiv.org/html/2607.22375)

### Inferences
- Parts that transfer to unscored ideas: showing two parents instead of one; mutation by explicit strategy; critic-then-author refinement; adding children without deleting parents; a shared written summary of what the judges keep objecting to; small protected sub-populations.
- Parts that depend on a scorer: very long runs (thousands to millions of samples), softmax selection on numeric fitness, evaluation cascades, and any claim of steady improvement. Where the scorer is an LLM, "improvement" means "improvement in the judge's opinion".
- Pairwise comparison is the standard replacement for a numeric score on text (co-scientist, AlphaWrite, Rainbow Teaming, and the Swiss tournament in section 6).
- The Mind Evolution cost figures (a few hundred small-model calls per problem) show that a team with a few dozen agents and five to ten rounds is operating at the same scale as a published system, not a toy version of one.

### Gaps
- AlphaWrite's original write-up was not read; population size and generation count in the reported experiment are unknown, and its preference figures come from an LLM judge.
- AlphaEvolve's ablation numbers and the features used for its MAP-Elites grid are only in figures. OpenEvolve's default island and grid settings are in a configuration document that was not read.
- FunSearch's island count and ablation numbers are in its supplement, not the main text.
- No study was found that measures an evolutionary loop on ideas against human judgement at scale; the largest human checks were 11 goals (co-scientist) and 25 pairs (IDEAgent).

## 3. Novelty search and open-endedness: how do methods that reward difference from an archive work, and how have LLMs been used to judge interestingness or novelty?

### Takeaway
Novelty search scores a candidate by its distance from its nearest neighbours in an archive and ignores quality; LLM-era systems compute that distance on embeddings or ask a model whether the candidate is "interestingly new" compared with the most similar archive entries. These methods produce the most variety per token, but on their own they drift and add complexity, and an LLM's novelty judgement is unreliable unless it is shown what already exists.

### Cited Findings

**Classical novelty search (older; scored robotics tasks)**
- Novelty is the average distance from an individual to its k nearest neighbours in behaviour space, computed against the current population plus an archive. The archive is filled either with the most novel individuals or with randomly chosen ones; one study used k = 15 and found the archive-filling choice mattered little. — [Doncieux et al. 2020, arXiv 2005.06224](https://ar5iv.labs.arxiv.org/html/2005.06224)
- The stated mechanism: because the reference set changes every generation, recently explored regions lose novelty and the population is pushed elsewhere. — [Doncieux et al. 2020](https://ar5iv.labs.arxiv.org/html/2005.06224)

**LLM as a model of interestingness (older, 2023 to 2024; scored agent training)**
- OMNI (June 2023): curricula based on learning progress get stuck on endless trivial variations (the paper's example is "rearranging silverware in slightly new configurations"). OMNI asks a model, given the tasks the agent already does well, to mark each candidate task as interesting or not; tasks judged boring have their sampling weight multiplied by 0.001. In Crafter the agent learned 14 interesting tasks against 9 with learning progress alone and 3 with uniform sampling. — [OMNI, arXiv 2306.01711](https://arxiv.org/html/2306.01711)
- OMNI's argument for using a model instead of a formula is Goodhart's law: hand-written novelty or interestingness measures get gamed, whereas models trained on human text may have absorbed human notions of what is interesting. The authors add that the same pathology may return if a generator is optimised against the model's judgement. — [OMNI](https://arxiv.org/html/2306.01711)
- OMNI-EPIC (May 2024): an unbounded archive starts from three seed tasks. To propose a task the generator sees a randomly selected archive task plus a set of similar ones (both successes and failures). After generation, a second check compares the new task with "the most similar tasks already in the archive" and asks whether it is interesting (novel, surprising, diverse, worthwhile); if not, it is discarded. Both steps see only part of the archive because of context limits. — [OMNI-EPIC, arXiv 2405.15568](https://arxiv.org/html/2405.15568)
- A 2024 position paper (older) defines open-endedness "through the lens of novelty and learnability" relative to an observer. Abstract only. — [Hughes et al., arXiv 2406.04268](https://arxiv.org/abs/2406.04268)

**Novelty search on text artefacts (2025; text and text-defined artefacts)**
- Lluminate (2025): each generation, summarise the current population; inject one randomly chosen creative strategy into the prompt; create children by varying one artefact, combining several, or writing from scratch; embed each result; score novelty as the average cosine distance to the k = 3 nearest neighbours; keep the most novel. Population 20, 10 children per generation, 30 to 60 generations. — [Lluminate, Joel Simon](https://www.joelsimon.net/lluminate)
- Lluminate findings (reported without exact numbers in the text): strategies "significantly increased" novelty over a no-strategy baseline; variation of existing artefacts produced more diversity than writing from scratch; crossover gave the highest novelty; the population summary "consistently improved performance"; a higher reasoning setting "didn't significantly increase diversity". Novelty was still rising after 60 generations. Tested on shaders, clock web pages and image prompts, not on prose. — [Lluminate](https://www.joelsimon.net/lluminate)
- Wander (November 2025): evolves natural-language image prompts. Mutation prompts include one of 10 "emitters" (for example "Completely change the composition", "Completely change the style", "Add additional elements, while retaining the primary focus"), chosen by a bandit that learns which emitters raise diversity. A candidate replaces the least novel pool member if it is more novel. — [Wander](https://arxiv.org/html/2511.00686v1)
- Wander results over 10 generations: Vendi diversity 3.60 with multiple emitters, 2.95 with one fixed emitter, 2.61 with none; about 24,000 tokens against about 176,000 for Lluminate; a stronger mutator model (o3 instead of GPT-4o-mini) gave 23% higher diversity at 20 generations. — [Wander](https://arxiv.org/html/2511.00686v1)

**Novelty filters inside quality-driven loops**
- ShinkaEvolve (scored) rejects a candidate whose embedding similarity to existing programs on its island exceeds 0.95, optionally asking an LLM whether it is "meaningfully different"; the ablation found the LLM check added only marginal gains over the embedding test, while having no rejection let near-duplicates proliferate. — [ShinkaEvolve](https://arxiv.org/html/2509.19349)
- Rainbow Teaming (older; text) discards a child whose BLEU similarity to its parent exceeds 0.6, which removed about 24% of mutated prompts. — [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- IDEAgent (2026; text) routes by novelty: a candidate that matches only historical ideas is rejected; one that matches exactly one active idea is treated as a new version of that idea; one that matches nothing and scores at least 60 on diversity is admitted if it passes the quality gate. — [IDEAgent](https://arxiv.org/html/2607.22375)
- The AI co-scientist's reviewer rated already-published ideas 6.14 out of 10 for novelty without web search and 2.38 with search. — [AI co-scientist](https://arxiv.org/pdf/2502.18864)

### Inferences
- The by-hand equivalent of the OMNI-EPIC check is one judging call per candidate: "here are the three to five most similar ideas already in the archive; is this one meaningfully different, yes or no, and why?" The coordinator can pick the similar ideas by cell, theme label or embedding.
- Because a model cannot see the whole archive, the comparison set must be the nearest neighbours, not a random sample; otherwise duplicates pass.
- Pure novelty selection suits an early widening phase. It needs a quality gate before anything is kept for good, since neither Lluminate nor Wander checks whether outputs are any good.
- The co-scientist result implies an LLM cannot judge "new to the world" from memory; it can judge "new relative to this list". For product ideas, novelty against the market needs search or human knowledge.

### Gaps
- Lehman and Stanley's original 2011 papers and the "novelty search with local competition" variant were not read directly; the description above comes from a later paper that restates the algorithm.
- Lluminate reports no numeric effect sizes in its text and has no prose or idea domain.
- No study was found measuring how often an LLM's "interestingly new" verdict agrees with human judges on ideas; OMNI-EPIC's 72.7% human agreement figure concerns its task-success detector, not interestingness.

## 4. Island models and niches: what is the evidence that separate sub-populations with occasional migration preserve diversity?

### Takeaway
Direct evidence in LLM systems is thin but consistent: one clean ablation (Mind Evolution) shows islands beating a single population at equal budget, and several 2026 results on ideas show that sharing context across generators destroys variety. Classical work adds that migration which is too frequent, or which always copies the best individual, makes islands identical.

### Cited Findings
- Mind Evolution (2025; scored): at the same budget of 800 candidates on Trip Planning, 87.5% success with the island model against 77.4% without. Its design: after each generation the top 5 solutions of each island are copied to the next island in a cycle; every 3 generations the 2 islands with the lowest mean score are refilled from the global best, and letting the LLM pick 5 diverse candidates out of the top 15 for the refill worked better than taking the top ones. — [Mind Evolution](https://arxiv.org/html/2501.09891)
- FunSearch (older; scored): islands evolve separately; every 4 hours the half of the islands with the lowest best score are wiped and each is reseeded with the best program from a randomly chosen surviving island. The paper says islands help avoid local optima and that supplementary ablations support each component, without giving figures in the main text. — [FunSearch](https://pmc.ncbi.nlm.nih.gov/articles/PMC10794145/)
- ShinkaEvolve (2025; scored): parents and inspirations are drawn from one island; members occasionally migrate, but each island's best program is blocked from migrating. — [ShinkaEvolve](https://arxiv.org/html/2509.19349)
- OpenEvolve's documentation states that "separate populations with periodic migration prevent premature convergence" (a design claim, not a measurement). — [OpenEvolve README](https://github.com/algorithmicsuperintelligence/openevolve)
- DEI (May 2026; scored, Core War programs only): four nodes each run their own archive with a different model and exchange only their champion each round. Merged archive coverage was 80.6% for the mixed-model ensemble, 59.0% for a same-model ensemble and 63.0% for a single node; QD score 45.90, 29.85 and 20.46. The paper contains one internal inconsistency (a figure caption says the same-model ensemble has the highest QD score). — [DEI, arXiv 2605.27130](https://arxiv.org/html/2605.27130)
- IDEAgent (2026; text): a "One-Shot" baseline in which all ideas share one reasoning context scored zero Yield, which the authors attribute to cross-contamination; a sequential baseline that carries memory between ideas scored 0.188, below a fully stateless baseline at 0.250. — [IDEAgent](https://arxiv.org/html/2607.22375)
- A June 2026 paper reports that selection pressure in LLM evolutionary search causes "diversity collapse" and proposes running the search at several temperature levels with exchange between them, modelled on parallel tempering; it claims better quality and diversity at equal validation budget on molecule, equation and algorithm discovery. Abstract only. — [Wang et al., arXiv 2606.10587](https://arxiv.org/abs/2606.10587)
- Classical evidence (older, 2005; scored test functions): in a study varying migration size and interval, the interval was the dominating factor and size played a minor role. Read through a search snippet only. — [Skolicki and De Jong, GECCO 2005](https://gpbib.cs.ucl.ac.uk/gecco2005/docs/p1295.pdf)
- A 2025 paper notes that migrating too frequently can lead to premature convergence, "where the subpopulations become too similar and lose diversity". Read through a search snippet only. — [Żychowski et al. 2025](https://pages.mini.pw.edu.pl/~zychowskia/Publications/DdCPM_PPRAI2025.pdf)

### Inferences
- The team's two earlier sessions were, in these terms, one island with full sharing: every agent had the same brief and nothing else. The IDEAgent and DEI results suggest that giving groups different starting material (sub-brief, strategy set or model) and keeping their context separate is what creates variety; migration then spreads good material without merging the groups.
- A hand-run form: three to five groups, each with its own slice of the grid or its own strategy set; after each round, copy only one to five of each group's best ideas to one neighbouring group; every few rounds, restart the weakest group from a varied selection of the best ideas overall.
- Mind Evolution migrates every generation but only a handful of items, so "occasional" is better read as "small" than "rare".

### Gaps
- Only one LLM-era ablation isolates islands at equal budget, and it is on a scored planning task. No island ablation on open-ended text was found.
- The DEI result mixes two factors (separate archives and different models) and comes from one code domain.
- The classical migration results were not read in full.

## 5. Practical recipe: population size, number of generations, mutation prompts that work on ideas, how to avoid drift into nonsense, and how to stop

### Takeaway
Text-domain systems use small populations (10 to 100 kept items) and few rounds (3 to 10 when a strong model is used), with each child produced from one or two parents under a named strategy and checked before it is kept. Reported gains flatten after about three rounds in idea-generation systems, so a short run with a clear stopping rule matches the evidence.

### Cited Findings

**Sizes and round counts reported**

| System (year) | Kept between rounds | New per round | Rounds | Judge |
|---|---|---|---|---|
| QDAIF stories (2023, older) | 20 to 100 cells | not stated | 2,000 iterations | LLM yes/no log-probabilities |
| QDAIF poetry (2023, older) | 25 cells | not stated | 200 iterations | GPT-4, 1 to 10 |
| Rainbow Teaming (2024, older) | 100 cells | batches of 16 to 64 | 2,000 iterations | pairwise LLM |
| Promptbreeder (2023, older) | 50 units | tournament | 20 to 30 generations | accuracy on data |
| Mind Evolution (2025) | 4 islands | 20 per island | 10 generations | program |
| AlphaEvolveWriting example (2025) | top 3 of 10 | 6 | 5 | pairwise Elo |
| Lluminate (2025) | 20 | 10 | 30 to 60 | embedding novelty |
| Nova (2024, older) | 15 seeds growing to 405 | 3 per idea | 3 | self-reflection, clustering |
| EvoGens (2026) | 40 | up to 110 | 3 | weighted LLM rubric |
| IDEAgent (2026) | 10 active | 1 seed plus at most 3 revisions | 10 seeds | LLM gates |

Sources: [QDAIF](https://arxiv.org/html/2310.13032); [Rainbow Teaming](https://arxiv.org/html/2402.16822); [Promptbreeder](https://arxiv.org/html/2309.16797); [Mind Evolution](https://arxiv.org/html/2501.09891); [AlphaEvolveWriting README](https://github.com/tamassimonds/AlphaEvolveWriting); [Lluminate](https://www.joelsimon.net/lluminate); [Nova](https://arxiv.org/html/2410.14255); [EvoGens](https://arxiv.org/html/2605.30961v1); [IDEAgent](https://arxiv.org/html/2607.22375)

**Depth against breadth**
- Mind Evolution at a fixed 800 candidates: 5 conversations for 10 generations gave 87.5%; 10 conversations for 5 generations gave 82.5%; 4 conversations for 13 generations gave 85.0% (scored). — [Mind Evolution](https://arxiv.org/html/2501.09891)
- IDEAgent: running the stateless baseline for 50 generations instead of 10 raised Yield by about 27% and 62% at the two thresholds, but the structured loop with 10 seeds was still 2.06 and 2.46 times higher (text). — [IDEAgent](https://arxiv.org/html/2607.22375)

**Mutation prompts with evidence, mapped to the team's list**
- Combine two: the co-scientist's "Combination" strategy merges the best aspects of several top hypotheses; Lluminate found crossover gave the highest novelty; EvoGens pairs each cluster's best idea with the most distant other parent, and removing crossover cut novelty from 0.40 to 0.25. — [AI co-scientist](https://arxiv.org/pdf/2502.18864); [Lluminate](https://www.joelsimon.net/lluminate); [EvoGens](https://arxiv.org/html/2605.30961v1)
- Invert an assumption: Lluminate's "Assumption Reversal" (list the domain's assumptions, pick the most fundamental one, reverse it, explore the consequences). — [Lluminate](https://www.joelsimon.net/lluminate)
- Move to another domain: Lluminate's "Forced Connections" (pick a distant, unrelated domain, map its elements onto the primary one, synthesise) and "Conceptual Blending" (select two input spaces, map correspondences, blend selectively); EvoGens' "radical" mutation towards semantically distant directions for its lowest-ranked ideas. — [Lluminate](https://www.joelsimon.net/lluminate); [EvoGens](https://arxiv.org/html/2605.30961v1)
- Make it smaller: the co-scientist's "Simplification" (simplify for easier verification and testing); SCAMPER's "Eliminate" in Lluminate. — [AI co-scientist](https://arxiv.org/pdf/2502.18864); [Lluminate](https://www.joelsimon.net/lluminate)
- Move away on purpose: the co-scientist's "Out-of-box thinking" generates divergent hypotheses by moving away from a given subset; Wander's emitters include "Completely change the composition" and "Completely change the style". — [AI co-scientist](https://arxiv.org/pdf/2502.18864); [Wander](https://arxiv.org/html/2511.00686v1)
- Aim at a named cell: QDAIF's guided rewrite towards a randomly chosen target genre and tone; Rainbow Teaming's one mutation per axis towards a sampled target cell. — [QDAIF](https://arxiv.org/html/2310.13032); [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- Repair from criticism: Mind Evolution's critic-then-author turn; IDEAgent's Critic feeding one repair and up to two refinements. — [Mind Evolution](https://arxiv.org/html/2501.09891); [IDEAgent](https://arxiv.org/html/2607.22375)
- Other generic strategies used in Lluminate: "Distance Association", "Replacement Template", SCAMPER (pick 2 to 3 of substitute, combine, adapt, modify, purpose, eliminate, reverse) and Oblique Strategies cards. Which strategy got used most differed by domain, with no correlation across domains (r = -0.02). — [Lluminate](https://www.joelsimon.net/lluminate)
- Several strategies beat one: Wander's diversity was 3.60 with a rotating set of emitters, 2.95 with a single fixed emitter and 2.61 with none. In the co-scientist, no single generation strategy dominated among correct hypotheses. — [Wander](https://arxiv.org/html/2511.00686v1); [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- Match mutation strength to rank: EvoGens gives its best ideas conservative edits and its worst ideas radical ones. — [EvoGens](https://arxiv.org/html/2605.30961v1)

**What to carry between rounds**
- The elites per cell or niche (QDAIF, Rainbow Teaming, EvoGens); a summary of the current population (Lluminate); a digest of recurring weaknesses from judging, appended to prompts (co-scientist; ShinkaEvolve's scratchpad); a memory of rejected patterns kept as short summaries (IDEAgent). — [QDAIF](https://arxiv.org/html/2310.13032); [Lluminate](https://www.joelsimon.net/lluminate); [AI co-scientist](https://arxiv.org/pdf/2502.18864); [ShinkaEvolve](https://arxiv.org/html/2509.19349); [IDEAgent](https://arxiv.org/html/2607.22375)
- A fixed short format per idea: EvoGens uses five fields; IDEAgent compresses each idea to a five-part signature before comparing. — [EvoGens](https://arxiv.org/html/2605.30961v1); [IDEAgent](https://arxiv.org/html/2607.22375)

**Avoiding drift into nonsense**
- Wander observed that novelty pressure makes outputs "diverge from the initial prompt's core concept" roughly once in five runs and proposed, without testing, an explicit relevance penalty at selection. — [Wander](https://arxiv.org/html/2511.00686v1)
- Lluminate has "no repair mechanism or minimum quality criteria", reports that many generated concepts are impractical, and found the most novel run produced outputs "nearly twice as long on average". — [Lluminate](https://www.joelsimon.net/lluminate)
- Counter-measures in use: children are added and must win a comparison instead of overwriting the parent (co-scientist); a gate on non-obviousness, soundness and clarity with a five-sample soundness panel (IDEAgent); elite replacement only when quality is higher (QDAIF); a critic step with written feedback (Mind Evolution). — [AI co-scientist](https://arxiv.org/pdf/2502.18864); [IDEAgent](https://arxiv.org/html/2607.22375); [QDAIF](https://arxiv.org/html/2310.13032); [Mind Evolution](https://arxiv.org/html/2501.09891)

**Stopping**
- Nova's authors "do not see a continuous increment in generating new ideas after 3 rounds"; without its planning step, unique ideas went from 42.4 to 44.1 between steps 2 and 3. — [Nova](https://arxiv.org/html/2410.14255)
- EvoGens by round: diversity 0.35, 0.53, 0.55; novelty 0.42, 0.38, 0.40. — [EvoGens](https://arxiv.org/html/2605.30961v1)
- With a score-based judge, Rainbow Teaming's archive stopped updating once scores saturated. — [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- Novelty-only search showed no saturation after 60 generations (Lluminate), and the co-scientist's self-assessed Elo showed none either. — [Lluminate](https://www.joelsimon.net/lluminate); [AI co-scientist](https://arxiv.org/pdf/2502.18864)

### Inferences
A simplified loop a coordinator could run by hand, assembled from the cited systems (the assembly and the specific numbers are my suggestion):

1. **Set the grid.** Two categorical axes, 4 to 5 values each (16 to 25 cells). Fix a five-line idea format.
2. **Seed with forced variety.** Round 0 agents each get a different cell and a different strategy or persona instead of the same brief. Three to four groups (islands) each own part of the grid or a different strategy set.
3. **Each round, each generating agent receives:** the brief; one or two current ideas from the archive (two when the operator is "combine"); one target cell; one strategy drawn from a list of 6 to 10; the current digest of judge objections. It returns one idea in the fixed format.
4. **Check each child with separate agents:** (a) is it on-brief and coherent; (b) is it meaningfully different from the three to five most similar archive ideas; (c) if the cell is occupied, compare with the occupant in both orders and replace only on a consistent win.
5. **Keep between rounds:** the grid of elites, a list of rejected patterns in one line each, and a short digest of recurring weaknesses.
6. **Migrate** one to five top ideas between groups each round; restart the weakest group every two to three rounds from a varied pick of the overall best.
7. **Stop** after 3 to 5 rounds, or earlier when the share of children that enter the archive falls below a set level (for example one in ten) for a full round.
8. **Hand the whole grid to people**, not a top-10 list.

- Rough cost for 25 cells with 30 generating agents over 5 rounds: 150 candidates, each needing about 3 to 4 checking calls, so about 600 to 750 small calls in total. This is comparable to Mind Evolution's 168 to 406 calls per problem.
- "Push to an extreme" has no direct tested equivalent in the sources; the closest are Wander's "completely change" emitters and SCAMPER's "modify". It is reasonable to include but untested.
- Idea-generation systems flatten at about three rounds because they have no reliable signal to climb; systems that run longer either have a program for a scorer or measure novelty alone.

### Gaps
- No source compares mutation strategies on product or feature ideas; strategy rankings differed by domain in the one study that looked.
- No source gives a validated stopping rule for unscored text; the rule in step 7 is an inference from saturation curves.
- No source measures the ideal number of parents for natural-language ideas; the "two beats one" finding is from code (FunSearch).
- Whether small models suffice as mutators is mixed: AlphaWrite reported gains with an 8B model; Wander found a stronger model gave 23% more diversity; IDEAgent reported that its pilot ideator choice changed mean soundness from 66.4 to 91.8.

## 6. Known failure modes (judge bias steering the search, loss of diversity, cost growth) and how authors counter them

### Takeaway
The three recurring failures are: the judge becomes the target (position bias, saturating scores, reward hacking at the top of the scale, invented novelty); selection plus shared context collapses the population onto a few themes; and judging cost grows faster than generation cost. The tested counters are pairwise judging in both orders, similarity filters before judging, separate judges from generators, cheap checks first, and people making the final cut.

### Cited Findings

**Judge bias steering the search**
- LLM judges show "position, verbosity, and self-enhancement biases" and "limited reasoning ability", though strong judges reached over 80% agreement with humans on chat answers (older, 2023). — [Zheng et al., arXiv 2306.05685](https://arxiv.org/abs/2306.05685)
- On research ideas, LLM judges agree with experts less than experts agree with each other: the best LLM ranker reached 53.3% against 56.1% human-to-human consistency, and other LLM judges scored 43.3% to 51.7%. Of the 49 ideas picked by the AI ranker and by a human reranker, only 17 overlapped (older, 2024). — [Si et al., arXiv 2409.04109](https://arxiv.org/html/2409.04109)
- IDEAgent's two external judge models agreed only moderately: weighted kappa 0.455 for non-obviousness, 0.268 for soundness, 0.210 for feasibility, 0.424 for diversity (2026). — [IDEAgent](https://arxiv.org/html/2607.22375)
- Reward hacking at the top: in QDAIF the correlation between AI-judged and human-judged quality dropped in the highest fitness range (0.995 to 1). Embedding-based feedback was worse, with top texts converging on the wording of the query. — [QDAIF](https://arxiv.org/html/2310.13032)
- Score saturation and judge overfitting: Rainbow Teaming's score-based variant got higher success by the scoring model's own measure but lower by GPT-4's, and stopped improving once the score maxed out. — [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- Position bias in tournaments: the co-scientist found a "second player advantage" with a simple comparison prompt, reduced by a multi-turn debate prompt. — [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- Invented novelty: without search, the co-scientist's reviewer rated published ideas 6.14 out of 10 for novelty. — [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- Goodhart risk when a generator is optimised against a model of interestingness. — [OMNI](https://arxiv.org/html/2306.01711)

Counters reported:
- Pairwise comparison instead of absolute scores, repeated with positions swapped and decided by majority. — [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- A Swiss-system tournament (5 rounds, each idea paired with others of similar running score), which widened the gap between top and bottom groups as rounds increased. — [Si et al.](https://arxiv.org/html/2409.04109)
- Different models for generating and judging, and averaging two judges. — [IDEAgent](https://arxiv.org/html/2607.22375)
- Ensembles of evaluators with uncorrelated blind spots (proposed, not tested). — [QDAIF](https://arxiv.org/html/2310.13032)
- Giving the reviewer a search tool, which cut the false novelty score to 2.38. — [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- Hiding numeric fitness from the mutating model, and telling it a list was in descending order when it was ascending to stop it copying the last entry. — [Promptbreeder](https://arxiv.org/html/2309.16797)
- Human final selection: the co-scientist keeps experts in the loop and Si et al. used human reranking. — [AI co-scientist](https://arxiv.org/pdf/2502.18864); [Si et al.](https://arxiv.org/html/2409.04109)

**Loss of diversity**
- Plain repeated sampling saturates: of 4,000 seed ideas generated per topic, only about 200 (5%) were non-duplicates at a 0.8 embedding-similarity threshold, and the share of new ideas per batch fell steadily (older, 2024). — [Si et al.](https://arxiv.org/html/2409.04109)
- Generating everything in one shared context gave zero Yield in IDEAgent's comparison. — [IDEAgent](https://arxiv.org/html/2607.22375)
- Selection pressure causes "diversity collapse" in LLM evolutionary search (abstract only). — [Wang et al. 2026](https://arxiv.org/abs/2606.10587)
- Without its similarity filter, Rainbow Teaming's archive had self-BLEU 0.79 against 0.42 with the filter (the unfiltered archive scored slightly higher on attack success, 0.99 vs 0.92). — [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- Without novelty rejection, near-duplicates proliferated in ShinkaEvolve. — [ShinkaEvolve](https://arxiv.org/html/2509.19349)
- Unprompted model output is homogeneous: Lluminate's baselines repeated the same motifs (one radial clock format, one colour palette). — [Lluminate](https://www.joelsimon.net/lluminate)
- AlphaWrite's authors warn of "creative convergence"; the co-scientist paper warns of "homogenizing research directions". — [InfoQ on AlphaWrite](https://www.infoq.com/news/2025/06/alphawrite); [AI co-scientist](https://arxiv.org/pdf/2502.18864)

Counters reported:
- One elite per cell and sampling that favours weak or empty cells. — [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- Similarity filters before judging (BLEU 0.6; embedding 0.95). — [Rainbow Teaming](https://arxiv.org/html/2402.16822); [ShinkaEvolve](https://arxiv.org/html/2509.19349)
- Islands with small migration, and blocking the best item from migrating. — [Mind Evolution](https://arxiv.org/html/2501.09891); [ShinkaEvolve](https://arxiv.org/html/2509.19349)
- A parent-selection bonus for items with few children. — [ShinkaEvolve](https://arxiv.org/html/2509.19349)
- Rotating mutation strategies. — [Wander](https://arxiv.org/html/2511.00686v1)
- Mixing models. — [DEI](https://arxiv.org/html/2605.27130)
- Selecting for complementarity to the rest of the set instead of quality alone (VendiEvolve, 2026; search snippet only). — [VendiEvolve](https://genaicreativity.org/icml2026/files/40/40_paper.pdf)
- Counting only mutually distinct ideas in the success measure. — [IDEAgent](https://arxiv.org/html/2607.22375)

**Cost growth**
- FunSearch needed about a million samples; AlphaEvolve cut this to thousands by using stronger models and richer prompts. — [FunSearch](https://pmc.ncbi.nlm.nih.gov/articles/PMC10794145/); [AlphaEvolve](https://arxiv.org/html/2506.13131)
- Tournaments are "computationally intensive"; the co-scientist limits cost by giving full debates only to top-ranked hypotheses and single-turn comparisons to the rest, and by prioritising matches between similar and new items. — [AI co-scientist](https://arxiv.org/pdf/2502.18864)
- Token use for the same task varied sevenfold between methods (about 24,000 for Wander against about 176,000 for Lluminate), mainly from regenerating large outputs and summaries each generation. — [Wander](https://arxiv.org/html/2511.00686v1)
- IDEAgent's cost per topic that yielded at least one idea at the strict threshold was US$6.52, against US$5.07 for the stateless baseline and US$16.32 for the Nova-style baseline; for at least two such ideas, US$22.00 against US$130.56. — [IDEAgent](https://arxiv.org/html/2607.22375)
- Sequential revision cost five to nineteen times more per problem than Mind Evolution (US$2.53 to US$3.23 against US$0.17 to US$0.52) because every turn re-reads a growing context. — [Mind Evolution](https://arxiv.org/html/2501.09891)
- Cheap checks first: AlphaEvolve's evaluation cascade and Rainbow Teaming's similarity filter both run before the expensive step. — [AlphaEvolve](https://arxiv.org/html/2506.13131); [Rainbow Teaming](https://arxiv.org/html/2402.16822)
- Lluminate suggests evolving short concept descriptions and expanding only the final ones. — [Lluminate](https://www.joelsimon.net/lluminate)

### Inferences
- The Si et al. result (5% unique out of 4,000) is the measured version of what the team saw: a single brief sampled in parallel has a low ceiling on distinct ideas, and adding agents mostly adds duplicates. Structure, not head-count, is what the 2026 systems change.
- Judging is the bottleneck for unscored ideas. With LLM-to-human agreement at or below human-to-human agreement, the LLM judge is good enough to reject duplicates and broken ideas and to keep a grid filled, but not to choose winners.
- The safest division of labour that follows from the evidence: models widen, deduplicate, label and repair; people choose among cells.
- Keeping ideas short during the loop (five lines) controls both cost and the length-with-novelty confound that Lluminate observed.

### Gaps
- No source quantifies self-preference bias (a model favouring its own output) inside an evolutionary loop; Zheng et al. name it only in general.
- No source reports what happens to judge bias over many rounds on product or creative ideas, for example whether the archive drifts towards what the judge model finds impressive.
- Rainbow Teaming's cost appendix was not read; the co-scientist gives no token or dollar cost.
- VendiEvolve and the parallel-tempering paper were seen only as an abstract or snippet, so their effect sizes are unknown.
