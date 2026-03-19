# Strategist Agent vs. Identification Rule: Comparison

**Decision needed:** Should we use Hugo's strategist/strategist-critic agents, the identification-strategy rule, or both?

---

## What Each Does

**Identification-strategy rule** (what I created):
- Always-on reference document loaded into context
- Tells Claude "every causal claim needs: estimand, assumption, threat, diagnostic"
- Lists strategy-specific requirements (FE, DiD, IV, RDD, SC)
- Robustness checklist
- Passive — shapes Claude's behavior when writing/reviewing code

**Hugo's strategist agent** (worker):
- Active agent you invoke to DESIGN an identification strategy
- Given a research question + data → produces a strategy memo, pseudo-code, robustness plan, falsification tests
- Ranks candidate strategies by credibility
- Anticipates referee objections
- Outputs structured documents to `quality_reports/strategy/`

**Hugo's strategist-critic agent** (critic):
- 4-phase sequential review: Claim → Design Validity → Inference → Polish
- Design-specific checklists (DiD, staggered DiD, IV, RDD, SC, event study) — extremely detailed
- Mandatory sanity checks (sign, magnitude, dynamics, consistency)
- Package-specific checks (fixest, did, rdrobust, Synth, etc.)
- Citation fidelity verification
- Early stopping: if core design is broken, focuses report there
- Outputs structured review report

---

## Comparison

| Dimension | Rule Only | Agents Only | Both |
|-----------|-----------|-------------|------|
| **When it helps** | Always (passive guidance) | On-demand (active design/review) | Always + on-demand |
| **Design phase** | Reminds you to document assumptions | Actually designs the strategy | Rule sets standards, agent does the work |
| **Review phase** | Reminds you to check things | Runs a 4-phase structured audit | Rule catches basics, agent does deep audit |
| **Context cost** | ~100 lines loaded every conversation | ~300+ lines only when invoked | Rule always loaded; agents only when needed |
| **Overlap** | Some — both list what to check | Some — agent is more thorough | Minimal — rule sets principles, agents execute |
| **Gap if missing** | No active design help | No passive guidance when writing code | None |

---

## Recommendation: Use Both

**The rule and agents serve different purposes with minimal overlap.**

- **Rule** = constitution (always-on, shapes all Claude behavior around causal claims)
- **Strategist** = designer (invoked to create identification strategies from scratch)
- **Strategist-critic** = auditor (invoked to review papers/code for identification validity)

**Concrete workflow:**
1. You're writing a .do file → the **rule** reminds Claude to document assumptions, check clustering, flag causal language without identification
2. You invoke `/identify` → the **strategist agent** designs the full strategy, outputs a memo
3. You invoke `/review --identification` → the **strategist-critic** runs the 4-phase audit

**What to adapt for applied micro:**
- Strategist: already generic and excellent — works as-is. Add Stata package checks alongside R.
- Strategist-critic: mostly R/package references (fixest, did, rdrobust). Need to add Stata equivalents (reghdfe, ivreghdfe, did_multiplegt, csdid, rdrobust in Stata, synth).
- Rule: keep as-is — it's the lightweight always-on version

**Proposed names on applied-micro branch:**
- `identification-strategy.md` (rule) — already created
- `strategist.md` (agent) — copy from Hugo, adapt for Stata
- `strategist-critic.md` (agent) — copy from Hugo, adapt for Stata

CS: Agree? Should I copy Hugo's agents and adapt for Stata?
