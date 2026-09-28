# Red team, iteration 6 (attacking v5): has the loop sanded the idea down, and can attestation carry the ambition?

**Verdict:** Being modest is the right default, but v5's "big bet" is the wrong one. A firewall that attests to its own policy is either unverifiable or only works in the minority of agents that run on the phone, and web agent identity is already a crowded fight between big players. The ambitious path is real only as a narrow, gated wedge: bridging existing standards to on-device Android agents. Everything before Gate 1 stays exactly as modest as v5.

## Findings, ranked

**1. The attestation handshake proves the wrong thing, for the wrong agents.**
- An app can check identity (who signed this?), but not behaviour (did the firewall actually run?).
- Python-over-ADB agents (droidrun, mobile-use, which are v5's first adapters) run on an untrusted host. Nothing ties their signature to the enforcement.
- ADB or developer mode is also exactly what Appdome-style protection already flags.
- Only an **on-device agent binary** can carry a hardware-backed claim. Android Key Attestation binds a key to a package name, signing cert and verified-boot state. That covers Operit and UNO, not the frameworks v5 leads with.

**Change:** reword the bet as "hardware-attested agent identity plus a signed policy manifest, for on-device agents." Say plainly that it cannot cover host-driven agents.

**2. The relying parties have no reason to let third-party agents in.**
- Banks and apps care about **liability** (who pays when something goes wrong), not firewalls. Visa's Trusted Agent Protocol, Mastercard Agent Pay and 3DS all work because they shift or assign liability. A policy attestation from a solo founder's OSS project assigns nothing.
- The mobile agents apps actually want to admit will be Gemini, Samsung and the OEM agents. Those get allow-listed directly through Play Integrity or partner deals.
- The long tail of third-party agents is what apps want to *block*.

**Change:** name one relying party whose incentive is positive before building anything. Candidates are accessibility-dependent users (where blocking agents has legal exposure) or a DMA interoperability argument. If none can be named, drop the bet.

**3. The "trust layer" slot is taken on the web, and it's heading to mobile through Google.**
- **Web Bot Auth:** Cloudflare, with the IETF working group; Visa, Mastercard and Amex build on it.
- **Visa TAP:** 12 launch partners.
- **Mastercard Agent Pay.**
- **Skyfire KYA / KYAPay.**
- **OpenAI/Stripe ACP.**
- **Google AP2:** already ships an Android SDK, and AP2 plus Mastercard Verifiable Intent moved to the **FIDO Alliance** in May 2026.
- I found no mobile GUI-agent attestation standard (**unverified**). The gap exists because the incumbents' next step is to fill it, most likely through Credential Manager plus Play Integrity.
- A "Plaid for agents" needs the Plaid ingredients: a painful two-sided integration that no incumbent owns. Here, Google owns both sides.

**Change:** don't invent a protocol. The only ambitious version with a chance is **the Android on-device profile of the existing standards**, contributed through the FIDO Payments TWG and the IETF webbotauth group:
- sign Web Bot Auth or AP2 mandates with a Keystore-attested key held by the agent app;
- reuse UNO's on-device approval and spending rules as the "intent mandate" UI.

That makes the founder a contributor to the standard, not a rival to it.

**4. The convergence is partly an artefact of the loop.**
- Five red teams each rewarded defensibility. The result is a security-plumbing contributor role for someone who builds consumer products.
- The founder asked for a miracle. The honest answer is that a miracle-scale outcome here needs Google, FIDO members or a card network to adopt your work. The odds are under 5%, but the option is cheap if it's gated.

**Change:** state both outcomes and their odds in v6. Don't present modest as the only answer.

**5. Disclosure etiquette: v5's entry move looks like ambulance-chasing.**
- The "Not an A11y" vectors are the **paper authors'** findings.
- Bundling a disclosure with a PR that plugs your own product is a known anti-pattern.
- Many maintainers class prompt injection as "by design", not a vulnerability.

**Change:**
- Ask the authors first.
- File through GitHub private vulnerability reporting, with no product mention.
- Offer SECURITY.md as a separate, no-strings PR.
- Propose AgentGuard only after the fix discussion.

**6. The upstream PR target is too heavy.**
Funded teams (€2.1M, $4.1M) won't merge an outside runtime into their critical path.

**Change:** the PR asks for a generic `before_action` / `on_action` hook in each framework. AgentGuard stays an external plugin. A merged hook counts toward the kill test, and it survives copying.

**7. The benchmark will be gamed or dismissed.**
- A firewall that blocks every action scores 0% attack success. So report **utility**, meaning task success on AndroidWorld with and without the firewall, plus false-confirmation rate and adaptive attacks.
- Cold-asking the Picek group for co-authorship within 60 days is unrealistic.

**Change:**
- Publish the harness.
- Invite the Picek group, and the paper authors, to re-run it.
- Treat co-authorship as a bonus, not a milestone.

**8. Grant fit has hidden blockers.**
- NLnet's new GenAI policy excludes work that is mostly LLM-generated. The founder works as "solo + AI coding help", so this is a direct conflict.
- The 3 Nov deadline is 5 weeks away.
- The OpenAI grant is paid in credits, not rent.

**Change:**
- Lead with OpenAI (credits for the benchmark), and submit to NLnet only after reading the revised policy, with honest disclosure of AI use.
- Keep bridge contract income as the real runway.
- Replace "≥5 conversations" with "≥2 interview loops or contract offers."

## Sharpest modification: modest by default, with ambition behind gates
- **Gate 0, by 31 Dec 2026:** v5's kill test, with the fixes above (hooks merged, utility-aware benchmark, grant filed, ≥2 interview loops or contract offers).
- **Gate 1, by 31 Mar 2027.** Continue the ambitious track only if **all** of these hold:
  - a draft Android profile, "Keystore-attested agent key + AP2/Web Bot Auth signing", is posted to the FIDO TWG or the IETF webbotauth list and gets substantive replies;
  - **one** relying party (an app-protection vendor, a fintech app or a bank) agrees **in writing** to pilot verifying the tokens;
  - ≥2 on-device agents (UNO plus Operit or an OEM) emit them.
- **Gate 2, by Sep 2027:** ≥3 relying parties and a named liability or fraud metric improved. Then raise money (Seldon Lab or Juniper). Otherwise, fold the profile into the job or acqui-hire pitch, where it is still the strongest signal.
- If Gate 1 fails, stop the ambitious track and don't reopen it.

Sources: [Cloudflare/Visa/Mastercard on Web Bot Auth](https://www.anybiz.io/blogs/ai-agent-identity-and-payments/), [Visa TAP](https://eco.com/support/en/articles/14845482-visa-trusted-agent-protocol-tap-explained), [Skyfire KYA](https://stellagent.ai/insights/skyfire-kyapay-know-your-agent), [AP2 Android SDK and FIDO move](https://eco.com/support/en/articles/15192002-ap2-protocol-explained-google-s-agentic-commerce-standard-2026), [AP2 docs](https://ap2-protocol.org/), [Play Integrity limits](https://developer.android.com/google/play/integrity/overview).
