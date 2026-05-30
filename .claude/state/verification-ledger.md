# Verification Ledger

Cache of verification results for the adversarial-default rule (`.claude/rules/adversarial-default.md`). Each row is one `(path, check)` pair. Agents consult this before running a check; if `File hash` matches the current `sha256(path) | head -c 12` AND `Result == PASS`, the cached result is cited and the check is not re-run.

**Columns:**

- *Path* — repo-relative path to the artifact under check.
- *Check* — slug from the per-domain table in `adversarial-default.md` (e.g., `no-hardcoded-paths`, `seed-set-once`, `parallel-trends`, `incentive-compatibility`), OR a `diagnosis:<symptom-slug>` row recording an investigated bug/error cause (`Result` = `DIAGNOSED` / `RULED-OUT`). Grep these before re-diagnosing — see `adversarial-default.md` § Diagnostic findings.
- *Verified At* — ISO 8601 UTC, minute precision.
- *File hash* — `sha256(<path>) | head -c 12`. Content hash, not metadata.
- *Result* — `PASS`, `UNVERIFIED`, `FAIL`, or `ASSUMED` (cost-prohibitive / infrastructure-unavailable). For `diagnosis:` rows, `DIAGNOSED` / `RULED-OUT`. See the verdict vocabulary in `.claude/references/evidence-gating-detail.md`.
- *Evidence* — short headline with the specific detail (line number, count, p-value, residue summary, etc.). Full output → session log.
- *Tier* — checkability tier `1` / `2` / `3` per the evidence-gating discipline (1 = script-decidable, 2 = locatable judgment, 3 = irreducible judgment). Optional; blank ⇒ Tier 1.
- *Artifact Citation* — Tier-2 `file:line-range[:test_id]` citation the verdict rests on. Optional; blank for Tier-1 rows.
- *Refuter Tally* — Tier-3 independent-refuter outcome (e.g. `0/3 refuted`). Optional; blank for Tier-1/2 rows.

**Backward compatibility:** the last three columns (`Tier`, `Artifact Citation`, `Refuter Tally`) were appended after `Evidence` so pre-existing 6-column rows stay valid — their trailing cells are simply empty. **A pre-existing row without the new columns is treated as Tier-1 with empty citation/tally.** Consumers parse the first six columns positionally; the appended columns never shift them.

**Update protocol** is in `.claude/rules/adversarial-default.md` § Verification ledger. Stale rows (file hash mismatch, or convention rule modified after `Verified At`) are re-run on access. The PostToolUse evidence recorder writes/updates `no-logic-change` rows in place (one per file).

---

| Path | Check | Verified At | File hash | Result | Evidence | Tier | Artifact Citation | Refuter Tally |
|------|-------|-------------|-----------|--------|----------|------|-------------------|---------------|
| _example_ scripts/01_clean.do | no-hardcoded-paths | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | grep returned 0 matches | | | |
| _example_ scripts/02_analysis.do | seed-set-once | 2026-04-28T10:00Z | f7e8d9c0b1a2 | FAIL | 0 occurrences in master.do | | | |
| _example_ paper/main.tex | bibliography-resolves | 2026-04-28T10:05Z | 9e8d7c6b5a4f | ASSUMED | Cost-prohibitive: full pdflatex+biber run not yet executed in this session | | | |

<!-- Real entries replace the _example_ rows above. Keep one row per (path, check). When a file changes, its rows become stale and are re-evaluated on next access. -->
| .claude/hooks/test_normdiff_lib.py | tests-pass | 2026-05-30T01:30Z | f4919ba6bebb | PASS | re-ran standalone: 32/32 checks passed (incl. 7 regression tests for the 4 review-caught bugs), exit 0 |
| .claude/hooks/test_normdiff_lib.py | tests-pass | 2026-05-29T18:45Z | f4919ba6bebb | PASS | re-verified: 32/32 checks passed, exit 0 |
| .claude/hooks/test_diagnostic_claim_audit.py | tests-pass | 2026-05-29T18:45Z | cd21751569a3 | PASS | pytest: 7 passed in 0.14s, exit 0 (direct python3 is no-op; pytest required) |
| .claude/hooks/evidence-gate-recorder.py | diagnosis:ledger-append-positional-parse | 2026-05-29T18:45Z | 2c604ecd47b4 | RULED-OUT | Only positional ledger consumer; reads rc[0]/rc[1] under len>=2 guard, appended cols 7-9 don't shift pos 0-1; live regression on ledger copy: insert OK, in-place update found row once, all pre-existing rows still parse |
| .claude/hooks/diagnostic-claim-audit.py | diagnosis:ledger-append-positional-parse | 2026-05-29T18:45Z | 54279b103d97 | RULED-OUT | Column-agnostic: ledger_consulted_this_session matches filename fragment in Read/Bash, never splits the table; immune to column changes |
| .claude/state/verification-ledger.md | ledger-append-not-insert | 2026-05-29T18:45Z | faf40002b020 | PASS | Tier/Artifact-Citation/Refuter-Tally are last 3 cols after Evidence; header+separator 9-col; 4 pre-existing 6-col rows intact and first-6-cols unbroken | | | |
| .claude/hooks/test_normdiff_lib.py | backward-compat-ledger-schema | 2026-05-29T20:00Z | 14d316326ba3 | PASS | 4 new tests added (6-col + 9-col parse at pos 0/1/4; _upsert_ledger_row update-in-place no-dup; append new row preserves old 6-col); full suite 36/36 passed, exit 0 | 1 | | |
