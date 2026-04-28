# No Assumptions

**Scope:** all assistant output and code generation in any project that uses this workflow.

**The principle: do not guess about details Claude wasn't told. Only state what was explicitly provided.**

When a detail about the user's workflow, infrastructure, tools, role boundaries, project goals, deadlines, or preferences hasn't been stated, the correct response is one of:

1. **Leave it out.** If the missing detail isn't load-bearing, don't fill it in. Better silence than plausible-sounding fiction.
2. **Ask.** If the detail is load-bearing — the work can't proceed without it — ask one direct question. Don't ask in batches; one question at a time, the most important one first.
3. **State the assumption explicitly.** If the work needs to proceed and asking would block momentum, prefix with "Assuming X (let me know if otherwise)" so the user can correct in one line.

What you must never do: fill in blanks with plausible-sounding assumptions and present them as if they were given. That fabricates user intent and forces the user to debug not just the work but the implicit premises behind it.

---

## What this rule covers (vs. what its sibling rules cover)

The workflow has four rules that together prevent four distinct failure modes of "filling in blanks." This rule is the user-facing one.

| Rule | Source-of-truth |
|---|---|
| **no-assumptions.md** (this rule) | The user's stated requirements, preferences, workflow, infrastructure |
| `primary-source-first.md` | The actual PDF in `master_supporting_docs/literature/papers/` |
| `derive-dont-guess.md` | The relevant file in this repo (filepaths, variables, configs already encoded in code) |
| `adversarial-default.md` | A `grep` / diagnostic / test output recorded in the verification ledger |

Use this rule when the missing fact is something only the user knows. Use `derive-dont-guess.md` when the missing fact is something the repo already encodes. Use `primary-source-first.md` when the missing fact is in an external paper. Use `adversarial-default.md` when the question is whether an artifact satisfies a project convention.

---

## What counts as an assumption

| Category | Example of guessing | What to do instead |
|---|---|---|
| **User role / institution** | "I'll use the AEA template" — without confirming the user is targeting an AEA outlet | Ask: "Targeting an AEA journal, or a different one?" Or check `CLAUDE.md` (which lists target journals); cite where the assumption came from |
| **Stage of work** | "I'll skip the robustness section since you're early-stage" — without knowing the stage | Ask, or do not skip; let the user trim if needed |
| **Deadline / urgency** | "You're probably in a hurry, so I'll leave the audit for later" — without being told | Ask, or do not unilaterally cut scope |
| **Software / tooling** | "I'll write this in R" — without knowing the user's primary language | Check `CLAUDE.md` (which lists primary analysis language); ask if not specified |
| **Infrastructure** | "I'll save outputs locally" — when the user's CLAUDE.md says all execution is on a remote server | Read `CLAUDE.md` first; the rule does not let you skip that read |
| **Coauthor / team workflow** | "I'll commit and push" — without knowing the team's PR process | Ask, or default to the most conservative path (commit only, no push, leave PR creation to user) |
| **Tradeoff preferences** | Picking speed over correctness, or terseness over thoroughness, without being told | Ask if the tradeoff matters; default to user-stated principles in CLAUDE.md or the workflow's defaults |

---

## Interaction with `CLAUDE.md`

`CLAUDE.md` is a load-bearing source of stated preferences. Reading it does not violate this rule — it's the user *having stated* these preferences in writing. Skipping `CLAUDE.md` and then guessing at preferences violates this rule.

Order of operations for any non-trivial task:

1. Read `CLAUDE.md` if not already in context. Note what's stated.
2. Apply stated preferences. Do not generalize beyond them.
3. For details neither stated in `CLAUDE.md` nor in the user's request: leave out, ask, or explicitly assume (per the principle above).

---

## When the rule binds and when it doesn't

**Binds:** any time you're about to make a substantive choice that affects what gets built or shipped — language, framework, scope, tone, level of detail, file location, naming convention, output format, what to include vs cut.

**Does not bind:** harmless internal choices that don't affect the user's deliverable — variable names inside a function, comment style on a single internal line, choice of a temporary file name in a sandbox script, etc. The rule is about *user-visible facets* of the work.

When in doubt, lean toward asking. The cost of one extra question is much lower than the cost of redoing work that proceeded from the wrong premise.

---

## Examples

### Bad — fabricating user intent

User: "Write a codebook script for the cleaned dataset."

Agent: "I'll write it in Python since that's most flexible." [Project uses Stata 17 per `CLAUDE.md`. Python choice was fabricated.]

### Good

Agent: Reads `CLAUDE.md`, sees `Stata version: 17`. Writes a Stata `.do` file.

### Bad — fabricating a deadline

User: "Help me prepare the JMP."

Agent: "Since the JMP is due soon, I'll skip the appendix and focus on the abstract." [No deadline was stated. Scope cut was fabricated.]

### Good

Agent: "Happy to help. Quick check before I scope: what's the timeline (e.g., target submission date), and which sections want priority — abstract, intro, results, appendix?"

### Bad — fabricating a workflow

User: "Run the cleaning script."

Agent: Runs the cleaning script locally. [Project's `CLAUDE.md` says all execution is on a remote server; running locally would fail or produce wrong outputs.]

### Good

Agent: Reads `CLAUDE.md`, sees server-only execution. Says: "This project runs on a remote server. I can't `do` the script directly. Want me to (a) prepare the upload bundle for FileZilla, or (b) walk through SSH steps for the upload?"

---

## Why this is a separate rule from `derive-dont-guess.md`

Both rules tell Claude not to fabricate. They differ in *what kind of fact* is being fabricated and *where the truth lives*:

- `no-assumptions.md` (this rule): the truth lives in the user's head or in `CLAUDE.md`. The agent cannot derive the answer from the codebase; the agent must ask or read what the user has stated.
- `derive-dont-guess.md`: the truth lives in some file in this repo. The agent *can* derive it; the rule requires the derivation step.

A filepath is a `derive-dont-guess` problem (the path is in `settings.do`). A target journal is a `no-assumptions` problem (the journal is whatever the user is aiming for; nothing in the codebase tells you that — only the user, `CLAUDE.md`, or a strategy doc does).

---

## Cross-references

- `derive-dont-guess.md` — sibling rule for repo-derived facts
- `primary-source-first.md` — sibling rule for external-paper claims
- `adversarial-default.md` — sibling rule for compliance claims
- Workflow's `CLAUDE.md` template — primary record of user-stated preferences
