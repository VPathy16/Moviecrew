# Bastion Crew — a per-employee agent team that runs fully offline inside air-gapped defence and secure-facility networks
Lens: Defence / air-gapped environments
## Customer & pain
Payers: defence primes, sub-contractors, shipyards, national labs, and government integrators (ITAR/CUI, UK/EU/Indian/Gulf defence supply chains) whose engineers work on disconnected or accredited networks. Cloud agents (Claude Code, Cowork, Copilot) are banned there. Staff do tedious manual work: compiling status reports, chasing approvals, reformatting documents to spec, tracking action items, scheduling, and moving files across security domains. Existing "secure AI" is a single chatbot on a GPU box with no actions, no memory of your work, and no rules on what it may touch.
## Product
Each employee gets a team of scoped vanaras, all running inside the enclave. Phone-equivalent: a hardened handset or thin client for reminders, calls and voice notes, and the daily-life agent (calendar, comms, errands). Cloud-equivalent: an on-prem "project node" (rack server or workstation) where agents keep working overnight on drafts, document checks and test-log triage. Desktop: an agent that operates files and internal web tools under least-privilege scopes. Shared memory is a local encrypted store that never leaves the enclave; agent-to-agent sync happens over the local network, and the phone agent can hand a spoken request to the project agent, which returns a finished document for approval. Reference tokens keep classified names, part numbers and personal data away from the model, and approvals and spend/action rules are enforced on the device and logged as a tamper-evident audit trail. Models are local open-weight (BYO), swapped per accreditation level.
## Wedge (first product, first 10 customers)
Start with unclassified-but-controlled (CUI/ITAR) work at small defence sub-contractors, where an on-prem install is acceptable and accreditation is lighter. First product: a single-box "Bastion Node" with the meeting/action-item and document-compliance agents, priced as a pilot. Get customers via a reference deployment with one friendly integrator or a defence-tech accelerator, and via offset/local-content schemes in India, EU and Gulf states. First 10: sub-contractors and mid-size suppliers reached through founder network and warm intros; a paid 90-day pilot each.
## Enterprise path
Pilot, then department deployment, then site-wide licences. Add accreditation evidence (common criteria style docs, SBOM, reproducible builds), then cross-domain transfer agents that hand work through a data diode with human approval. Partner with integrators who already hold accreditation and resell.
## Business model & pricing
Per-seat annual licence (about $600-1,500 per employee/yr) plus a per-site node fee and support/accreditation services. Pilots $15-40K. Services margin funds early growth.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
Their agents depend on cloud models and telemetry; air-gapped accredited versions are low-volume, slow-sales, and support-heavy. Government clouds exist but do not cover disconnected sites or sovereignty requirements of non-US buyers. Local vendors want a neutral, inspectable, model-agnostic layer.
## Biggest risk
Sales cycles and accreditation: 12-24 months to real revenue, and a solo founder may lack the credibility and clearances to be trusted. Also local models may be too weak for reliable actions (guess).
## Uses founder's existing assets
Scoped agents locked to their own tools, handover between agents, on-device approvals and spend rules, reference-token privacy, the service-agnostic MCP pipeline (pointed at internal tools), scheduled background jobs, voice, and BYO model key (becomes BYO local model).
## Scores
market_size: 6
defensibility: 7
feasibility_solo_30k: 3
asset_fit: 8
excitement: 7
