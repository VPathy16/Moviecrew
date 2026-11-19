# R2 Prompt & context engineer

## 1. The claim I most disagree with
On-device #6: on a PlanCheck failure, retry at temp 0.3 "with the failure reason appended as a USER line". That is a new, untrained context label. APP_TURN_FORMAT section 4 forbids added lines, and UserTurn.kt:12 says the privacy rules hang on the labels. A free-text reason on a 2B model is out-of-distribution input at the moment it is already failing, and a retry sampled at 0.3 can move the model away from the cautious behaviour. Retry greedy with the same bytes, or fall back to code. Architect #3 ("short RESULT line on recoverable failures") has the same flaw.

## 2. Conflicts and how I resolve them
- **Skip the model (on-device #1) vs stable trained prompt.** No conflict in the prompt: a router in front changes no bytes. The risk is a quiet second behaviour. Resolve: fast path only for whole-utterance patterns (timer, alarm, stop, yes/no), never on a call with notes or a private word. Fast-path turns do not enter history. Same PlanCheck gates.
- **Code-written confirm (architect, safety) vs trained wording.** The confirm text is model output, not input, so replacing it causes no skew. Resolve: the code renders the question for every gated tool (PlanRunner.kt:139 vs `questionFor` :157); the model's wording is used only for a private-fact ask. Store the code text if history stays (it will not).
- **RESULT re-plan vs single-turn data.** RESULT is trained only as NEEDS_PERMISSION, NOT_AVAILABLE and "results in SCREEN". Resolve: re-plan only with those three forms, and the re-plan prompt is still single-turn (no history). Recoverable failures (extract miss, truncation) are handled by code saying cannot_confirm. A new RESULT: FAILED(...) form needs training rows first; ask the team.
- **Extractive copy (on-device #5) vs the trained copy prompt.** Hanu was trained on plans; the copy prompt on the SIDE slot is already an untrained prompt, so a numbered pick is no further from training and is verifiable by construction. Accept, but gate it on the eval set. I did not read the copy prompt text, so this is inference.
- **Evals' frozen holdout vs DPO data.** The 999 pairs were mined from earlier failures and may be in v4's training mix. If so they are not a holdout. Ask the training team which ids were trained on; build the holdout from fresh phone traces.

## 3. What I change from round 1
- Withdraw "extend the cached prefix"; keep system-only prefix and adopt on-device's disk KV snapshot, keyed by rendered prompt (per name) plus model sha.
- Go further than on-device: zero earlier turns, not one. Also add architect #8 (never store refused or unreadable plans).
- Demote menu top-k tuning below the backstop; it matters when mail/consent items arrive.
- Add evals' idea: log the rendered-prompt hash and raw plan in every trace.
- Keep the point that few-shot additions to the app are off the table.

## 4. Unified build order
| # | Item | Owner lens | Effort | Prevents |
|---|---|---|---|---|
| 1 | Speaker/private-fact backstop in code, default "show on screen" | safety+architect | M | 3/20 spoken leaks |
| 2 | Zero history, drop `(nothing saved...)`, cap notes at 5, golden rendered-prompt test | prompt | S | train/serve skew |
| 3 | Exact-yes consent, code-rendered confirm bound to the action | safety+architect | S | "okay what's on my calendar" hijack, vague confirms |
| 4 | Model-free fuzz: DPO rejected plans through PlanCheck/Runner | evals | S | bugs 1-3 class |
| 5 | Trace v2 (raw plan, rendered-prompt hash, rejected_by) then desktop replay using real UserTurn | evals | M then L | unreplayable failures |
| 6 | SecretFilter v2 (spoken digits) and one masked logging path | safety | M | spoken PIN stored/logged |
| 7 | Deterministic fast path plus arithmetic in code | on-device | M | tip+split miss, invented times, 20-40 s turns |
| 8 | One ToolSpec registry, typed StepResult, typed context-overflow error | architect | M | drift (bug 7), silent "" |

After these: disk KV snapshot, streaming say, extractive copy, thermal governor.
