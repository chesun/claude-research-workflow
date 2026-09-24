# Session Log: 2026-09-24 -- Model routing (ADR-0003) and the dual-workflow feature policy

**Status:** COMPLETED

## Objective

Decide and wire a model split now that two frontier tiers are available: `fable` for thinking, planning, and review; `opus` for execution. Settle how features wanted in both this repo and the sibling consulting workflow are handled.

## Changes Made

| File | Change | Reason |
|------|--------|--------|
| `decisions/0003_model-routing-fable-review-opus-execution.md` | New ADR | Record the routing decision, its safety condition (ADR-0002 must hold), and the experiment |
| `decisions/README.md` | Index rows for ADR-0002 (was missing) and ADR-0003 | Index was stale |
| `.claude/agents/*.md` (16 of 17) | `model: inherit` → `fable` (critics, referees, editor, verifier, tikz-reviewer, writer) or `opus` (coder, data-engineer, explorer, librarian, storyteller) | Per ADR-0003; `orchestrator` unchanged |
| `.claude/skills/review-build/SKILL.md` | Dispatch rule: reviewers on `model: fable` | Reviewer never on a weaker model than the author |
| `.claude/rules/independent-review.md` | Item 5 names the review model | Same |
| `.claude/rules/agents.md` | New § Model routing under Adversarial Pairing | One place that states the mapping |
| `TODO.md` | Experiment read-out item | Keep the "is this working" question visible |

## Design Decisions

| Decision | Alternatives Considered | Rationale |
|----------|------------------------|-----------|
| Reviewers `fable`, workers `opus`, main session `fable` | Everything on `fable`; everything on `opus` | Cost is not a constraint; gains are speed on execution and author/reviewer on different models. Safe only because ADR-0002 makes review mandatory |
| `writer` stays on `fable` | `opus` like other workers | Voice preservation is the next build and prose fidelity is judgment-heavy; revisit after |
| Aliases, not dated IDs | Dated pins per agent | The 2026-09-22 survey skipped dated pins as brittle |
| Dual-workflow features: copy-and-adapt, one-way (here → consulting repo), ported features registered in that repo's `INHERITANCE.md`, each port reviewed there | Shared plugin installed in both | A personal-hosted plugin on a firm machine is a firm-policy question, and it would bypass the consulting repo's ADR-0016 review on import. Its ADR-0001 already chose copy-and-adapt |

## Incremental Work Log

- Discussed the split and the dual-workflow question; user approved the plan.
- Wrote ADR-0003; retagged 16 agent files; wired `/review-build`, `independent-review.md`, `agents.md`; fixed the ADR index.
- Not committed in this log entry; see the commit that follows.

## Verification Results

| Check | Result | Status |
|-------|--------|--------|
| Every agent file has exactly one `model:` line with a value in {fable, opus, inherit} | see commit | PASS |
| `agents.md` § Model routing lists the same mapping as the frontmatter | grep cross-check | PASS |
| ADR-0003 cites only existing files | paths checked | PASS |

## Open Questions / Blockers

- [ ] Both aliases resolve on the account each repo's sessions run under; verify on the next machine or account change.
- [ ] Claim-verifier (`/verify-claims`): build here as candidate two and port, or build first in the consulting repo where source access is gated. User's call when it comes up.

## Next Steps

- [ ] Run the next few builds under the split; record findings by severity and fix rounds per review here and in the review reports.
- [ ] Revisit the `writer` exception after the voice-preservation build.
