# The four-rule epistemic stack

This is the workflow's most distinctive feature. Four rules sit on top of every agent's behaviour, each preventing a different category of "filling in blanks." They form a complete-by-construction set: every fact an agent could fabricate falls into exactly one of the four source-of-truth categories.

Without these rules, agents follow the standard pattern of language models — fill in plausible-sounding details when asked, sometimes correct, often not. With them, fabrication becomes a deterministically-catchable failure mode.

---

## The principle

When an agent doesn't know a fact, the right move is one of three: ask, leave out, or explicitly disclose the assumption. The wrong move is to fill in a plausible-looking answer. The four rules are scoped versions of this same principle, each pointing at a different *source of truth* for a different category of fact.

| Rule | Source-of-truth | Failure mode prevented |
|---|---|---|
| `no-assumptions.md` | The user's stated requirements | Guessing user prefs, deadlines, target journal, infrastructure |
| `primary-source-first.md` | The actual paper PDF in `master_supporting_docs/literature/papers/` | Citing or framing a paper without reading it |
| `derive-don't-guess.md` | The relevant file in this repo | Fabricating filepaths, variable names, macros, output conventions |
| `adversarial-default.md` | A grep / diagnostic / test output recorded in the verification ledger | Asserting compliance without producing evidence |

Each is documented in full in `.claude/rules/`. This page is a tour, not a substitute.

---

## `no-assumptions.md` — user-side facts

**What it prevents.** An agent guessing the target journal, the deadline, the audience, the team's commit policy, the deployment target, the user's level of expertise, or any other fact that lives in the user's head and hasn't been written down yet.

**Why it's good.** The most expensive class of error in research workflows is "the agent inferred urgency / scope / preference and the inference was wrong." It's expensive because the user has to debug not just the work but the implicit premises behind it.

**How it's enforced.** The rule is loaded into every agent's prompt. Critics deduct for paper claims that fabricate stage, deadline, or audience without evidence in `CLAUDE.md` or the user's stated requirements. There's no hook for this rule because user-side facts can't be programmatically checked — only an agent reading the conversation can tell whether a claim is grounded.

**Concrete example.** User: "Help me prepare the JMP." Without the rule, an agent might respond "Since the JMP is due soon, I'll skip the appendix and focus on the abstract." That sentence fabricates urgency. With the rule, the agent asks: "What's the timeline, and which sections want priority?"

---

## `primary-source-first.md` — external papers

**What it prevents.** An agent making framing claims about a paper without having read the actual PDF. This is the failure mode that motivated the rule: a misreading once propagated through a decision log, an analysis memo, a session log, and a slide review without any of those documents catching the error, because the original misreading was paraphrased and re-paraphrased without anyone re-opening the source.

**Why it's good.** Citations in research are load-bearing. A wrong framing claim about a paper, propagated through derivative documents, is a class of bug that's expensive to debug and erodes trust in the workflow's overall output.

**How it's enforced.** Two hooks:

- A **PreToolUse hook** (`primary-source-check.py`) blocks edits to scoped files (`decisions/`, `quality_reports/plans/`, `quality_reports/session_logs/`, `quality_reports/reviews/`, `theory/`, etc.) when those files cite a paper that lacks reading-notes evidence in `master_supporting_docs/literature/reading_notes/`.
- A **Stop hook** (`primary-source-audit.py`) audits the agent's conversation prose at turn-end for the same. Conversation citations are subject to the same rule as file citations.

The hook is satisfied when either (a) a PDF exists at `master_supporting_docs/literature/papers/<surname>_<year>.pdf`, or (b) reading notes exist at the equivalent path in `reading_notes/`. The escape-hatch comment `<!-- primary-source-ok: stem -->` allows illustrative or test-case mentions where no framing claim is being made.

**Citation-style convention.** Two-coauthor papers always written as "Author and Author (year)", never comma-separated, never with `&`. Standard economics convention plus avoids hook regex false-positives on comma-adjacent surnames.

---

## `derive-don't-guess.md` — repo-internal facts

