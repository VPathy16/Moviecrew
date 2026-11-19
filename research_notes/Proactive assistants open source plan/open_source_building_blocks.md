# Open-source building blocks for "Boop" (Android-native Kotlin/Compose AI assistant), as of late October 2026

> **How the data was collected.** Repo metadata (license SPDX, star count, last push date, most recent tags) was fetched on 2026-10-24/26 from the ecosyste.ms GitHub mirror (`repos.ecosyste.ms/hosts/GitHub/repositories/<owner>%2F<repo>`), because the GitHub API was blocked in this environment. Package versions come from Maven Central `maven-metadata.xml`, Google Maven `group-index.xml`, PyPI JSON and the npm registry. LICENSE and README text was read through jsDelivr's GitHub mirror (`cdn.jsdelivr.net/gh/...`). Star counts are snapshots and drift daily. Where ecosyste.ms "latest tag" disagrees with a package registry, the registry is treated as authoritative and the conflict is noted. **License flags:** ⚠️ = copyleft, non-commercial, source-available or custom terms that conflict with permissive distribution.

---

## 1. Personal agent platforms: OpenClaw and other open personal assistants

### Takeaway
OpenClaw (MIT, about 392k stars, near-daily releases) is the reference design for a personal agent. It has a single Gateway control plane, pluggable chat channels, device "nodes" (Android among them), sub-agent sessions, scheduled automations and a skills registry. It is TypeScript and server-shaped, so Boop should take its **protocol and orchestration ideas and its security lessons, not its code**. The record so far includes a one-click RCE, more than 21k exposed instances and about 12% malicious skills in ClawHub at one point. Among the alternatives, Google AI Edge Gallery (Apache-2.0, Kotlin) is the most directly reusable Android codebase. Watch for Khoj (AGPL-3.0), Open WebUI (custom branding license) and Panda/blurr (personal-use license).

