# The Whole Picture: Critic Behavior, Gates, and Dispatch Context

**Date:** 2026-05-28
**Scope:** Resolving whether modifying the critic to "only judge residue after a deterministic gate" leaves deterministically-checkable properties unchecked in non-workflow contexts.
**Grounding:** All claims cite the four supplied maps (Dispatch Contexts, Critic Toolsets, Hook Enforcement Model, Property Inventory). No file paths invented beyond those maps.

---

## 1. Context Matrix

Rows = dispatch contexts. Columns answer the three questions that determine whether a deterministic property gets checked.

| Dispatch context | Does a deterministic gate stage exist here? | Can the critic run the deterministic check itself? | Who, if anyone, runs the deterministic check? |
|---|---|---|---|
| **JS Workflow pipeline** (proposed gate-agent stage, options 2a/2b) | Only if the proposal is built — **none exists today** (Property map: "no gate-agent pattern exists"; Dispatch map: "No deterministic pre-dispatch Bash gates currently exist") | **No** — critics have only Read/Write/Grep/Glob, no Bash (Toolset map: all 8 critics, `coder-critic.md:4`) | Proposed: a gate-agent with Bash runs `normdiff.py` before the critic (proposal:43,84). Today: nobody, unless the Orchestrator runs a discretionary Bash check (`orchestrator.md:4` has Bash, but Dispatch map: "currently doesn't per documented protocol") |
| **Standalone `/review` skill** (`/review --code`, etc.) | **No** — "No pre-dispatch gate exists for ad-hoc review invocations" (Dispatch map, `review/SKILL.md:16-30`). Skill *could* run Bash first but "Currently no such gates are mentioned in SKILL.md" | **No** (same toolset limit) | Nobody runs a pre-critic deterministic gate. The skill dispatches the critic directly (Dispatch map) |
| **Orchestrator loop** (orchestrated pipeline) | **No input-based gate** — gates are outcome-based on score >= 80 (`workflow.md:70-94`, `agents.md:31-35`). Orchestrator *has* Bash but gating is discretionary prose, not a formalized stage | **No** | Potentially the Orchestrator (has Bash, `orchestrator.md:4`), but "the gap is in the orchestrator's documented dispatch logic — it lists which agents to dispatch but not pre-dispatch validation steps" |
| **Ad-hoc direct invocation** ("just review this") | **No** — most permissive path; "critic deduction tables fire only when a critic is dispatched inside the orchestrated pipeline; ad-hoc usage bypasses deductions" (`derive-dont-guess.md:9`) | **No** | Nobody — unless a **harness-level hook** fires (Hook map: hooks fire in ALL paths) |

**The matrix's load-bearing pattern:** the "Can the critic run the check itself?" column is **No in every row** — uniformly, because the toolset gap (no Bash) is context-independent (Toolset map: "None of the critics can directly execute git commands or run Python scripts"). The "Does a gate stage exist?" column is **No in every row today**, and even under the proposal it becomes Yes only in the JS Workflow row. So the user's worry is correct in its premise: a residue-only critic, paired with a gate that exists in just one of four contexts, leaves the deterministic property checked by nobody in the other three.

---

## 2. The user's worry, and the "uniformly evidence-gated" reframe

### The worry, stated precisely

If the critic's checklist is **bifurcated by context** — "in the pipeline I skip deterministic properties because the gate handled them; elsewhere I check them" — then the critic must *know which context it is in* and *trust that a gate ran*. Critics cannot run the gate themselves (column 2 = No everywhere), and three of four contexts have no gate (column 1 = No). So bifurcation produces exactly the silent fall-through the user fears: the property is removed from the critic's remit on the assumption of a gate that, in standalone / orchestrator / ad-hoc contexts, never ran.

This is not hypothetical. The Property map records that `no_logic_change` — a **deterministic** property (normalized-content diff verifiable, proposal:43,84) — was "asserted by coder-critic as judgment, caught only by external diff review" in the 2026-05-28 incident. That is the bifurcation failure already happening once, before any formal context-split is even introduced.

### The reframe: uniform evidence-gating, not contextual bifurcation

The proposed reframe is: **do not change *which* properties the critic checks by context. Change the *evidentiary bar* uniformly.** The critic reports a deterministically-checkable property as `PASS` only if gate evidence exists — a verification-ledger row, or a passed-in diff. Absent that evidence, it reports `UNVERIFIED` and deducts, in **every** context. The property never leaves the critic's checklist; only the verdict vocabulary changes from `{PASS, FAIL}` to `{PASS, FAIL, UNVERIFIED}`.

**Do the maps support this? Yes, partially — and they show exactly where it has teeth and where it does not.**

**Where it has teeth (mechanism already exists):**

