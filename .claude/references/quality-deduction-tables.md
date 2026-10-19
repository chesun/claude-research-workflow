# Quality — per-target deduction tables

**Class:** B (overlay-customized; see `.claude/file-classes.toml`, and merge by hand, never copy over an overlay's version). Pointer-loaded detail for `.claude/rules/quality.md` § 3 Per-Target Deduction Tables (moved from the rule on 2026-10-19); there is no auto-load.

The rule keeps the score gates, the severity gradient, the § 3 Enforcement block and the replication tolerances. Each critic agent in `.claude/agents/` carries the deduction table it applies.

**Concrete deductions critics apply when scoring their target.** These supplement the severity gradient with target-specific rubrics.

### Paper LaTeX (`paper/main.tex`)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Compilation failure (pdflatex/xelatex) | -100 |
| Critical | Numbers in text don't match tables | -25 |
| Critical | Undefined citation | -15 |
| Critical | Broken reference (`\ref`) | -15 |
| Critical | Overfull hbox > 10pt | -10 |
| Critical | Typo in equation | -10 |
| Major | Notation inconsistency | -5 |
| Major | Missing figure/table at referenced path | -5 |
| Major | Hedging language ("interestingly", "it is worth noting") | -3 per (max -15) |
| Major | Anti-AI-prose violations (em-dash density, AI vocabulary cluster, tricolon overuse, significance inflation, etc.) — see `.claude/rules/anti-ai-prose.md` for the full catalog and `agents/writer-critic.md` for the per-pattern table | varies, capped at -30 |
| Minor | Overfull hbox 1–10pt | -1 |
| Minor | Long lines >100 chars (except math formulas) | -1 |

### R Scripts (`.R`)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Syntax errors / script doesn't run | -100 |
| Critical | Domain-specific bugs (wrong clustering, wrong estimand) | -30 |
| Critical | Code doesn't match strategy memo | -25 |
| Critical | Hardcoded absolute paths | -20 |
| Major | Missing robustness checks from memo | -15 |
| Major | Wrong clustering level | -15 |
| Major | Missing `set.seed()` | -10 |
| Major | Missing `.rds` saves | -10 |
| Major | Magnitude of main result implausible | -10 |
| Major | Missing figure/table generation | -5 |
| Major | Non-reproducible output (no `sessionInfo()`) | -5 |
| Minor | No documentation headers | -5 |
| Minor | Missing outputs (stale) | -5 |

### Stata Scripts (`.do`)

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Script doesn't run | -100 |
| Critical | Domain-specific bugs (wrong clustering, wrong estimand) | -30 |
| Critical | Code doesn't match strategy memo | -25 |
| Critical | Hardcoded absolute paths | -20 |
| Major | Missing robustness checks | -15 |
| Major | Missing `set seed` | -10 |
| Major | Missing `esttab`/`outreg2` output | -5 |
| Minor | No documentation headers | -5 |

### Talks (Beamer) — Advisory, Non-Blocking

| Severity | Issue | Deduction |
|----------|-------|-----------|
| Critical | Compilation failure | -100 |
| Major | Slide count outside format range | -10 |
| Major | Result not in paper (talk-only result) | -10 |
| Major | Notation mismatch with paper | -5 |
| Major | Anti-AI-prose violations on slides (em-dash density, tricolon overuse, AI vocabulary, hook-slide promotional inflation) — see `.claude/rules/anti-ai-prose.md` (voice profile `slide`) and `agents/storyteller-critic.md` for the per-pattern table | varies, capped at -15 |
| Minor | Overfull hbox | -2 |
| Minor | Dense slide without spacing fix | -1 |

Talk scores are reported as "Talk: XX/100" but do **not** block commits or PRs.
