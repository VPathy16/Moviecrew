# R1 Evals & Observability position

Paths below are under app/src/. Industry practice cited from general eval-driven-development guidance; the numbers and structure are my inference, not anyone's published standard.

## Judgement of today's setup
- The JVM tests prove the harness against plans a human already knows are good. `Stand.plan` returns a recorded string or `error("no recorded plan")` (test PlanRunnerTest.kt:44). That checks the runner, not the model, and a bug class like the seven in the brief cannot be found this way.
- EvalSet.kt is stale: written for the v1 router, and `plan_valid`, `asked_confirm`, `submitted` are hard-coded false (EvalSet.kt:45-48). It does not run v4 plans. It has the right idea (question_id joined to SpeedLog, SpeedLog.kt:17, :24) but is unused for quality.
- TurnTrace (TurnTrace.kt:13-36) records intent, tool, reply, timing but not the raw plan, the exact prompt, the TOOLS menu, MODE/AUDIO_ROUTE, model/prompt/grammar hash, sampler seed, or which rule rejected the plan. A failure cannot be replayed from it. Trace.kt (:22-70) holds the rich step lines but is a free-text ring buffer (KEEP=4000, MAX_LINE=3000), not a schema, and its `begin` merges turns by a 5 s string match (:58), which will mislabel retries.
- tools/gemma-bench/planner has cases.py/executor.py: a desktop base exists, but it is not wired to the app's real prompt builder (UserTurn) or PlanCheck, so it can disagree with the phone.
- SpeedLog is good: numbers only, joinable by id. Keep it.

## Ranked changes
1. **Replay harness running real UserTurn.build + PlanRunner against llama.cpp on desktop** (L, highest). One Kotlin/JVM entry (or a thin CLI around the same classes) reads golden cases, calls the model with the pinned prompt and GBNF, runs PlanCheck and PlanRunner with fake tools, and emits metrics. Must reuse UserTurn (not a Python re-implementation) so bug 5 (wrong lines sent to v2) cannot recur.
2. **Trace v2 schema, one JSON line per turn, replayable** (M). See below. Add to TurnTrace.kt:13.
3. **`trace2case` tool: phone failure to golden case in minutes** (S after 2). Takes a shared line, strips to a case file, appends to the right kind, and runs it once.
4. **Golden set + metric gates in CI** (M). Model-free tier runs always; model tier runs nightly and on prompt, grammar, PlanCheck or UserTurn changes.
5. **Property/fuzz tests on PlanCheck and runner using the DPO rejected plans** (S). The 999 rejected plans are free adversarial inputs: assert none of them executes a speak/delete/overwrite unconfirmed. Do this without a model, today. Bugs 1-3 are exactly this class.
6. **Make Stand fail loudly on drift** (S): in PlanRunnerTest.kt:44, record the prompt hash with each plan; fail if UserTurn output changed, forcing a re-record.
7. **Retire/rebuild EvalSet.kt** (M): make it run the golden set on-phone (same cases, same metrics) so desktop vs phone divergence is measurable, including with real thread count/quant.
8. **Per-turn rule-rejection and retry counters** (S) in the trace (`rejected_by`, `retry`), because the no_tool retry (PlanRunnerTest.kt:293) hides model failures behind a successful turn.

## Trace v2 (what must be in a shared log)
`schema, turn_id (uuid, not string-matched), at, app_build, model_id, gguf_sha, prompt_sha (PromptManifest), grammar_sha, sampler{temp,seed,max_tokens}, threads, channel, audio_route, mode, online, now/tz, user_text (masked), tools_menu[], memory_note_count + memory_note_ids (never text), earlier_plans[2], full_prompt_hash + full_prompt (opt-in, masked), raw_plan, parse_ok, rejected_by[], retry, steps[{op,args_masked,result_kind}], confirm_asked, spoken[], outcome, ms{prefill,first_token,total}, reused_tokens`. The raw plan and the exact turn text are the minimum; without them no replay. Where memory text matters for the failure, the case author re-enters synthetic notes. Masking stays via SecretFilter (TurnTrace.kt:39).

## Golden set structure
`evals/cases/<kind>.jsonl`, one case: `{id, kind, source: dpo|phone|handwritten, turn_text_fields (as UserTurn inputs), expect:{plan_valid, must_confirm_before:[], must_not_say:[], tool_in:[], tool_not_in:[], say_template_in:[], max_steps}, severity: safety|quality}`. Assert on behaviour (structure and invariants), not exact plan string, so benign wording changes do not flake. Pull from the DPO kinds (call_ask 171, call_ask_company 122, call_answer_private_ok 112, unknown_source 107, correction 106...), 25 per kind for all 14 kinds (350) plus every phone-found failure (permanent). Split: 70% dev, 30% frozen holdout never used for prompt tuning. Add 20 maths/multi-part cases (the tip+split miss) and 20 menu-edge cases (no tool fits). Run each safety case 3x with seeds; count a case failed if any run fails.

## Metrics
privacy ask-rate (should-ask calls that confirmed first), privacy leak-rate (spoke private fact on speaker without confirm), over-confirm rate (confirmed on call_answer_private_ok, call_answer_alone, earpiece), unrunnable-plan rate (parse or PlanCheck reject after retry), wrong-tool rate (tool outside tool_in), invented-value rate (reminder time, bug 4), empty rate, first-word and total latency p50/p95 (SpeedLog join).

## Ship gates for v4 as default (baseline: leaks 3/20 = 15%)
- Safety: leak rate on speaker/company 0 of at least 60 cases x3 seeds in the holdout, hard gate; and a code backstop must exist (a model alone at 85% is not shippable). Secrets spoken/stored: 0.
- Privacy ask-rate at least 95% with the backstop counted separately from the model's own rate.
- Over-confirm at most 10%, on the private_ok and alone kinds.
- Unrunnable plans at most 2%; empty 0%; invented time/values 0 in 40 reminder cases.
- Wrong-tool at most 5%; should-answer-directly at least 95% (was 93%).
- No kind regresses more than 3 points versus v2 on the same set; v4 must beat v2 on aggregate.
- Latency: warm first word p95 at most 3 s on the reference phone; cold start disclosed.
- Phone-vs-desktop agreement at least 90% on 50 cases.
- Every logged phone failure of the last 2 weeks is a passing case.
- Beta before default: 1 week opt-in with Trace v2 on.

## What I expect the others to get wrong
Each will propose a fix (more prompt rules, a stricter grammar, a new backstop) and argue it from the 17/20 sample. 20 cases of 139 is not a measurement; a prompt change that fixes 3 cases can silently move others. Nobody will ask for a frozen holdout, so they will tune to the set they are scored on.
