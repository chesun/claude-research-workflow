# Task Completion Verification

**At the end of every task, verify the output actually works.** This is non-negotiable.

Verification complements the `verifier` agent — agent dispatch is reserved for pre-submission audits; this rule applies at every routine task boundary (commit, PR, end-of-session).

---

## Per-Target Checklists

### Paper LaTeX (`paper/main.tex` or Overleaf path)

1. Compile with 3-pass `pdflatex` (or `xelatex`) + `bibtex`/`biber` — check for errors.
2. Verify all `\ref{}` and `\cite{}` resolve (no `undefined references` warnings).
3. Check for overfull hbox warnings > 1pt.
4. Verify tables compile and display correctly.
5. Verify figures exist at referenced paths.
6. Report verification results to the user.

### Talks (Beamer `.tex`)

1. Compile with `pdflatex` — check for errors.
2. Verify figures/tables match paper versions (same script output).
3. Check for overfull hbox warnings.
4. Verify slide count is appropriate for the format (see `single-source-of-truth.md`).

### Analysis Scripts

- **Stata:** run `do scripts/stata/main.do`; check log for errors; verify output `.tex`/`.pdf` files exist and are non-zero.
- **R:** run `Rscript scripts/R/filename.R`; verify output files (PDF, RDS, .tex) exist with non-zero size; spot-check estimates for reasonable magnitude; verify `set.seed()` is present for stochastic analyses.
- **Python:** activate venv, run `python script.py`; verify outputs.

---

## Common Pitfalls

- **Assuming success** — always verify output files exist AND contain correct content.
- **Stale figures** — script output may be older than the paper revision; check timestamps.
- **Hardcoded paths** — paths must be relative to project root.
- **Missing packages** — `library()` / `ssc install` / `requirements.txt` must match what the script needs.

---

## Verification Checklist

- [ ] Output file created successfully
- [ ] No compilation/render errors
- [ ] Figures/tables display correctly
- [ ] All references and citations resolve
- [ ] Results reported to user

---

## When to Dispatch the Verifier Agent

The `verifier` agent is a separate, heavier-weight audit. Dispatch it when:

- Before a commit that touches the paper, talks, or analysis scripts.
- Before a PR.
- Before submission (submission mode — runs the full 6-check AEA audit; see `replication-protocol.md` §5.2).

For routine end-of-task verification (what this rule covers), you don't need to dispatch the agent — run the checklist above directly.
