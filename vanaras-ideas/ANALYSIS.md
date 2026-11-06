# Vanaras — analysis of 100 company ideas

100 agents each proposed one company through a different lens (lenses.txt). Every idea is in ideas/, and the
self-scores are in scores.csv (python3 score.py).

## Read this first: the scores are weak signal
Each agent scored its own idea, so totals bunch between 29 and 40 out of 50 and every idea rates itself "good".
Use the scores to sort, not to decide. The clustering and the judgement below matter more.

## What 100 ideas say, in one line
Almost every idea (about 85 of 100) rebuilt the same core: scoped vanaras locked to their own tools, approvals
and spend rules enforced on the phone, and personal data passed as reference tokens. Only the customer changed.
**The trust layer is the constant; the vertical is the variable.** That is the Vanaras company.

## The six real clusters
| Cluster | ~Count | Examples | Verdict |
|---|---|---|---|
| A. The trust layer itself (authority, approvals, memory, sync) | 15 | 100 Leash, 035 Warrant, 087, 083, 097, 033, 034, 036, 037 | Strongest; top 2 scores; uses every UNO asset |
| B. Solo / micro-company back office ("AI staff") | 17 | 099 Kishkinda, 002 Foreman, 084, 075 Cashvana, 094, 013 | Closest to "a company of AI employees"; clear ROI |
| C. Household / personal life | 8 | 026 Hearth, 027 Kinfolk, 093 Carebench, 092 Renewly, 028 | Closest to UNO today; high emotion; pay risk |
| D. Regulated professionals (privacy is the product) | 16 | 007 Briefkeep, 005, 006, 029 Keepwell, 042, 030 | Good fit for reference tokens; slow sales |
| E. One role inside a company (sales, PM, IT, SOC...) | 35 | 009, 012, 047, 052, 060, 088, 090 | Many ideas, weak differentiation, head-on with copilots |
| F. Company-wide rollout (BYO agents, MDM, OEM) | 9 | 078 Sherpa Seat, 079, 039, 038, 081 | This is the enterprise stage, not the start |

Many ideas are the same idea under different names ("Tether" appears 9 times; "Leash" 3), so the real
diversity is about 6 directions, not 100.

## Top 3
1. **Leash (100, with 035 and 087): your phone is the boss of all your agents.**
   - What it is: the phone holds the rules and approvals for every agent you run: cloud coding agents,
     desktop computer-use agents, MCP tools. A thin gateway in the cloud checks each action and asks the phone
     for a tap when it's risky. It keeps one log across all agents and gives each agent a daily spend cap.
   - Why it's first: it is the layer that makes "one team across phone, cloud and desktop" possible, it is
     vendor-neutral (no lab will police a rival's agents), and the founder is its first user.
   - Wedge: "approvals and spend caps for your coding agent" (an MCP gateway plus the Android app).
   - Enterprise path: agent identity plus corporate-card-style controls per employee.
   - Risk: labs ship their own mobile approvals (Claude Code already has phone approval flows), and MCP auth
     standards may absorb the gateway. Agent-security startups are well funded (see options-loop/).
2. **Kishkinda (099): the back office of a company with one human and twelve vanaras.**
   - What it is: each vanara is a "hire" with a job description (its scoped tools), a budget (spend rules),
     a manager (you) and an audit trail.
   - Wedge: a "Collections Clerk" that chases unpaid invoices, priced on outcome.
   - Why: it is literally "AI employees working for you like a company", with clear ROI.
   - Risk: Xero, QuickBooks and Ramp add agents themselves; one wrong payment costs the brand.
3. **Hearth (026): a chief of staff for the whole family.**
   - What it is: each family member has private vanaras that share one home memory, with rules on who
     approves what.
   - Why: it is closest to what UNO already does, and it is a daily-life product big tech avoids
     (multi-person consent, minors).
   - Risk: willingness to pay, and trust with children's and health data.

## Recommendation
Build Vanaras as one platform with one wedge:
- **Platform:** the Leash layer (phone as root of trust, scoped agents, approvals, reference tokens, shared
  memory, sync across phone, cloud and desktop). This is what the 100 ideas agree on.
- **First product:** pick one of:
  - (a) Leash for people running coding and cloud agents. The founder is the user, and it needs the least
    new surface.
  - (b) Kishkinda's Collections Clerk. Paying SMB customers, and closest to the "AI company" story.
- **Enterprise:** cluster F (078 Sherpa Seat): employees bring their own vanaras, and IT gets the admin
  console.
- **Avoid for now:** cluster E, single roles inside companies. That is head-on with Microsoft, Google and
  Salesforce copilots.

## Next step
Take the top 2–3 through the red team + market research loop before building.