### Cited Findings
**OpenClaw: license, maturity, governance**
- `openclaw/openclaw`: MIT, 392,267 stars, last push 2026-10-17, latest tag `v2026.10.10-beta.2` (2026-10-17). Several release tags appear per day. Description: "The AI that really does things. Any OS. Any Platform." — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/openclaw%2Fopenclaw)
- npm `openclaw` latest is 2026.10.7 (published 2026-10-24), MIT — [npm registry](https://registry.npmjs.org/openclaw)
- ClawHub, the skill and plugin registry for OpenClaw: MIT, 9,513 stars, prod deploy `v2026.10.06.1` — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/openclaw%2Fclawhub)
- Creator Peter Steinberger announced his move to OpenAI on 2026-02-15. Sam Altman said OpenClaw would live on in a foundation as open source with OpenAI support. Later reporting describes an independent 501(c)(3) OpenClaw Foundation with sponsors (OpenAI, NVIDIA, Microsoft, Tencent), not owners — [MacStories](https://www.macstories.net/linked/openclaw-creator-peter-steinberger-joins-openai/); [Trending Topics](https://www.trendingtopics.eu/opwnclaw-foundation-launches-with-openai-nvidia-microsoft-and-tencent-as-sponsors/); [OpenSourceForU](https://www.opensourceforu.com/?p=96842)
- OpenClaw mobile apps were reportedly released on 2026-06-29. The Android app acts as a secure "node" for chat, voice, approvals and device-aware automation. Reviews were mixed: a 2.2-star Play rating, with pairing failures cited. v2026.7.3 added a Wear OS companion. These are secondary and mirror sources — [Let's Data Science](https://letsdatascience.com/news/openclaw-launches-android-companion-app-for-agents-2044ee21); [APKMirror listing, publisher "openclaw-foundation"](https://www.apkmirror.com/apk/openclaw-foundation/openclaw/openclaw-2026-6-9-release/openclaw-2026-6-9-2-android-apk-download/)

**OpenClaw: architecture (primary docs)**
- **Gateway:** a single long-lived process owns every messaging surface (WhatsApp via Baileys, Telegram via grammY, Slack, Discord, Signal, iMessage, WebChat). It binds `127.0.0.1:18789` by default and also serves canvas widget documents under `/__openclaw__/canvas/` — [OpenClaw docs: Architecture](https://docs.openclaw.ai/concepts/architecture)
- **Wire protocol:** a typed WebSocket API with JSON frames. The first frame must be `connect`, or the socket is hard-closed. Messages are `{type:"req",id,method,params}`, `{type:"res",id,ok,payload|error}` and `{type:"event",event,payload,seq?,stateVersion?}`. Events are not replayed, so clients refresh after gaps. `send` and `agent` require idempotency keys, backed by a dedupe cache. Schemas are written in TypeBox, emitted as JSON Schema, and Swift models are generated from that — [Architecture](https://docs.openclaw.ai/concepts/architecture)
- **Nodes:** macOS, iOS, Android and headless nodes connect with `role:"node"`, declare capabilities in `connect`, and expose commands such as `camera.*`, `screen.record` and `location.get` — [Architecture](https://docs.openclaw.ai/concepts/architecture). The design principle: "the agent's brain lives on the Gateway; device capabilities live on nodes" — [HackMD deep dive](https://hackmd.io/Z39YLHZoTxa7YLu_PmEkiA)
- **Auth and pairing:** every client sends a device identity and signs a server-issued challenge. New devices need pairing approval and then receive a device token. Loopback connections can be auto-approved, while LAN and tailnet connections always need explicit approval. `gateway.auth.mode:"none"` disables shared-secret auth — [Architecture](https://docs.openclaw.ai/concepts/architecture)
- **Scheduler:** timed work runs through one `GatewayScheduler`. After the host sleeps, overdue jobs run once and missed periodic ticks are coalesced — [Architecture](https://docs.openclaw.ai/concepts/architecture)
- **Heartbeats are retired.** Heartbeat monitoring "now uses ordinary automation jobs". Doctor converts each `HEARTBEAT.md` or `tasks:` block into an editable job with its own schedule, prompt, scratch and run history. Explicit setup creates one "Proactive check" job that "runs every 30 minutes unless the provider supplies a different initial cadence." Doctor handles heartbeat shapes shipped from July 2026 onward — [OpenClaw docs: Heartbeat migration](https://docs.openclaw.ai/gateway/heartbeat)
- **Automations** cover cron schedules, webhooks, Gmail Pub/Sub triggers, "stream sources, pacing, and condition triggers", and delivery modes (announce, webhook, none) — [OpenClaw docs index (llms.txt)](https://docs.openclaw.ai/llms.txt)
- **Sub-agents:**
  - `sessions_spawn` returns `runId` and `childSessionKey` without waiting. Children are hidden unless spawned with `visible:true`. Context is isolated by default, and `context:"fork"` copies the parent transcript.
  - Children inherit the parent's tool policy, sandbox, concurrency limits and timeout. The default max spawn depth is 5.
  - `sessions_yield` ends the parent's turn so that the next message can be the child's completion event. `subagents` can wait on or cancel runs.
  - `sessions_send` delivers agent-to-agent messages tagged `[Inter-session message ... isUser=false]`, so the receiver treats them as data, not user instructions.
  - Cross-agent visibility scopes are `self`, `tree`, `agent` and `all`, and the default is `all`.
  - [OpenClaw docs: Session tools](https://docs.openclaw.ai/concepts/session-tool)
- **Other subsystems** (doc index only): multi-agent routing via agent bindings to channel accounts, SOUL.md personality files, a per-agent workspace, a pluggable "context engine" (compaction and sub-agent lifecycle), and "active memory". Active memory is a blocking sub-agent that recalls history only when rule-based recall is insufficient, with LanceDB as one backend. Sandbox backends are Docker, Podman, SSH, OpenShell and Crabbox, with workspace access modes none/ro/rw — [docs index](https://docs.openclaw.ai/llms.txt)

**OpenClaw: security model and known issues**
- **Trust model:** "one trusted boundary per gateway: a single operator, or a team whose members trust each other". "OpenClaw is not a hostile multi-tenant security boundary." Defaults are a loopback bind, pairing codes for unknown DM senders, and mention-gated, allowlisted groups. Container images default to an *exposed* bind. "Agents with message-tool access can send across conversations and channel providers by default." — [OpenClaw docs: Security](https://docs.openclaw.ai/gateway/security)
- **CVE-2026-25253 (CVSS 8.8):** a one-click RCE. The Control UI trusted a `gatewayUrl` query parameter and auto-connected, which leaked the auth token. Fixed in 2026.1.29 (2026-01-30). The Docker sandbox could be escaped by using the stolen token to disable exec approvals and set `tools.exec.host` to `gateway`. Command-injection CVEs CVE-2026-24763 and CVE-2026-25157 followed on 2026-02-02, as did indirect prompt injection via browsing (CVE-2026-22708) — [Adversa AI](https://adversa.ai/blog/openclaw-security-101-vulnerabilities-hardening-2026/)
- **Further flaws from the same writeup:** localhost connections were auto-approved, so a same-host reverse proxy bypassed auth. Requests without an Authorization header fell back to Guest mode, which still allowed a Python REPL. The WebSocket server accepted any origin. mDNS broadcast filesystem paths and hostnames — [Adversa AI](https://adversa.ai/blog/openclaw-security-101-vulnerabilities-hardening-2026/)
- **Supply chain ("ClawHavoc"):** Koi Security audited 2,857 ClawHub skills and found 341 malicious, about 12% (published 2026-02-03). 335 of them delivered the AMOS macOS stealer through a fake "Prerequisites" section — [Adversa AI](https://adversa.ai/blog/openclaw-security-101-vulnerabilities-hardening-2026/)
- **Exposure and related incidents:** Censys counted 21,639 internet-exposed instances on 2026-01-31. The Moltbook social network (built around OpenClaw agents) exposed about 1.5M API tokens through Supabase with RLS disabled (found by Wiz on 2026-01-31) — [Adversa AI](https://adversa.ai/blog/openclaw-security-101-vulnerabilities-hardening-2026/)
- An academic taxonomy found the Channel Input Interface accounts for 119 advisories (25.3%). It also found that mutable platform identity fields were used as security-relevant policy keys — [arXiv 2603.27517](https://arxiv.org/html/2603.27517v2); see also [arXiv 2603.12644](https://arxiv.org/html/2603.12644v1)

**OpenClaw-inspired alternatives**
- IronClaw (`nearai/ironclaw`): Apache-2.0, Rust, 12,662 stars, v1.4.1 (2026-09-29). "Agent OS focused on privacy, security and extensibility" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/nearai%2Fironclaw)
- nanobot (`HKUDS/nanobot`): MIT, Python, 49,210 stars, v0.3.5 (2026-09-15). "Ultra-lightweight… personal AI agent" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/HKUDS%2Fnanobot)

**Other open personal assistants**
- Leon (`leon-ai/leon`): MIT, TypeScript, 17,582 stars, last push 2026-10-12. The latest tags are component tags from 2026-02-19 (`tcp-server_v2.0.0`, `python-bridge_v1.4.0`) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/leon-ai%2Fleon)
- OpenVoiceOS (`OpenVoiceOS/ovos-core`, Mycroft successor): Apache-2.0, Python, 296 stars on the core repo, frequent alpha tags (`3.6.1a1`, 2026-09-16) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/OpenVoiceOS%2Fovos-core)
- Home Assistant core: Apache-2.0, 91,619 stars, 2026.10.2 (2026-10-16). The **Home Assistant Companion for Android** (`home-assistant/android`) is Apache-2.0 **Kotlin**, 3,978 stars, with monthly releases (2026.10.1 on 2026-10-06) — [ecosyste.ms core](https://repos.ecosyste.ms/hosts/GitHub/repositories/home-assistant%2Fcore); [ecosyste.ms android](https://repos.ecosyste.ms/hosts/GitHub/repositories/home-assistant%2Fandroid)
- Jan (`janhq/jan`): 44,978 stars, Rust/Tauri, v0.8.6 (2026-10-09). ecosyste.ms lists the license as "other", but the LICENSE file says Apache License 2.0 (Menlo Research) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/janhq%2Fjan); [LICENSE](https://cdn.jsdelivr.net/gh/janhq/jan@main/LICENSE)
- ⚠️ Open WebUI: 156,278 stars, v0.12.3 (2026-10-16). Since v0.6.6 (2025-04-19) it uses a modified BSD-3 license with a **branding clause**: you may not alter or hide "Open WebUI" branding unless the deployment has 50 or fewer users per rolling 30 days, or you have an enterprise license. A CLA is required for contributions. Code up to v0.6.5 remains BSD-3. Nixpkgs marks the license non-free — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/open-webui%2Fopen-webui); [Open WebUI license docs](https://docs.openwebui.com/license/); [nixpkgs commit](https://code.ornl.gov/nix/nixpkgs/-/commit/ac3ae15f554aadd84e29c7c0a73b9fa54f568721)
- ⚠️ Khoj (`khoj-ai/khoj`): **AGPL-3.0**, 37,754 stars. The last tag was `2.0.0-beta.28` (2026-03-26), the last push was 2026-08-02, and the last stable PyPI release was 1.42.10 (2025-07-15). Activity is slowing — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/khoj-ai%2Fkhoj); [PyPI](https://pypi.org/pypi/khoj/json)
- Letta (ex-MemGPT): Apache-2.0, 25,171 stars; see section 3.

**Android-native open assistants and LLM apps (code you can actually reuse)**
- **Google AI Edge Gallery** (`google-ai-edge/gallery`): Apache-2.0, **Kotlin**, 25,044 stars, 1.0.20 (2026-10-06), roughly monthly releases. Features include "Agent Skills" (tools such as Wikipedia, maps and "rich visual summary cards"), "Mobile Actions", which provides offline device control from a fine-tune of FunctionGemma 270m, Audio Scribe, Thinking Mode, and EmbeddingGemma 2 on-device semantic search — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/google-ai-edge%2Fgallery); [README](https://cdn.jsdelivr.net/gh/google-ai-edge/gallery@main/README.md)
- SmolChat-Android (`shubham0204/SmolChat-Android`): Apache-2.0, Kotlin, 837 stars, v15 (2026-04-17). Runs any GGUF model on-device via llama.cpp — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/shubham0204%2FSmolChat-Android)
- PocketPal AI: MIT, TypeScript/React Native, 8,708 stars, v1.18.0 (2026-09-25) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/a-ghorbani%2Fpocketpal-ai). Maid: MIT, 2,733 stars, v3.0.0 (2026-03-10) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/Mobile-Artificial-Intelligence%2Fmaid)
- ⚠️ Panda / blurr (`Ayush0Chaudhary/blurr`), "This app can now use Android, just like a human": Kotlin, 980 stars, last push 2026-01-13. The license is a **"PERSONAL USE LICENSE"**, so it is **not open source** for redistribution — [LICENSE](https://cdn.jsdelivr.net/gh/Ayush0Chaudhary/blurr@main/LICENSE); [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/Ayush0Chaudhary%2Fblurr)

### Inferences
- **What Boop should borrow from OpenClaw (ideas and design, not code):**
  1. Its sub-agent semantics map almost one-to-one onto Boop's helper agents with per-helper threads:
     - Isolated vs forked context.
     - Inherited tool policy and sandbox.
     - A depth limit.
     - A yield-and-announce completion model.
     - Visibility scopes.
     - Inter-agent messages tagged `isUser=false`. This tag is a cheap prompt-injection mitigation Boop should copy.
  2. Its "heartbeat to automation job" migration confirms that proactivity is best modelled as ordinary scheduled jobs with their own prompt, scratch and run history. For Boop that means WorkManager periodic jobs plus a "Proactive check" default, not a special heartbeat subsystem.
  3. The typed request/response/event protocol (connect-first handshake, idempotency keys, no event replay) is a good template if Boop ever exposes a desktop or watch companion, or lets the phone act as a node for a remote agent.
  4. The security failures are a checklist of what not to do:
     - Never trust URL or deep-link parameters for endpoints or tokens.
     - Never auto-approve "local" callers.
     - Fail closed, not to a guest mode.
     - Treat a skill marketplace as a malware vector: sign and review skills, show permissions, and never auto-run "prerequisites".
     - Do not key policy on mutable channel identity fields.
- OpenClaw's Android app is a thin node of a desktop/server Gateway. Boop is the reverse, an on-phone brain. Boop's on-device-first, privacy-gateway design is a genuine differentiator against OpenClaw's 2.2-star Android experience. That rating comes from a single secondary source.
- The Google AI Edge Gallery codebase (Apache-2.0, Kotlin, Google-maintained) is the best place to copy Android code for on-device model download and management, skills/tool UI, FunctionGemma "mobile actions" and audio transcription.
- The HA Companion for Android (Apache-2.0 Kotlin) is a mature reference for Android assistant-integration plumbing. Its specific Assist/voice classes were not verified in this session.
- Avoid copying code from Khoj (AGPL), Open WebUI after v0.6.5 (branding clause) and Panda/blurr (personal-use) into a permissively licensed app.

### Gaps
- No primary-source star count or Play listing for the OpenClaw Android app. Its 2026-06-29 launch date and 2.2-star rating come only from secondary sources.
- I could not verify OpenClaw's Android node permissions model or any Android-specific CVE. Researchers did not catalogue one.
- Leon 2.0, OVOS and Home Assistant Assist pipeline internals (wake word → STT → intent → TTS, the Wyoming protocol) were not researched in depth in this session.
- The OpenClaw skills format details (SKILL.md, compatibility with Anthropic Agent Skills) were not fetched. The docs page `clawhub/skill-format` exists.

---

## 2. Agent frameworks usable from Kotlin/JVM on Android

### Takeaway
**JetBrains Koog (Apache-2.0, 1.3.0 in Sep 2026) is the only mature agent framework that explicitly targets Android.** Its changelog lowered `minSdk` from 35 to 23. It has MCP integration, sub-graphs and sub-tasks, planners, checkpoint persistence, history compression, long-term memory and OpenTelemetry. The official **MCP Kotlin SDK** (0.15.0, Kotlin Multiplatform, relicensing to Apache-2.0) is the right MCP layer. LangChain4j and Google ADK Java are healthy, but they are JVM-server-first, with reported Android breakages for LangChain4j. Embabel and Spring AI are server-side Spring stacks.

### Cited Findings
- **Koog** (`JetBrains/koog`): Apache-2.0, Kotlin, 4,617 stars, last push 2026-10-16 — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/JetBrains%2Fkoog)
  - Maven Central `ai.koog:koog-agents` and `ai.koog:agents-core` latest is **1.3.0** (metadata updated 2026-09-23) — [Maven metadata](https://repo1.maven.org/maven2/ai/koog/koog-agents/maven-metadata.xml)
  - The README feature list says "Deploy agents across JVM, JS, WasmJS, **Android**, and iOS targets". The same README's "Supported targets" line omits Android, so it is internally inconsistent — [README](https://cdn.jsdelivr.net/gh/jetbrains/koog@develop/README.md)
  - The changelog settles it: "**Lower Android minSdk**: Decreased Android `minSdk` from 35 to 23" (#2059). LLM clients take a pluggable `KoogHttpClient.Factory`, with a Ktor default "auto-discovered on JVM/Android" and OkHttp pluggable. Planners (`GOAPPlanner`, `SimpleLLMPlanner`) moved to `agents-planners`. `subgraphWithTask` and `subtask` exist. Checkpoint persistence works with `runFromCheckpoint`, including for planner agents. The `AgentMemory` feature was replaced by `LongTermMemory`. The 1.0 line removed all deprecated APIs — [CHANGELOG](https://cdn.jsdelivr.net/gh/JetBrains/koog@develop/CHANGELOG.md)
  - The README also lists MCP tool integration, retries plus persistence, "intelligent history compression", OpenTelemetry exporters (Langfuse, W&B Weave), RAG and memory, and streaming with parallel tool calls — [README](https://cdn.jsdelivr.net/gh/jetbrains/koog@develop/README.md)
  - A third-party note says JetBrains guarantees no breaking changes to stable modules for at least one year — [DEV Community](https://dev.to/karanverma/building-practical-ai-agents-with-koog-10-an-engineers-perspective-30dk)
- **Official MCP Kotlin SDK** (`modelcontextprotocol/kotlin-sdk`): 1,468 stars. Maven `io.modelcontextprotocol:kotlin-sdk` and `kotlin-sdk-client` latest is **0.15.0** (2026-07-28). The JVM jars are small: client 173 KB, core 1.36 MB — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/modelcontextprotocol%2Fkotlin-sdk); [Maven metadata](https://repo1.maven.org/maven2/io/modelcontextprotocol/kotlin-sdk/maven-metadata.xml)
  - License: "The MCP project is undergoing a licensing transition from the MIT License to the Apache License, Version 2.0… All new code… licensed under Apache-2.0" — [LICENSE](https://cdn.jsdelivr.net/gh/modelcontextprotocol/kotlin-sdk@main/LICENSE)
  - It is Kotlin Multiplatform (JVM 11+, Native, JS, Wasm) with stdio, SSE, **Streamable HTTP** and WebSocket transports. Clients are built on Ktor (`StreamableHttpClientTransport`) — [README](https://cdn.jsdelivr.net/gh/modelcontextprotocol/kotlin-sdk@main/README.md)
  - The older `JetBrains/mcp-kotlin-sdk` is archived (MIT, 0.1.0, Dec 2024) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/JetBrains%2Fmcp-kotlin-sdk)
- **LangChain4j**: Apache-2.0, Java, 13,258 stars. Maven `dev.langchain4j:langchain4j` is **1.22.0** (2026-10-07), with roughly weekly releases (1.20.1 on 09-25, 1.20.2 on 09-28, 1.21.0 on 10-02) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/langchain4j%2Flangchain4j); [Maven metadata](https://repo1.maven.org/maven2/dev/langchain4j/langchain4j/maven-metadata.xml)
  - Reported Android issues include a regex error in `DefaultPromptTemplateFactory` on Android and a missing `native/lib/linux-aarch64/libtokenizers.so` on the Android platform. Fix status is unknown — [ecosyste.ms issue index](https://opencollective.ecosyste.ms/collectives/langchain4j/issues?page=9)
- **Google ADK for Java** (`google/adk-java`): Apache-2.0, 1,754 stars. Maven `com.google.adk:google-adk` is **1.13.0** (2026-10-21), with releases roughly every two weeks. A2A integration is documented. The Python ADK is Apache-2.0, has 21,926 stars and is at v2.12.0 — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/google%2Fadk-java); [Maven metadata](https://repo1.maven.org/maven2/com/google/adk/google-adk/maven-metadata.xml); [README](https://cdn.jsdelivr.net/gh/google/adk-java@main/README.md)
- **Embabel** (`embabel/embabel-agent`): Apache-2.0, Kotlin, 4,524 stars, v1.5.3 (2026-10-05). "Agent framework for the JVM" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/embabel%2Fembabel-agent); [Maven metadata](https://repo1.maven.org/maven2/com/embabel/agent/embabel-agent-api/maven-metadata.xml)
- **Spring AI**: Apache-2.0, 9,560 stars, 2.0.0 GA (2026-06-12), 2.1.0-RC1 on Maven (2026-10-22) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/spring-projects%2Fspring-ai); [Maven metadata](https://repo1.maven.org/maven2/org/springframework/ai/spring-ai-model/maven-metadata.xml)
- **A2A protocol** (`a2aproject/A2A`): Apache-2.0, 26,200 stars, v1.0.0 (2026-03-12), v1.0.1 (2026-05-28) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/a2aproject%2FA2A)
- **Google AI Edge on-device agent SDKs** on Google Maven: `com.google.ai.edge.localagents:localagents-fc` (function calling) at 0.1.0 and `localagents-rag` at 0.3.0 — [Google Maven group index](https://dl.google.com/android/maven2/com/google/ai/edge/localagents/group-index.xml)

### Inferences
- **Shortlist:**

| Component | License | Maturity | Android fit | What to borrow |
|---|---|---|---|---|
| Koog 1.3.0 | Apache-2.0 | 4.6k★, releases every ~1–2 months | **Good**: official Android target, minSdk 23, OkHttp pluggable | The strategy-graph and subgraph model for helper agents, checkpoint/persistence for long WorkManager jobs, history compression, the OpenTelemetry hooks. Could replace parts of Boop's own loop or serve as a reference |
| MCP Kotlin SDK 0.15.0 | MIT→Apache-2.0 | 1.5k★, monthly | **Good**: KMP, Ktor | Use it directly for the MCP client, if Boop isn't already on it, to track spec changes (Streamable HTTP, auth, MCP Apps) |
| LangChain4j 1.22 | Apache-2.0 | 13k★, weekly | **Fair/risky**: JVM-server focus, reported Android bugs | Ideas: AI Services, structured outputs, RAG pipelines |
| ADK Java 1.13 | Apache-2.0 | 1.8k★, biweekly | Unverified on Android | Multi-agent patterns (sequential, parallel, loop agents), the A2A bridge, eval tooling |
| Embabel 1.5.3 / Spring AI 2.x | Apache-2.0 | active | **Poor**: Spring server stack | GOAP planning ideas (Embabel); a server-side relay if Boop ever needs one |
| AI Edge localagents-fc/rag | (Google Maven; license not checked) | early (0.1–0.3) | Native Android | On-device function calling and RAG with Gemma/LiteRT |

- Boop already has its own multi-provider agent loop. The lowest-risk path is to keep that loop and adopt Koog **selectively**: its persistence and checkpoint concepts, history compression and subgraph patterns. A wholesale rewrite would cost more than it gains.
- Use A2A only if Boop wants its helpers to interoperate with external agents. Internally, OpenClaw-style session tools are simpler.

### Gaps
- No primary confirmation that ADK Java runs on Android: dependency footprint, Java 17 requirements, gRPC/Netty pulls.
- Koog's exact APK size impact and Ktor/kotlinx-serialization transitive footprint were not measured.
- The license of the AI Edge localagents artifacts was not checked.
- Embabel's dependency on Spring is inferred from its positioning and was not verified from its POM.

---

## 3. Memory: mem0, Letta, Zep/Graphiti

### Takeaway
All the leading memory projects are permissively licensed (Apache-2.0 or MIT) but are **Python/TypeScript servers**. None runs on-device on Android. Zep Community Edition is deprecated, and Graphiti is Zep's self-host path, but it needs a graph database. For Boop, the realistic choices are to borrow memory *designs* (mem0's extract/update pipeline, Letta's memory blocks, OpenClaw's escalating "active memory" sub-agent) and implement them on-device with SQLite plus a vector extension or the AI Edge RAG SDK. Alternatively, Boop could offer an optional self-hosted mem0 or Graphiti server.

### Cited Findings
- **mem0** (`mem0ai/mem0`): Apache-2.0, 67,564 stars, v2.2.1 (PyPI 2026-09-25), with a TS SDK `ts-v3.3.1`. A self-hosted server runs via `docker compose`, and auth has been on by default since a recent upgrade — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/mem0ai%2Fmem0); [PyPI](https://pypi.org/pypi/mem0ai/json); [README](https://cdn.jsdelivr.net/gh/mem0ai/mem0@main/README.md)
  - mem0 claims 92.5 on LoCoMo (up from 71.4), but the README notes the scores reflect "Mem0's managed platform, which includes proprietary optimizations not available in the open-source" version. Its eval framework is open — [README](https://cdn.jsdelivr.net/gh/mem0ai/mem0@main/README.md)
- **Letta** (ex-MemGPT): Apache-2.0, 25,171 stars. PyPI `letta` is 0.34.12 (2026-10-12). ecosyste.ms tags show only 0.16.8 (2026-05-14), which conflicts, so PyPI is taken as current. It offers an "App Server for local or self-hosted agents" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/letta-ai%2Fletta); [PyPI](https://pypi.org/pypi/letta/json); [README](https://cdn.jsdelivr.net/gh/letta-ai/letta@main/README.md)
- **Zep Community Edition** is deprecated and unsupported. Zep points users to Zep Cloud (which has a free tier) or the open-source Graphiti — [Zep deprecation notice](https://help.getzep.com/ce-deprecation-notice)
  - The `getzep/zep` repo (Apache-2.0, 4,963 stars) is now "Examples, Integrations, & More" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/getzep%2Fzep)
- **Graphiti** (`getzep/graphiti`): Apache-2.0, 31,987 stars. `graphiti-core` is 0.31.2 (2026-10-20), and there is an MCP server, mcp-v1.1.1 (2026-10-15). It builds real-time temporal knowledge graphs. The Kuzu backend is reportedly deprecated, leaving Neo4j, FalkorDB and Neptune — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/getzep%2Fgraphiti); [PyPI](https://pypi.org/pypi/graphiti-core/json); [developersdigest summary](https://www.developersdigest.tech/agent-memory/graphiti)
- **Cognee**: Apache-2.0, 32,561 stars, v1.6.3 (2026-10-07) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/topoteretes%2Fcognee). **supermemory**: MIT, 31,253 stars, "can be run fully locally" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/supermemoryai%2Fsupermemory)
- **On-device building blocks:**
  - sqlite-vec: Apache-2.0, 8,195 stars. It is still alpha (v0.1.10-alpha.4, 2026-05-18) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/asg017%2Fsqlite-vec)
  - Google AI Edge RAG SDK: `localagents-rag` 0.3.0 — [Google Maven](https://dl.google.com/android/maven2/com/google/ai/edge/localagents/group-index.xml)
  - EmbeddingGemma 2 on-device semantic search, demonstrated in AI Edge Gallery — [Gallery README](https://cdn.jsdelivr.net/gh/google-ai-edge/gallery@main/README.md)
  - Koog `LongTermMemory` — [Koog CHANGELOG](https://cdn.jsdelivr.net/gh/JetBrains/koog@develop/CHANGELOG.md)
- **OpenClaw "active memory":** deep history recall that escalates only when rule-based recall is insufficient. It is implemented as a blocking sub-agent with recall tools and supports LanceDB — [OpenClaw docs index](https://docs.openclaw.ai/llms.txt)

### Inferences
- **Shortlist:**

| Component | License | Maturity | On-device? | Borrow |
|---|---|---|---|---|
| mem0 OSS | Apache-2.0 | 67k★, frequent | No (Python/TS server) | The memory extraction → dedupe/update → retrieval pipeline design. Optional self-host backend |
| Letta | Apache-2.0 | 25k★, active | No (server) | Memory-block abstraction (core/archival), self-editing memory tools |
| Graphiti | Apache-2.0 | 32k★, very active | No (needs graph DB) | Temporal fact model (valid-from/valid-to edges) for "what changed" memory |
| sqlite-vec / AI Edge RAG SDK | Apache-2.0 / Google | alpha / 0.3 | **Yes** | Actual on-device vector store |
| Koog LongTermMemory | Apache-2.0 | 1.3.0 | **Yes** (Kotlin) | Drop-in if Boop adopts Koog |

- Boop's privacy gateway (references instead of raw PII) fits mem0-style memory well: store memories with PII references, not raw values.
- Do not treat mem0's 92.5 LoCoMo figure as achievable with the open-source build.

### Gaps
- No verified data on Letta's current memory-block/sleeptime-agent APIs in 2026.
- The Graphiti Kuzu deprecation comes from a secondary source.
- No benchmark comparing on-device memory approaches on Android.

---

## 4. Agent-drawn UI: A2UI and its Compose renderer, MCP Apps / MCP-UI, OpenAI Apps SDK, generative UI

### Takeaway
There are now two complementary open standards:
- **A2UI** (Google, Apache-2.0): declarative JSON that the client renders with *native* components. Android has official AndroidX alpha libraries, `androidx.a2ui` and `androidx.a2ui.compose` at 1.0.0-alpha02 (2026-10-21). This is the natural fit for Boop's result cards.
- **MCP Apps** (official MCP extension since January 2026, co-authored by Anthropic, OpenAI and the MCP-UI creators): MCP servers ship HTML UIs as `ui://` resources rendered in a sandboxed iframe. Boop would host these in a locked-down WebView.

Supporting both lets Boop render native cards from its own agents and third-party UIs from MCP servers such as Swiggy, Zomato and Zerodha.

### Cited Findings
- **A2UI spec and repo** (`a2ui-project/a2ui`, formerly `google/A2UI`): Apache-2.0, 16,757 stars, last push 2026-10-21, tags including `python/a2ui-agent-sdk/v0.9.0` (2026-10-17) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/a2ui-project%2Fa2ui)
  - The README states the current production release is **v0.9.1**, with **v1.0 a release candidate** and v0.8 legacy. a2ui.org labels versions differently (a conflict) — [GitHub](https://github.com/google/A2UI); [a2ui.org](https://a2ui.org/)
  - Official web/Flutter renderers are Flutter, Lit, Angular and React, with a shared web-core — [Google Developers Blog: A2UI v0.9](https://developers.googleblog.com/a2ui-v0-9-generative-ui/)
  - npm `@a2ui/lit` and `@a2ui/web_core` are at 0.14.0 (2026-10-17), Apache-2.0 — [npm](https://registry.npmjs.org/@a2ui/lit)
- **AndroidX A2UI (official Compose renderer):**
  - Artifacts: `androidx.a2ui.compose:compose-runtime`, `compose-ui` and `compose-ui-testing` at **1.0.0-alpha02 (2026-10-21)**; alpha01 shipped 2026-09-23.
  - alpha01 "maps A2UI protocol messages to Compose primitives with fine-grained reactivity based on the Compose Snapshot state system". It includes a basic catalog (Button, Card, Row/Column, Image, Icon, List, Tabs, Modal, TextField, Slider, CheckBox, ChoicePicker, DateTimeInput, Divider, Video, AudioPlayer), custom components and catalogs, `ProvideActionInterceptor`, `A2uiReadinessEvaluator`, `A2uiTestSurface`, and Material defaults (`materialA2uiBasicCatalogV1`).
  - Requirement: Compose `compileSdk` **37.1**.
  - alpha02 brought breaking catalog-API changes. Implementers now override only `openUrl`.
  - [Android Developers: A2UI Compose release notes](https://developer.android.com/jetpack/androidx/releases/a2ui-compose)
- Core artifacts `androidx.a2ui:a2ui-model` and `a2ui-engine` are at 1.0.0-alpha02. The POM describes them as "The A2UI core data layer for renderer developers", Apache-2.0, built from AOSP `frameworks/support`, inception year 2026 — [Google Maven group index](https://dl.google.com/android/maven2/androidx/a2ui/group-index.xml); [a2ui-engine POM](https://dl.google.com/android/maven2/androidx/a2ui/a2ui-engine/1.0.0-alpha02/a2ui-engine-1.0.0-alpha02.pom)
- The `compose-ui` 1.0.0-alpha02 AAR is 246 KB — [Google Maven](https://dl.google.com/android/maven2/androidx/a2ui/compose/compose-ui/1.0.0-alpha02/compose-ui-1.0.0-alpha02.aar)
- A secondary source reports Material 3 1.5.0 adds an `A2uiSurface` composable, and that the Compose renderer targets A2UI spec 0.9.x. Both are unverified against primary notes — [eCorpIT](https://ecorpit.com/google-a2ui-android-jetpack-compose/)
- **MCP Apps (SEP-1865):**
  - It went live as the first official MCP extension in January 2026, "ready for production".
  - Lineage: built on MCP-UI and OpenAI's Apps SDK, and co-authored by Anthropic and OpenAI maintainers plus the MCP-UI creators.
  - Mechanics: tools declare `_meta.ui.resourceUri` pointing at a `ui://` resource, and hosts render the HTML in a sandboxed iframe.
  - Reported adopters include Claude, ChatGPT, VS Code Copilot, M365 Copilot, Cursor and Goose.
  - The MIME type differs across sources (`text/html+mcp` vs `text/html;profile=mcp-app`).
  - [MCP blog (2025-11-21 proposal)](https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/); [MCP blog tag: apps](https://blog.modelcontextprotocol.io/tags/apps/); [morphllm summary](https://www.morphllm.com/mcp-apps)
- `modelcontextprotocol/ext-apps` (spec plus SDK): 2,968 stars, v2.0.3 (2026-09-25). npm `@modelcontextprotocol/ext-apps` 2.0.3 is MIT, and the repo is transitioning to Apache-2.0 — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/modelcontextprotocol%2Fext-apps); [npm](https://registry.npmjs.org/@modelcontextprotocol/ext-apps); [LICENSE](https://cdn.jsdelivr.net/gh/modelcontextprotocol/ext-apps@main/LICENSE)
- **MCP-UI** (`MCP-UI-Org/mcp-ui`): Apache-2.0, 5,219 stars, `@mcp-ui/client` 7.1.1 (2026-05-09). Releases have slowed since MCP Apps standardised — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/MCP-UI-Org%2Fmcp-ui); [npm](https://registry.npmjs.org/@mcp-ui/client)
- `openai/openai-apps-sdk-examples`: MIT, 2,371 stars, last push 2026-04-15 — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/openai%2Fopenai-apps-sdk-examples)
- **Generative UI stacks (web):**
  - CopilotKit, "Makers of the AG-UI Protocol", which supports Mobile: MIT, 38,187 stars, v1.79.1 (2026-10-15) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/CopilotKit%2FCopilotKit)
  - Vercel AI SDK: the LICENSE says Apache-2.0, 27,381 stars, `ai@6.0.315` (2026-10-23) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/vercel%2Fai); [LICENSE](https://cdn.jsdelivr.net/gh/vercel/ai@main/LICENSE)

### Inferences
- **Shortlist:**

| Component | License | Maturity | Android fit | Borrow |
|---|---|---|---|---|
| androidx.a2ui + a2ui.compose | Apache-2.0 | alpha02; breaking changes expected | **Native Compose** | Use directly for agent-drawn cards: custom catalog wrapping Boop's existing result cards; `ProvideActionInterceptor` to route actions through Boop's approval rules |
| A2UI spec / agent SDK | Apache-2.0 | v0.9.1 prod, v1.0 RC | Model-side prompt and schema | Teach Boop's LLM to emit A2UI JSON. The catalog-schema advertising lets any LLM provider target it |
| MCP Apps (ext-apps) | MIT→Apache-2.0 | official extension, v2.0.3 | Via WebView sandbox | Host MCP server UIs (e.g., a Zomato menu picker) in a sandboxed WebView with a postMessage bridge |
| MCP-UI client | Apache-2.0 | 7.1.1, slowing | Web-only reference | Host-side bridge reference code |
| AG-UI (CopilotKit) | MIT | very active | Web-first | Event-stream ideas for agent↔UI state sync |

- Pin exact alpha versions. Note that `compileSdk 37.1` is required, which may force a toolchain bump.
- The action interceptor is the right place to enforce Boop's approval rules on agent-drawn UI actions such as "Place order".

### Gaps
- minSdk of `androidx.a2ui.compose` was not stated.
- I could not confirm whether the Material 3 `A2uiSurface` API is in a stable or alpha Material 3 release.
- No primary statement was found on whether OpenAI's Apps SDK now *is* MCP Apps or is merely compatible.
- No Kotlin/Android MCP Apps host SDK was found. Boop would build the WebView bridge itself.

---

## 5. Charts and dashboards in Compose

### Takeaway
**Vico (Apache-2.0, Compose Multiplatform, 3.3.1, Aug 2026)** is the default choice. It is actively maintained, M3-themed, and adds about 1 MB of compressed AAR before R8. ComposeCharts (Apache-2.0, about 0.4 MB AAR) is a lighter animated alternative. KoalaPlot (MIT) covers more plot types. MPAndroidChart is View-based.

### Cited Findings
- **Vico** (`patrykandpatrick/vico`): Apache-2.0, Kotlin, 3,194 stars, last push 2026-10-18. Recent tags are v3.3.0 (2026-08-16) and v3.3.1 (2026-08-28). Description: "A powerful and extensible chart library for Compose Multiplatform." — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/patrykandpatrick%2Fvico)
  - Maven `com.patrykandpatrick.vico:compose` and `compose-m3` are at 3.3.1 (2026-08-28). The `compose-android` AAR is 1,063,941 bytes and the `compose-m3-android` AAR is 3,929 bytes — [Maven metadata](https://repo1.maven.org/maven2/com/patrykandpatrick/vico/compose/maven-metadata.xml); [AAR](https://repo1.maven.org/maven2/com/patrykandpatrick/vico/compose-android/3.3.1/compose-android-3.3.1.aar)
- **ComposeCharts** (`ehsannarmani/ComposeCharts`): Apache-2.0, 917 stars, 1.0.0 (2026-07-21). Maven `io.github.ehsannarmani:compose-charts` 1.0.0 has an Android AAR of 396,636 bytes. "Animated & Flexible Practical Charts For Jetpack Compose" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/ehsannarmani%2FComposeCharts); [Maven metadata](https://repo1.maven.org/maven2/io/github/ehsannarmani/compose-charts/maven-metadata.xml)
- **KoalaPlot** (`KoalaPlot/koalaplot-core`): **MIT**, 785 stars, v0.12.0 (2026-07-25), Compose Multiplatform — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/KoalaPlot%2Fkoalaplot-core)
- **MPAndroidChart**: Apache-2.0, 38,185 stars. It shows a burst of new tags (v3.2.0, v4.0.0, v4.0.1, 2026-09-26/28) after years of dormancy, and the repo language is now Kotlin. It is View-based (line, bar, pie, radar, bubble, candlestick) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/PhilJay%2FMPAndroidChart)
- **YCharts** (`codeandtheory/YCharts`): Apache-2.0, 646 stars, last release v2.1.0 (2023-06-27). Effectively stale — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/codeandtheory%2FYCharts)

### Inferences
- **Shortlist:**

| Library | License | Maturity | Size proxy (AAR) | Borrow |
|---|---|---|---|---|
| Vico 3.3.1 | Apache-2.0 | 3.2k★, frequent | ~1.06 MB (compose) + core | Default for agent dashboards (line, column, candlestick for Kite portfolio) |
| ComposeCharts 1.0.0 | Apache-2.0 | 0.9k★, newly 1.0 | ~0.40 MB | Lightweight animated cards (pie, bar, line) |
| KoalaPlot 0.12 | MIT | 0.8k★, pre-1.0 | not measured | Extra plot types if needed |
| MPAndroidChart 4.x | Apache-2.0 | 38k★, revived | not measured | Avoid in a Compose app (View interop) |

- AAR size is a compressed upper-bound proxy. Real APK delta after R8 shrinking will be smaller and should be measured with an APK Analyzer diff.
- If A2UI is adopted, register a chart component in the custom A2UI catalog backed by Vico. Agents then emit `{"component":"LineChart",…}` and Boop renders it natively.

### Gaps
- No measured post-R8 APK delta for any chart library.
- The size of Vico's `core-android` artifact couldn't be retrieved (the artifact name differs).
- The license and maintainer behind MPAndroidChart's 2026 revival were not verified.

---

## 6. Voice: STT, TTS, VAD, realtime frameworks and Indic support

### Takeaway
**sherpa-onnx (Apache-2.0)** is the best single on-device voice toolkit for Android. It covers STT, TTS (it can run Kokoro, Piper and VITS models), VAD, diarization and Kotlin bindings. For Indic languages:
- **Kokoro-82M (Apache-2.0)** has Hindi voices.
- **Piper voices** exist for hi, ml, mr, te, ne, bn and ur, but the Piper engine is now **GPL-3.0** (piper1-gpl).
- **Moonshine** is now MIT for all streaming models in every language.
- **Gemma 4 E2B/E4B** (Apache-2.0) add native on-device audio understanding.
- **Silero VAD (MIT)** is the safe VAD choice. TEN VAD carries an Agora non-compete condition.
- Pipecat (BSD-2) and LiveKit Agents (Apache-2.0) are *server-side* Python frameworks with Android client SDKs. They are only relevant if Boop adds a cloud voice relay as an alternative to Gemini Live.

### Cited Findings
- **sherpa-onnx**: Apache-2.0, C++, 15,444 stars, v1.13.8 (2026-09-10), very active. It covers "Speech-to-text, text-to-speech, speaker diarization, speech enhancement, source separation, and VAD" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/k2-fsa%2Fsherpa-onnx)
  - VoxSherpa TTS is a **GPL-3.0** Android app built on sherpa-onnx. It runs Kokoro-82M, Piper and VITS, supports Hindi, and requires Android 11+ on ARM64. Its performance estimates show Kokoro much slower than real time on budget phones (about 2–3 minutes per minute of audio on a 6-core device) — [VoxSherpa TTS](https://github.com/CodeBySonu95/VoxSherpa-TTS)
  - Indic ASR for sherpa-onnx exists only as **community conversions** of AI4Bharat IndicConformer on Hugging Face (Tamil, Malayalam, Telugu, Punjabi, multi-Indic). I found no official sherpa-onnx Hindi model in a search — [HF search: sherpa-onnx indic](https://huggingface.co/api/models?search=sherpa-onnx%20indic)
- **AI4Bharat IndicConformerASR**: MIT, 83 stars, last push 2025-06-20 — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/AI4Bharat%2FIndicConformerASR). ⚠️ **IndicF5** (Indic TTS): **no license** declared in the repo — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/AI4Bharat%2FIndicF5)
- **whisper.cpp**: MIT, 54,442 stars, v1.9.4 (2026-09-11) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/ggml-org%2Fwhisper.cpp)
- **Moonshine** (`moonshine-ai/moonshine`):
  - Code is MIT, 11,259 stars, v0.1.6 (2026-10-02).
  - "Moonshine models are released under the MIT License by default, in every language and at every size. This includes all streaming speech-to-text models." The **only** non-MIT models are the legacy non-streaming non-English models (Arabic, Japanese, Korean, Mandarin, Spanish, Ukrainian, Vietnamese; Base/Tiny), which stay under the non-commercial Moonshine Community License. TTS and G2P models are licensed separately per their own readmes.
  - It supports Android, iOS, Python, JS/WASM and more.
  - [LICENSE](https://cdn.jsdelivr.net/gh/moonshine-ai/moonshine@main/LICENSE); [README](https://cdn.jsdelivr.net/gh/moonshine-ai/moonshine@main/README.md); [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/moonshine-ai%2Fmoonshine)
  - **Conflict:** several secondary sources (Pipecat docs, Mintlify mirror) still describe *all* non-English models as non-commercial. The current LICENSE is narrower — [Pipecat Moonshine docs](https://docs.pipecat.ai/api-reference/server/services/stt/moonshine)
- **Kokoro-82M**: weights Apache-2.0 (HF tag), about 10.3M downloads. The PyPI `kokoro` package is 0.9.4 (2025-04-05), and the GitHub repo `hexgrad/kokoro` was last pushed 2025-08-06, so it is quiet. Hindi has 2 female and 2 male voices (`lang_code='h'`, espeak-ng `hi`). Its VOICES.md warns that non-English support "may be absent or thin due to weak G2P and/or lack of training data" — [HF model API](https://huggingface.co/api/models/hexgrad/Kokoro-82M); [VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/raw/main/VOICES.md); [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/hexgrad%2Fkokoro)
  - A third-party guide gives an Android Kokoro ONNX bundle of about 330 MB — [soniqo guide](https://soniqo.audio/guides/kokoro/android)
- **Piper:**
  - The original `rhasspy/piper` (MIT) is **archived**, last tag 2023.11.14.
  - ⚠️ The maintained continuation, `OHF-Voice/piper1-gpl`, is **GPL-3.0**, with 5,943 stars, v1.8.0 (2026-09-04); the PyPI `piper-tts` license is GPL-3.0-or-later.
  - Voices exist for **hi_IN, ml_IN, mr_IN, te_IN, ne_NP, bn_BD and ur_PK**.
  - [ecosyste.ms piper](https://repos.ecosyste.ms/hosts/GitHub/repositories/rhasspy%2Fpiper); [ecosyste.ms piper1-gpl](https://repos.ecosyste.ms/hosts/GitHub/repositories/OHF-Voice%2Fpiper1-gpl); [PyPI](https://pypi.org/pypi/piper-tts/json); [piper-voices voices.json](https://huggingface.co/rhasspy/piper-voices/raw/main/voices.json)
- **Silero VAD**: MIT, 10,456 stars, v6.2.3 (2026-09-23) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/snakers4%2Fsilero-vad)
- ⚠️ **TEN VAD**: "Apache License v2.0… with the following additional conditions", including "You may not Deploy the ten-vad in a way that competes with Agora's offerings". It is therefore **not OSI-permissive** — [LICENSE](https://cdn.jsdelivr.net/gh/TEN-framework/ten-vad@main/LICENSE). The TEN framework itself is licensed "other", with 11,194 stars — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/TEN-framework%2Ften-framework)
- **openWakeWord**: Apache-2.0 code, but stale; the last release was v0.6.0 (2024-02-11) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/dscripka%2FopenWakeWord)
- **Pipecat**: BSD-2-Clause, 16,547 stars, PyPI `pipecat-ai` 1.14.0 (2026-10-24), with releases about weekly. The Android client is on Maven as `ai.pipecat:client` 1.2.0 (2026-07-17). The GitHub repo `pipecat-client-android` itself shows old tags, last v0.2.0 in 2024 — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/pipecat-ai%2Fpipecat); [PyPI](https://pypi.org/pypi/pipecat-ai/json); [Maven metadata](https://repo1.maven.org/maven2/ai/pipecat/client/maven-metadata.xml)
- **LiveKit Agents**: Apache-2.0, 14,875 stars, `livekit-agents` 1.8.9 (2026-10-24), with 2.0.0b1 beta tagged 2026-10-12. The LiveKit Android SDK is Apache-2.0 Kotlin, v2.28.2 (2026-09-07) — [ecosyste.ms agents](https://repos.ecosyste.ms/hosts/GitHub/repositories/livekit%2Fagents); [PyPI](https://pypi.org/pypi/livekit-agents/json); [ecosyste.ms android SDK](https://repos.ecosyste.ms/hosts/GitHub/repositories/livekit%2Fclient-sdk-android)
- **Gemma 4 E2B/E4B** are built for phones, with 128K context and "native audio" so speech recognition runs on the handset. Google says Gemini Nano 4 will be based on them — [TechWyse](https://www.techwyse.com/news/ai-search/google-deepmind-gemma-4-open-models-apache-2-0-release); [Implicator](https://www.implicator.ai/google-releases-gemma-4-under-apache-2-0-dropping-its-custom-ai-license/)

### Inferences
- **Shortlist for Boop's phone speech fallback and offline voice:**

| Need | Pick | License | Notes |
|---|---|---|---|
| Runtime | sherpa-onnx | Apache-2.0 | One native lib for ASR, TTS and VAD. Kotlin API, active |
| VAD | Silero VAD (via sherpa-onnx) | MIT | Avoid TEN VAD (Agora non-compete) |
| English/streaming ASR | Moonshine streaming or Whisper (whisper.cpp / sherpa) | MIT | Moonshine is lower-latency. Avoid the 7 legacy non-English Moonshine models |
| Indic ASR | IndicConformer (community sherpa ONNX conversions) or Whisper multilingual; Gemma 4 E2B audio as an LLM-native option | MIT / Apache-2.0 | Quality is unverified. Needs evaluation on Hindi, Tamil, Telugu and others |
| TTS (Hindi) | Kokoro-82M (Apache-2.0) via sherpa-onnx; Piper `hi_IN` voices as an alternative | Apache-2.0 / ⚠️ GPL engine | Calling the *Piper voice models* through sherpa-onnx avoids linking the GPL piper1 engine. Per-voice model licenses must be checked |
| Realtime cloud voice | Pipecat or LiveKit Agents (server) + Android client | BSD-2 / Apache-2.0 | Only if replacing or augmenting Gemini Live with a provider-agnostic voice pipeline |

- Kokoro is heavy (about 330 MB per one guide) and slow on budget phones. Android's built-in TTS should remain the default, with Kokoro optional.

### Gaps
- No Indic WER benchmarks for on-device models were found in this session.
- Per-voice licenses of the Piper Indic voices were not checked; each voice has its own MODEL_CARD.
- openWakeWord model licensing was not verified.
- Whether sherpa-onnx publishes an official Hindi ASR model was not established.

---

## 7. On-device models and runtimes

### Takeaway
The most important change is that **Gemma 4 (released 2026-04-02) is Apache-2.0**. That removes the custom Gemma Terms of Use problem that applied to Gemma 3/3n. Its E2B and E4B variants target phones with native audio. On Android, **LiteRT-LM (Apache-2.0, Kotlin API, GPU/NPU, tool use)** is Google's go-forward runtime. MediaPipe LLM Inference is maintenance-only or deprecated on mobile. **llama.cpp (MIT)** remains the universal GGUF runtime and has an official Kotlin binding. ExecuTorch (BSD-3) and MLC-LLM (Apache-2.0) are viable but niche for Boop.

### Cited Findings
- **Gemma 4:**
  - Released 2026-04-02 under **Apache 2.0**, dropping the custom Gemma license.
  - Variants: E2B (about 2.3B effective parameters), E4B (about 4.5B effective), a 26B MoE (4B active) and a 31B dense model.
  - Available through AI Studio, Hugging Face, Kaggle and Ollama.
  - [Google Open Source Blog: "Gemma 4: Expanding the Gemmaverse with Apache 2.0"](https://opensource.googleblog.com/2026/03/gemma-4-expanding-the-gemmaverse-with-apache-20.html); [Google AI forum launch post](https://discuss.ai.google.dev/t/gemma-4-launch-announcement/138069); [Implicator](https://www.implicator.ai/google-releases-gemma-4-under-apache-2-0-dropping-its-custom-ai-license/)
  - One secondary source (emelia.io) lists different sizes ("12B", "27B A4B"), which conflicts with the above — [emelia.io](https://emelia.io/hub/gemma-4-open-source-guide)
- **LiteRT-LM** (`google-ai-edge/LiteRT-LM`): Apache-2.0, 6,701 stars, v0.18.1 (2026-10-20), with nightly 0.19.0 builds. Google Maven `com.google.ai.edge.litertlm:litertlm-android` runs 0.8.0 through 0.18.1, and there is also `litertlm-jvm`. The 0.18.1 AAR is 20.9 MB (native libs, multi-ABI) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/google-ai-edge%2FLiteRT-LM); [Google Maven index](https://dl.google.com/android/maven2/com/google/ai/edge/litertlm/group-index.xml)
  - The Kotlin API for Android and JVM supports "GPU and NPU acceleration, multi-modality, and tools use" through `Engine`, `EngineConfig` and `createConversation` — [ai.google.dev LiteRT-LM Android](https://ai.google.dev/edge/litert-lm/android)
  - Gemma 4 ships in `.litertlm` format — [HF model card](https://huggingface.co/i2so/gemma-4-E2B-it-litert-lm)
- **MediaPipe LLM Inference API:** "now in maintenance-only mode. New features and optimizations will be focused on LiteRT-LM… We recommend migrating your projects to LiteRT-LM". One page variant says the Android and iOS implementations are deprecated while Web is not — [Google LLM Inference guide](https://developers.google.com/edge/mediapipe/solutions/genai/llm_inference)
  - The MediaPipe repo is Apache-2.0, 37,365 stars, v1.1.1 (2026-10-14) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/google-ai-edge%2Fmediapipe)
- **llama.cpp**: MIT, 131,886 stars, continuous builds (b11786 on 2026-10-21) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/ggml-org%2Fllama.cpp)
  - The official Android binding is `examples/llama.android`, with a Kotlin API that streams tokens as a Kotlin `Flow`, automatic chat-template formatting, and acceleration "up to SME2 for Arm and AMX for x86-64" — [llama.cpp docs/android.md](https://cdn.jsdelivr.net/gh/ggml-org/llama.cpp@master/docs/android.md)
- **MLC-LLM**: Apache-2.0, 23,249 stars, v0.20.0 (2026-07-07). Before that, the previous tagged release was v0.19.0 (2025-02-11), so cadence is slow — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/mlc-ai%2Fmlc-llm)
- **ExecuTorch**: BSD license (Meta, Arm, Qualcomm copyrights), 5,105 stars. Maven `org.pytorch:executorch-android` is 1.5.1 (2026-10-01) — [LICENSE](https://cdn.jsdelivr.net/gh/pytorch/executorch@main/LICENSE); [Maven metadata](https://repo1.maven.org/maven2/org/pytorch/executorch-android/maven-metadata.xml)
- **ONNX Runtime Android** (needed for sherpa-onnx and GLiNER-style models): Maven `com.microsoft.onnxruntime:onnxruntime-android` is 1.31.0 (2026-10-09). The full multi-ABI AAR is 55 MB — [Maven metadata](https://repo1.maven.org/maven2/com/microsoft/onnxruntime/onnxruntime-android/maven-metadata.xml)
- **Google AI Edge Gallery** demonstrates FunctionGemma 270m fine-tunes for offline "Mobile Actions" and EmbeddingGemma 2 — [Gallery README](https://cdn.jsdelivr.net/gh/google-ai-edge/gallery@main/README.md)

### Inferences
- **Shortlist:**

| Runtime | License | Maturity | Android fit | Use in Boop |
|---|---|---|---|---|
| LiteRT-LM 0.18.1 | Apache-2.0 | very active (weekly) | **Best**: Kotlin API, GPU/NPU, tool calling | Primary on-device LLM (Gemma 4 E2B/E4B) for offline mode, PII pre-screening, intent routing |
| llama.cpp | MIT | extremely active | Good: Kotlin binding, CPU (SME2) | Fallback for arbitrary GGUF models (Qwen, Llama, Phi) |
| ExecuTorch 1.5.1 | BSD | active | Good | Only if using PyTorch-exported models |
| MLC-LLM 0.20 | Apache-2.0 | slow cadence | OK | Low priority |
| MediaPipe LLM Inference | Apache-2.0 | maintenance-only | Deprecated path | Migrate off it |

- Gemma 4 E2B under Apache-2.0 makes a fully open on-device helper (offline mode, privacy-gateway classifier, quick intent routing) license-clean for Boop. Earlier Gemma 3n weights fell under the Gemma Terms of Use. That is prior knowledge, not re-verified this session.
- Native runtimes add MBs per ABI. LiteRT-LM (about 21 MB AAR) and ONNX Runtime (about 55 MB multi-ABI AAR) should be shipped via ABI splits or Play Feature Delivery modules.

### Gaps
- Primary Google docs on Gemma 4 sizes, and on LiteRT-LM NPU support per device (Tensor, Snapdragon, MediaTek), were not fetched.
- No on-device tokens/sec benchmarks were gathered.
- The license of the FunctionGemma and EmbeddingGemma 2 weights was not checked; they might still be under Gemma terms.

---

## 8. Phone automation / GUI agents

### Takeaway
Most open GUI-agent projects are Python **host-side** controllers that drive a phone over ADB, plus large vision models. They are useful for ideas and benchmarks, not for embedding. The one Android-side component, **Droidrun/Mobilerun Portal** (a Kotlin accessibility service with a local WebSocket/HTTP API), is **AGPL-3.0**, even though the Droidrun Python agent is MIT. Boop should build its own AccessibilityService and take its design ideas from these projects. Its safety design should assume prompt injection from on-screen content.

### Cited Findings
- **Droidrun, renamed Mobilerun** (`droidrun/mobilerun`): **MIT** Python agent, 9,676 stars, v0.6.22 (2026-10-05). PyPI `droidrun` is 0.7.2 (2026-10-25). "LLM agnostic mobile Agent" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/droidrun%2Fmobilerun); [LICENSE](https://cdn.jsdelivr.net/gh/droidrun/mobilerun@main/LICENSE); [PyPI](https://pypi.org/pypi/droidrun/json)
- ⚠️ **Mobilerun Portal** (the on-device Android app): **GNU AGPL-3.0-or-later**. It is "an Android accessibility service that provides real-time visual feedback and data collection for UI elements". It exposes local control APIs: an HTTP socket server, WebSocket JSON-RPC on default port 8081, and a ContentProvider. It also offers a "Reverse WebSocket connection for cloud control", a local auth token, and notification-event streaming — [Portal LICENSE](https://cdn.jsdelivr.net/gh/droidrun/mobilerun-portal@main/LICENSE); [Portal README](https://cdn.jsdelivr.net/gh/droidrun/mobilerun-portal@main/README.md)
- **Mobile-Agent** (`X-PLUG/MobileAgent`, Alibaba): MIT code, 9,326 stars, last push 2026-07-07. Mobile-Agent-v3.5 uses the GUI-Owl-1.5 models (7B and 32B on HF). As of 2026-03-31 it is offered on Alibaba Cloud Wuying Cloud Phone — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/X-PLUG%2FMobileAgent); [README](https://cdn.jsdelivr.net/gh/X-PLUG/MobileAgent@main/README.md)
- **AppAgent** (Tencent): MIT, 6,909 stars, last push 2025-03-19, so it is stale — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/TencentQQGYLab%2FAppAgent)
- **Open-AutoGLM** (Zhipu/Z.ai): Apache-2.0 code, 26,417 stars, last push 2026-03-06. "An Open Phone Agent Model & Framework" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/zai-org%2FOpen-AutoGLM)
- **UI-TARS** (ByteDance): Apache-2.0, 11,610 stars, last push 2026-01-27 — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/bytedance%2FUI-TARS)
- **mobile-use** (minitap): Apache-2.0, 3,299 stars, v3.6.3 (2026-03-19) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/minitap-ai%2Fmobile-use)
- **mobile-mcp** (`mobile-next/mobile-mcp`): Apache-2.0, 9,737 stars, 1.0.10 (2026-10-11). An "MCP Server for Mobile Automation… (iOS, Android, Emulators, Simulators and Real devices)" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/mobile-next%2Fmobile-mcp)
- **AndroidWorld** (Google Research benchmark): Apache-2.0, 972 stars, active — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/google-research%2Fandroid_world)
- **OmniParser** (Microsoft screen parser): the repo is CC-BY-4.0, 25,529 stars, v2.0.1 (2025-09-09) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/microsoft%2FOmniParser)
- ⚠️ **Panda/blurr** (Kotlin, accessibility-based): personal-use license only — [LICENSE](https://cdn.jsdelivr.net/gh/Ayush0Chaudhary/blurr@main/LICENSE)
- **Google AI Edge Gallery "Mobile Actions"**: offline device control using a FunctionGemma 270m fine-tune, Apache-2.0 app code — [README](https://cdn.jsdelivr.net/gh/google-ai-edge/gallery@main/README.md)
- **Safety context:** OpenClaw's node layer exposes camera, screen recording, location and system command execution to the agent. Researchers flag it as the most sensitive surface — [mintmcp](https://www.mintmcp.com/blog/openclaw-works-architecture-skills-security); [arXiv 2603.12644](https://arxiv.org/html/2603.12644v1). OpenClaw does not sanitize web content before it enters the LLM context — [Giskard](https://www.giskard.ai/knowledge/openclaw-security-vulnerabilities-include-data-leakage-and-prompt-injection-risks)

### Inferences
- **Shortlist:**

| Project | License | Activity | Android fit | Borrow |
|---|---|---|---|---|
| Droidrun/Mobilerun agent | MIT | very active | Host-side Python | Prompting and planning approach: accessibility-tree + screenshot hybrid, step verification |
| ⚠️ Mobilerun Portal | **AGPL-3.0** | active | On-device Kotlin | **Ideas only** (do not copy code): a11y-tree JSON serialization, element-highlight overlay, token-protected local API |
| Mobile-Agent v3.5 / GUI-Owl | MIT code; model license unverified | active | Cloud models | Multi-agent split (manager, operator, reflector) and the reflection loop |
| Gallery Mobile Actions | Apache-2.0 | active | **On-device** | Small function-calling model for intent→Android action. Code is copyable |
| AndroidWorld | Apache-2.0 | active | Benchmark | Evaluate Boop's phone-control helper |
| mobile-mcp | Apache-2.0 | active | Desktop/ADB | Tool schema design for mobile actions |

- **Safety design for an accessibility-based helper in Boop:**
  - Treat all screen text as untrusted data. OpenClaw's `isUser=false` tagging is one pattern.
  - Require Boop's approval rules for irreversible actions (pay, send, delete, order).
  - Exclude banking and password fields; `FLAG_SECURE` windows are not readable anyway.
  - Never expose a network control socket. The Portal's reverse-WebSocket "cloud control" is precisely the attack surface to avoid.
  - Google Play's AccessibilityService policy also constrains this use case. That is general knowledge, not verified this session.

### Gaps
- Licenses of the GUI-Owl-1.5, AutoGLM-Phone and UI-TARS model weights were not checked; they may differ from the code licenses.
- OmniParser's model-weight licenses were reportedly mixed (AGPL for the YOLO-derived detector, in prior knowledge) but were not verified this session.
- Google Play's current (2026) accessibility-API policy for AI agents was not researched.

---

## 9. Sandboxed code execution, cloud computers and browser agents

### Takeaway
For a phone app, sandboxing beyond `androidx.javascriptengine` means a **remote** sandbox.
- **E2B** (Apache-2.0 SDKs and Apache-2.0 self-hostable infra built on Firecracker) is the most open, production-grade option.
- ⚠️ **Daytona archived its public repo in mid-2026.** The last open release was v0.190.0, under AGPL-3.0, and development went private, so avoid building on it.
- For web automation, **Browser Use (MIT)** and **Playwright (Apache-2.0)** dominate. Stagehand (MIT) and Steel (Apache-2.0) are good companions. ⚠️ Skyvern is AGPL-3.0.

### Cited Findings
- **androidx.javascriptengine**, which Boop already uses, is at 1.1.1 stable on Google Maven — [Google Maven index](https://dl.google.com/android/maven2/androidx/javascriptengine/group-index.xml)
- **E2B** (`e2b-dev/E2B`): Apache-2.0 per the repo, 14,524 stars, last push 2026-10-24. PyPI `e2b` 2.59.0 and `e2b-code-interpreter` 2.11.3 were both released 2026-10-22, and PyPI metadata lists **MIT**, which conflicts with the repo license — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/e2b-dev%2FE2B); [PyPI](https://pypi.org/pypi/e2b/json)
  - The self-hostable infrastructure repo `e2b-dev/infra` is Apache-2.0 — [LICENSE](https://cdn.jsdelivr.net/gh/e2b-dev/infra@main/LICENSE)
- ⚠️ **Daytona** (`daytonaio/daytona`): **archived**, 71,515 stars, last push 2026-07-24, last tag v0.190.0 (2026-06-23). No license is now detected on the archived repo — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/daytonaio%2Fdaytona)
  - A community fork, "Nightona", says the upstream repo was archived in June 2026 and core development moved private, and that the last open release, v0.190.0, was AGPL-3.0. This is a self-published source — [Nightona README](https://cdn.jsdelivr.net/gh/nightona-co/nightona@main/README.md)
- **Firecracker**: Apache-2.0, 37,361 stars, v1.17.0 (2026-09-04) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/firecracker-microvm%2Ffirecracker)
- **kubernetes-sigs/agent-sandbox**: Apache-2.0, 4,318 stars, v0.5.6 (2026-08-20). "Isolated, stateful, singleton workloads, ideal for… AI" agents — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/kubernetes-sigs%2Fagent-sandbox)
- **Browser Use**: MIT, 118,632 stars, 0.13.13 (2026-10-15). It is an open-source Python library plus a paid Browser Use Cloud ("stealth browsers from $0.02/hour") — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/browser-use%2Fbrowser-use); [README](https://cdn.jsdelivr.net/gh/browser-use/browser-use@main/README.md)
- **Playwright**: Apache-2.0, 98,026 stars, v1.63.0 (2026-09-04) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/microsoft%2Fplaywright)
- **Stagehand** (Browserbase): MIT, 25,729 stars, 4.2.1 (2026-10-10) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/browserbase%2Fstagehand)
- **Steel Browser**: Apache-2.0, 7,858 stars, v0.5.4-beta (2026-08-25). An "Open Source Browser API for AI Agents" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/steel-dev%2Fsteel-browser)
- ⚠️ **Skyvern**: **AGPL-3.0**, 23,239 stars, v1.0.56 (2026-10-14) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/Skyvern-AI%2Fskyvern)
- **Nanobrowser**: an Apache-2.0 Chrome-extension agent, 14,141 stars, last release v0.1.13 (2025-11-22), so it is slowing — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/nanobrowser%2Fnanobrowser)
- **OpenClaw sandbox backends**: Docker, Podman, SSH, OpenShell and Crabbox. It also has a capability matrix of what is sandboxed vs what runs on the Gateway host — [OpenClaw docs index](https://docs.openclaw.ai/llms.txt)

### Inferences
- **Shortlist:**

| Component | License | Maturity | Fit for Boop | Borrow |
|---|---|---|---|---|
| E2B SDK + infra | Apache-2.0 (PyPI says MIT) | very active | Remote "cloud computer" tool via REST/SDK, callable from Kotlin over HTTP | Optional heavy code/data tasks beyond the JS sandbox. Self-host on Firecracker for privacy |
| ⚠️ Daytona | archived; last OSS AGPL-3.0 | dead upstream | Avoid | — |
| Browser Use | MIT | extremely active | Server-side Python | Its DOM-distillation and action-schema design for Boop's in-app browser agent |
| Stagehand | MIT | active | Server-side TS | `act`/`extract`/`observe` primitive design for the WebView agent |
| Playwright | Apache-2.0 | very active | Server | Remote headless browser when the WebView is insufficient |
| ⚠️ Skyvern | AGPL-3.0 | active | Avoid code reuse | Ideas only |

- Boop's in-app browser agent can borrow Browser Use's and Stagehand's page-to-LLM serialization (interactive-element indexing) and implement it with JS injected into the WebView. Both are permissively licensed, so porting the logic is fine.
- Firecracker requires a Linux KVM host, so it is a server-side choice, not on-phone. This is an inference from its design.

### Gaps
- No primary Daytona announcement of the archival was found; the evidence is the ecosyste.ms archived flag plus the fork README.
- The E2B license inconsistency between the repo (Apache-2.0) and PyPI (MIT) was not resolved. Both are permissive.
- No Android-native remote-sandbox client SDK was found. Boop would call E2B's REST API.

---

## 10. PII detection and redaction usable on-device

### Takeaway
**Microsoft Presidio (MIT, now under a "Data Privacy Stack" org)** is the reference. It has India-specific recognizers (PAN, Aadhaar, vehicle registration, voter ID, passport, GSTIN) but is Python-only. Its regex and checksum recognizers are easy to port to Kotlin. For on-device ML detection, permissively licensed small models exist:
- **GLiNER PII models** (Apache-2.0), runnable via ONNX Runtime.
- **OpenAI Privacy Filter** (Apache-2.0, April 2026, 1.5B total / 50M active parameters, 128K context, transformers.js support).

Two are flagged: ⚠️ Piiranha is CC-BY-NC-ND, and NVIDIA gliner-PII has a custom license. **Phileas** (Apache-2.0, Java) is the only JVM-native redaction engine found.

### Cited Findings
- **Presidio** (`data-privacy-stack/presidio`, moved from `microsoft/presidio`): MIT, 11,495 stars, last push 2026-10-19. PyPI `presidio-analyzer` is 2.2.365 (2026-10-25), MIT. The docs moved to presidio.dataprivacystack.org — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/data-privacy-stack%2Fpresidio); [PyPI](https://pypi.org/pypi/presidio-analyzer/json); [docs](https://presidio.dataprivacystack.org/supported_entities/)
  - India entities: **IN_PAN, IN_AADHAAR, IN_VEHICLE_REGISTRATION, IN_VOTER, IN_PASSPORT, IN_GSTIN**. There is no UPI entity.
  - Global entities: CREDIT_CARD, CRYPTO, DATE_TIME, EMAIL_ADDRESS, IBAN_CODE, IP_ADDRESS, MAC_ADDRESS, NRP, LOCATION, PERSON, PHONE_NUMBER, MEDICAL_LICENSE, URL, UUID.
  - NLP engines: spaCy/Stanza, transformers, and a GLiNER sample.
  - [Presidio supported entities](https://presidio.dataprivacystack.org/supported_entities/)
- **Phileas** (`philterd/phileas`): Apache-2.0, **Java**, 110 stars, 4.4.0 (2026-09-03). "The open source PII and PHI redaction and de-identification engine" — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/philterd%2Fphileas)
- **GLiNER**: Apache-2.0, 4,125 stars. PyPI `gliner` is 0.2.29 (2026-09-08) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/urchade%2FGLiNER); [PyPI](https://pypi.org/pypi/gliner/json)
  - PII checkpoints and their licenses: `knowledgator/gliner-pii-base-v1.0` Apache-2.0 (2025-09-27); `urchade/gliner_multi_pii-v1` Apache-2.0 (multilingual); `gretelai/gretel-gliner-bi-large-v1.0` Apache-2.0; ⚠️ `nvidia/gliner-PII` license "other" (2025-12-07) — [HF API knowledgator](https://huggingface.co/api/models/knowledgator/gliner-pii-base-v1.0); [HF API urchade](https://huggingface.co/api/models/urchade/gliner_multi_pii-v1); [HF API nvidia](https://huggingface.co/api/models/nvidia/gliner-PII)
- **OpenAI Privacy Filter** (`openai/privacy-filter`), uploaded 2026-04-22: Apache-2.0, about 173k downloads.
  - It is a "bidirectional token-classification model for PII detection and masking".
  - It is derived from a gpt-oss-like checkpoint: "1.5B parameters total and 50M active parameters".
  - "Runs in a web browser or on a laptop". It has a 128K context and "runtime control" of precision/recall operating points.
  - It ships with transformers and transformers.js pipelines.
  - [HF model card](https://huggingface.co/openai/privacy-filter/raw/main/README.md)
- ⚠️ **Piiranha** (`iiiorg/piiranha-v1-detect-personal-information`): **CC-BY-NC-ND-4.0**, which is non-commercial and no-derivatives — [HF API](https://huggingface.co/api/models/iiiorg/piiranha-v1-detect-personal-information)
- **ai4privacy** `llama-ai4privacy-english-anonymiser-openpii`: MIT — [HF API](https://huggingface.co/api/models/ai4privacy/llama-ai4privacy-english-anonymiser-openpii)
- ⚠️ **LLM Guard** (Protect AI): MIT, but the repo is **archived** and the last release was v0.3.16 (2025-05-19) — [ecosyste.ms](https://repos.ecosyste.ms/hosts/GitHub/repositories/protectai%2Fllm-guard)
- **ONNX Runtime Android** 1.31.0, the runtime for GLiNER-style ONNX models on device — [Maven metadata](https://repo1.maven.org/maven2/com/microsoft/onnxruntime/onnxruntime-android/maven-metadata.xml)

### Inferences
- **Shortlist for Boop's privacy gateway:**

| Layer | Component | License | On-device? | Borrow |
|---|---|---|---|---|
| Deterministic | Presidio's recognizer patterns (IN_PAN, IN_AADHAAR with Verhoeff checksum, IN_GSTIN, IN_VOTER, IN_PASSPORT, IN_VEHICLE_REGISTRATION, CREDIT_CARD Luhn, IBAN, phone, email) | MIT | Port to Kotlin | Regexes, checksum validators and context-word boosting. Add UPI ID (`name@bank`) and IFSC, which Presidio lacks |
| JVM engine | Phileas | Apache-2.0 | Possibly (Java). Android compatibility unverified | Filter and policy model (redact/mask/encrypt per entity type) |
| ML NER | GLiNER PII (knowledgator / urchade multi) via ONNX Runtime | Apache-2.0 | Yes (ONNX), with size and latency trade-offs | Names, addresses and free-text PII the regexes miss |
| ML (heavier) | OpenAI Privacy Filter | Apache-2.0 | Maybe: 1.5B total parameters is heavy for phones despite 50M active | Server-side or high-end devices. Benchmark before adopting |
| Avoid | Piiranha (NC-ND), nvidia/gliner-PII (custom), LLM Guard (archived) | — | — | — |

- Boop already replaces personal data with references. These components would strengthen the *detection* step. The deterministic Indian ID recognizers are the highest-value, lowest-cost addition.

### Gaps
- Phileas's Android compatibility and dependency size were not verified.
- The ONNX export and on-device latency of OpenAI Privacy Filter and of GLiNER on mid-range Android were not found.
- The text of the NVIDIA gliner-PII license was not read.
- The terms of Google ML Kit Entity Extraction (closed but free on-device, detects addresses, phone numbers, payment cards, IBAN and more) were not researched this session.
- Presidio's "Project transition update" page, covering why it moved from Microsoft to the Data Privacy Stack org, was not read.
