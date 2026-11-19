# Creativity lenses for individual agents, and briefing and orchestrating many parallel subagents

Notes compiled 19 November 2026. Findings dated before 2025 are marked "older". Evidence labels used throughout:

- **[A] Experimental support**: controlled human or LLM experiments, reviews or meta-analyses were found.
- **[B] Mixed or thin**: a few experiments with conflicting, small or indirect results.
- **[C] Popular, lightly tested**: no controlled evidence found in this research.

Where a finding comes from a search-result summary and the full text was not opened, it is marked "(summary only)".

## 1. Methods catalogue: what each method is, the evidence, and a one-paragraph agent instruction

### Takeaway
Only a few of the eleven lenses have direct experimental backing (analogy with a distant source, constraints and narrow problem scope, lead or extreme users, TRIZ to a modest degree); SCAMPER and Six Thinking Hats have mixed results, and morphological grids, worst-idea, jobs-to-be-done, design fiction, backcasting and first principles are popular but had no controlled tests that this research could find. Creativity training as a whole has a real but smaller effect than usually claimed (about 0.3 SD after correcting for publication bias), so the lenses are better treated as a way to send agents to different places than as a way to make any one agent more creative.

### Cited Findings

**Background: how well do creativity techniques work at all?**
- A 2024 Psychological Bulletin meta-analysis of 169 creativity-training studies found an unadjusted effect of 0.53 SD, falling to 0.29–0.32 SD after adjusting for strong publication bias; the authors conclude training may be less effective than previously thought (summary only). — [White Rose repository](https://eprints.whiterose.ac.uk/209749/)
- Older meta-analysis (Ma; 202 effect sizes): the Osborn-Parnes Creative Problem Solving programme and synectics-based (analogy) training had the largest effects; single techniques such as SCAMPER and incubation had among the smallest (summary only; older). — [NCCU repository](https://ah.lib.nccu.edu.tw/bitstream/140.119/4636/1/922413H004004.pdf)
- Older (2010): in a controlled experiment, a hybrid structure (individuals work alone first, then meet) generated more ideas, better ideas, and better discernment of the best ideas than teams; building on others' ideas, a common brainstorming rule, was counterproductive. — [Girotra, Terwiesch and Ulrich, Mack Institute](https://mackinstitute.wharton.upenn.edu/2010/idea-generation-and-the-quality-of-the-best-idea/)

**SCAMPER [B]** (checklist of seven transformations: Substitute, Combine, Adapt, Modify, Put to other use, Eliminate, Reverse)
- Human evidence is mixed: among the smallest effects in Ma's meta-analysis (above); a design-by-analogy study found SCAMPER did not reduce design fixation but did raise the quantity of novel ideas, while WordTree (an analogy method) reduced fixation (summary only; 2016, older). — [AI EDAM, Cambridge](https://www.cambridge.org/core/product/2DD81FEE8ED682F6DFF415BF2948EFA6)
- Chulvi et al. (2013, older) ran 16 design teams (7 SCAMPER, 7 TRIZ, 1 brainstorming, 1 no method) and report that novelty and utility differed between methods; the repository page does not state the direction, and the groups are small. — [Javeriana repository](https://perfilesycapacidades.javeriana.edu.co/es/publications/influence-of-the-type-of-idea-generation-method-on-the-creativity/)
- LLM evidence (May 2026 preprint, embedding metrics only): a SCAMPER prompt scored mean novelty 0.494 versus 0.468–0.474 for control prompts, but its top-5 novelty (0.554) was below control (0.571–0.586), and it produced about half as many ideas (11.7 versus 19–24). — [IDEAFix, arXiv 2606.00875](https://arxiv.org/html/2606.00875)

**TRIZ and contradiction principles [B, leaning A]** (state a contradiction, then resolve it with one of 40 inventive principles instead of compromising)
- Students improved ideation novelty, variety and quality when using TRIZ in addition to brainstorming (ASEE 2012, older; summary only). — [Vargas Hernandez and Okudan Kremer](https://peer.asee.org/21369.pdf)
- LLM evidence: of the classic methods tested in IDEAFix, TRIZ came closest to the top novelty scores; the best TRIZ variant reached mean novelty 0.542 and rarity 0.289 versus 0.468–0.474 and 0.235–0.237 for control, with fluency of 9–12 ideas. — [IDEAFix, arXiv 2606.00875](https://arxiv.org/html/2606.00875)
- AutoTRIZ (March 2024) automates TRIZ with an LLM but is a tool paper and reports no comparative novelty or diversity results (summary only). — [arXiv 2403.13002](https://arxiv.org/html/2403.13002v1)

**Morphological analysis / attribute grids [C for humans; indirect LLM support]** (split the problem into independent attributes, list values for each, then combine)
- Sources located for human use were descriptive only (the method "can reveal combinations that might not be obvious when thinking linearly"), with no measured novelty or variety results. — [descriptive example](https://mindmappingsoftwareblog.com/morphological-analysis/)
- LLM analogue 1: Luminate (CHI 2024) has the model first generate the dimensions of a design space and then generate responses across them; evaluated with 8 professional writers, not with a diversity benchmark (summary only). — [arXiv 2310.12953](https://arxiv.org/abs/2310.12953)
- LLM analogue 2: AttrPrompt (NeurIPS 2023, older) found simple class-conditional prompts limit diversity and inherit model biases; prompts with assigned, varied attributes matched the simple prompt's downstream performance using 5% of the data (summary only). — [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/ae9500c4f5607caf2eff033c67daa9d7-Paper-Datasets_and_Benchmarks.pdf)

**Synectics and forced analogy [A for originality, with a usefulness cost]** (map a mechanism from another domain onto the problem)
- Synectics-based training had among the largest effects in Ma's meta-analysis (above).
- Franke, Poetz and Schreier (2014, older; 213 problem solvers from roofing, carpentry and inline skating): solvers from analogous markets gave substantially more novel solutions with lower potential for immediate use; the effect grew with distance and was strongest in the upper tail of novelty (summary only). — [Management Science](https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.2013.1805)
- 2026 experiment (140 humans, seven LLMs, 1,002 raters): see section 2 for numbers; humans transferred surface features, LLMs transferred structural and functional properties. — [Liu et al., arXiv 2603.19087](https://arxiv.org/html/2603.19087)

**Random stimulus / lateral thinking [B]** (force a connection from an unrelated word or object)
- In Liu et al. (2026) the source was randomly assigned from 26 options (cactus, octopus, pickle and so on); this raised human originality (mean 2.93 versus 2.57 for a user-need framing; b = 0.36) but gave no average gain for LLMs unless the pair was semantically distant. — [arXiv 2603.19087](https://arxiv.org/html/2603.19087)
- In LLM research ideation (May 2026 preprint), cross-domain retrieved seeds beat no retrieval (60% versus 40% pairwise novelty wins) and same-domain retrieval (67% versus 30%), but only matched a random-seed control (47% versus 53%) (summary only). — [arXiv 2605.11532](https://arxiv.org/pdf/2605.11532)
**Assumption reversal and "worst possible idea" [C]**
- A 2020 design-education study of a related "wrong theory protocol" reports divergent, empathetic ideas, and notes that facilitation of the bad-ideas method can harm creativity; it is not a controlled test of reverse brainstorming (summary only; link-to-paper mapping not verified). — [NSF public access](https://par.nsf.gov/servlets/purl/10208404)
- Nearest LLM evidence: the "AI-specific" prompt family in IDEAFix, described as having the model generate ideas, categorise them, then generate outside those categories ("category negation"), was among the highest on top-end novelty and rarity; its best variant had the highest figures in the table (novelty 0.525, top-5 0.633; rarity 0.294, top-10 0.397). — [IDEAFix](https://arxiv.org/html/2606.00875)

**Six Thinking Hats [B]** (one thinking mode at a time: facts, feelings, caution, benefits, alternatives, process)
- Vernon and Hocking (2014, older): six hats and a "six good men" question technique both raised fluency versus controls, more robustly for six men; the same literature notes self-reported idea generation after hats training showed no benefit and that claims for creative thinking "have yet to be clearly and empirically supported" (summary only). — [Canterbury repository](https://repository.canterbury.ac.uk/download/8e7677d0510491997b3795c09d971b5de34ec0862ff460901ef5a574a2c7580d/186548/12778a_Vernon%20and%20Hocking_Thinking%20hats%20and%20good%20men_FAV.pdf)
- A 2017 follow-up (Thinking Skills and Creativity, vol. 26) found the structured techniques less effective on an ill-defined problem-finding task; a 2019 two-experiment paper (Göçmen and Coşkun) found the green hat produced more unique ideas than yellow or red (summary only; these two links came from the search results and their mapping to the two papers was not verified). — [CORE copy 1](https://core.ac.uk/download/287638219.pdf); [CORE copy 2](https://core.ac.uk/download/287636632.pdf)

**Jobs-to-be-done and extreme users [A for lead/extreme users; C for JTBD]**
- Lead users (Lilien et al., 2002, older; natural experiment at 3M): funded lead-user ideas had forecast year-5 sales of $146 million, more than 8 times traditional projects; the sample was 5 lead-user ideas versus 42 others, and the figures are forecasts, not realised sales. The method deliberately includes users in "advanced analog" markets with the need in a more extreme form. — [Management Science record](https://econpapers.repec.org/RePEc:inm:ormnsc:v:48:y:2002:i:8:p:1042-1059)
- No controlled evidence on jobs-to-be-done was found. The nearest test is the "user-need" condition in Liu et al. (2026): need-first ideas by humans were less original than cross-domain ideas (2.57 versus 2.93), but the top need-first ideas matched LLM ideas on utility and feasibility, whereas the most original cross-domain human ideas were less useful and less feasible. — [arXiv 2603.19087](https://arxiv.org/html/2603.19087)

**Constraint-based creativity [A]**: see section 2.

**Design fiction and backcasting [C]**
- Sources found were method descriptions or small student workshops with no comparison group or originality measure. — [Design Society workshop paper](https://asiachapter.designsociety.org/download-publication/46811/WHAT+IF+XR+IS+FULLY+UTILISED+IN+DESIGN+EDUCATION%3F+PRELIMINARY+RESULTS+FROM+A+PARTICIPATORY+DESIGN+FICTION+STUDY)
- Nearest LLM evidence: "prospective scenario" prompts in IDEAFix had mean novelty 0.495–0.513 (above control 0.468–0.474) but top-5 novelty 0.549–0.576 (not above control) and only about 10 ideas per prompt. — [IDEAFix](https://arxiv.org/html/2606.00875)

**First-principles decomposition [C]**
- No source found; see Gaps. The method is included in the catalogue on the strength of its popularity only.

**Cross-cutting LLM finding that should shape every lens instruction**
- IDEAFix: all method-inspired prompts beat control prompts with statistical significance, but "no single method simultaneously maximizes idea fluency, novelty, rarity and diversity", and novelty gains tracked how explicit the divergence instruction was ("wild", "unconventional", "think outside the box") more than the method's structure. — [IDEAFix](https://arxiv.org/html/2606.00875)

### Inferences

Draft one-paragraph instructions (my wording, not from sources; `{GOAL}` is the shared goal, `{N}` the idea count). Each should be preceded by the same short goal statement and followed by the same output contract (section 5).

- **SCAMPER**: "State in one line the most obvious way {GOAL} is met today. Apply all seven operators in turn: substitute a part, combine with something else, adapt from elsewhere, magnify or shrink, put to another use, eliminate, reverse or reorder. Give one idea per operator that changes how the thing works, not how it looks. Label each idea with its operator. Finish with two extra ideas from Eliminate and Reverse, pushed as far as they go."
- **TRIZ**: "Write three contradictions inside {GOAL}, each as 'we want X to improve, but then Y gets worse'. Do not compromise. Resolve each one so both sides improve, using a named principle: segmentation, taking out, prior action, the other way round, intermediary, self-service, turning harm into benefit, cheap short-lived copy, nesting, or separating the two demands in time, in space or by condition. Name the principle with each idea."
- **Morphological grid**: "You own one cell: {USER} x {SITUATION} x {MECHANISM}. Generate only inside it. First list three sub-variants of each attribute, then combine them and pick the {N} least obvious combinations. Each idea must name its combination. If a combination looks absurd, keep it and say what would have to be true for it to work."
- **Forced analogy (Synectics)**: "Your source domain is {DOMAIN}, assigned to you and deliberately far from {GOAL}. List five mechanisms by which that domain solves its own problems (how it works, not how it looks). Map each onto {GOAL} as 'In {DOMAIN}, A does B to get C; here that becomes ...'. Transfer the function, never the surface feature. Add one idea written from the point of view of the product itself."
- **Random stimulus**: "You were dealt three words at random: {W1}, {W2}, {W3}. You may not swap them. For each, list four properties or behaviours, then force a link from each property to {GOAL}. Keep the links that feel strained. Report the {N} most surprising ideas and the word and property each came from."
- **Assumption reversal and worst idea**: "List ten things everyone assumes about how {GOAL} must be done (who pays, who does the work, when, in what order, what is included). Reverse each and draw one workable idea from the reversal. Then write five deliberately terrible ideas and, for each, the kernel that could be flipped into a good one."
- **Six Hats (one hat per agent)**: "You wear only the {HAT} hat. Green: produce alternatives and provocations, no evaluation. Black: list ten ways current solutions fail people, then one idea per failure. Red: start from what people feel before, during and after, and design for the feeling. Do not switch hats."
- **Jobs-to-be-done with an extreme user**: "Your user is {EXTREME USER} in {SITUATION}. Write the job as 'When ..., I want to ..., so I can ...', with the practical, emotional and social sides. List what they use today, including workarounds and doing nothing. Propose {N} ideas that do the job far better for this user, then mark which would carry over to ordinary users."
- **Hard constraint**: "Achieve {GOAL} under this non-negotiable limit: {CONSTRAINT} (for example no screen, no budget, ten seconds, no internet, one tenth of the price, no staff). Ideas that break the limit are invalid. Give {N} ideas, then say which keep their value if the limit is lifted."
- **Design fiction and backcasting**: "It is {YEAR} and {GOAL} was achieved in a way that surprised today's experts. Write a three-sentence artefact from that world (a headline, a review, a complaint). Work backwards: what had to exist five years, two years and six months earlier? Submit the earliest step that could start now. Do this for {N} different futures, one of them strange."
- **First principles**: "Ignore existing solutions. Break {GOAL} into what must be true: the outcome, for whom, and the steps and costs that cannot be removed. Ask 'why is this needed?' of each step until you reach something irreducible. Rebuild from there: ideas that delete a step, change who performs it, or cut the largest cost tenfold."

Other inferences:
- Because explicit divergence wording drove novelty more than method structure in IDEAFix, each lens paragraph should carry one plain sentence asking for unconventional ideas; the method's main job is to send the agent somewhere different from its neighbours.
- Method prompts roughly halved the number of ideas per call in IDEAFix, so each brief needs an explicit idea count.
- Lenses that raise originality at a usefulness cost (far analogy, random stimulus) and lenses that keep usefulness (user need, near analogy) are complements; a mixed portfolio with a later selection pass fits the evidence better than choosing one.
- Hats other than green are evaluative; they fit a later critique pass better than a generation pass.

### Gaps
- Direction of the Chulvi et al. (2013) TRIZ-versus-SCAMPER result, and a reported 2024 comparison of TRIZ, SCAMPER, KJ and brainstorming, could not be read (PDF not extractable).
- No controlled evidence located for morphological analysis in humans, reverse brainstorming, jobs-to-be-done, design fiction, backcasting or first-principles ideation. Absence here means "not found in roughly 50 searches and fetches", not "does not exist".
- Design heuristics (the 77-card set) were not checked. A human random-word experiment (Belski et al., 2014) surfaced in a search summary, but neither its results nor a reliable link were retrieved.
- IDEAFix did not publish its prompt texts in the portion read, used embedding distance instead of human judges, and is an unreviewed preprint.

## 2. What research says about constraints and creativity, and about analogical distance

### Takeaway
Moderate constraints and narrower problem statements tend to raise originality, and only excessive constraint hurts (an inverted U). Far analogies raise originality, especially at the top end, but tend to lower immediate usefulness, and one large field study found near sources predicted the ideas experts shortlisted; for strong LLMs the gain from a cross-domain source appears only when the source is truly distant.

### Cited Findings

**Constraints**
- Acar, Tarakci and van Knippenberg (Journal of Management, 2019; older) reviewed research across management fields and propose an inverted U-shaped effect of constraints on creativity and innovation, working through motivational, cognitive and social mechanisms. — [Erasmus repository](https://pure.eur.nl/en/publications/creativity-and-innovation-under-constraints-a-cross-disciplinary-/)
- The same authors, summarising 145 empirical studies: individuals, teams and organisations "benefit from a healthy dose of constraints. It is only when the constraints become too high that they stifle creativity and innovation." — [HBR, 22 Nov 2019](https://hbr.org/2019/11/why-constraints-are-good-for-innovation)
- Haught-Tromp ("Green Eggs and Ham hypothesis", published 2016–17; older): in two rhyme-writing experiments, a required-word constraint produced more creative output, with a carry-over effect after the constraint was removed. — [Rider University PDF](https://www.rider.edu/sites/default/files/docs/tromp_haught-tromp_PACA_2016.pdf)
- Rietzschel, Nijstad and Stroebe (2014, older): a narrow problem led to more original ideas than a broad one with no change in the number of ideas; originality instructions did not change quantity; problem scope did not affect which ideas people selected. — [Utrecht University portal](https://research-portal.uu.nl/en/publications/effects-of-problem-scope-and-creativity-instructions-on-idea-gene/)
- A press piece distinguishes suggestive constraints, which point toward one path, from prohibitive constraints, which block one path and leave the rest open (summary only; the researcher attribution in the search summary was not verified). — [VCU News, 2019](https://news.vcu.edu/article/get_back_inside_the_box_thats_where_youre_most_creative)

**Analogical distance**
- Chan, Dow and Schunn (CSCW 2014 companion; older): 2,344 concepts and 4,557 inspirations from 2,452 contributors across 12 OpenIDEO challenges, 241 shortlisted by expert panels. "Surprisingly, we find that innovators who cite conceptually near sources of inspiration achieve a higher success rate than those who prefer far sources." They describe prior evidence as mixed, with most earlier studies having 12 or fewer people per cell and 30–60 minute sessions. — [CMU PDF](https://www.cs.cmu.edu/~spdow/files/conceptualDistance-CSCW2014.pdf)
- The journal version (Design Studies) adds that citing any source was linked to more creative ideas, with closer sources linked to higher quality (summary only). — [Author page](https://spdow.ucsd.edu/publication/do-the-best-design-ideas-really-come-from-conceptually-distant-sources)
- Franke, Poetz and Schreier (2014): analogous-market solvers were more novel but less immediately usable; novelty rose with distance and most in the upper tail. — [Management Science](https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.2013.1805)
- Liu, Dubova, Conklin, Harada and Griffiths (arXiv, March 2026, revised September 2026): greater semantic distance predicted originality for humans (beta = .10) and LLMs (beta = .18). For o3 and Claude Sonnet 4 the cross-domain benefit was null over all pairs (b = 0.02, p = .64), significant for the most distant half (b = 0.12) and the most distant tenth (b = 0.24). Among the top 10% most original ideas, human cross-domain ideas were less useful, less investment-worthy and less feasible. — [arXiv 2603.19087](https://arxiv.org/html/2603.19087)
- Sio, Kotovsky and Cagan (2015 meta-analysis of 43 design studies; older): examples made people produce more example-related ideas and fewer categories, though more novel ones; benefits were largest with fewer and less common examples, and a single uncommon example helped most (summary only). — [Design Studies record](https://eld.bl.uk/catalog/100081707150_0x000001)

### Inferences
- A hard, single, prohibitive constraint per agent ("no screen", "no budget") is the form best supported; stacking several constraints on one agent risks the falling side of the inverted U.
- Narrowing each agent's problem scope is itself a constraint with experimental support for originality, which is a second argument for cell-based assignment (section 4).
- Assign analogy sources at two distances on purpose: a few near sources (adjacent products and industries) to protect usefulness, and more far sources (biology, logistics, games, rituals) to feed the novel tail. For strong models, near sources add little originality, so far sources must be truly remote.
- Instruct agents to transfer mechanism, not appearance; the 2026 study found structure transfer predicted utility.

### Gaps
- The full Acar et al. review was not read, so its taxonomy of constraint types and moderators is not reported here.
- Mehta and Zhu's scarcity experiments surfaced only through a blog and are left out as unverified.
- No LLM experiment that varies the number or severity of constraints per prompt was found.

## 3. Have these methods been tested with LLMs, and did diversity or novelty rise?

### Takeaway
Yes, but the direct tests are few and recent: a 2024 Wharton study of 35 prompts, a 2026 benchmark of 25 method-inspired prompts across five models, and 2026 studies of cross-domain analogy. They agree that identical prompts collapse onto a narrow idea set, that structured or stepwise prompts raise diversity somewhat, that no single method wins on every measure, and that handing the model generic creativity advice or example ideas does not help and can hurt.

### Cited Findings
- Meincke, Mollick and Terwiesch (January 2024, older; GPT-4, temperature 0.7, product ideas for students, 10 sessions of 100 ideas per prompt). Mean within-pool cosine similarity (lower is more diverse): human group 0.243; chain-of-thought 0.255; "creative entrepreneur" persona 0.348; Steve Jobs persona 0.368; base prompt 0.377; Harvard Business Review brainstorming article supplied 0.387; Stanford design-thinking article supplied 0.392; hybrid brainstorming 0.393; previous top ideas supplied 0.403; seven successful example ideas supplied 0.428; telling the model the cosine similarity 0.432. — [Mack Institute PDF](https://mackinstitute.wharton.upenn.edu/wp-content/uploads/2024/02/for-web-AI-idea-variance.pdf)
- Their chain-of-thought prompt was: list 100 short titles; then check the list and "modify the ideas as needed to make them bolder and more different. No two ideas should be the same"; then write descriptions. About 15% of runs skipped the second step and were removed. It raised the estimated number of unique ideas from about 3,700 to 4,700; its advantage was strongest between 100 and 500 ideas and vanished after about 750 in one session. — [Mack Institute PDF](https://mackinstitute.wharton.upenn.edu/wp-content/uploads/2024/02/for-web-AI-idea-variance.pdf)
- A secondary write-up reports the authors found low overlap between pools from different prompts and suggest combining small pools from different strategies (not confirmed in the pages read). — [Substack commentary](https://aiblewmymind.substack.com/p/how-to-make-gpt-4-break-its-repetitive)
- Si, Yang and Hashimoto (September 2024, older): of 4,000 seed ideas generated per research topic, "there are only 200 non-duplicate unique ideas" (about 5%, at a 0.8 similarity threshold); the share of new ideas in each batch keeps falling and the total plateaus. — [arXiv 2409.04109](https://arxiv.org/html/2409.04109)
- Deng, Brucks and Toubia (arXiv, February 2026, revised November 2026): ideas from independent LLM sessions are less diverse than ideas from independent humans, for two reasons: LLMs "aggregate knowledge into a unified distribution" where humans are partitioned, and LLMs fixate within a session as humans do. Ordinary-person personas improve partitioning but amplify fixation; chain-of-thought reduces fixation; the two combined gave the highest diversity, above humans. — [arXiv 2602.20408](https://arxiv.org/abs/2602.20408)
- IDEAFix (30 May 2026 preprint; Llama-3.1-70B, Qwen3-30B, Gemini 2.5 Flash, GPT-4o, Grok 4.1 fast; 81 design briefs; 25 prompts): per-family results are in section 1. Brainstorming-style and "category negation" prompts had the highest top-end novelty and rarity, TRIZ came close, and C-K theory and SCAMPER did not reliably raise novelty. Diversity within a list moved little (0.42–0.49 across all prompts). Outputs from different providers stayed in "a shared semantic space, leading to persistent homogenization". Analogies, personas and morphological grids were not tested. — [arXiv 2606.00875](https://arxiv.org/html/2606.00875)
- Analogies with LLMs: Liu et al. (2026) in section 2; a May 2026 preprint reports an analogical-reasoning pipeline that draws on consistently more distant domains and scores highest on novelty across three LLMs (summary only). — [arXiv 2605.11258](https://arxiv.org/pdf/2605.11258)
- Older (2023): LLM-generated cross-domain analogies were often judged helpful for reformulating design problems (summary only). — [Ding et al., arXiv 2302.12832](https://arxiv.org/pdf/2302.12832v2.pdf)
- Verbalized Sampling (October 2025, revised July 2026): asking for several responses with their probabilities ("Generate 5 jokes about coffee and their corresponding probabilities") "increases diversity by 1.6-2.1x over direct prompting" in creative writing; more capable models benefit more. — [arXiv 2510.01171](https://arxiv.org/abs/2510.01171)
- LLM Discussion (2024, older): several LLM instances with assigned roles discussing in three phases beat single-LLM and other multi-LLM baselines on originality, elaboration, fluency and flexibility (summary only). — [arXiv 2405.06373](https://arxiv.org/html/2405.06373v3)
- A 2026 survey describes collapse on two axes: repeated samples from one model converge, and independently trained models converge on similar responses (summary only). — [arXiv 2604.01504](https://arxiv.org/pdf/2604.01504)

### Inferences
- The earlier sessions' collapse into about a dozen themes is the expected result of one identical brief: Si et al. saw 95% duplication and Deng et al. explain it as every session sampling one shared distribution.
- The two best-supported LLM-specific moves are cheap to add to every brief: a self-check step ("list titles, make them bolder and more different, then describe") and a distinct partition cue per agent (persona, cell or lens).
- Supplying articles about creativity (HBR, design thinking) made diversity slightly worse than the base prompt in 2024; describing a technique in general terms is weaker than making the agent execute its steps.
- Mixing model vendors is unlikely to restore diversity by itself, given cross-provider convergence.
- Model generations have moved since the 2024 studies (GPT-4, Claude 3.5); effect sizes may not transfer, though the 2026 studies point the same way.

### Gaps
- No LLM experiment was found that tests morphological grids, Six Hats, jobs-to-be-done, backcasting or first-principles prompts head to head.
- No study was found that measures diversity across dozens of parallel agents given different lenses versus the same brief; the closest are single-call prompt comparisons.
- A search summary suggested persona prompts are only "a superficial change" for highly aligned models, but the source paper could not be pinned down (possibly arXiv 2608.02618); treat as unverified and in tension with Deng et al.

## 4. Coverage by design: splitting the idea space in advance versus one open brief

### Takeaway
For humans an open brief given to independent people works, because people already differ; for LLM agents it does not, because every agent draws from the same distribution. The evidence favours giving each agent a narrow, different slice (a cell, a persona or a lens) plus an instruction to go deep, although no study was found that tests a full user-by-situation-by-mechanism grid directly.

### Cited Findings
- Human parallel search has little redundancy: across five data sets of 1,368 opportunities, repetition was small even for a narrow domain, with an estimated 1,000 unique ideas in the narrowest domain and more than 2,000 in broader ones; the least similar ideas were not generally the most valuable (2011, older; summary only). — [Kornish and Ulrich, Management Science](https://ideas.repec.org/a/inm/ormnsc/v57y2011i1p107-128.html)
- LLM parallel search has heavy redundancy: 5% unique after 4,000 generations. — [Si et al.](https://arxiv.org/html/2409.04109)
- The stated cause is aggregation versus partition of knowledge; personas work as partition cues. — [Deng, Brucks and Toubia](https://arxiv.org/abs/2602.20408)
- Narrow problem statements raise originality without reducing quantity. — [Rietzschel et al., 2014](https://research-portal.uu.nl/en/publications/effects-of-problem-scope-and-creativity-instructions-on-idea-gene/)
- Brainstorming research links originality to deep exploration within categories and to the number of content categories surveyed (summary only). — [Dual pathway to creativity model, University of Groningen](https://pure.rug.nl/ws/portalfiles/portal/156012256/The_dual_pathway_to_creativity_model_Creative_ideation_as_a_function.pdf)
- Assigned attributes beat plain prompts for diversity in synthetic data generation. — [AttrPrompt, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/file/ae9500c4f5607caf2eff033c67daa9d7-Paper-Datasets_and_Benchmarks.pdf)
- Generating the dimensions of the space first, then filling it, is the design of Luminate. — [arXiv 2310.12953](https://arxiv.org/abs/2310.12953)
- Excluding already-covered categories and asking for ideas outside them gave the best top-end novelty and rarity among 25 prompts. — [IDEAFix](https://arxiv.org/html/2606.00875)
- In multi-agent research, the cure for duplicated work was explicit division of labour: complex queries get "more than 10 subagents with clearly divided responsibilities" (June 2025). — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Within one session the idea space drains: each new idea grows more similar to earlier ones, and prompt advantages disappear after about 750 ideas. — [Meincke et al.](https://mackinstitute.wharton.upenn.edu/wp-content/uploads/2024/02/for-web-AI-idea-variance.pdf)

### Inferences
- A workable recipe: the coordinator (a strong model or a person) first writes three or four axes, for example user type, situation or moment, mechanism, and time horizon (this quarter, three years, ten years), with four to six values each; each agent then receives one cell and one lens. With 30 to 40 agents, fill the grid so that every value of every axis appears at least twice and no two agents share both a cell and a lens.
- Keep each agent's list short (roughly 5 to 10 ideas), since fixation and exhaustion grow within a session; breadth should come from more cells, not longer lists.
- Reserve a minority of agents for unstructured wildcards (random stimulus, far analogy) because a grid can only cover the axes someone thought of.
- Use the dozen themes from the earlier sessions as an exclusion list, described as abstract categories and not as vivid example ideas, since supplied examples anchored GPT-4 in the 2024 study while category negation helped in 2026.
- Because the most distant ideas are not usually the most valuable (Kornish and Ulrich), coverage is a means of finding good ideas in unexplored cells, not a goal in itself; a selection pass is still needed.

### Gaps
- No experiment was found comparing a pre-assigned grid of cells against an open brief for LLM agents on final idea quality. The recommendation rests on adjacent evidence.
- No source gives guidance on how many axes or cells are optimal, or on time-horizon splits specifically.

## 5. Orchestration practice: what AI labs and practitioners recommend

### Takeaway
The consistent advice is that each subagent brief must be self-contained (objective, output format, boundaries, sources or tools), that subagents see nothing unless it is restated, that parallel agents suit independent "read-like" work such as idea generation, and that total token cost rises several-fold even though each context stays small. At November 2026 prices, a few dozen short brainstorm agents on a small model cost cents; the expensive parts are the coordinator and any judging.

### Cited Findings

**Brief content and specificity**
- Each subagent needs "an objective, an output format, guidance on the tools and sources to use, and clear task boundaries"; without these, agents duplicated work or left gaps (June 2025; older than a year). — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Effort-scaling rules written into the lead's prompt: simple fact-finding, 1 agent with 3–10 tool calls; comparisons, 2–4 subagents with 10–15 calls each; complex research, more than 10 subagents with clearly divided responsibilities. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- "Think of Claude as a brilliant but new employee who lacks context"; test a prompt by showing it to a colleague with minimal context; explain why an instruction matters so the model can generalise (current docs, read November 2026). — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

**Shared context**
- "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history..."; a rule that must hold has to be restated in the delegation prompt. — [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents.md)
- Opposing view for interdependent work (Cognition, June 2025): "Share context, and share full agent traces, not just individual messages" and "Actions carry implicit decisions, and conflicting decisions carry bad results"; two subagents building parts of one game produced mismatched styles. — [Cognition](https://cognition.com/blog/dont-build-multi-agents)
- LangChain's reconciliation (June 2025): multi-agent systems that mainly "read" are easier than those that "write"; tasks where all agents need the same context or have many dependencies are a poor fit (summary only). — [LangChain blog](https://blog.langchain.com/how-and-when-to-build-multi-agent-systems)
- Google Research, DeepMind and MIT (December 2025; 180 configurations): multi-agent coordination helped on parallelisable tasks (about +81% on one finance benchmark) and degraded strictly sequential tasks by 39–70%; independent agents with no checker amplified errors 17.2x versus about 4.4x with a central orchestrator (summary only). — [Google Research blog](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)

**Output formats and merging**
- Have subagents write results to external storage and return lightweight references, to cut information loss and coordinator token load. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- "Running many subagents that each return detailed results can consume significant context." — [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents.md)
- Use JSON or other structured formats for state so schema requirements are explicit; be specific about output format and constraints. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

**Parallelism and limits**
- Claude Code runs up to 20 subagents at once by default (adjustable); there is no cap on the total per session; parallel work "works best when the research paths don't depend on each other". — [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents.md)
- Suggested rule: "Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams that don't need to share state." — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

**Small versus strong models**
- Anthropic's research system paired a stronger lead (Claude Opus 4) with cheaper subagents (Claude Sonnet 4) and beat a single Opus 4 agent by 90.2% on an internal evaluation (June 2025). — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- "Control costs by routing tasks to faster, lower-cost models like Haiku"; a subagent's model can be set per definition or per invocation. — [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents.md)
- Model strength changes ideation results: o3 and Claude Sonnet 4 ideas were rated most original (means 3.83 and 3.76 on a 5-point scale) while Llama-3.3-70B did not reliably beat humans. — [Liu et al.](https://arxiv.org/html/2603.19087)
- Counterpoint on embedding metrics: Llama-3.1-70B and Grok scored highest on novelty, rarity and diversity, GPT-4o lowest on rarity. — [IDEAFix](https://arxiv.org/html/2606.00875)
- LLMs are unreliable judges of ideas: the best LLM ranker reached 53.3% agreement with experts against 56.1% between human reviewers (2024, older). — [Si et al.](https://arxiv.org/html/2409.04109)

**Costs**
- Agents use about 4 times the tokens of chat, and multi-agent systems about 15 times; token usage alone explained 80% of performance variance on one benchmark (June 2025). — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- Subagents save the main context window, not total tokens: "each subagent spends tokens of its own while it runs". — [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents.md)
- List prices per million tokens, input / output, read 19 November 2026: Claude Haiku 5.5 $0.10 / $0.50 (prompts up to 100,000 tokens); Claude Haiku 4.5 $1 / $5; Claude Sonnet 5.5 $2 / $10; Claude Opus 5.5 $4 / $20; Claude Fable 5.2 $8 / $40. The Batch API gives 50% off both directions; cache reads cost 0.1x base input on most models. Models from Claude 4.7 on use a tokenizer producing about 30% more tokens for the same text. — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)

### Inferences
- Brainstorming is close to the ideal case for parallel subagents: agents read, do not write to shared artefacts, and need no knowledge of each other. Cognition's objection applies to the merge step, which should be done by one agent holding all outputs.
- Shared context for ideation should be small and factual (goal, audience, hard limits, exclusion categories, output schema). Everything else each agent receives should differ. This departs from Cognition's "share everything" rule on purpose, because shared material is also a shared anchor.
- Illustrative cost, my arithmetic on the list prices above, assuming 40 agents each reading a 3,000-token brief and writing 2,000 tokens: about $0.05 on Haiku 5.5, $0.52 on Haiku 4.5, $1.04 on Sonnet 5.5 and $4.16 on Fable 5.2, before any discount. Tool use, thinking tokens and retries multiply these figures.
- A reasonable split: small models for the generation fan-out, a strong model for designing the grid, deduplicating and clustering, and people (or a strong model with human spot checks) for final selection, given judge unreliability. A small pilot comparing a small and a mid-size model on a few cells would settle whether the small model's ideas are good enough.
- An output contract that makes merging mechanical: one JSON object per idea with fields for agent id, lens, cell, a title of eight words or fewer, a one-sentence mechanism, target user, situation, the assumption it breaks, and what would have to be true. Files written to a shared folder, one per agent, with only a path and a count returned to the coordinator.
- With 30 to 40 agents and a default cap of 20 concurrent subagents, run in two waves; the second wave can receive the first wave's category list as exclusions.

### Gaps
- No lab publishes cost figures for brainstorming-style fan-outs; the cost line above is an estimate.
- OpenAI, Google ADK and Microsoft agent-framework documentation were not opened in this research; the guidance here leans on Anthropic, Cognition, LangChain and Google Research sources.
- No source states a tested rule for when a small model is "enough" for ideation; the two studies cited disagree on which models look most novel because they measure different things (human ratings versus embedding distance).

## 6. Reported mistakes

### Takeaway
The failure modes documented most often are identical or vague briefs that cause duplicated work, examples in the brief that every agent copies, missing stopping rules, and trusting a model to judge its own ideas.

### Cited Findings
- Vague brief, duplicated work: told only to "research the semiconductor shortage", one subagent explored the 2021 automotive chip crisis while two others duplicated work on 2025 supply chains. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- No effort or stopping rule: early versions spawned 50 subagents for simple queries, searched endlessly for sources that did not exist, and kept going after they had sufficient results. — [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)
- In 1,642 annotated traces from seven multi-agent frameworks, the most common failure modes were step repetition (15.7%), reasoning-action mismatch (13.2%), unawareness of termination conditions (12.4%), disobeying the task specification (11.8%), incorrect verification (9.1%) and no or incomplete verification (8.2%); overall failure rates ran from 41% to 86.7%. Better role specifications alone raised one system's task success by 9.4% and adding a high-level verification step by 15.6%; the authors say prompt-level fixes are inconsistent and structural changes are needed. — [Cemri et al., MAST, arXiv 2503.13657](https://arxiv.org/html/2503.13657v3)
- Anchoring on examples (LLM): supplying seven successful ideas or previous top ideas made GPT-4's pools less diverse than the base prompt (0.428 and 0.403 versus 0.377). — [Meincke et al.](https://mackinstitute.wharton.upenn.edu/wp-content/uploads/2024/02/for-web-AI-idea-variance.pdf)
- Anchoring on examples (humans): examples lead to more example-related ideas and fewer categories. — [Sio, Kotovsky and Cagan meta-analysis](https://eld.bl.uk/catalog/100081707150_0x000001)
- Vendor guidance: examples must "vary enough that Claude doesn't pick up unintended patterns", and models "tend to converge toward generic, 'on distribution' outputs" unless told otherwise (the second quote comes from the docs' frontend-design section). — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Same brief to everyone: independent LLM sessions converge on similar themes; scaling the count mostly repeats duplicates. — [Deng et al.](https://arxiv.org/abs/2602.20408); [Si et al.](https://arxiv.org/html/2409.04109)
- Over-long single sessions: early outputs constrain later ones (fixation), and ordinary-person personas make this worse unless paired with a stepwise self-check. — [Deng et al.](https://arxiv.org/abs/2602.20408)
- Weak persona choices: famous-innovator personas moved diversity only slightly (Steve Jobs 0.368 versus base 0.377). — [Meincke et al.](https://mackinstitute.wharton.upenn.edu/wp-content/uploads/2024/02/for-web-AI-idea-variance.pdf)
- Agents silently skipping a step: about 15% of chain-of-thought runs skipped the "make them bolder and more different" step. — [Meincke et al.](https://mackinstitute.wharton.upenn.edu/wp-content/uploads/2024/02/for-web-AI-idea-variance.pdf)
- Results flooding the coordinator: many detailed subagent reports consume the main context. — [Claude Code subagent docs](https://code.claude.com/docs/en/sub-agents.md)
- Letting agents build on each other's ideas during generation was counterproductive in human groups. — [Girotra, Terwiesch and Ulrich](https://mackinstitute.wharton.upenn.edu/2010/idea-generation-and-the-quality-of-the-best-idea/)
- Trusting LLM judges: near-chance agreement with experts on idea quality. — [Si et al.](https://arxiv.org/html/2409.04109)
- Over-delegation: recent Claude models may spawn subagents where a direct approach would do; multi-agent is a poor fit when value does not justify the token cost. — [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices); [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system)

### Inferences
- A brief for a mass brainstorm should contain no example ideas at all; if illustration is unavoidable, give one uncommon example from an unrelated domain, in line with the fixation meta-analysis.
- Every brief needs a stopping rule in plain terms: an exact idea count, a ban on follow-up research beyond a stated budget, and an instruction to stop and report if the cell proves empty.
- Add a cheap verification step at the coordinator: check each returned file against the schema and the assigned cell, and re-run agents that drifted or skipped the self-check, since specification drift and skipped steps are common.
- Pass ideas between agents only between waves and only as exclusion categories, not during generation.

### Gaps
- No published post-mortem of a large LLM brainstorming run was found; the mistakes listed come from research-agent systems, coding-agent systems and single-prompt ideation studies.
- "Too much shared context" as a cause of convergence is supported indirectly (example anchoring, fixation) and was not tested directly in any source read.
