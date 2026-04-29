---
name: review
description: All quality reviews — routes to appropriate critics based on target file type and flags. Replaces /paper-excellence, /proofread, /econometrics-check, /review-r, /review-paper.
argument-hint: "[file path or --flag] Options: --peer [journal], --methods, --proofread, --code, --replicate [lang], --all"
allowed-tools: Read,Grep,Glob,Write,Bash,Task
---

# Review

Unified review command that routes to the appropriate critic agents based on the target and flags.

**Input:** `$ARGUMENTS` — file path and/or flags.

---

## Routing Logic

### Auto-detect by file type
- `.tex` paper file → **Comprehensive review** (writer-critic + strategist-critic + Verifier)
- `.R`, `.py`, `.do`, `.jl` file → **Code review** (coder-critic standalone, categories 4-12)
- `.tex` talk file (in talks/) → **Talk review** (storyteller-critic)

### Explicit flags (override auto-detect)
- `--peer` → **Full peer review** (domain-referee + methods-referee, independent blind reports + editorial synthesis)
- `--peer [journal]` → **Journal-calibrated peer review** (same, but referees emulate that journal's review culture via .claude/references/journal-profiles.md)
- `--methods` → **Causal audit** (strategist-critic standalone, 4-phase review)
- `--proofread` → **Manuscript polish** (writer-critic standalone, 6 categories)
- `--code [file]` → **Code review** (coder-critic standalone, categories 4-12)
- `--replicate [language]` → **Cross-language replication** (Coder re-implements in target language + coder-critic + comparison)
- `--all` or no file → **Paper excellence** (all critics in parallel + weighted score)

---

## Mode Details

### Comprehensive Review (default for .tex paper)
Dispatch in parallel:
1. **strategist-critic** — causal design audit (4 phases)
2. **writer-critic** — manuscript polish (6 categories)
3. **Verifier** — compilation check
Compute weighted aggregate score.

### Full Peer Review (`--peer` or `--peer [journal]`)
Simulates journal peer review:
1. Dispatch **domain-referee** — subject expertise review (5 dimensions, weighted)
2. Dispatch **methods-referee** — econometric methods review (5 dimensions, weighted)
3. Both reviews are independent and blind
4. If a journal name is provided, pass it to both referees — they read `.claude/references/journal-profiles.md` and calibrate to that journal's review culture
5. Both write reports to `quality_reports/reviews/YYYY-MM-DD_<target>_domain_review.md` and `..._methods_review.md` per `.claude/rules/agents.md` § 2.
6. Orchestrator dispatches **editor** to synthesize an editorial decision: Accept / Minor / Major / Reject (saved as `..._editor_review.md`).

### Code Review (`--code` or auto-detect .R/.py/.do)
Dispatch **coder-critic** in standalone mode:
- Categories 4-12 only (code quality, no strategy comparison)
- Critic writes report to `quality_reports/reviews/YYYY-MM-DD_<target>_coder_review.md` per the canonical path.

### Causal Audit (`--methods`)
Dispatch **strategist-critic** standalone (applied-micro overlay):
- Full 4-phase review (claim, design, inference, polish)
- Critic writes report to `quality_reports/reviews/YYYY-MM-DD_<target>_strategist_review.md`.

### Manuscript Polish (`--proofread`)
Dispatch **writer-critic** standalone:
- 6 categories: structure, claims-evidence, ID fidelity, writing, grammar, compilation
- Critic writes report to `quality_reports/reviews/YYYY-MM-DD_<target>_writer_review.md`.

### Cross-Language Replication (`--replicate [language]`)
Re-implement existing code in a different language and compare outputs:
1. Auto-detect source language from file extension (`.R`, `.py`, `.do`, `.jl`)
2. Dispatch **Coder** in replication mode — re-implement in target language (writes to `scripts/[target-language]/`)
3. **coder-critic** reviews both implementations and writes report to `quality_reports/reviews/YYYY-MM-DD_<target>_replicate_<lang>_coder_review.md`.
4. Compare numerical outputs per `.claude/references/domain-profile.md` Quality Tolerance Thresholds.

Divergences are flagged with exact values. The report includes a side-by-side table.

---

## Review-report path convention

All critics write to `quality_reports/reviews/YYYY-MM-DD_<target>_<critic>_review.md`. Critics consult `quality_reports/reviews/INDEX.md` first; if an `Active` review exists for the same target, they follow the supersession protocol (mark prior `Status: Superseded by <new-path>`, `git mv` to `archive/`, set `Supersedes:` in the new report, update `INDEX.md`). See `quality_reports/reviews/README.md` for full lifecycle conventions.

---

## Scoring

| Mode | Blocking? | Gate |
|------|-----------|------|
| Comprehensive | Yes | 80 commit, 90 PR |
| Peer Review | Yes | Referee recommendation |
| Code Review | Yes | 80 commit |
| Causal Audit | Yes | 80 commit |
| Proofread | Yes (paper), Advisory (talks) | 80 commit |

---

## Principles
- **Smart routing.** File type determines the default review mode.
- **Flags override.** Use explicit flags for targeted reviews.
- **Critics never edit source artifacts.** They do write review reports to `quality_reports/reviews/` — that is the audit trail. Source vs report distinction per `.claude/rules/agents.md` § 2.
- **Proportional severity.** Phase-aware deductions per quality.md.