- The evidence-as-precondition pattern is already in the repo. The Adversarial-default rule has critics "read verification ledgers produced by external Bash agents, rather than re-running verifications themselves" (Toolset map; `coder-critic.md:188-230`). The critic already *consults* `.claude/state/verification-ledger.md` and already deducts when a ledger row is stale (-15, `coder-critic.md:197`) or a compliance claim lacks a ledger row (-25, `coder-critic.md:196`). The reframe generalizes this existing -25/-15 to *every* deterministic property in the Property inventory's 13-item deterministic tier, with `UNVERIFIED` as the explicit verdict rather than a silent omission.
- The schema-enforced-evidence option (3a, `coder-critic.md:190-200`; proposal:69) is the enforcement teeth: a critic verdict requires explicit `{command, raw_output}` fields, "not bare assertion." Under schema validation, a critic *cannot emit `PASS` on `no_logic_change` without attaching the diff output*. That structurally prevents the 2026-incident failure (passing `no_logic_change: true` with no diff) regardless of context.
- It is context-uniform by construction: the critic applies the same rule (`evidence present → PASS, else UNVERIFIED`) in pipeline, standalone, orchestrator, and ad-hoc alike. No context-detection logic needed. This sidesteps the column-1 problem entirely — the critic never has to know whether a gate stage ran, only whether evidence is in hand.

**Where it does NOT have teeth (the honest limit):**

- **It is still an LLM judging its own discipline.** The critic is the same Read/Grep/Glob agent (Toolset map). "Report UNVERIFIED if no evidence" is itself a prose instruction the LLM must follow — the same class of instruction that *already failed* in the 2026 incident when the critic asserted a deterministic property as judgment. The Property map states this plainly: "no hook blocks a critic from asserting a deterministic property without evidence." Schema enforcement (3a) narrows the gap (empty-evidence verdicts get rejected, proposal:69) but the map flags it "not yet implemented," and a determined or sloppy model can still *fabricate* a `raw_output` field. Schema validation checks *presence*, not *authenticity*, of evidence.
- **Some properties the critic CAN grep, so `UNVERIFIED` is avoidable there — but `no_logic_change` is exactly the one it cannot.** The Toolset map splits coder-critic's checks into (b) grep-runnable (set.seed location, library vs require, derived-entity presence, the two Variant-8 regexes) and the harder ones. For category-(b) properties the critic can self-produce evidence via its Grep tool, so `UNVERIFIED` collapses to a real `PASS`/`FAIL`. But `no_logic_change` requires a **normalized diff** (`normdiff`/`stata_sweep.py --check`), and the Toolset map is explicit: state-machine balance must be checked "via python3 .claude/skills/tools/stata_sweep.py --check (NOT naive grep)" and the critic "CANNOT run the python script." So for the single property that caused the incident, the evidence-gating reframe degrades to: the critic can only ever emit `UNVERIFIED` (loud, deducting) unless someone *else* produced the diff. That is strictly better than a false `PASS` — the worst case is a loud failure, never a silent one — but it does not actually verify the property in any context where no external diff was produced.

**Verdict on the reframe:** The maps support it as the correct *critic-side* fix. It converts the failure mode from "silent false PASS" (the 2026 incident) to "loud UNVERIFIED + deduction" in all four contexts, which is the user's stated worst-case acceptance criterion. But because the critic has no Bash, evidence-gating *relocates* the verification work for diff-class properties onto whoever produces the evidence; it does not perform that work. If nobody produces the diff, the property is correctly flagged but never actually checked. That is the seam that motivates the structural answer in §3.

---

## 3. The stronger structural answer: make the deterministic gate a HOOK

### The argument

The critic has no Bash and cannot run the gate in **any** context (Toolset map, uniform across all 8 critics). Therefore the deterministic gate must live somewhere that (a) has Bash and (b) fires regardless of dispatch path. The Hook map identifies exactly one layer with both properties: **harness-level hooks registered in `.claude/settings.json`**, which "fire regardless of dispatch path (parent session or Task-dispatched subagent)" and "bind BEFORE skill/agent dispatch logic runs... cannot be bypassed by skill routing or agent selection" (`destructive-action-guard.py:27-31`; `settings.json:50-204`).

This matches the repo's own established precedent, documented three times in the Hook map: a prose-level rule that "didn't bind" until a hook gave it teeth.

- **destructive-actions** — prose existed, the 2026-04-25 incident happened anyway, then "This rule installs hooks that close both gaps" (`destructive-actions.md:23-24`).
- **primary-source-first** — cached-context citations slipped through prose; PreToolUse + Stop hooks now block (`primary-source-first.md:9-10`).
- **derive-dont-guess** — "prose without a trigger doesn't bind"; PostToolUse advisory + opt-in PreToolUse blocking hooks added (`derive-dont-guess.md:15-16`).

`no_logic_change` asserted-as-judgment is the *same class of failure* (a prose-level expectation that a deterministic property be honestly reported, failing in practice). The precedent says: close it with a hook.

### Feasibility from the maps

**Can a hook run a normdiff? Yes — the machinery already exists and hooks already invoke Python.**

