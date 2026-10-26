# R1 Architect: judging the Hanu harness (paths under app/src/main/java/com/mealmate/app/local/)

I am citing public practice (Anthropic "Building effective agents": simple composable workflows, tool design/ACI, verify with code) from memory and inferring where noted. I have no inside knowledge of anyone's internals.

## Verdict
This is a plan-then-execute workflow with a code-owned verifier, which is the right shape for a 2B model at 13 tok/s. A ReAct loop would cost a model call per step (seconds each) and invite drift. Control flow belongs to the harness; the model only picks a route and fills slots. Most of the 7 bugs in the brief came from the gap between what the model wrote and what the harness enforced, not from the model itself.

## Good (keep)
- `PlanTools` port (PlanRunner.kt:17) and an injected clock (`now`, :67) give deterministic JVM tests with recorded plans.
- Verify-by-code: `Facts.isIn` for copied facts (PlanParts.kt:216, PlanRunner.kt:307), `numbersFrom` for spoken numbers (:436), `safeToSay` (:445), and the schedule guard against invented times (:370). These are the "evaluator in code" pattern and the best part of the design.
- Confirm as a real stop-and-resume (Pending, Connectors.kt:57; TurnEngine.kt:36-49), with the overwrite check done in code regardless of the model (:145).
- Grammar-constrained output, one branch, no loops, 8-step cap: bounded blast radius.
- Short-circuits that skip the model when code is surer: recall (TurnEngine:55), "one short fact" said verbatim (:426).

## Fragile
1. **Four registries of "what a tool is"** that must agree by hand: the Plan.kt:34 regex, `PlanCheck.RUNS` (PlanParts:119), the `step()` switch (PlanRunner:198), and `Connectors.TOOLS` plus menu strings (Connectors:15,40), alongside the team's gbnf and tools.json. Bug 7 (dotted names) was this drift. There is no arity or type check, so a malformed call such as `alarm.set()` just yields an empty slot and a generic question.
2. **Errors are `null`.** `step()` returns null for a failed search, a bad page, a bad compute, or a type mismatch (:200-209, :257, :281). `runCatching{}` hides the cause. The user sees SORRY or NOT_FOUND whatever failed, and the model never sees an observation. There is no repair path except the single `no_tool` retry (:72, TurnEngine:77). An unreadable plan (:76) or a plan truncated at the token limit dies at once.
3. **Confirm text is model-written** (:139) and PlanCheck only checks adjacency (PlanParts:140). The user can answer yes to "Is that okay?" and approve a different action than the one shown. `questionFor` (:158) exists but is only the fallback.
4. **Hidden execution inside `say`**: `speak()` runs `open()` and `extract()` on a `Hits` slot (:414). This is control flow after "plan done", it bypasses step tracing, and it can run extra network and LLM work.
5. **`runCatching` around suspend calls** (:208, :272; TurnEngine:55) swallows `CancellationException`. A hung-up call keeps running tools.
6. **No per-step timeout or turn budget**, and `open()` embeds every hit serially (:263-265).
7. **State is a volatile in-memory `pending`** (Turns.kt:80) with a 3-minute TTL. A process kill loses a half-run plan after side effects already happened. There is no effect journal, so a crash plus a retry can double-set an alarm.
8. **A refused or unreadable plan is still stored as history** (TurnEngine:81), which poisons the "last 2 plans" context.

## Ranked changes
| # | Change | Effort | Impact |
|---|---|---|---|
| 1 | **Speaker-privacy backstop in code**: a `PlanCheck` rule that marks private slots (speaker/company facts) and requires a confirm on CALL+speaker route regardless of the plan. Measured leak: 3/20. | M | Highest: this is the one live safety failure |
| 2 | **One `ToolSpec` registry**: name, arg types and arity, effect class (read / undoable / irreversible), confirm policy, executor. Derive RUNS, the menu, the step dispatch and the plan-check gates from it. Add a contract test that fuzzes plans from the gbnf through parse, check and run. | M | High: kills the drift class |
| 3 | **Typed `StepResult`** (Ok, Empty, Failed(reason), NeedsUser) instead of null, plus **one bounded re-plan** with a short RESULT line on recoverable failures (extract miss, unreadable or truncated plan). The harness decides when to re-plan, not the model. | M | High: this is the missing observation-to-action loop |
| 4 | **Harness-rendered confirmations**: build the question from the action and its args, and bind the approval to a hash of that action. Resume refuses if the plan differs. | S | High |
| 5 | **Trace-to-test replay**: every TurnTrace becomes a golden fixture. Add the 999 DPO pairs and the 139-prompt run as an end-state regression suite (what the user heard and which effects happened, not plan text). | M | High |
| 6 | **Cancellation, timeouts and a turn budget**: rethrow `CancellationException`, set per-tool deadlines, stop embedding every hit (rank by keywords first). | S | Medium |
| 7 | **Move `extract`/`open` out of `speak()`** into explicit auto-inserted steps, so everything that runs appears in the trace and the step cap. | S | Medium |
| 8 | **Persist `Pending` and an effect journal** (idempotency keys per act), so resume survives a process kill and nothing runs twice. Don't store refused plans as history. | M | Medium |

## Where the harness should own control flow
Tool choice stays with the model. Sequencing guards, confirmation wording, retries, time resolution, numbers and facts stay in code. Any rule currently expressed only in the prompt, or only in the DPO data, should have a code twin.
