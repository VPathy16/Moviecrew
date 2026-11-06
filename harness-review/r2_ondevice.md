# r2 On-device specialist
Phone numbers below are my inference (30 tok/s prefill, 5-8 tok/s decode, throttled after ~60 s), not measurements.

## 1. Claim I most disagree with
Architect #3: "one bounded re-plan with a RESULT line on recoverable failures." A re-plan is a second plan() call: re-read the changed tail (~2 s) plus decode a 40-100 token plan (6-15 s). It stacks on a turn that already costs plan + copy (+ up to MORE_PAGES extra copies, PlanRunner.kt:289-293). Worse, RESULT turns are on the brief's "not built" list, so Hanu was never trained on them (prompt specialist's skew point applies). Trained model + untrained input = the failure we cannot measure. Most recoverable failures (extract miss, truncated plan) are fixed by code: retry the next page, raise planMaxTokens, return a typed error. Re-plan only the no_tool case, which already exists (PlanRunner.kt:72).

## 2. Conflicts and my resolution
- Prompt "never trim the system prompt, single-turn only" vs latency: no conflict. I never proposed trimming (r1 #4 was a disk KV snapshot). I accept single-turn: it also frees the 3072-cell slot (local_engine.cpp:180) and keeps the prefix hot. Follow-ups ("make it 6pm") are code-resolved against Pending.
- Architect re-plan / evals extra checks vs a 20-40 s turn: budget the turn. Hard cap 2 model decodes per turn on call channel (plan + at most one 2-token pick). Verifiers are code (Facts.isIn, PlanCheck): free. Any extra model verifier is rejected.
- Safety "default to show on screen" vs voice-first: right on speaker, wrong on earpiece/bluetooth. Gate on route (CallRoute) and make the code-generated question a 6-word template, spoken in ~2 s. Over-trigger budget: evals' over-confirm <=10% is the right cap.
- Skip-the-model vs DPO behaviour: the fast path may only take intents where DPO has no privacy kind (alarm, timer, open app, stop, yes/no). Anything touching memory notes, files or the call+speaker route goes through Hanu AND the backstop. Evals must cover the fast path with the same golden cases, or it becomes an untested second brain.
- Safety "tighten consent to exact yes <=3 words" vs fast path: same code, merge them.

## 3. Changes to my r1 list
- Withdraw #6's higher-temperature retry: not reproducible in evals, and 0.3 sampling on a grammar model adds a failure class. Retry greedy with a RESULT-free reason only when no_tool.
- Withdraw "intent classifier model call" in place of keywords: adds a call. Fix the keyword ranker with embeddings (already loaded).
- Upgrade #3: typed error for the silent "" at local_engine.cpp:180 is now first-order, since evals want rejected_by in Trace v2.
- Add: "rejected" grammar count (GenerateStats.rejected) into Trace v2 as an uncertainty signal.

## 4. Unified build order
1. Speaker/privacy backstop in speak()/safeToSay, default show-on-screen on speaker (safety, M): the 3/20 leak.
2. Tighten consent + code-generated confirm text (safety/architect, S): "yes" hijack, wrong-action approval.
3. Trace v2 + raw prompt/plan + typed errors incl. the silent "" (evals, M): unreplayable failures.
4. Fuzz PlanCheck with the 999 rejected plans, model-free (evals, S): bugs 1-3 class.
5. Single-turn serving + drop untrained "(nothing saved about this)" + rendered-prompt golden test (prompt, S): train/serve skew.
6. Deterministic fast path for alarm/timer/open/stop/yes-no (on-device, S-M): latency and bug 4.
7. Replay harness on real UserTurn + PlanRunner, frozen holdout, ship gates (evals, L): v4 can't be gated otherwise.
8. Stream say to TTS + prompt KV snapshot to disk (on-device, M): 40 s cold start, time-to-first-word.
Next tier: single ToolSpec registry, extractive copy, thermal governor, Pending persistence.
