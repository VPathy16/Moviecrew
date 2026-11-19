# R1 Safety and guardrails position (agenda item 3)

Paths relative to app/src/main/java/com/mealmate/app/. I read the code; I did not run it. Anything marked "infer" is reasoning, not a test.

## Verdict on current guardrails
Good bones: plan check before run, fail-closed unsupported tools, trash on delete, write-over-existing forced to ask (PlanRunner.kt:145, which fixed bug 3), set_pref USER_ONLY (Workspace.kt:80), untrusted SCREEN masking (UserTurn.kt:55-62), unknown route defaults to speaker (CallRoute.kt:~36). The weakness: **every privacy-relevant decision on a call still starts from a model-written `confirm`**. If Hanu skips it (3/20), no code notices. The runner enforces *what the model asked for*, not *what the policy requires*.

## Holes found by reading
1. **No speaker backstop.** `say(chat,{text})` goes straight out (PlanRunner.kt:~395; safeToSay at :445 only checks SecretFilter). A memory note or file content can be spoken on speaker with no confirm. The 17/20 number is the whole defence.
2. **"yes" hijack.** TurnEngine.kt:36-47 treats any utterance of 6 words or fewer that starts with yes/ok/sure/fine as consent (Connectors.kt:66-78). "okay what's on my calendar" resumes the pending delete and discards the new request. On a speaker, a bystander or TV saying "yes" also consents to the very thing the confirm protects. Also, a stale pending from a *different* topic still resumes within 3 min.
3. **Model-authored confirm text.** PlanRunner.kt:139 uses the model's question; `questionFor` (:157) is only the fallback. The model can ask "Is that okay?" before `delete(notes/tax.txt)`. The user never hears the target. Consent is meaningless if the prompt text is not code-generated for gated tools.
4. **SecretFilter fail-open on speech.** STT gives words: "my pin is four eight two one". WORD_AFTER (SecretFilter.kt:22) matches only "four" and masks that one word, leaving "eight two one" in the stored transcript (partial mask). Missed outright: "wifi password is x" (needs `password` directly before `is`), "password hunter2" (no verb), "security code 123", bare 12-digit Aadhaar (AADHAAR :33 needs separators), a card with one STT digit error (Luhn fails, :74), PAN, bank account, UPI IDs, API keys. Luhn and Verhoeff checks trade recall for precision in exactly the wrong direction for a spoken line.
5. **Web text is an unfiltered channel to the user's ears.** Passages go raw into the copy prompt (PlanRunner.kt:~304); only `Facts.isIn` gates it (:307), which proves the text *is on the page*, not that it is benign. An attacker page saying "refund line: call 98xxxx, share the code" is copied and spoken verbatim as a "short fact" (:~426) with no model wording and, on calls, no source. It cannot call tools, which is good (infer: injection into `plan()` is not possible since page text never reaches the plan prompt; confirm this stays true when RESULT re-plan turns are added, where it becomes the top risk).
6. **Logging inconsistency.** Trace.line uses Redactor.scrub, not SecretFilter (Trace.kt:71), and Trace.begin/line("turn","request «…»") logs raw user text (TurnEngine.kt:51). TurnTrace is SecretFilter-masked. The log is "shareable by the user", so a spoken PIN could ride out. Infer: depends on Redactor coverage, which I did not audit.
7. `remember` and `cal.add` are ungated; `confirm` before UNDOABLE is silently skipped (:138), so "confirm then alarm" never asks even if the model meant a privacy ask. Low risk today.

## Ranked changes
| # | Change | Effort | Impact |
|---|---|---|---|
| 1 | **Speaker backstop in `speak()`/safeToSay**: when channel=CALL and route != earpiece/bluetooth, and the line to be said overlaps a MEMORY NOTE, a file read, or a PII class (phone, address, amount, DOB, health words), and no approved confirm preceded it, replace with a code-generated confirm ("That's private. Say it out loud, or show it on screen?") and set Pending. Default to *show on screen* rather than speak. Turns 3/20 leaks into a deterministic rule. Keep the model's confirm as the happy path. | M | Highest |
| 2 | **Tighten consent**: pending resumes only on an exact short yes (<=3 words, no trailing content), else it is cancelled and the new utterance is planned. For gated or private-on-speaker, require a typed/tapped yes or a repeated explicit phrase; never resume off a bare "ok". | S | High |
| 3 | **Code-generate the confirm question for gated tools** from the next step's tool and resolved path (use `questionFor` always, append the model's wording only as context). | S | High |
| 4 | **SecretFilter v2**: number-words to digits pre-pass, keyword window ("pin|otp|cvv|password" within 3 tokens of any digit/word run), drop Luhn for 13-19 digit runs when a card word is near, accept unseparated Aadhaar when near "aadhaar", add PAN/IFSC/account/UPI/API-key shapes. Prefer over-masking; add a fuzz test set from STT-style strings. | M | High |
| 5 | **Treat web-copied text as untrusted on output**: reject copies containing digits+"call/send/share/code/click", URLs, or imperative verbs unless the question asked for them; always speak "According to <host>" on calls too. | S | Med |
| 6 | **One logging path**: route Trace.line and `log()` through SecretFilter.mask first, drop raw request text from Trace.begin. | S | Med |
| 7 | **Policy table in code** (tool x channel x route -> allow / confirm / refuse), checked in PlanCheck, so rules live in one auditable file, not spread across prompt, regex and runner. | M | Med, grows with mail/consent connectors |
| 8 | **Build the safety eval now**: replay the 999 DPO pairs plus adversarial STT secrets through *harness*, report leak rate after backstop (target 0 for the covered classes). | M | Enables 1 and 4 |

## Enforce in code vs trust the model
Code: consent, destructive actions, route policy, secret masking, logging, tool allowlist, ownership of the question text. Model: *intent* (what the user wants), *classification hints* (is this private), wording. The model should *raise* flags the code can also raise; it should never be the only thing that can.

## What to expect specialists to get wrong
They will treat the 85-90% as a training problem (more DPO, better prompt). A fine-tune cannot reach the 100% a privacy rule needs; the backstop must be deterministic, and it should be allowed to over-trigger (a needless "show on screen?" costs one second, a leak costs trust).
