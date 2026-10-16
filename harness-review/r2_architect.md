# R2 Architect (paths under app/src/main/java/com/mealmate/app/local/)

## 1. Claim I most disagree with
On-device #1: "50%+ of turns never touch the 2B model" via deterministic alarm/timer templates. The slot-extraction half of that is a second NLU in regex, and the code shows how that goes: TimeWords/When (PlanRunner.kt:535-578) is already the brittlest file in the runner (English-plus-a-few-Hinglish cue lists, a bare-hour special case, "today" vs "tomorrow" asymmetry), and Connectors.ranked (:31) is keyword routing the prompt and on-device specialists both want to replace. Growing it to carry half of all traffic doubles the Hinglish surface and moves the 7-bug problem into code with no model to blame. Safe subset: closed-class control utterances only (stop, cancel, yes/no on a Pending, "what time is it"), where no slots are extracted.

## 2. Conflicts and my resolution
- **Skip the model vs stable trained format** (on-device vs prompt): fast path only for the closed set above; widen only once router precision is measured on the golden set.
- **Over-trigger privacy vs UX** (safety vs evals' over-confirm <=10%): over-trigger only when CALL and route is speaker/unknown AND the line matches a private class. Earpiece is exempt. Default to "show on screen". Track over-confirm as a metric, not a gate.
- **One bounded re-plan vs 13 tok/s** (me vs on-device and prompt): I lose this one. A RESULT or "failure reason" line is an untrained input (prompt's skew point) and costs a 5-15 s decode on a phone. Replace with code-owned repair (next page, already at :289; query rewrite; plain honest error). A re-plan only for an unreadable plan, in chat, never on a call.
- **Zero leaks vs a 20-case sample** (evals vs everyone): 0/60 only bounds the true rate near 5% (rule of three). Gate the deterministic backstop (all 999 DPO rows plus fuzz, must be 0 by construction). Report the model's own ask-rate, do not gate on it.
- **History** (prompt: drop; on-device: keep one): drop to zero. Pending and YesNo already carry yes/no follow-ups.

## 3. What I change
- Withdraw/downgrade my #3: typed StepResult stays (honest errors, trace), model re-plan goes.
- Fold safety's policy table (tool x channel x route) into my ToolSpec registry.
- Promote consent hardening (YesNo "okay what's on my calendar" hijack, Connectors.kt:66-78) and history removal; both are S and I missed them.
- Trace v2 becomes a prerequisite for everything measured.

## 4. Unified build order
| # | Item | Lens | Effort | Prevents |
|---|---|---|---|---|
| 1 | Drop earlier-plans history; remove untrained strings ("(nothing saved...)"); typed error for slot overflow instead of "" | prompt, on-device | S | Train/serve skew; silent empty replies |
| 2 | Tight consent (exact short yes, else cancel and replan) plus code-generated confirm text bound to the action | safety, architect | S | "yes" hijack; "Is that okay?" before delete |
| 3 | Model-free tests: DPO rejected plans through PlanCheck/Runner; golden rendered-prompt diff; Stand hash check | evals, prompt | S | Bugs 1-3 and 5 class |
| 4 | Speaker backstop in speak(), default show-on-screen | safety | M | The 3/20 leaks |
| 5 | Trace v2 (raw plan, prompt hashes, rejected_by) plus trace2case | evals | M | Unreplayable phone failures |
| 6 | ToolSpec registry plus policy table, typed StepResult, cancellation/timeouts, extract out of say() | architect, safety | M | Registry drift; hung calls; hidden execution |
| 7 | SecretFilter v2 (number words, keyword window) plus single logging path | safety | M | Spoken PINs stored or logged |
| 8 | Desktop replay harness with real model, frozen holdout, ship gates | evals | L | Tuning to the scored set |

Next: disk-persisted KV, TTS streaming, extractive copy candidates.
