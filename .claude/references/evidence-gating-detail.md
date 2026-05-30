# Evidence-Gating Detail

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/adversarial-default.md` § Evidence gating. Open this when that section points you here; there is no auto-load.

This is the heavy content the always-on rule deliberately defers: the three checkability tiers, the `{PASS, UNVERIFIED, FAIL}` vocabulary in full, the normalizer interface, the citation-existence contract (Phase 3), and the optional-hardening spec.

**Design of record:** `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` §7. **Build plan:** `quality_reports/plans/2026-05-29_evidence-gating-build-plan.md`.

---

## The one principle (restated)

> A verdict is only as good as the evidence it carries. Require the evidence in every verdict; scale the verification *mechanism* to how checkable that evidence is.

This is the operational form of `adversarial-default.md` ("burden of proof is on the asserter; compliance is a positive claim requiring positive evidence"), extended across the full checkability spectrum. The job of the discipline is to make "show evidence" *uniform* (every verdict, every dispatch context) and *graduated* (the producing/checking mechanism differs by claim type; the requirement never relaxes).

**The unit of gating is a claim, not an action.** Enforcement fires when a verifiable claim is *made or in force* — a "no-logic-change" batch declaration, a critic's "goal achieved" verdict — never on every edit indiscriminately. A Tier-1 hook is *registered* broadly (on `Edit|Write`, the only way to observe an edit) but *activates* only when its claim is in force, and is a silent no-op otherwise. An edit that makes no verifiable claim has nothing to gate.

---

## Step 0 — Operationalize before verifying

No "achieved / compliant / correct" verdict is meaningful unless the target was first operationalized into **falsifiable acceptance criteria**. A vague goal ("make it cleaner", "improve performance") is unfalsifiable, so "achieved" is unverifiable by construction — and an unverifiable verdict must be refused *before any work or any critic runs*.

This extends the workflow's existing **Requirements Specification** protocol (`workflow.md` §1: MUST/SHOULD/MAY + CLEAR/ASSUMED/BLOCKED) with one addition: every acceptance criterion is tagged with the **tier** at which it will be verified. Operationalization is what *assigns* each claim to a tier; without it there is nothing to gate. Most apparent "judgment" dissolves into checkable sub-claims once the goal is operationalized, leaving the smallest possible Tier-3 residue.

---

## The three checkability tiers

| Tier | Claim type | Evidence is… | Producer | Verifier | Guarantee | Example |
|---|---|---|---|---|---|---|
| **1 — Script-decidable** | a script gives a yes/no | deterministic script output (diff, grep, test exit) | non-model actor | **non-model actor** (same script) | **Hard** | no-logic-change; no-hardcoded-paths; seed-once; citation resolves; tests pass |
| **2 — Locatable judgment** | decomposes into sub-claims each pinned to an artifact | cited artifact (`file:line`, a test, an output value) + sufficiency argument | the critic (model) | **split**: a script existence-checks the citation (line exists, test passes); a model judges sufficiency | **Medium** | "goal A achieved" where A = a guard at line 47 + a passing null test |
| **3 — Irreducible judgment** | no single artifact pins it | a reasoned argument | the critic (model) | **independent** model(s) prompted to refute; diverse-lens panel | **Soft / probabilistic** | is this proof correct? is the identification sound? is this clearer? |

The tiers are a spectrum, not silos. Operationalization (Step 0) pushes as many sub-claims as possible *down* toward Tier 1.

---

## The verdict vocabulary in full

Across **all tiers** and **all four dispatch contexts** (JS Workflow pipeline, standalone `/review`, orchestrator loop, ad-hoc), a verdict is exactly one of:

- **`PASS`** — only with tier-appropriate evidence attached: Tier-1 script output, Tier-2 resolved citation + sufficiency argument, Tier-3 survived independent refutation.
- **`UNVERIFIED`** — evidence is absent or not yet produced. **Loud, deducting, never silent.** This is the floor that converts a silent false `PASS` into an audible failure in every context. A required-but-missing ledger row for an in-scope artifact under a verifiable claim is `UNVERIFIED`, not a default `PASS`.
- **`FAIL`** — the claim was checked and disproven.

No bare assertion is ever a `PASS`. The vocabulary is context-uniform by construction — a critic never needs to know which dispatch context it is in, only whether evidence is in hand. This is why the critic checklist is **not** bifurcated by context: every deterministic property stays on the checklist; only the evidentiary bar changes.

**Tier verdicts also recorded in the ledger** as `DIAGNOSED` / `RULED-OUT` for `diagnosis:` rows — those are the pre-existing judgment-claim record the schema already supports.

---

## The normalizer interface (Tier-1 evidence producer)

The Tier-1 no-logic-change check is a language-agnostic core plus pluggable per-language normalizers, implemented in `.claude/hooks/normdiff_lib.py` and consumed by the PostToolUse recorder (`.claude/hooks/evidence-gate-recorder.py`) and `/tools normdiff <file>`.

Three steps, only the middle one per-language:

- `extract_executable_regions(text, language) -> list[str]` — whole file for `.do`/`.doh`/`.R`/`.r`/`.py`/`.tex`. (Chunk extraction for `.qmd`/`.ipynb` is deferred.)
- `normalize(region, language) -> list[str]` — the only language-specific code. Drops blank lines, strips comments + scaffold, replaces path literals with a `PATH` token. Driven by a per-language config dict (`line_comment`, `block_comment`, `scaffold_patterns`, `path_token_patterns`).
- `normdiff(baseline, current, language) -> {added, removed}` — language-free set comparison of normalized lines.

**Substantive line:** code = non-comment / non-blank after path-tokenization; LaTeX "no-logic-change" reads as "no-content-change" — `%` comments stripped, path tokens (`\input`, `\includegraphics`, `\addbibresource`) replaced, with `\label{}` / `\cite{}` *arguments* counting as substantive. Encoding: read as UTF-8; on `UnicodeDecodeError` → empty residue (fail-open).

**Empty residue ⇒ a path/preamble/scaffold-only refactor (records `PASS`). Non-empty residue ⇒ an analysis/content change recorded as the `UNVERIFIED` evidence the critic gate consumes.**

Language dispatch reuses `derive_lib.language_for_path()`. Recorder scope is **research artifacts only** (`paper/`, `talks/`, `scripts/`, `replication/`, `figures/`, `tables/`, `preambles/`); `.claude/**`, `quality_reports/**`, `templates/**`, `master_supporting_docs/**`, `decisions/**`, `data/**`, `explorations/**`, and all `.md` are out of scope — a no-logic-change claim is meaningful for research artifacts, not infrastructure.

---

## Enforcement actors, mapped to tier

- **Tier 1 → non-model actors.** The PostToolUse recorder (always-on, silent, writes residue to the ledger) is the interim guarantee. Optional hardening (below) adds a harness PreToolUse block and a git pre-commit backstop. A script decides; no model in the verdict path.
- **Tier 2 → schema-enforced evidence + a citation existence-check.** The critic cannot emit `PASS` without a structured `{claim, artifact_citation, sufficiency_argument}`; a lightweight script then confirms the cited artifact *resolves* (line exists; named test runs and passes). The model still judges *sufficiency*; fabricated *artifacts* are caught mechanically. (Phase 3.)
- **Tier 3 → independent adversarial verification.** One or more verifiers — *never the producing critic* — prompted to refute, or a diverse-lens panel. A majority-refute kills the `PASS`. Mandatory only for load-bearing judgment verdicts (identification soundness, proof correctness, "goal achieved" on a shipped artifact); optional elsewhere, because adversarial panels cost N× tokens per claim. (Phase 4.)

**Separation of powers, generalized** (`agents.md` §2): Tier 1 producer and verifier can both be non-model (no conflict possible). Tier 2/3 verifier must be **independent of the producer** — a model grading its own justification is self-scoring.

---

## The citation-existence contract (Phase 3)

Tier-2 evidence is a citation of form `file:line-range[:test_id]`. A lightweight check resolves it:

- `resolve_citation(citation) -> {exists, output}` — the cited line range must exist in the file; if a `:test_id` is present, the named test is run (extension-dispatched) and must pass.
- **Fail-open when infra is unavailable:** a citation that cannot be checked because the test runner / interpreter is absent records an **`ASSUMED`** ledger row (not `FAIL`), with the reason in Evidence. This catches *fabricated artifacts* (a line/test that does not exist) without penalizing a genuinely uncheckable environment.

This is what makes Tier 2 more than trust: presence of a structured citation is schema-enforced; existence of the cited artifact is mechanically checked. Neither catches a fabrication that *survives both* — that is the honest limit (see below).

---

## Optional hardening (post-Phase-1, not load-bearing)

These add *blocking* on top of the always-on *recording*. The guarantee (record + critic-gate) does not depend on them.

- **`refactor-mode` manifest + opt-in PreToolUse block.** `.claude/state/refactor-mode.enabled`, newline-delimited repo-relative paths, exact-match, blank/`#` lines ignored, empty = none, **git-ignored**. When active and the edited file is in scope, the hook blocks an edit whose recorded residue is non-empty. Off by default. `.claude/state/README` documents it. Managed by `/tools refactor-mode on/off`.
- **Git `pre-commit` backstop.** Runs the normdiff on staged-vs-`HEAD`; the "refactor-shaped commit" predicate is *all staged supported files have empty recorded residue*. Catches the ad-hoc manual-refactor case the PostToolUse recorder sees but does not block. Machine-local — needs an install path (`bin/setup-machine.sh` extension or documented post-clone copy). `git commit --no-verify` still bypasses it.

---

## Honest limits

- **Hard guarantees exist only at Tier 1.** Judgment cannot be made deterministic; Tier 2/3 reduce error, they do not eliminate it.
- **Presence ≠ authenticity.** Schema enforcement guarantees evidence is *attached*, not that it is *true*. Tier 2 catches fabricated *artifacts*; Tier 3 catches fabricated *reasoning*; neither catches a fabrication that survives both.
- **Only Edit/Write-tool edits are recorded.** External-editor changes and `git commit --no-verify` bypass the recorder. Closing this needs the optional commit hook, which `--no-verify` still bypasses.
- **The normalizer is heuristic.** Path-normalization is imperfect (per ADR-0011 reasoning); false positives exist, which is why Tier-1 blocking is opt-in (`refactor-mode`) and the recorder only records — the critic gate adjudicates.
