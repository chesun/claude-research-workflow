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
- **Tier 3 → independent adversarial verification.** One or more verifiers — *never the producing critic* — prompted to refute, or a diverse-lens panel. A majority-refute kills the `PASS`. Mandatory only for load-bearing judgment verdicts (identification soundness, proof correctness, "goal achieved" on a shipped artifact); optional elsewhere, because adversarial panels cost N× tokens per claim.

> **Read** `.claude/references/evidence-gating-tier3-panel.md` before dispatching a Tier-3 panel. Tier-3 enforcement is **independent adversarial verification** via a panel (a protocol obligation for load-bearing verdicts; optional elsewhere — nothing blocks). The full convention — mandatory-vs-optional criteria, the two panel shapes, the majority/tie-break decision rule, the `REFUTED`-vs-`UNVERIFIED` distinction, and the producer-verifier independence requirement — lives there (Phase 4). There is no auto-load; open it when you reach this row.

**Separation of powers, generalized** (`agents.md` §2): Tier 1 producer and verifier can both be non-model (no conflict possible). Tier 2/3 verifier must be **independent of the producer** — a model grading its own justification is self-scoring.

---

## The citation-existence contract (Phase 3)

Tier-2 evidence is a structured `{claim, artifact_citation, sufficiency_argument}`. The `artifact_citation` is a string that a lightweight, non-model check resolves mechanically. Implemented in `.claude/hooks/citation_existence_lib.py`; exposed manually as `/tools cite-check <citation>` (`.claude/skills/tools/cite_check.py`).

**Citation format:** `file[:line-or-range][:test_id]`.

- `scripts/01_clean.do:47` — file + single line.
- `scripts/01_clean.do:40-52` — file + inclusive line range.
- `tests/test_x.py:88:test_foo` or `tests/test_x.py::test_foo` — file + named test (the pytest `::` node form is also accepted).
- `paper/main.tex` — file only (existence of the file).

**I/O:** `resolve_citation(citation: str, repo_root) -> {exists: bool, kind: str, status: str, detail: str}`.

- `exists` — True iff the artifact resolves (file present, cited line / range in range, and — if a test is named — the test ran and passed).
- `kind` — `'line' | 'test' | 'file'` (what was actually resolved).
- `status` — `'RESOLVED' | 'MISSING' | 'ASSUMED'`.
- `detail` — human-readable reason / evidence (goes into the ledger Evidence cell).

**The MISSING-vs-ASSUMED rule (load-bearing):**

- **`MISSING`** — a real fabrication / broken-evidence signal: the file does not exist, the line / range is out of range, the named test *failed* or was *not collected* (does not exist), or the citation is malformed / unsafe. `exists = False`. The CLI exits nonzero.
- **`ASSUMED`** — infrastructure absence *only*: a test was named but the whitelisted runner for that file type is unavailable (no runner for the extension, or the toolchain — e.g. pytest — is not installed), or a read/spawn error prevented the check. This must **not** read as fabrication. `exists = False` (we could not confirm), but the row is recorded `ASSUMED` with the reason, and the CLI exits 0 (fail-open). This mirrors the verdict-vocabulary rule: a genuinely uncheckable environment is `ASSUMED`, not penalized.
- **`RESOLVED`** — file present, line(s) in range, any named test ran and passed. `exists = True`.

So a *missing line* is `MISSING` (fabrication); a *missing test runner* is `ASSUMED` (infra). The two are deliberately separated: the check catches fabricated artifacts without punishing an environment that cannot run the test.

**The security boundary (the citation is untrusted input):** a citation string must NEVER become arbitrary command execution or a path-traversal read. Four defenses, in order:

1. **Path containment.** The file part is resolved *relative to* `repo_root` and the realpath must stay inside `repo_root`. Absolute paths, `..` traversal, and symlinks that escape the tree are rejected → `MISSING` ("path escapes repo"). Uses `os.path.realpath` + `commonpath`.
2. **test_id whitelist.** A test id must match a conservative identifier pattern (function / class-qualified / pytest-node / `[param]` shapes only — no slash, space, quote, or shell metacharacter). Anything else is rejected → `MISSING` ("unsafe test id") *before* any subprocess is spawned.
3. **Fixed, whitelisted runner.** Tests run only via a per-extension runner from a hard-coded table (python → `['python3','-m','pytest', '<relpath>::<test_id>']`), with `shell=False`, an args **list** (never a command string), and `cwd=repo_root`. The *extension*, not the citation, selects the program. An extension with no table entry is `ASSUMED` (infra-absent), never executed.
4. **No shell, ever.** `subprocess` is called with a list and `shell=False`; there is no path that passes the citation to a shell.

This is what makes Tier 2 more than trust: presence of a structured citation is schema-enforced (below); existence of the cited artifact is mechanically checked here. Neither catches a fabrication that *survives both* — that is the honest limit (see below).

---

## Workflow schema-enforcement convention (what makes Tier-2 binding — Q5)

The verdict-vocabulary deductions in the critic agents are *advisory prose* on their own — a model can ignore prose. The mechanism that makes Tier-2 evidence **binding** is the harness, not the agent file: when a critic runs inside a JS `Workflow()`, route it via `agent(..., { schema })` with the evidence fields **required**. `StructuredOutput` then mechanically rejects an empty-evidence verdict — the critic literally cannot return a `PASS` (or any verdict) without populating `claim` and `artifact_citation`.

Convention (apply when a critic that issues Tier-2 verdicts runs in a schema-routed workflow):

```js
const verdict = await agent(criticPrompt, {
  schema: {
    type: "object",
    properties: {
      claim:              { type: "string" },   // the locatable-judgment claim
      artifact_citation:  { type: "string" },   // file[:line-or-range][:test_id]
      sufficiency_argument: { type: "string" }, // why the cited artifact suffices
      verdict:            { type: "string", enum: ["PASS", "UNVERIFIED", "FAIL"] }
    },
    required: ["claim", "artifact_citation", "verdict"]
  }
});
// Then existence-check the citation mechanically:
//   resolve_citation(verdict.artifact_citation, repoRoot)
// MISSING ⇒ downgrade PASS to UNVERIFIED (fabricated/absent artifact).
```

`required: ["claim", "artifact_citation"]` is the load-bearing line: it converts "the critic *should* attach evidence" (prose) into "the critic *cannot return* without evidence" (schema). `sufficiency_argument` is recommended but not in `required`, because a model judging sufficiency is Tier-2 by definition and the existence-check, not the schema, is what mechanically guards the artifact.

**Precise enforcement boundary (do not overclaim):** schema enforcement binds **only** when the critic runs inside a schema-routed `Workflow()` (or any harness that enforces `StructuredOutput`'s `required`). In **ad-hoc / standalone** critic use — a `/review` invocation, an orchestrator dispatch without a schema, a human reading the agent file — there is no `StructuredOutput` gate, so the evidence requirement reverts to **advisory prose** (the critic *should* attach a citation; nothing mechanically stops it from not doing so). The citation-existence check (`resolve_citation` / `cite-check`) is available in *both* contexts, but it only runs if something invokes it; the schema is what *forces* the citation to exist in the first place.

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
