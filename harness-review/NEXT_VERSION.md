# Next version: everything that is not in this one, and can we release this?

Branch `experiment/real-person-avatar`, state at commit after d61f2c7 (16 Oct 2026). Hanu v2 stays the default model; Hanu v4 is an opt-in model.

## Release verdict

| Question | Answer |
|---|---|
| Public release with **Hanu v4 as the default**? | **No.** Its own gates are not met (below). |
| Public release of the app with v2 as default and v4 opt-in? | **Not yet.** Blockers B1-B5 below. |
| Internal / tester **beta**, v2 default, v4 opt-in? | **Yes, after one phone pass** (B1) and cutting a release branch (B4). |

Why not public yet, in order of weight:
- **B1. v4 has never been seen running on a phone.** Everything about it was measured on a desktop CPU: cold prompt read 16 s (the phone will be slower), warm first word 0.7-1.4 s.
  Test builds 2-5 were sent but no phone report on v4 has come back; the only phone evidence is v2 screenshots. The harness changes (exact-yes consent, speaker backstop,
  asking for a made-up time, one-turn prompts, notes/files/reminder tools) also change v2's behaviour and have not been run on a phone.
- **B2. The 2.7 GB model download is unsafe for ordinary users.** It resumes and checks size and SHA-256, but has no Wi-Fi-only rule, no free-space check (about 3.5 GB needed),
  and no signed manifest with a version rule. Acceptable for testers (it sits behind a developer row), not for a public release.
- **B3. No release build has been made.** Release signing falls back to the debug key unless a release key is configured, and release builds minify (R8): the llama.cpp JNI,
  kotlinx serialization and the on-device engine have never been smoke-tested minified.
- **B4. The branch is 307 commits ahead of `main`** and carries experiments (real-person avatar and more). A release branch has to be cut and reviewed for what ships.
- **B5. The ship gate for v4 is not met.** Locked call-safety set (50): through the app 38/50, 0 leaks (model alone 37/50, 1 leak); 8 of 17 answerable cases refused or asked,
  4 of 15 "should ask" not asked. The team's own number for v4 on this set has not been compared; eval_hard, menu_eval_unseen, the scorer locks and the README were not in the folder.
  About a quarter of the 151 probe plans end in "I can't do that on the phone yet".

What is in good shape: 639 unit tests, all passing (the one that failed, LiveSessionTest, was a stale test and is fixed); the speaker backstop catches 146 of 146 labelled leaks on the DPO data with
no false blocks; every spoken line goes through one gate; secrets (including spoken digits) are masked in memory, tool arguments, spoken lines, transcripts and logs; a phone failure can be turned into a
no-model test; the pinned prompt/model pair is checked at load; v2 keeps its own trained format.

### Beta checklist (do before sending testers a build)
1. Phone pass on v4 with HANU_V4_TEST_SCRIPT.md (Moviecrew repo): note warm-up time, first-word time on turns 1 and 3, and any private line said on speaker without a yes.
2. Phone pass on v2 (default): alarm, timer, reminder (with and without a time), notes, "what reminders do I have", the speaker/earpiece privacy cases.
3. `assembleLiteRelease` with a real signing key; install it; run steps 1-2 on the minified build.
4. Cut `release/x.y` from the experiment branch; review the diff against main for anything that should not ship.
5. Show the download size and ask for Wi-Fi before the 2.7 GB download (the minimum of B2).

## Next version: backlog

### Safety and privacy
- Streaming `say` to TTS **after** the gate, per approved sentence (the gate runs on the whole plan today).
- Model-free fast path in **shadow mode** first (stop/cancel/yes/no/simple timer), shipping each rule at 99% agreement with the model, through the same gate.
- `RESULT:` re-plan turns, only the three trained forms (NEEDS_PERMISSION, NOT_AVAILABLE, results in SCREEN); needs consent state for connectors.
- SCREEN line sender for mail/notification/web text (the helper marks it untrusted and masks secrets; nothing sends it yet).
- Show-on-screen path for private lines in the **chat** is not needed (no one listens in), but the call screen needs a visible "private" style for OnScreen lines.