- The diff tool is already in the repo as a runnable script: `python3 .claude/skills/tools/stata_sweep.py --check` (Toolset map, `coder-critic.md:88-92`), and the proposal references a `normdiff.py` pattern (proposal:43,84). Hooks are themselves Python scripts run by the harness with full Bash-equivalent execution (Hook map: `diagnostic-claim-audit.py`, `primary-source-check.py`, `derive-check-advisory.py` all run Python logic at hook events). There is no capability gap: a hook *can* shell out to `stata_sweep.py --check` / `normdiff`.
- Precedent for a hook running a non-trivial structural Python check on edits already exists: `stata-comment-balance-check.py` is a **PreToolUse hook on `Edit|Write`** that "enforces Stata greedy-/* parser bug prevention on ALL Edit/Write" including "Variant-8 detection at edit time" (Hook map, `settings.json:75-79`; `stata-code-conventions.md`). That is structurally the same operation a `no_logic_change` hook would perform: parse code, compute a structural property, block/warn. The pattern is proven.

**What triggers it? This is the real design question, and the maps constrain the answer.**

A normalized-content diff inherently needs **two versions** (before vs. after a refactor). Hook event types and their fit:

- **PreToolUse (`Edit|Write`)** sees the *delta* — for Edit, `new_string` vs `old_string`; for Write, full content (Hook map, `primary-source-first.md:24`). An Edit's old/new strings give a hook the before/after pair *for that single edit* — sufficient to run a normalized diff on the changed region and flag injected logic (a new `keep if`, a renamed macro). This is the natural trigger and mirrors how `derive-check` and `primary-source-check` "scan the delta" of each Edit/Write. **Limitation:** a refactor delivered as a full-file `Write` (not an Edit) gives the hook the new content but not the prior version in-band; the hook would need to read the prior file from disk/git itself, which it can do (it has Bash-equivalent execution), but that adds a git-read step.
- **PostToolUse** could run the diff after the edit lands and inject an advisory (the `derive-check-advisory.py` non-blocking pattern, Hook map). Good for a soft "this edit may have changed logic" warning; weaker because it fires after the write.
- **A pre-commit-style check** (the proposal's alternative framing) — the `/commit` skill already runs "internal pre-flight Bash checks (derive-lib) before staging" (Hook map, `commit/SKILL.md:36-43`). A normdiff could be added there. **But the Hook map is explicit that this is NOT context-independent**: "these are NOT registered hooks — they are script-internal logic... TOOL-SPECIFIC gates (only when the skill is invoked), not CONTEXT-INDEPENDENT gates." So a `/commit`-embedded check protects the commit path only, not ad-hoc edits — strictly weaker than a registered hook.

**Conclusion on the structural answer:** Making the deterministic gate a registered `Edit|Write` hook is feasible (the diff script exists; hooks already run comparable Python structural checks; precedent is explicit and threefold) and it is the only mechanism in the maps that achieves true context-independence. Once it exists, the JS Workflow pipeline's gate-agent stage (proposal options 2a/2b) becomes a **fail-fast optimization** — it surfaces the violation earlier and in a structured place — rather than *the* guarantee. The guarantee moves to the hook, which fires in all four contexts including ad-hoc.

---

## 4. Recommendation, reconciling §2 and §3

**Do both, layered — the same two-layer model the Hook map already describes ("CONTEXT-INDEPENDENT HOOKS plus CONTEXT-DEPENDENT CRITICS"). They are complementary, not alternatives.**

1. **Layer 1 — hook (the guarantee).** Register a deterministic `no_logic_change`/refactor-integrity check as a harness-level hook on `Edit|Write`, shelling out to the existing `stata_sweep.py --check` / `normdiff` machinery. This is the load-bearing, context-independent floor — it fires in pipeline, standalone, orchestrator, and ad-hoc identically, closing the seam §2 leaves open. It follows the repo's own established precedent exactly (destructive-actions, primary-source-first, derive-dont-guess: prose → hook). Have the hook write its result to `.claude/state/verification-ledger.md` so downstream consumers see the evidence.

2. **Layer 2 — uniformly evidence-gated critic (the residue + the fail-fast read).** Do **not** bifurcate the critic's checklist by context. Keep every deterministic property on the checklist; change the verdict bar uniformly to `{PASS, FAIL, UNVERIFIED}`, where `PASS` on a deterministic property requires a ledger row or passed-in diff (extends the existing `coder-critic.md:188-230` ledger-consult pattern). Add schema-enforced evidence (option 3a) so the critic *cannot* emit `PASS` on a deterministic property without attaching `{command, raw_output}`. With Layer 1 populating the ledger, the critic's `PASS` is now backed by hook-produced evidence in every context; without Layer 1 evidence, it loudly reports `UNVERIFIED` — never a silent false `PASS`.

**Why this ordering:** §2 alone (critic-only) is insufficient because the critic has no Bash and cannot self-verify diff-class properties — its best case for `no_logic_change` is `UNVERIFIED`, which flags but does not check. §3 alone (hook-only) is sufficient for the *deterministic* slice but says nothing about the 8 judgment-heavy properties (latent-bug reality, label/semantic accuracy, etc., Property map) that genuinely need the LLM critic. The hook guarantees the deterministic floor; the evidence-gated critic consumes that floor's evidence and adds judgment on top. The JS Workflow gate-agent stage (2a/2b) is then an *optional accelerator* on the hook's foundation, not the thing the user is depending on.

**Net answer to the user's worry:** Under this recommendation the deterministically-checkable properties do **not** fall through in non-workflow contexts. The hook checks them everywhere (Layer 1); the critic reports them everywhere with evidence-or-UNVERIFIED (Layer 2). The worst case in any context is a loud, deducting `UNVERIFIED` or a hook block — never the silent false `PASS` of the 2026-05-28 incident.

> **Positioning (added on revision):** this two-layer recommendation is the *no-logic-change slice* of a broader discipline. The hook (Layer 1) is **Tier-1 enforcement** and the evidence-gated critic (Layer 2) is the **uniform verdict mechanism** — both are instances of the unified discipline in §7, which generalizes the same principle to judgment-class claims ("goal A achieved") that no script can decide.

---

## 5. Why not just give the critics Bash?

The obvious shortcut — add `Bash` to the critic frontmatter so it can run the diff itself — was considered and **rejected**. It is mechanically trivial (a one-line `tools:` change) but does not solve the problem and carries real cost.

**Decisive reason — Bash-in-critic is not determinism.** Determinism comes from *a script deciding the verdict*, not from *a model that has the ability to run a script*. A critic with Bash is still an LLM choosing whether to run the check, when, and how to read and report the output. That is the exact failure class that caused the incident: the 2026 critic asserted `no_logic_change: true` — giving it Bash means it *could* have run `stata_sweep.py --check`, not that it *would* have, nor that it would have read the result honestly. Capability is not a guarantee. A hook or gate-script is deterministic *by construction*: it fires on the tool event regardless of any model's discretion, and a script — not a model — computes pass/fail.

**Cost — it erodes separation of powers** (`agents.md` §2; critics evaluate, never create/mutate source). Critics already hold `Write`, but `Write` is *governed*: `protect-files.sh` and the orchestrator's "flag any critic write outside `quality_reports/reviews/`" rule both key on the `Edit|Write` matcher. Bash bypasses that entirely — `echo >`, `tee`, `sed -i`, `cp`, `mv` are unguarded write vectors the guardrail hooks do not observe (`destructive-actions.md`: `protect-files.sh` "is registered only on the Edit|Write matcher and cannot observe Bash invocations"). A Bash-equipped critic could mutate source, re-run the analysis, and "fix" its own findings — collapsing the critic/creator boundary the architecture exists to keep.

**It is also weaker on coverage.** A critic runs only when dispatched; ad-hoc edits with no critic still get no check. A hook fires on every `Edit|Write` regardless of dispatch path — the context-independence the whole analysis turns on.

**Legitimate narrow use (not a substitute).** Bash-for-critic would help only as a Layer-2 *enhancement*: letting the critic self-gather evidence (run the grep/diff itself) so its `PASS` is evidence-backed rather than degrading to `UNVERIFIED`. Even then it wants *scoped* Bash (only `git diff` / `stata_sweep.py`), which is not expressible in agent frontmatter (that is allow/deny per *tool*, not per *command*) — it needs a `settings.json` permissions layer, and accepts the separation-of-powers tradeoff as a deliberate choice. **Decision: keep the deterministic guarantee in a non-model actor; do not give critics Bash.**

---

## 6. How the non-model actors work (explainers)

A **non-model actor** is a plain script whose verdict is *computed by code, not chosen by a model*. Same input → same output; it fires on the harness event, not on whether the model remembered to invoke it. This section explains the two-and-a-half concrete realizations, grounded in the I/O contract of the hooks already in this repo (`stata-comment-balance-check.py`, `derive-check-advisory.py`).

### Actor A — the harness hook (Layer 1, the guarantee)

This is the only *pure* non-model actor available in all four dispatch contexts. It is a Python script registered in `.claude/settings.json` and run by the harness on a tool event.

**How it runs (the real contract, from the existing hooks):**

1. **Registration.** A line under `PreToolUse` matcher `Edit|Write|MultiEdit`:
   `python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/refactor-integrity-check.py` (block), or under `PostToolUse` for advisory — exactly how `stata-comment-balance-check.py` (block) and `derive-check-advisory.py` (advisory) are wired today.
2. **Input.** The harness pipes the tool call as JSON on stdin: `{tool_name, tool_input: {file_path, old_string, new_string, content, ...}, cwd}` (`json.load(sys.stdin)`, `stata-comment-balance-check.py:126`).
3. **Compute before/after.** For a `Write`, after-text is `tool_input["content"]`; for an `Edit`, the hook reads the current on-disk file and simulates the `old_string→new_string` replacement to get after-text (`_build_post_text`, lines 85–114). The **refactor baseline** (`HEAD`) is fetched separately by the hook shelling out to `git show HEAD:<path>` — the same call the incident's `fu00c_normdiff.py:4` used. So the hook compares `normalize(HEAD)` vs `normalize(after-edit)`, scaffolding-stripped and path-tokenized, and flags any non-path analysis-line residue (a new `keep if`, a renamed macro).
4. **Verdict.** Block: `json.dump({"decision": "block", "reason": "..."}, sys.stdout)` (line 240). Advisory: `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "..."}, "suppressOutput": true}` so the warning reaches the model's next turn (`derive-check-advisory.py:76–85`).
5. **Fail-open + filters.** Any exception → `sys.exit(0)` (never breaks the edit); a suffix filter exits silently on non-`.do` files; a "legacy tolerance" check skips files already dirty before the edit (`stata-comment-balance-check.py:176–179, 246–249`).
6. **Evidence trail.** On every run it appends its result (PASS/residue) to `.claude/state/verification-ledger.md`, so Layer 2 (the critic) can consume hook-produced evidence in any context.

**The one genuinely hard design point — this invariant is *conditional*.** Comment-balance is *always* wrong (an unmatched `/*` is never desired), so its hook can block unconditionally. "Zero logic change," by contrast, is the desired invariant *only during a mechanical refactor* — in normal work, analysis lines *should* change. So the hook needs a **mode signal**, or it would block every legitimate logic edit. Two grounded options:

- **State-file toggle** (mirrors `derive-check-block.py`'s opt-in `.claude/state/derive-guess-block.enabled`): a `.claude/state/refactor-mode.enabled` listing files under refactor; the hook blocks only when active and the file is in scope. Off by default.
- **Advisory-always, block-in-mode:** always emit a non-blocking `additionalContext` ("this edit changed N analysis lines vs HEAD — confirm intended"); flip to blocking only when refactor-mode is on. This is the `derive-dont-guess` two-tier pattern (advisory default, opt-in blocking) and is likely the right default.

### Actor B — the pipeline gate (the fail-fast optimization, *not* a pure non-model actor)

Inside a JS `Workflow()`, the script sandbox has no Bash/filesystem, so the deterministic check cannot run in the script body. The realization is a thin **gate-agent** as the first pipeline stage: it shells out to the same `stata_sweep.py`/`normdiff` script and returns `{pass, residue, evidence}` via a `schema`; the `pipeline` stage `throw`s on `!pass`, which drops the item before the critic stage runs.

Be precise about its nature: **the gate-agent has a model in the loop**, so it is not a *pure* non-model actor like Actor A — but the *check itself* is deterministic (a script computes the verdict; the agent only invokes it and pastes raw stdout into `evidence`). Its value is *fail-fast*: it surfaces the violation earlier, in a structured place, and removes the bad item from the batch. It is an accelerator on top of Actor A, never the guarantee — because it exists in only the JS-Workflow context.

### Actor C — a real git `pre-commit` hook (optional, true incident-baseline)

A `.git/hooks/pre-commit` script running the normdiff on *staged-vs-HEAD* is the cleanest match to the incident's own check (HEAD vs working tree) and fires on **any** commit regardless of who triggers it. Trade-offs: it is machine-local (not installed by `settings.json`; would need a line in `bin/setup-machine.sh` to install on clone), and it guards the commit path only — so it is a complement to Actor A, not a replacement. The `/commit` skill's existing internal pre-flight Bash checks are a weaker variant (they fire only when that skill is invoked, per the Hook map).

### Comparison

| | Actor A — harness hook | Actor B — pipeline gate-agent | Actor C — git pre-commit |
|---|---|---|---|
| Pure non-model (script decides)? | **Yes** | No (thin agent invokes the script) | Yes |
| Fires in all dispatch contexts? | **Yes** (every Edit/Write) | No (JS Workflow only) | No (commit path only) |
| Baseline available | HEAD via `git show` + per-edit delta | HEAD vs working (full script) | staged vs HEAD |
| Can block before damage? | Yes (PreToolUse) | Yes (drops the item) | Yes (rejects commit) |
| Install cost | `settings.json` line + script | workflow script + gate script | `setup-machine.sh` + script |
| Role | **the guarantee** | fail-fast optimization | commit-path backstop |

The recommendation in §4 is **Actor A as the load-bearing guarantee**, with Actor B as an optional accelerator inside workflows and Actor C as an optional commit-path backstop. The deterministic script (`stata_sweep.py --check` / a generalized `normdiff`) is shared by all three.

---

## 7. The Unified Evidence-Gating Discipline

Everything above is one instance of a single discipline. The no-logic-change failure and the "goal A achieved without evidence" failure are the *same epistemic error* — a verdict asserted without the evidence that grounds it. This section states the discipline that covers both, and every other verdict the workflow produces.

### 7.0 The one principle

> **A verdict is only as good as the evidence it carries. Require the evidence in every verdict; scale the verification *mechanism* to how checkable that evidence is.**

This is not new philosophy — it is the operational form of `adversarial-default.md` ("burden of proof is on the asserter; compliance is a positive claim requiring positive evidence"), extended from its mostly-Tier-1 checklists across the full checkability spectrum. The discipline's job is to make "show evidence" *uniform* (every verdict, every dispatch context) and *graduated* (the mechanism that produces and checks the evidence differs by claim type, but the requirement never relaxes).

**The unit of gating is a claim, not an action.** Enforcement fires when a verifiable claim is *made* or *in force* — a "no-logic-change" batch declaration, a critic's "goal achieved" verdict — never on every edit indiscriminately. This is why a Tier-1 hook is *registered* broadly (on `Edit|Write`, the only way to observe an edit) but *activates* only when its claim is in force, no-op otherwise (see Q1). An edit that makes no verifiable claim has nothing to gate.

### 7.1 Step 0 — Operationalize before verifying (the upstream gate)

No "achieved / compliant / correct" verdict is meaningful unless the target was first operationalized into **falsifiable acceptance criteria**. A vague goal ("make it cleaner", "improve performance", "achieve A") is unfalsifiable, so "achieved" is unverifiable by construction — and an unverifiable verdict must be refused *before any work or any critic runs*, not patched afterward.

This is a spec/plan-time discipline and it prevents lazy prompting: it forces "did it work? yes" to become "criterion 1 (tests pass) → Tier 1; criterion 2 (null handled) → Tier 2; criterion 3 (no new sample restriction) → Tier 1." It extends the workflow's existing **Requirements Specification** protocol (`workflow.md` §1: MUST/SHOULD/MAY + CLEAR/ASSUMED/BLOCKED) with one addition: every acceptance criterion is tagged with the **tier** at which it will be verified. Operationalization is what *assigns* each claim to a tier below; without it there is nothing to gate.

**Decisive effect:** most apparent "judgment" dissolves into checkable sub-claims once the goal is operationalized. The irreducible-judgment residue is smaller than it first looks — and the same architecture recurses: operationalize → script-gate the decidable → evidence-ground and adversarially-verify the residue. That is "deterministic gate first, LLM critic for the residue" applied at the *goal* level rather than the *line* level.

### 7.2 The three tiers of verifiable evidence

| Tier | Claim type | Evidence is… | Producer | Verifier | Guarantee | Example |
|---|---|---|---|---|---|---|
| **1 — Script-decidable** | a script gives a yes/no | deterministic script output (diff, grep, test exit) | non-model actor | **non-model actor** (same script) | **Hard** | no-logic-change; no-hardcoded-paths; seed-once; citation resolves; tests pass |
| **2 — Locatable judgment** | decomposes into sub-claims each pinned to an artifact | cited artifact (`file:line`, a test, an output value) + sufficiency argument | the critic (model) | **split**: a script existence-checks the citation (line exists, test passes); a model judges sufficiency | **Medium** | "goal A achieved" where A = a guard at line 47 + a passing null test |
| **3 — Irreducible judgment** | no single artifact pins it | a reasoned argument | the critic (model) | **independent** model(s) prompted to refute; diverse-lens panel | **Soft / probabilistic** | is this proof correct? is the identification sound? is this clearer? |

The tiers are a spectrum, not silos: operationalization (7.1) pushes as many sub-claims as possible *down* toward Tier 1, leaving the smallest possible Tier-3 residue.

### 7.3 The uniform verdict vocabulary

Across **all tiers** and **all four dispatch contexts**, a verdict is one of:

- **`PASS`** — only with tier-appropriate evidence attached (Tier-1 script output / Tier-2 resolved citation + sufficiency / Tier-3 survived independent refutation).
- **`UNVERIFIED`** — evidence absent or not yet produced. Loud, deducting, never silent. This is the floor that converts the incident's silent false `PASS` into an audible failure in every context.
- **`FAIL`** — disproven.

No bare assertion is ever a `PASS`. The vocabulary is context-uniform by construction, so a critic never needs to know which dispatch context it is in — only whether evidence is in hand. This is the §2 reframe, now stated as the discipline's interface.

### 7.4 The verification ledger as the universal evidence record

`.claude/state/verification-ledger.md` is already the substrate and already spans tiers: its grep/test rows are Tier 1, and its `diagnosis:` rows (`DIAGNOSED` / `RULED-OUT` + "how confirmed") are *already a Tier-2/3 record of a judgment claim with its grounding*. The discipline extends the same table to carry: the **tier**, the **artifact citation** (Tier 2), and the **refuter tally** (Tier 3). One record, queryable by `grep`, with the file-hash staleness mechanism auto-invalidating a verdict when its artifact changes — which already works for judgment rows.

### 7.5 Enforcement actors, mapped to tier

- **Tier 1 → the non-model actors of §6.** Harness hook (the guarantee, all contexts); pipeline gate-agent and git pre-commit as accelerators. A script decides; no model in the verdict path.
- **Tier 2 → schema-enforced evidence + a citation existence-check.** The critic cannot emit `PASS` without a structured `{claim, artifact_citation, sufficiency_argument}` (option 3a); a lightweight script/hook then confirms the cited artifact *resolves* (the line exists; the test runs and passes). The model still judges *sufficiency*, but fabricated *artifacts* are caught mechanically.
- **Tier 3 → independent adversarial verification.** One or more verifiers — *never the producing critic* — prompted to refute, or a diverse-lens panel (the Workflow tool's adversarial-verify / judge-panel patterns). A majority-refute kills the `PASS`. This is the only check available when no artifact pins the claim.

### 7.5a Enforcement strength — block only where the check is deterministic

A discipline that *blocks* everywhere would be unusable (judgment checks have too many false positives); one that only *advises* everywhere would not have prevented the incident (advisory prose is exactly what failed). The resolving principle ties strength to checkability:

- **Block** only at **Tier 1**, and even there ship **advisory-by-default with opt-in blocking** — the `derive-dont-guess` precedent (a `.enabled` state file). The Tier-1 check is deterministic but still *heuristic* (path-normalization is imperfect, per ADR-0011), so false positives exist. During a known mechanical-refactor batch you flip blocking on (`refactor-mode.enabled`, §6 Actor A); otherwise the same check runs advisory.
- **Advise + deduct** at **Tier 2 / Tier 3** and at the **operationalization gate** (Q6) — anything involving judgment. The verdict floor (`UNVERIFIED`, §7.3) and a critic deduction are the enforcement; a hard block on a probabilistic check would stop legitimate work.

So the audible-failure guarantee (`UNVERIFIED` is never silent) holds at *every* tier, but the *hard stop* is reserved for the one tier where a script — not a model — is sure.

### 7.6 Separation of powers, generalized

The producer-verifier separation scales with tier and is the same principle `agents.md` §2 already enforces ("creators don't self-score"):

- Tier 1: producer and verifier can both be non-model — no conflict of interest possible.
- Tier 2/3: the verifier must be **independent of the producer**. A model grading its own justification is self-scoring; that is exactly why Tier 3 requires a *separate* adversarial actor, not the critic's own second opinion.

### 7.7 Honest limits (what the discipline cannot do)

- **Hard guarantees exist only at Tier 1.** Judgment cannot be made deterministic; Tier 2/3 reduce error, they do not eliminate it.
- **Presence ≠ authenticity.** Schema enforcement guarantees evidence is *attached*, not that it is *true*. Tier 2 catches fabricated *artifacts* (existence/test-pass is machine-checkable); Tier 3 catches fabricated *reasoning* (an independent refuter); neither catches a fabrication that survives both. The discipline converts "trust me" into "here is a falsifiable argument a second actor checked" — which is the achievable bar, not certainty.

### 7.8 What this becomes (the unified artifact)

The eventual deliverable is **not** a pile of separate fixes. It is one discipline with one record (the ledger) and one verdict vocabulary, realized as:

1. An upstream **operationalization gate** (extend the requirements-spec protocol: every acceptance criterion tagged with a tier).
2. **Tier-1 enforcement** via the non-model hook (§6) — the load-bearing guarantee.
3. **Tier-2 enforcement** via schema-forced cited evidence + a citation existence-check.
4. **Tier-3 enforcement** via independent adversarial verification in workflows.
5. The **verification ledger** extended to record all three tiers uniformly.

**Home (decided, Q10):** a **single rule** whose mission is to *operationalize `adversarial-default` using evidence gating* — it names the tiers, the verdict vocabulary, the operationalization gate, and the enforcement-strength principle (§7.5a). The principle is not split across files; whether the rule extends `adversarial-default.md` in place or is renamed `evidence-gating.md` is a build-time mechanical choice. The no-logic-change hook ships as its first concrete Tier-1 instance. (Designed, not built.)

---

## Open questions for the user

1. **Hook trigger granularity.** ✅ **RESOLVED — register broadly, act narrowly (gate on the claim, not the edit).** Two things the word "trigger" conflates must be separated:

   - **Registration** (when the script *runs*): PreToolUse `Edit|Write`, with a `git show HEAD:<path>` baseline so the normdiff measures working-vs-HEAD, not just one edit's delta (full-file `Write`s use the same git read). This is mandatory — it is the only way the harness lets a hook observe an edit before it lands.
   - **Activation** (when the hook *checks/blocks*): conditional on a no-logic-change claim being in force — i.e. **`refactor-mode` is on AND the file is in the declared refactor set.** Otherwise the hook is a silent no-op: a logic-changing edit is the *expected, correct* behavior in normal work, so there is no claim to verify and nothing to flag. This mirrors `stata-comment-balance-check.py` (registered on every `Edit|Write`, exits silently for out-of-scope files).

   The conditionality is on the *claim* (refactor-mode), not the *dispatch context* — so when the claim is in force the hook still fires across pipeline / standalone / ad-hoc alike. The two axes are orthogonal; context-independence is preserved.

2. **Block vs. advisory.** ✅ **RESOLVED → §7.5a.** Advisory-by-default with opt-in blocking at Tier-1 only (flip on via `refactor-mode.enabled` during a mechanical-refactor batch). Tier 2/3 and the operationalization gate advise + deduct, never block.

3. **Scope beyond Stata.** ✅ **RESOLVED → language-agnostic from the start.** The discipline is universal, so the rule is language-free by construction. The only language-aware part is the Tier-1 normdiff gate, realized as an **agnostic core + interface with pluggable per-language normalizers** (a single regex set cannot serve all — stripping Stata scaffolding is meaningless for R). The interface is three steps, only the middle one per-language:

   - `extract_executable_regions(text, lang)` — whole file for `.do`/`.R`/`.py`; **code chunks only for `.qmd`/`.ipynb`** (Quarto interleaves YAML + prose + chunks).
   - `normalize(region, lang)` — the per-language module: comment syntax, scaffold patterns, path-token patterns. The *only* language-specific code.
   - `diff(baseline_norm, current_norm)` — language-free residue computation.

   The hook dispatches by file extension, reusing the existing `derive_lib.language_for_path()` mapping helper. **Build scope (decided):** ship four normalizers now — **Stata** (`.do`/`.doh`; port the existing `stata_sweep.py` scaffold/path logic), **Python** (`.py`), **R** (`.R`/`.r`), and **LaTeX** (`.tex`). For LaTeX, "no-logic-change" reads as **"no-content-change"**: the normalizer strips `%` comments and normalizes path tokens (`\input`, `\includegraphics`, `\addbibresource`), so a path/preamble refactor that leaves prose/math/structure intact passes — same core, "substantive line" = content rather than analysis logic. **Quarto (`.qmd`) is deferred** — it needs `extract_executable_regions` chunk handling *and* broader Quarto infrastructure the repo does not yet have; queued to `TODO.md` rather than bundled here.

4. **`UNVERIFIED` and the score gate.** ✅ **RESOLVED.** A load-bearing **Tier-1** `UNVERIFIED` is treated as **FAIL (blocks the <80 commit gate) when `refactor-mode` is on**; otherwise it is a **deduction** that lowers the score without a hard stop. Friction stays proportional to risk — the hard block only during the batch where zero-logic-change is the expected invariant.

5. **Schema enforcement timeline.** ✅ **RESOLVED → schema-enforced from the start, not prose-first.** Prose-only Tier 2 is "the same class as the rule that already failed once" (the synthesis's own warning). The structured `{claim, artifact_citation, sufficiency_argument}` requirement is the actual teeth that stops a bare verdict — ship it with the rule, not later.
### Discipline-level questions (added on revision — §7)

6. **Operationalization gate strength.** ✅ **RESOLVED → advisory.** The gate is an advisory expectation in the requirements-spec protocol, not a block — it reduces friction, and it is consistent with the discipline's own enforcement principle (§7.5a): you block only on deterministic checks, and "are these criteria operationalized enough?" is itself a judgment. Realized as a reminder + a critic deduction when a verdict cites no tagged criteria, never a hard stop.

7. **Tier-2 citation existence-check.** ✅ **RESOLVED → build it.** It is cheap (resolve the `file:line`; run the named test) and it is what makes Tier 2 more than trust — it mechanically catches *fabricated artifacts*. Without it Tier 2 collapses to an unverified assertion.
8. **Tier-3 mandate scope.** ✅ **RESOLVED → mandatory only for load-bearing judgment verdicts** (identification soundness, proof correctness, "goal achieved" on a shipped artifact); optional elsewhere. Adversarial panels cost N× tokens per claim, so a blanket mandate is too expensive — scope the cost to the verdicts where being wrong is expensive.
9. **Ledger schema extension.** ✅ **RESOLVED → extend columns** (`tier`, `artifact_citation` for Tier 2, `refuter_tally` for Tier 3) rather than overload `Evidence`. Keeps the ledger greppable per-tier (`grep '| 3 |'` for all judgment verdicts); overloading one free-text column loses that. The `diagnosis:` rows show the schema already stretches to judgment claims, so this is an additive change.
10. **Unified artifact form.** ✅ **RESOLVED → one rule.** Combine into a single rule whose mission is to **operationalize `adversarial-default` using evidence gating** (tiers + verdict vocabulary + operationalization gate). The name is not load-bearing; the principle must not be split across two files. Whether that means extending `adversarial-default.md` in place or renaming it to `evidence-gating.md` is a mechanical choice to make at build time — the constraint is one rule, one principle.
