# Thesis Crew — a persistent team of agents that runs your research from reading list to defended thesis
Lens: Students and researchers
## Customer & pain
Payers: PhD students and postdocs (individually), then labs and graduate schools (PIs, deans). Pain: a research project lives across five places. Papers and PDFs sit on the laptop, reading notes on the phone, long experiments and literature monitoring nowhere, and each AI chat forgets the last one.
## Product
- Phone vanara (Reader): captures papers, voice notes and ideas on the go, reminds about advisor meetings and deadlines, and drafts the weekly update email for approval.
- Cloud vanara (Watcher): runs 24/7 on a project's repo, so it monitors arXiv/PubMed/citation alerts for the topic, re-runs analysis scripts and reproducibility checks, and drafts related-work sections while the laptop is off.
- Desktop vanara (Librarian): organises local PDFs, Zotero and LaTeX, fills reference libraries, and checks every citation against a real DOI before it is written.
- Shared memory holds the research question, hypotheses, what was tried and rejected, and the advisor's feedback. Handover: the Reader hears "Prof. said try method B", the Watcher finds two new papers on B and queues a run, the Librarian pulls the PDFs and adds the citations. Unpublished data is replaced by reference tokens, so the model never sees raw data or participants' identities, which makes it usable under ethics and IRB rules.
## Wedge (first product, first 10 customers)
An Android app plus a small desktop helper for one job: the literature loop (capture, weekly digest, verified citations, advisor-update draft). Recruit 10 PhD students by hand through lab mailing lists and Reddit r/PhD and r/GradSchool, then two friendly labs.
## Enterprise path
Labs, then departments and graduate schools, then university IT and R&D orgs at pharma and deep-tech companies. R&D teams are the same product with the company's rules in place of the university's.
## Business model & pricing
Individuals $12/month, or $8 for students on annual plans (guess). Lab plan $15 per seat/month, min 5 seats. Institutional site licences $20-40K/year (guess). BYO key keeps gross margin above 80%; optional managed inference is an add-on.
## Why big tech (Google/Apple/Microsoft/OpenAI/Anthropic) won't just do it
They ship horizontal assistants and generic "deep research" tools. They ship generic tools; universities distrust sending unpublished data to any one vendor, and a model-neutral layer is what they can accept.
## Biggest risk
Students have little money and switch tools freely, and adoption inside a lab depends on a single champion. A verified-citation guarantee that fails even once destroys trust.
## Uses founder's existing assets
- Scoped vanaras with locked tools map directly to Reader, Watcher and Librarian.
- Handover between agents and scheduled background jobs carry the weekly digest and monitoring.
- Approvals and spend rules on the device gate emails to advisors and any paid-API usage.
- Reference tokens keep unpublished data and participants' details away from the model.
- The MCP pipeline classifying tools by role connects Zotero, arXiv, PubMed, Overleaf and GitHub without custom code.
- Voice supports lab-note dictation, and BYO model key removes inference cost.
## Scores
market_size: 6
defensibility: 5
feasibility_solo_30k: 8
asset_fit: 8
excitement: 7
