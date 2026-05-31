# Requirements Specification: [Title]

**Date:** [YYYY-MM-DD]
**Status:** DRAFT | APPROVED

---

## Objective

[One sentence: what success looks like]

---

## Requirements

### MUST Have (Non-Negotiable)

- [ ] [Required feature or constraint]
- [ ] [Required feature or constraint]

### SHOULD Have (Preferred)

- [ ] [Preferred feature or enhancement]
- [ ] [Preferred feature or enhancement]

### MAY Have (Optional, If Time)

- [ ] [Nice-to-have enhancement]
- [ ] [Nice-to-have enhancement]

---

## Clarity Status

| Aspect | Status | Notes |
|--------|--------|-------|
| [Ambiguous aspect] | CLEAR / ASSUMED / BLOCKED | [How it was resolved or why it's assumed] |
| [Another aspect] | CLEAR / ASSUMED / BLOCKED | [Explanation] |

**Status Definitions:**
- **CLEAR:** Fully specified, no ambiguity
- **ASSUMED:** Reasonable assumption made in absence of clarity; user can override
- **BLOCKED:** Cannot proceed until this is answered

---

## Acceptance Criteria

Every criterion is operationalized into a **falsifiable** check and tagged with the **Verification Tier** at which "achieved" will be confirmed. This is Step-0 operationalization (see `.claude/rules/adversarial-default.md` § Evidence gating, and `.claude/references/evidence-gating-detail.md`): pushing apparent judgment down into checkable sub-claims *before* any work runs, so that a later verdict of "achieved / compliant" cites a tagged criterion rather than asserting itself. A vague goal that cannot be tier-tagged is not yet a criterion — operationalize it further or mark it BLOCKED.

Every row must specify **both** a **Level** (MUST/SHOULD/MAY) **and** a **Verification Tier** (Tier 1/2/3); these are independent axes. The Level says how binding the criterion is; the Tier says how its "achieved" verdict gets confirmed. They do not constrain each other — a Tier-1 check can be MUST, SHOULD, or MAY, and a Tier-3 judgment can likewise be any level.

| # | Criterion (measurable, falsifiable) | Level | Verification Tier | How it will be checked |
|---|-------------------------------------|-------|-------------------|------------------------|
| 1 | [e.g. script runs to completion, exit 0] | MUST | Tier 1 (script-decidable) | [e.g. `Rscript main.R`; exit code] |
| 2 | [e.g. guard at the documented line + null test passes] | SHOULD | Tier 2 (locatable judgment) | [e.g. `file:line` citation + named test] |
| 3 | [e.g. identification argument is sound] | MUST | Tier 3 (irreducible judgment) | [independent refutation / panel — see `.claude/references/evidence-gating-tier3-panel.md`] |

**Verification Tier definitions:**

- **Tier 1 — script-decidable:** a deterministic script yields yes/no (diff, grep, test exit). Prefer this; operationalization should push as many criteria here as possible.
- **Tier 2 — locatable judgment:** decomposes into sub-claims each pinned to an artifact (`file:line`, a test, an output value) plus a sufficiency argument.
- **Tier 3 — irreducible judgment:** no single artifact pins it; verified by independent refutation or a diverse-lens panel. Keep this residue as small as operationalization allows.

> **Advisory, never blocking.** Tier-tagging is a discipline, not a gate. Its purpose is to prevent lazy "did it work? yes" verdicts. An untagged criterion does not block the spec; it earns a reminder. (A critic deduction for "achieved / compliant" verdicts that cite no tagged criterion is a candidate future hardening, not wired into any critic agent today.)

---

## Approval

[ ] User approved: [Date]
