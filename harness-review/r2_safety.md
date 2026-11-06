# R2 Safety (paths under app/src/main/java/com/mealmate/app/)

## 1. The claim I most disagree with
**On-device #2: stream `say` to TTS from the plan's first `say(` token, "keeping the safe-to-say gate per sentence."** PlanCheck runs only after the whole plan is parsed (PlanRunner.kt:77-80). The speaker rule hangs on a `confirm` that comes *before* the `say`. Streaming speaks before either check can run. SecretFilter is also not per-sentence safe: "my pin is" / "four eight two one" split across sentences, and number words already slip through (SecretFilter.kt:22). One leaked sentence is unrecoverable audio. The plan is 30-100 tokens, so buffering it costs seconds, not the 20-40 s the specialist worries about. Stream *after* the gate, per sentence of already-approved text.

## 2. Conflicts and my resolution
- **Fast path (ondevice #1) vs PlanCheck/safeToSay.** A template turn that builds its own reply skips both. Resolve: the fast path emits a synthetic `Plan` into the same `Run` and `safeToSay`; one funnel. `ToolMenu.SENSITIVE` words (UserTurn.kt:~85) and any CALL+speaker turn with notes never take it.
- **Streaming vs backstop.** See 1: gate first, stream second.
- **Bounded re-plan (architect #3) and the temp-0.3 retry with a reason line (ondevice #6) vs injection and prompt purity.** A RESULT line carrying page text is the top injection channel. Resolve: reason strings come from code only; page text is masked and marked untrusted; the re-plan may use read-only tools plus `say`, never gated tools, `remember` or `write`; no retry at all after a privacy refusal (retry-until-pass defeats the rule). Prompt lens is right that an untrained USER line is skew; use a RESULT line only once it is trained.
- **Extractive copy (ondevice #5) vs web-text risk.** Extractive is better: the model picks a candidate index, so injected text can only be selected, not authored. Still run the output filter on candidates (imperatives plus phone/URL).
- **Evals "over-confirm <=10%" vs my deliberate over-triggering.** Resolve by making the backstop's action cheap: it routes the private line to the *screen* ("on your screen") instead of asking, so a false positive costs nothing. Measure model over-confirm pre-backstop and backstop fire-rate separately, as evals proposed.
- **Architect action-hash confirm** and my consent fix are the same change; merge.

## 3. What I change
- Withdraw R1 #5 as a regex on digits+"call/send" (too blunt); replace with candidate selection plus filter.
- Fold R1 #7 (policy table) into the architect's `ToolSpec` (effect class, channel policy).
- Change #1: backstop default is *show on screen*, not a spoken yes. A bystander's "yes" on a speaker is not consent.
- Raise the evals fuzz idea (999 DPO rejected plans through PlanCheck/Run, no model) to step 1. Prompt's "drop history" also removes SecretFilter-masked tokens in model turns.

## 4. Unified build order
| # | Item | Lens | Effort | Prevents |
|---|---|---|---|---|
| 1 | DPO-rejected-plan fuzz: none may speak, delete or overwrite unconfirmed | evals | S | bugs 1-3 recurring; finds holes with no model |
| 2 | One output gate (PlanCheck + safeToSay + policy) every path must pass, built on a `ToolSpec` registry with effect class and channel | architect+safety | M | fast-path/stream/re-plan bypass; registry drift (bug 7) |
| 3 | Speaker backstop: private overlap on CALL+non-earpiece goes to screen | safety | M | 3/20 leaks |
| 4 | Exact-yes consent; harness-rendered confirm bound to action hash | safety+architect | S | "okay, what's my calendar" resuming a delete; wrong-target yes |
| 5 | SecretFilter v2 (spoken digits, keyword windows) and all logging through it | safety | M | partial masks, Trace.kt:71 leaks |
| 6 | Single-turn prompts, drop untrained strings, rendered-prompt golden test | prompt | S | silent train/serve skew |
| 7 | Trace v2, desktop replay with real UserTurn, frozen holdout, ship gates | evals | L | tuning to the 20 cases; unreproducible failures |
| 8 | Deterministic fast path (alarm/timer/yes-no) through gate 2, then typed results and bounded read-only re-plan | ondevice+architect | M | latency and invented times (bug 4) |
