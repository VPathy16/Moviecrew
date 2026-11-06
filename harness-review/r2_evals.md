# R2 Evals & Observability

## 1. Claim I most disagree with
On-device #1: "50%+ of turns never touch the 2B model" via a fast path. Every harness bug in the brief (#4 invented time, #2 skipped confirm) surfaced because the model's output hit the runner. The only router in the repo is the keyword ranker (Connectors.kt:15-34), which the prompt lead already calls brittle, and EvalSet.kt:34-39 still routes through the v1 LocalRouter. A fast path with no measurement silently converts "model failure we can see" into "regex failure we cannot". It is fine in principle; it is wrong as a first move.

## 2. Conflicts and how I settle them by measurement
- **Fast path vs representative evals.** Run it in shadow mode: model plan and rule both computed, trace `route` and `agree`. Each rule ships only at 99% agreement on the golden set plus 2 weeks of phone logs. Eval metrics are reported per route, never blended.
- **ToolSpec registry (architect) vs team's fixed tools.json/GBNF.** Generate the registry from tools.json at build; a contract test parses every GBNF-generated plan through parse, check and run. Metric: drift count must be 0.
- **Code-written confirm (architect, safety) vs DPO chosen wording.** Assert confirm presence, order and target, not text. Measure yes/no parse rate and "approved wrong action" in a 40-case script with templated vs model text. Template wins if equal.
- **Extractive copy (on-device) changes what is measured.** Keep Facts.isIn (PlanParts.kt:216) as the oracle. Run both copy methods on the same page fixtures; compare exact-fact accuracy and false-NONE rate. Measure the product, not the model.
- **Single-turn history (prompt) vs RESULT re-plan (architect).** Both are untrained. Add follow-up and RESULT cases to the holdout and compare success with and without; only trained rows justify keeping either.
- **Safety "over-trigger is cheap" vs over-confirm gate.** With the backstop on, over-confirm on call_answer_private_ok (112) and call_answer_alone (74) must stay 10% or less. If not, tune the lexicon.

## 3. Changes to my round-1 list
- **Withdraw "3 seeds".** Plan decoding is greedy (local_jni.cpp:83), so seeds do nothing. Use paraphrase and STT-noise variants of each case instead; seeds only matter after the temp-0.3 retry.
- **Gate end-to-end, not model-alone.** The leak gate is 0 with backstop; the model-only rate is reported separately and must not regress.
- **Accept the prompt lead's point:** DPO prompts are single-turn and menu-light. Add a "production-shaped" tier: 2 earlier masked plans, 3-5 item menus, 5 notes, `(nothing saved about this)`.
- **Add to Trace v2:** `route` (fast/model), rendered-prompt sha, bundle manifest, one masked log path (Trace.line uses Redactor, Trace.kt:71, while TurnTrace uses SecretFilter).

## 4. Unified build order
| # | Item | Lens | Effort | Prevents |
|---|---|---|---|---|
| 1 | Rendered-prompt contract test + bundle manifest in trace | Prompt/Evals | S | silent train/serve skew |
| 2 | Replay harness (real UserTurn+PlanCheck+runner) + DPO rejected-plan fuzz, end-state asserts | Evals | M | harness bugs 1-7 recurring |
| 3 | Speaker backstop in speak/safeToSay | Safety | M | 3/20 private leaks |
| 4 | Exact-yes consent + code-generated confirm text | Safety/Arch | S | "okay what's my calendar" resuming a delete |
| 5 | Trace v2, one masked log path, trace2case | Evals/Safety | M | unreproducible phone failures, PIN in shared log |
| 6 | Typed StepResult, typed context-overflow error, history cut to 1 | Arch/OnDevice | M | silent "" and null errors |
| 7 | ToolSpec generated from tools.json | Arch | M | registry drift |
| 8 | Shadow-mode fast path, then disk KV and streaming | OnDevice | M | latency, after proof |

**This week:** 1, 2 (fuzz first, it needs no model), then 3 with 4.
