# Hanu harness review: what five specialists agreed, where they disagreed, and the build order

Two rounds. Round 1: five specialists (agent-harness architect, prompt/context engineer, safety/guardrails, evals/observability,
on-device small-model) each read the real code (`/home/user/mealmate`) and wrote a position. Round 2: each read the other four,
named the claim they most disagreed with, resolved the conflicts, and proposed one build order. Full papers: `r1_*.md`, `r2_*.md`.

**Honest limits.** The specialists are model agents, not the Claude team; they cite public industry practice (simple workflows, tool
design, context engineering, eval-driven development, guardrails) and said where they were inferring. They read code and ran nothing.
Phone latency numbers are their estimates (30 tok/s prefill, 5-8 tok/s decode), not measurements.

## Where all five agree
1. **Privacy needs a deterministic code rule.** v4 asked first on 17 of 20 speaker/company turns. Grammar and PlanCheck guarantee syntax, not
   privacy; more prompt or DPO will not make 85-90% into 100%. Backstop in `speak()`/`safeToSay`: on a call whose route is speaker/unknown,
   a line that overlaps a memory note, file content or a private class and had no approved confirm goes to the screen instead.
   Earpiece and Bluetooth are exempt. Default is "show on screen", not a spoken yes (a bystander's "yes" is not consent).
2. **The harness is the fragile part, not only the model.** Most of the seven bugs found so far came from missing structure around the
   model. Plan-then-execute with code verifiers (`Facts.isIn`, `numbersFrom`, `safeToSay`) is the right shape for a 13 tok/s model.
3. **Drop the earlier-turn history.** All 999 DPO prompts are single-turn; the app sends the last 2 plans (and masked ones). Zero history.
   Remove untrained strings (`(nothing saved about this)`), cap memory notes at 5.
4. **Consent is too loose** (a bug I introduced): `YesNo` treats any utterance of 6 words or fewer that starts with "ok/sure/fine" as yes, so
   "okay what's on my calendar" would resume a pending delete. Require an exact short yes, and render the confirm question in code, bound to the action.
5. **Test the harness with no model first**: run all 999 DPO *rejected* plans through PlanCheck/Runner; none may speak a private fact,
   delete or overwrite without an approved confirm. Plus a byte-for-byte rendered-prompt test against the team's format.
6. **Trace v2**: raw plan, exact turn text, TOOLS menu, model/prompt/grammar hashes, rejected_by, route (fast/model), one masked logging
   path (`Trace.line` uses `Redactor`, `TurnTrace` uses `SecretFilter`), and a `trace2case` tool that turns a shared log line into a test.
7. **One tool registry** (arity, types, effect class, channel policy, executor) generated from the team's `tools.json`; the hand-kept
   lists in `Plan.kt`, `PlanParts.kt`, `PlanRunner.kt` and `Connectors.kt` drift (bug 7 was this).

## Disagreements and how they were settled
| Question | Resolution |
|---|---|
| Bounded model re-plan with a RESULT/failure line (architect) | **Dropped.** An untrained input line, plus a 5-15 s decode on a phone. Code-owned repair instead (next page, bigger token cap, typed errors). Re-plan only for `no_tool` (exists) or an unreadable plan in chat; RESULT only in the three trained forms. |
| Skip the model for 50%+ of turns (on-device) | **Narrowed.** Closed-class turns only (stop, cancel, yes/no on a pending question, timer/alarm with no slot guessing), through the same output gate, never on a call with notes. Ship first in **shadow mode**: ship each rule only at 99% agreement with the model. |
| Stream `say` to TTS from the first token (on-device) | **Gate first, then stream.** PlanCheck runs after the whole plan parses, the speaker rule hangs on a confirm that precedes the say, and SecretFilter is not per-sentence safe ("my pin is" / "four eight two one"). The plan is short, so buffering costs seconds. |
| Over-trigger privacy rule vs UX (safety vs evals' over-confirm <= 10%) | Over-trigger only on CALL + speaker/unknown + a private-class match; route to screen so a false positive is cheap. Report model over-confirm and backstop fire-rate separately. |
| "0 leaks in 60 cases" gate (evals) | **Gate the deterministic backstop** (all 999 rows plus fuzz, 0 by construction); *report* the model's own ask-rate. 0/60 only bounds the true rate near 5%. "3 seeds" withdrawn: decoding is greedy. |
| Retry at temperature 0.3 with the reason appended (on-device) | **Withdrawn.** Untrained label, not reproducible in evals. Retry greedy with the same bytes, or fall back to code. |
| Extractive copy (model picks a numbered candidate) | **Accepted, gated on evals**: run both methods on the same page fixtures and compare exact-fact accuracy and false-NONE rate; keep `Facts.isIn` as the oracle. |
| Is the DPO file a holdout? | **Unknown, ask the training team** which ids were in v4's training mix. If they were, build the holdout from fresh phone traces. |
| Code-written confirm text vs the model's trained wording | Code renders the question for every gated tool (output, so no train/serve skew); assert confirm presence, order and target, not wording. |

## Unified build order
| # | Item | Lens | Effort | Prevents |
|---|---|---|---|---|
| 1 | DPO-rejected-plan fuzz through PlanCheck/Runner (no model) + rendered-prompt golden test | evals, prompt | S | bugs 1-3 and 5 recurring |
| 2 | Exact-yes consent + code-rendered confirm bound to the action | safety, architect | S | "yes" hijack; vague confirms; wrong-target approval |
| 3 | Zero history, drop untrained strings, cap notes at 5 | prompt | S | train/serve skew |
| 4 | Speaker backstop in `speak()`/`safeToSay`, default to the screen | safety | M | the 3/20 leaks |
| 5 | One output gate + ToolSpec registry + typed StepResult + typed overflow error (the silent `""` at `local_engine.cpp:180`) | architect, safety | M | registry drift; bypass by new paths; silent empty replies |
| 6 | Trace v2 + one masked log path + `trace2case` | evals | M | unreproducible phone failures; PINs in shared logs |
| 7 | SecretFilter v2 (spoken digits, number words, keyword windows) | safety | M | spoken PINs stored or logged |
| 8 | Desktop replay harness with the real model, frozen holdout, end-to-end ship gates (backstop on) | evals | L | tuning to the 20-case sample; shipping v4 blind |

Next tier: fast path in shadow mode, disk KV snapshot of the system prompt, stream-after-gate, extractive copy, Pending persistence.
Ship gate for v4 as default: backstop 0 leaks on all DPO rows + fuzz; model ask-rate >= 95%; over-confirm <= 10%; unrunnable plans <= 2%.
