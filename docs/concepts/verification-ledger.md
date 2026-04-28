# Verification ledger

The `adversarial-default.md` rule says: every compliance claim requires positive evidence. Without a counterbalance, that demand would force every check to re-run on every task — a tax on productivity that quickly wipes out any benefit.

The verification ledger is the counterbalance. Results cache by `(path, check, sha256[:12])` so unchanged artifacts aren't re-checked. First check on a new artifact pays the verification cost; subsequent checks pay only the lookup cost.

This page covers the format, lookup protocol, when entries become stale, and how the ledger interacts with the rule.

---

## Where it lives

`.claude/state/verification-ledger.md` — tracked in git so the cache is cross-session and cross-machine. Format: a single markdown table; one row per `(path, check)` pair; sortable, greppable.

```markdown
| Path | Check | Verified At | File hash | Result | Evidence |
|------|-------|-------------|-----------|--------|----------|
| scripts/01_clean.do | no-hardcoded-paths | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | grep returned 0 matches |
| scripts/01_clean.do | seed-set-once | 2026-04-28T10:00Z | a1b2c3d4e5f6 | PASS | line 5: `set seed 20260428` |
| scripts/02_analysis.do | no-hardcoded-paths | 2026-04-28T10:05Z | f7e8d9c0b1a2 | FAIL | line 47: `use "/Users/foo/data.dta"` |
```

---

## Columns

- **Path** — repo-relative path to the artifact under check.
- **Check** — slug from the per-domain table in `adversarial-default.md` (e.g., `no-hardcoded-paths`, `seed-set-once`, `parallel-trends`, `incentive-compatibility`, `bibliography-resolves`).
- **Verified At** — ISO 8601 UTC, minute precision. The timestamp the check ran.
- **File hash** — `sha256(<path>) | head -c 12`. The file's content hash at the moment of check, truncated for readability.
- **Result** — `PASS`, `FAIL`, or `ASSUMED` (cost-prohibitive / infrastructure-unavailable).
- **Evidence** — short headline with the specific detail (line number, count, p-value, etc.). Long output goes in a session log; the ledger shows the headline.

---

## Lookup protocol

Before running check `C` on path `P`:

1. Compute `current_hash = sha256(P) | head -c 12`.
2. Read the ledger row for `(P, C)`.
3. Branch on what's there:

| Row state | File hash | Action |
|---|---|---|
| Row exists, `Result == PASS` | matches | Cite the cached row; skip running the check |
| Row exists, `Result == PASS` | differs | Stale → re-run, update the row in place |
| Row exists, `Result == FAIL` | matches | Still FAIL — flag as unresolved violation |
| Row exists, `Result == FAIL` | differs | Stale → re-run, update the row |
| Row doesn't exist | n/a | Run, append a new row |
| Row exists, `Result == ASSUMED` | any | Treat as untrusted; re-run if possible, otherwise inherit |

The intent: caching only applies to PASS rows on unchanged artifacts. Failures, hash mismatches, and assumed rows always trigger re-evaluation.

---

## Stale invalidation triggers

Beyond the file-hash check, three triggers force re-run regardless of cached state:

1. **The convention itself changed.** If the relevant rule file (e.g., `stata-code-conventions.md`) was modified after the row's `Verified At` timestamp, re-run. A rule update can invalidate a previously-passing artifact.
2. **`/tools verify --force`.** User-invoked. Rebuilds the ledger from scratch. Use when you've lost trust in cached results (e.g., suspect drift, or before a paranoid pre-submission audit).
3. **Pre-submission gate.** The `verifier` agent in submission mode runs `/tools verify --force` semantics automatically. Submission-grade audit doesn't trust the cache; every check re-runs.

---

## Cost analysis

The ledger's value depends on the asymmetry between check cost and lookup cost:

| Operation | Approximate cost |
|---|---|
| `sha256` of a typical script | microseconds |
| Lookup in the ledger (grep) | microseconds |
| `grep` over project for hardcoded paths | milliseconds |
| Compile a paper end-to-end with `pdflatex + biber` | tens of seconds |
| Run a master script end-to-end | minutes |
| AEA-deposit replication run on fresh clone | tens of minutes |

The lookup-vs-check asymmetry is at least 100x for the cheapest checks, and many orders of magnitude for the most expensive. Caching is essentially free; re-running is not. The ledger is what makes the adversarial-default rule's "demand evidence on every claim" sustainable.

---

## Audit utilities

The ledger is a living receipt. Useful greps:

```bash
grep '| FAIL |' .claude/state/verification-ledger.md
# → all open violations, project-wide

grep '01_clean.do' .claude/state/verification-ledger.md
# → verification history for one specific file

grep '| ASSUMED |' .claude/state/verification-ledger.md
# → all unverified-by-cost claims; review before submission
```

The `ASSUMED` query is especially important pre-submission. Each `ASSUMED` row represents a check that wasn't actually performed; the submission-mode verifier fails the project if any `ASSUMED` rows remain in load-bearing paths (`replication/`, `paper/`, `scripts/`, `experiments/`).

---

## What the ledger does NOT do

- **It does not re-verify automatically.** Stale rows are detected on access, not by background job. If you don't access a check, the stale row sits.
- **It is not a build system.** It doesn't track dependencies between artifacts. A file changing doesn't trigger re-verification of files that depend on it.
- **It does not eliminate human judgment.** A passing row means the mechanical check passed; it does not mean the underlying choice is correct. (See [`appropriate-use.md`](appropriate-use.md) for the substantive-vs-mechanical distinction.)

---

## Cross-references

- `.claude/rules/adversarial-default.md` — the rule that creates the ledger and lists which checks should populate it
- `.claude/state/verification-ledger.md` — the actual ledger file (gitignored if no real entries; example rows shown when first created)
- [`epistemic-rules.md`](epistemic-rules.md) — the four-rule stack; `adversarial-default` is the rule the ledger supports
- [`quality-scoring.md`](quality-scoring.md) — critics consult the ledger for their `Compliance Evidence` section in score reports