### Tools the model writes that the phone cannot run yet (by probe count)
1. Web forms: `script` and `navigate` + `submit` (8), including WhatsApp/SMS/email via `script`.
2. `recall` and `forget` (4), then the `forget_delete` bundle in the menu.
3. `set_layout` (3) and the preferences with nothing behind them: voice.language, reply.length, persona.formality, persona.name_for_user, avatar.style, home.order.
4. Messaging and mail connectors with consent: mail_search/mail.draft, msg.draft, outlook, drive, slack, teams, call.dial, contact.find (9+); each needs `[consent:x]` state and the safety gate.
5. Rest of CONNECTOR_LIST_v4: maps, rides, orders, bank, fitbit, photos, notion, github, upi.request, home.*, media, news, podcast, translate, etc.
6. A real clock-alarm cancel (Android has no API; a "reminder-backed alarm" would make alarms cancellable).

### Model, prompt and speed
- Disk KV snapshot of the system prompt (keyed by rendered prompt + model sha) so a restart doesn't re-read 1,250 tokens (16 s on desktop, longer on a phone).
- Extractive copy: code picks candidate spans, the model answers with one number (gate on evals: exact-fact accuracy and false-NONE rate against `Facts.isIn`).
- Arithmetic in code for the tip/split class of questions (v4 returned only the tip); typed step results in the runner (honest errors) beyond the per-step trail.
- Thermal governor and a hard cap of two model decodes per call turn.
- Earlier turns: v4 gets none (training is single-turn); v2 keeps two. Revisit once the team trains multi-turn rows.
- Speed: first-word on a phone for v4 vs v2 (turns.csv for the P4 test).

### Evals and observability
- Run the locked sets in full when the team adds the missing files: eval_hard (21), menu_eval_unseen (65), the scorer-lock hash files, the everyday-query and probe scorers, the README's locked settings.
- Reproduce the team's reported numbers for v4 on the same files before trusting the harness-level numbers; the DPO pairs are not a holdout.
- Holdout from fresh phone traces; the fuzz keeps all rejected DPO plans as a no-model regression set.
- Phone traces: keep "Record full prompts" off by default; a documented way to export a turn log and run `tools/trace2case.py`.

### Release engineering (item 10 and B2-B4)
- Safe downloads: Wi-Fi only, resume, free-space check, signed manifest with a version number that refuses older.
- mmap on, never `--mlock`, imatrix file only: confirm in the engine settings on a phone.
- Release signing, R8 keep rules for JNI/serialization, a Play-policy review (on-device model download size, voice/call permissions).
- Merge or cut the release branch; decide what from the avatar experiment ships.

### Open questions for the training team
- Was any of the 999 DPO pairs ever outside v4's training mix? (Answered: all were trained on.) So what is the clean holdout for the 3-in-20 speaker-privacy sample: the locked call-safety set only?
- The 6 odd DPO rows (v3_sample, TOOLS first) are understood and excluded.
- Their reported v4 numbers per locked set, and the scorer-lock hashes, to compare against the replay.
- `RESULT: FAILED(...)` needs training rows before the app can send it.
- "Slower/faster" speed changes need the current speed shown to Hanu: a new line label, so it needs training too.

### Known limitations in this version (say them in the release notes)
- Hanu v4 is opt-in and needs a 2.7 GB download and about 3 GB of free memory; the first answer after launch can be slow while the prompt warms up.
- Clock alarms cannot be listed or cancelled from the app (she keeps a note of the ones she set and says so).
- Only `voice.speed` of the settings Hanu can change is applied.
- On a speaker call, private notes are put on the screen instead of spoken unless the user says yes (or says they are alone).
