# Build Plan — Evidence-Gating Discipline

**Status:** DRAFT v3 — two review rounds incorporated; awaiting approval (nothing implemented)
**Date:** 2026-05-29
**Spec / design of record:** `quality_reports/reviews/2026-05-28_whole-picture-critic-gates-dispatch.md` §7
**Reviews incorporated:** `..._synthesis_review.md` (REVISE-FIRST) + `..._rereview.md` (REVISE-AGAIN)
**Design commit:** `a5d6b73` on branch `design/evidence-gating-discipline`

**v3 changelog (the big one):** C1 redesigned — **decouple evidence-recording from claim-gating** (user decision). The Tier-1 hook becomes a silent always-on *recorder* (PostToolUse); the *gate* fires at claim-time (the evidence-gated critic, optional commit hook). This removes the vapor-tooling dependency the re-review caught (no `/tools refactor-mode`, no `bin/` pre-commit needed for the guarantee — they become optional hardening). Also: M4 decided (fresh normalizer), M9 decided (recorder = interim guarantee), M10/M11 corrected with verified facts, references-loading clarified.

---

## The core architecture (v3)

**Separate evidence-gathering from claim-gating** — the two are different events, and conflating them caused both prior C1 dead-ends:

- **Record (always, silent, cheap, no tooling):** a **PostToolUse** hook on every supported edit computes the normalized-content diff vs `HEAD` and *records the residue to the verification ledger* — one row per file, updated in place. No user-facing advisory, non-blocking (the edit already landed). Needs nothing new beyond the hook + lib + ledger. Zero noise (it never nags), zero default-off hole (the evidence always exists).
- **Gate (only at claim-time):** blocking happens where a no-logic-change claim is actually *made* — the evidence-gated critic reads the ledger and **cannot emit a clean-refactor `PASS` when a non-empty residue was recorded**; an optional commit-time / opt-in pre-edit block can be layered on as hardening. This honors "gate on claims, not actions": the *gate* is claim-conditional; the *evidence* is gathered continuously.

So **the guarantee is distributed**: Phase 1 (recorder) + Phase 2 (critic consumes the ledger). The recorder alone has standalone value (a deterministic evidence trail) but does not itself block — that is honest and intended.

---

## Guiding constraints

- Gate on claims, not actions [design §7.0]. Block only at claim-time; Tier-1 recorder is non-blocking [§7.5a].
- One rule operationalizing `adversarial-default` via evidence gating [Q10].
- Respect context-tightening: always-on rule stays lean; detail in a pointer-loaded `.claude/references/` doc [M11].
- Derive, don't guess: facts below verified (counts/classes re-checked 2026-05-29).

---

## Resolved decisions

1. **C1 — record-always + gate-at-claim-time** (user-decided). See core architecture. `refactor-mode` manifest + git `pre-commit` backstop are **optional hardening** (opt-in pre-edit/commit blocking), NOT load-bearing — deferred out of Phase 1, so their absence no longer leaves a hole.
2. **M4 — write a fresh `normalize()`** in `normdiff_lib.py`. Do not try to reuse `stata_comment_lib.py`'s `is_path_glob_open/close` in place (they live inside repair functions); if useful, lift the path-char predicate into a shared pure helper, but the normalize path is new.
3. **M9 — the Phase-1 recorder + ledger is the interim guarantee.** Phase 2 critic verdict-vocabulary deductions are advisory until Phase 3 schema validation; state this in the rule and soften interim deductions. No implication of binding enforcement Phase 1 can't deliver.
4. **Rule home (M11) — extend `.claude/rules/adversarial-default.md` in place** (verified **8** inbound references: the rule itself + 7 — `agents/{coder-critic,verifier,writer-critic}.md`, `rules/{anti-ai-prose,derive-dont-guess,destructive-actions,no-assumptions}.md`). Split content: principle + enforcement-strength stay always-on; tier tables + vocabulary + operationalization → `.claude/references/evidence-gating-detail.md`, loaded by an **explicit pointer/Read instruction** from the rule and the critics (mirroring how `references/domain-profile.md` is referenced — there is no automatic lazy-load system; "lazy" = the reader opens it when pointed).

