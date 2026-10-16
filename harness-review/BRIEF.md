# Brief: the Hanu harness (read this first)

## What this is
Vanaras / "Maya": an Android voice+chat assistant. A fine-tuned on-phone model, **Hanu** (Gemma 4 E2B, Q4_K_M, llama.cpp, ~2.7 GB,
13 tokens/s on a phone-class CPU), writes ONE "plan" per turn in a small plan language (grammar-constrained, GBNF). The **harness**
is everything around the model: it builds the prompt, parses and checks the plan, runs the steps, asks the user, and speaks.
The model never talks freely; the app runs the plan. Repo: /home/user/mealmate (branch experiment/real-person-avatar), Kotlin.
Docs from the training team (read-only): /root/.claude/uploads/3970291e-b5f2-5d98-b95b-1c1ebfbbd473/ :
APP_TURN_FORMAT.md, CONNECTOR_LIST_v4.md, tools.json, prefs.schema.json, SPEC_CHANGES.md, dpo_pairs_v029.jsonl (999 pairs).
Also: /tmp/claude-0/-home-user-Moviecrew/3970291e-b5f2-5d98-b95b-1c1ebfbbd473/scratchpad/hf/system_prompt.txt (the pinned 4 KB system prompt).

## Code map (app/src/main/java/com/mealmate/app/)
- local/engine/TurnEngine.kt   one turn: pending-confirm resume → memory notes → TOOLS menu → UserTurn.build → PlanRunner.turn (+ no_tool retry) → say
- local/plan/UserTurn.kt       exact turn text (memory notes, MODE, AUDIO_ROUTE, USER, TOOLS...), ToolMenu rules, PromptManifest (pinned prompt hash)
- local/plan/Connectors.kt     the 10 TOOLS menu items the phone can run, keyword ranking (top 3-5), minutes(), Pending, YesNo
- local/plan/Plan.kt           parser for the plan language
- local/plan/PlanParts.kt      PlanCheck (rules before anything runs: <=8 steps, confirm before delete/forget/submit, secret in args), Passages, Facts, Arithmetic
- local/plan/PlanRunner.kt     runs the plan: tools, confirm-as-real-question (stop + resume on "yes"), search→open→extract→copy→verify, say templates, safeToSay
- local/plan/Workspace.kt      notes files (write/read/list/delete with trash), Prefs (set_pref validated against the team's schema)
- privacy/SecretFilter.kt      PIN/OTP/CVV/card/Aadhaar/password detection + masking; used on memory writes, tool args, every spoken line, transcripts
- local/LocalBrain.kt          model load, plan(), warm-up of the plan prompt, per-model prompt/grammar assets, prompt pin check
- local/LocalModels.kt         model catalog (Hanu v2 default, Hanu v4 optional), manifest hash, minContext, planMaxTokens
- local/engine/TurnTrace.kt, diag/Trace.kt   turn trace (JSON line) and step-by-step trace lines; SpeedLog -> turns.csv
- web/Web.kt, PageText.kt, PageRenderer.kt    search (Brave/DuckDuckGo/Bing), page fetch + readable text, hidden-WebView render
- assets/plan_v4/{system_prompt.txt,plan.gbnf}  v4 prompt + grammar;  assets/plan/ = v2's (older, v0.2.4)
- src/test/java/.../local/plan/{PlanRunnerTest,UserTurnTest,WorkspaceTest}.kt, privacy/SecretFilterTest.kt: the JVM tests (recorded plans as stand-in model)
- native: app/src/main/cpp/local_engine.cpp (2 KV slots: PLAN and SIDE; prefix reuse; grammar-constrained generation)

## Measurements we have (desktop CPU; phone is slower)
- Real v4 on 139 prompts from the DPO file (10/kind): on call turns that should ask before speaking a private fact (speaker / company):
  17/20 asked, 3/20 leaked. Should-answer-directly turns: 28/30 right. 0 empty outputs. These pairs are mined from earlier failures, so hard.
- 20-turn phone-script replay with the exact app text: 19/20 sensible plans. Model miss: tip+split maths (returned only the tip).
- Latency: cold read of the ~1,250-token system prompt = 16 s (desktop); warm first word 0.7-1.4 s with ~1,240 tokens reused from the cache.
- Page-reading pipeline traced on the real "Jailer 2 release date" query: Bing answers, pages read, model copies the date. Weak spot: only one page opened.

## Bugs the harness had, found only by running real model output through it (all fixed since)
1. confirm() was a no-op: on speaker the model asked "say your private detail out loud?" and the app spoke it anyway.
2. confirm() inside `if found(...) { confirm; delete }` was skipped -> delete ran unasked.
3. Model wrote write() over an existing file without confirm -> overwrote.
4. Model invented a reminder time ("today 18:00" for "remind me about milk today") -> app used it (v2 wrote 10:00, app rolled to tomorrow).
5. MODE/AUDIO_ROUTE/TOOLS lines would have been sent to the older v2 model that was never trained on them.
6. Model with no TOOLS menu said say(cannot_know, future) for "when will Jailer 2 be released"; with a menu it searched.
7. Plan reader rejected dotted tool names (alarm.set); run_js needs input.now/tz added; plans up to 500 tokens (engine silently returned "" when prompt+reply > slot).

## Things NOT built yet (future list)
speaker-privacy backstop in code; RESULT re-plan turns; mail/consent connectors; most preferences; streaming say to TTS; saved prompt KV to disk;
safe download manager; earlier turns in the prompt (training data is single-turn, app sends last 2 plans).

## Ground rules for you
READ-ONLY: do not edit repo files, do not run gradle. You may read code, run python3 -I / grep, and read the docs above. Be concrete: cite file:line.
Draw on public industry practice (Anthropic's "Building effective agents", tool-design/ACI and context-engineering guidance, eval-driven development,
guardrails/permission models, constrained decoding, small-model fine-tuning practice). Say plainly where you are inferring rather than citing.
You are NOT the real Claude team and have no inside knowledge of how they work internally; do not claim it.