**What it prevents.** An agent fabricating a fact that the project already encodes — a filepath, a variable name, a macro, a package version, an output convention, a directory layout, a config value. The trigger incident: in a real session, an agent generated `use "data/cleaned/main.dta"` for a Stata script when `do/settings.do` had defined `$csacclndatadir/main_v3.dta`. The agent guessed where to look instead of grepping the existing scripts.

**Why it's good.** Repo-internal facts are derivable in milliseconds (one `grep`). Fabricating them produces code that doesn't run; the user has to debug the work plus the agent's implicit guess about where things live. The cost of derivation is negligible; the cost of fabrication compounds.

**How it's enforced.** The rule is loaded into every coder and writer agent's prompt. Each agent must cite the source `file:line` for any repo entity it references. Critics deduct for fabricated paths, undefined macros, fabricated variable names, output paths that don't follow any existing convention, or numeric values in paper text that don't appear in tracked output files.

When no precedent exists in the repo (the project is new, or the entity is genuinely first), the agent must explicitly disclose: "Creating a new convention here because no existing pattern was found in [files searched]."

**Per-entity-type lookup table.** The rule includes concrete `grep` commands for each entity type — datasets, macros, packages, output paths, seeds, etc. — so agents have a deterministic recipe rather than judgement-based shortcut.

---

## `adversarial-default.md` — compliance claims

**What it prevents.** An agent saying "the code follows the no-hardcoded-paths convention" without actually checking. The trigger: a real session where an agent reviewed inherited Stata code, said "no issues found," and passed it. The code had many hardcoded paths.

**Why it's good.** "Looks fine" is the absence of evidence, not evidence of absence. For compliance claims about any artifact (code, design, identification, replication, bibliography), the burden of proof should be on the asserter, not the critic. Otherwise, hidden defects accumulate and surface late — at submission, when the cost of fixing is highest.

**How it's enforced.** Critics demand positive evidence for every compliance claim — a `grep` result, a diagnostic output, a test pass, a hash match. The verification ledger at `.claude/state/verification-ledger.md` caches results so unchanged artifacts aren't re-checked: each row records `(path, check, sha256[:12])` and an evidence string. On a subsequent task, the file-hash match means the cached PASS is cited; the actual check doesn't re-run. File-hash mismatch triggers re-run.

This is the rule that makes "adversarial" sustainable. Without the ledger, demanding evidence on every check would slow every task. With the ledger, first check pays the verification cost; subsequent checks on unchanged artifacts pay only the lookup cost.

**Six per-domain checklists.** Each domain (Stata code, R code, Python code, data, design, identification, replication, bibliography) has a concrete list of `(check_name, command, PASS criterion)` triples that critics reference. The full table is in the rule file.

---

## Why all four together

Each rule alone catches one class of failure. Together, they catch all four:

| Failure | Rule that catches it |
|---|---|
| "I assumed you wanted the JMP done by Friday" | `no-assumptions.md` |
| "Niederle (2024) shows that p-hacking is good" *(without having read Niederle)* | `primary-source-first.md` |
| `use "data/main.dta"` when the path is `$datadir/main_v3.dta` | `derive-don't-guess.md` |
| "The code follows project conventions" *(without grep evidence)* | `adversarial-default.md` |

There's no overlap between the categories: a fact is either user-side, paper-side, repo-side, or compliance-side. Together, the four rules form a complete-by-construction stance against fabrication.

The cost is verification overhead. The benefit is that everything an agent claims is auditable: you can ask "where did you get that?" and the answer is always a tracked file, a recorded grep, or an explicit assumption.

---

## Cross-references

- [`.claude/rules/no-assumptions.md`](../../.claude/rules/no-assumptions.md)
- [`.claude/rules/primary-source-first.md`](../../.claude/rules/primary-source-first.md)
- [`.claude/rules/derive-dont-guess.md`](../../.claude/rules/derive-dont-guess.md)
- [`.claude/rules/adversarial-default.md`](../../.claude/rules/adversarial-default.md)
- `concepts/verification-ledger.md` *(planned for v0.2.x)* — the ledger format and lookup protocol in depth
- `concepts/upstream-differences.md` *(planned for v0.2.x)* — these four rules as the most distinctive contribution vs upstream
