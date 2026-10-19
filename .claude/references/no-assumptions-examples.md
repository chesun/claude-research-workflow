# No Assumptions — what counts and worked examples

**Class:** A (universal). Pointer-loaded detail for `.claude/rules/no-assumptions.md` § What counts as an assumption and § Examples (moved from the rule on 2026-10-19); there is no auto-load.

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
