# Verification Ledger

Cache of verification results for the adversarial-default rule (`.claude/rules/adversarial-default.md`). Each row is one `(path, check)` pair. Agents consult this before running a check; if `File hash` matches the current `sha256(path) | head -c 12` AND `Result == PASS`, the cached result is cited and the check is not re-run.

**Columns:**

- *Path* — repo-relative path to the artifact under check.
- *Check* — slug from the per-domain table in `adversarial-default.md` (e.g., `no-hardcoded-paths`, `seed-set-once`, `parallel-trends`, `incentive-compatibility`), OR a `diagnosis:<symptom-slug>` row recording an investigated bug/error cause (`Result` = `DIAGNOSED` / `RULED-OUT`). Grep these before re-diagnosing — see `adversarial-default.md` § Diagnostic findings.
- *Verified At* — ISO 8601 UTC, minute precision.
- *File hash* — `sha256(<path>) | head -c 12`. Content hash, not metadata.
- *Result* — `PASS`, `FAIL`, or `ASSUMED` (cost-prohibitive / infrastructure-unavailable).
- *Evidence* — short headline with the specific detail (line number, count, p-value, etc.). Full output → session log.

**Update protocol** is in `.claude/rules/adversarial-default.md` § Verification ledger. Stale rows (file hash mismatch, or convention rule modified after `Verified At`) are re-run on access.

---

| Path | Check | Verified At | File hash | Result | Evidence |
|------|-------|-------------|-----------|--------|----------|
| _example_ scripts/01_clean.do | no-hardcoded-paths | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | grep returned 0 matches |
| _example_ scripts/02_analysis.do | seed-set-once | 2026-04-28T10:00Z | f7e8d9c0b1a2 | FAIL | 0 occurrences in master.do |
| _example_ paper/main.tex | bibliography-resolves | 2026-04-28T10:05Z | 9e8d7c6b5a4f | ASSUMED | Cost-prohibitive: full pdflatex+biber run not yet executed in this session |

<!-- Real entries replace the _example_ rows above. Keep one row per (path, check). When a file changes, its rows become stale and are re-evaluated on next access. -->
| .claude/hooks/test_normdiff_lib.py | tests-pass | 2026-05-30T01:30Z | f4919ba6bebb | PASS | re-ran standalone: 32/32 checks passed (incl. 7 regression tests for the 4 review-caught bugs), exit 0 |