---

## Phase 1 — Tier-1 evidence recorder (the foundation)

**Goal:** a language-agnostic normalized-content diff that, on every supported edit, silently records the residue (analysis/content change beyond path swaps) to the ledger. Non-blocking.

**Files:**

- NEW `.claude/hooks/normdiff_lib.py` — agnostic core + per-language normalizers (mirrors `derive_lib.py`/`stata_comment_lib.py`; shared libs live in `.claude/hooks/`). Whole-file (region-awareness reserved for deferred Quarto):
  - `extract_executable_regions(text, language) -> list[str]` (whole file for stata/r/python/latex).
  - `normalize(region, language) -> list[str]` — **fresh impl (M4):** drop blank lines, strip comments + scaffold, replace path literals with `PATH` token. Per-language config dict (`line_comment`, `block_comment`, `scaffold_patterns`, `path_token_patterns`).
  - `normdiff(baseline, current, language) -> {added, removed}` — set comparison of normalized lines; language-free.
  - "Substantive line" (M5/M6): code = non-comment/non-blank after path-tokenization; LaTeX = non-comment (`%`)/non-blank content, path tokens (`\input`/`\includegraphics`/`\addbibresource`) replaced, `\label{}`/`\cite{}` *args* count.
  - Encoding (M8): `read_text("utf-8")`; on `UnicodeDecodeError` → empty residue (fail-open).
- NEW `.claude/hooks/evidence-gate-recorder.py` — **PostToolUse** `Edit|Write|MultiEdit` (coexists with `derive-check-advisory.py`, also PostToolUse). Because it runs *after* the edit lands, it is much simpler than a PreToolUse hook:
  1. **Language filter:** `derive_lib.language_for_path()` → language (covers `.do/.doh/.r/.R/.py/.tex`; m2: smoke all six); unsupported (incl. all `.md` — plans/reviews/ADRs/session-logs are inherently out of scope) → exit 0.
  1b. **Path scope (research artifacts only):** record only when the repo-relative path is under a research-artifact root — `paper/`, `talks/`, `scripts/`, `replication/`, `figures/`, `tables/`, `preambles/` (derived from CLAUDE.md Folder Structure). Explicitly EXCLUDE `.claude/**` (the workflow's own hooks/tools/infra — incl. this recorder), `quality_reports/**`, `templates/**`, `master_supporting_docs/**`, `decisions/**`, `data/**` — even when they contain `.py`/`.tex`. A no-logic-change claim is meaningful for research artifacts, not infrastructure. `explorations/` (sandbox) excluded by default. (Roots ASSUMED from CLAUDE.md — confirm; make the list a small constant at the top of the hook so it is easy to adjust.) Out-of-scope path → exit 0.
  2. **Current content = read the file from disk** (already written — no edit simulation needed; M7 dissolves).
  3. **Baseline = `git show HEAD:<path>`; catch exit 128 (not in HEAD) → empty baseline** (new file → all content is residue; C2). Do not collapse into generic fail-open.
  4. `normdiff(baseline, current, language)`; **write/update the ledger row** (M3): `Path | Check=no-logic-change | Verified At | File hash | Result ∈ {PASS, UNVERIFIED} | Evidence(residue summary)`. Update-in-place per `(path, no-logic-change)` so the ledger is bounded by file count, not edit count. Wrap in try/except; **fail-open on IO error** (never error the turn on ledger-write failure).
  5. Non-blocking always (PostToolUse): emit nothing user-facing (silent record). Optionally a `suppressOutput` advisory only if residue is large AND a claim signal exists — default silent.
- NEW `.claude/skills/tools/normdiff.py` + `/tools normdiff <file>` subcommand (manual/orchestrator/pipeline-gate-agent reuse). Register in `.claude/skills/tools/SKILL.md`.
- EDIT `.claude/settings.json` — add `evidence-gate-recorder.py` under the existing PostToolUse `Write|Edit|MultiEdit` matcher (alongside `derive-check-advisory.py`). No ordering concern (PostToolUse, non-blocking — M2 dissolves for the default path). Write via `BYPASS_SHARED_GUARD=1` per `destructive-actions.md` Tier-3 (m3).
- NEW `.claude/hooks/test_normdiff_lib.py` — per-language fixtures (path-swap → empty residue; injected `keep if`/`library()`/changed `\label{}` → residue); LaTeX (M6): preamble/`\newcommand` rename → empty; changed `\cite{}` key → residue; blank lines stripped. Hook smoke: new file (no HEAD) → full residue recorded; clean edit → PASS row; logic edit → UNVERIFIED row with residue; ledger-unwritable → fail-open, no turn error.

**Verification:** test suite; all six suffixes smoke; new-file records residue (not skip); ledger row updates in place; fail-open on decode + IO. Recorder is non-blocking by construction.

---

## Phase 2 — The rule, the verdict vocabulary, the ledger schema, and the GATE

**This is where the gate lives** (the recorder only records). Critic consumption of the ledger is the claim-time gate.

**Files:**

- EDIT `.claude/rules/adversarial-default.md` (Class A) — add ONLY: the principle (§7.0), gate-on-claims, enforcement-strength (§7.5a), and a pointer to the detail doc. Lean. **State the known limit plainly:** only Edit/Write-tool-mediated edits are recorded; external-editor changes and `git commit --no-verify` bypass the recorder (honest gap, not a defect).
- NEW `.claude/references/evidence-gating-detail.md` (Class A) — tier table, `{PASS, UNVERIFIED, FAIL}` vocabulary, normalizer interface, citation-existence contract, optional-hardening (refactor-mode/pre-commit) spec.
- EDIT `.claude/state/verification-ledger.md` — extend schema with `tier`, `artifact_citation`, `refuter_tally`. **(M3) Backward-compat test** that an existing 6-column row parses post-extension; **audit consumers for positional parsing** (verified: `coder-critic.md` consult logic, `diagnostic-claim-audit.py`). NOTE: the ledger *file content* is local state (only `.claude/state/.gitkeep` is universal) — it does **not** propagate; only the *format* (described in the rule) propagates.
- EDIT `.claude/agents/coder-critic.md` (Class A) — **the gate:** when reviewing a refactor, consult the ledger's `no-logic-change` row; a non-empty recorded residue ⇒ cannot emit clean-refactor `PASS` (→ `UNVERIFIED`/`FAIL` + deduction). Adopt the verdict vocabulary + new columns.
- EDIT `CLAUDE.md` (**Class B** — verified line 61): Core Principles bullet. Apply to overlays **manually**, not via propagation.

**Verification:** rule + reference lint; `grep -rn adversarial-default` confirms all 8 refs intact after the split; backward-compat test green; consumer audit done; a recorded non-empty residue blocks a clean-refactor critic PASS in a smoke test.

---

## Phase 3 — Tier-2 enforcement (schema evidence + citation existence-check)

- EDIT critic agents — require `{claim, artifact_citation, sufficiency_argument}`; inside a JS `Workflow()` route via `agent(…,{schema})` with `required:[claim, artifact_citation]` so StructuredOutput rejects empty-evidence verdicts (Q5 — from the start).
- NEW `.claude/hooks/citation_existence_lib.py` + check — `resolve_citation(citation) -> {exists, output}`; format `file:line-range[:test_id]`; extension-dispatched test run; **fail-open (ASSUMED row, not FAIL) if infra unavailable** (Q7).

**Verification:** non-resolving citation flagged; resolving passes; infra-absent → ASSUMED.

---

## Phase 4 — Operationalization gate (advisory) + Tier-3 convention

- EDIT `templates/requirements-spec.md` (Class A; verified: no tier column today) — add a **"Verification Tier"** column. EDIT `.claude/rules/workflow.md` **(Class B — verified line 66)** §1 — every acceptance criterion tagged with its tier; advisory (reminder + critic deduction), never block (Q6). workflow.md edit applies to overlays **manually**.
- NEW `.claude/references/` Tier-3 adversarial-verify panel template — mandatory only for load-bearing judgment verdicts (Q8).

**Verification:** requirements-spec emits tier-tagged criteria; a load-bearing judgment verdict triggers the panel in a sample workflow.

---

## Phase 5 — Propagation (class-aware — M10 corrected)

Verified classes (`.claude/file-classes.toml`): default = Class A (universal). **Class B (manual to overlays):** `CLAUDE.md` (line 61), `rules/workflow.md` (line 66) — and `rules/quality.md`/`agents/{orchestrator,verifier,writer}.md` if later touched. `coder-critic.md`, `adversarial-default.md`, `rules/agents.md`, and the new hooks/lib/references are **Class A**.

- `/tools propagate` the Class-A set (rule, detail doc, hooks, lib, normdiff.py, SKILL.md, settings.json). `/tools sync-overlays` for the Class-A pieces.
- Apply the Class-B edits (CLAUDE.md bullet; workflow.md tier column) to `applied-micro` + `behavioral` **manually**.
- Ledger *content* is local state — do not propagate; the format propagates via the rule text.
- **(m4)** Before propagating, confirm `.claude/file-classes.toml` covers the new files (they match `.claude/hooks/*.py`, `.claude/skills/tools/*.py`, `.claude/rules/*.md` → Class A by default; the new `references/` doc needs a class entry — add `.claude/references/*.md` to `[universal]` or confirm default).

**Verification:** `/tools sync-status`; a consumer has the recorder registered + tests pass; no Class-B overlay file overwritten.

---

## Optional hardening (post-Phase-1, not load-bearing)

- `refactor-mode` manifest + opt-in **PreToolUse** blocking variant (`.claude/state/refactor-mode.enabled`, newline-delimited repo-relative paths, exact-match, blank/`#` ignored, empty=none, **git-ignored — add to `.gitignore`**; `.claude/state/README` documents it). Blocks at edit-time during a declared refactor batch.
- Git `pre-commit` backstop — needs an operational "refactor-shaped commit" predicate (e.g. *all staged supported files have empty recorded residue*) and an install path (`bin/` does **not** exist; `templates/setup-machine.sh` is LFS/DVC-only — decision: create `bin/` + extend the template, or document post-clone copy). Catches the ad-hoc-manual-refactor case the PostToolUse recorder still sees but doesn't block.
- `/tools refactor-mode on/off` to manage the manifest.

These add *blocking* on top of the always-on *recording*; the guarantee (record + critic-gate) does not depend on them.

---

## Risks & mitigations

- **External-editor / `--no-verify` bypass** — only Edit/Write-tool edits are recorded. Stated as a known limit in the rule; not closable without the optional commit hook (which `--no-verify` still bypasses).
- **Recorder cost** — `git show HEAD` + normalize per supported edit; PostToolUse (non-blocking), bounded ledger (update-in-place). Acceptable at interactive cadence.
- **Normalizer false positives** — per-language test corpus; recorder only records (no false block); the critic gate adjudicates.
- **Ledger column-shift breaking consumers (M3)** — backward-compat test + consumer audit before the schema change.
- **Class-B clobber (M10)** — Phase 5 handles CLAUDE.md + workflow.md manually.

## Sequencing

Phase 1 (recorder) is independent + buildable now (no vapor dependency). Phase 2 turns recording into a gate (critic consumption) — this is the real guarantee, so Phase 1+2 ship together for the guarantee to bite. Phases 3–4 build on the vocabulary + ledger. Phase 5 last. Optional hardening any time after Phase 1. Each phase = its own commit; worker-critic loop where code is involved.

## Out of scope

- Quarto `.qmd` normalizer (deferred — TODO backlog entry exists; needs chunk extraction + Quarto infra).
- Harness-level `gate()` primitive (proposal 2c — flagged upstream).
