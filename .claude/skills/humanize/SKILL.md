---
name: humanize
description: Strip AI writing patterns from any external-facing document (paper, slides, README, blog post, cover/response letter). Universal entry point that infers the voice profile from the file path and dispatches the appropriate agent in humanizer mode. Replaces /write humanize.
argument-hint: "[file path] [--profile academic|slide|correspondence|blog|docs] [--audit | --apply]"
allowed-tools: Read, Grep, Glob, Edit, Task
---

# Humanize

Apply the project's anti-AI-prose pass to any external-facing document. Reads `.claude/rules/anti-ai-prose.md` (catalog of ~35 patterns across 6 categories) and removes the AI tells while preserving the author's voice and the document's register.

**Input:** `$ARGUMENTS` — file path, optional profile flag, optional mode flag.

---

## Modes

### `/humanize [path]` — Apply (default)

Edit the file in place to strip the AI patterns flagged by the rule. The agent reports what it changed.

### `/humanize [path] --audit`

Read-only. Produces a review report listing every pattern hit (location, severity, suggested rewrite) without modifying the file. Output: `quality_reports/reviews/YYYY-MM-DD_<target>_humanizer_review.md`. Use when you want to inspect before accepting changes.

---

## Voice profile inference

The skill infers the profile from the file path (see `anti-ai-prose.md` § Voice profiles):

| Path matches | Profile |
|---|---|
| `paper/**` | `academic` |
| `talks/**` | `slide` |
| `*cover-letter*`, `*response-letter*` | `correspondence` |
| `blog/**`, `*-blog.md` | `blog` |
| `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/**` | `docs` |
| (no match) | Ask the user before proceeding |

Override with `--profile <name>`.

---

## Dispatch

The skill picks the right agent based on file type:

| File type | Dispatched agent |
|---|---|
| `.tex` in `paper/` | `writer` (humanizer mode) |
| `.tex` in `talks/` | `storyteller` (humanizer mode) |
| `.md` (any external scope) | `writer` (humanizer mode, generic-prose dispatch) |

The agent receives:
- The target file path
- The voice profile
- The mode (audit or apply)
- A pointer to `.claude/rules/anti-ai-prose.md`

---

## Out of scope

The skill **refuses** to run on paths that the rule excludes (`quality_reports/`, `decisions/`, `master_supporting_docs/`, `.claude/`, `scripts/`, `do/`). These are internal artifacts; humanizing them spends cycles on prose nobody outside the project reads.

If the user explicitly insists on running on an excluded path (e.g., a session log they want to publish), they pass `--force-scope`. The skill warns and proceeds.

---

## Escape comments

The agent respects `<!-- anti-ai-ok: <reason> -->` comments per the rule. Patterns inside a paragraph that contains such a comment are not flagged or rewritten.

---

## Output

- **Apply mode:** edited file + summary in conversation ("changed N patterns: 3 critical, 5 major, 2 minor")
- **Audit mode:** review report at `quality_reports/reviews/YYYY-MM-DD_<target>_humanizer_review.md`, no file edits

In both modes, the agent reports the per-category breakdown so the user can see whether the pass was mostly lexical (vocabulary) or structural (sectioning, sentence rhythm).

---

## Principles

- **The author's voice wins.** When the rule and the author's existing style conflict, preserve the author's style. The catalog is a rebuttable presumption.
- **Don't over-strip in academic register.** Hedging modals ("may", "suggests") are legitimate in papers. Don't remove them mechanically; remove only when stacked or filler.
- **Idempotent.** Running `/humanize` on already-humanized prose should be a no-op. If the pass keeps finding things on re-run, the agent is over-rewriting — flag and stop.
- **Auditable.** Every change in apply mode should be defensible by pointing at the catalog row that flagged it.

---

## Relationship to `/write humanize`

`/write humanize [file]` is **deprecated** in favor of `/humanize [path]`. The `/write` skill no longer has a humanize mode; it now drafts only. For backward compatibility, `/write humanize <file>` aliases to `/humanize <file>` and prints a one-line deprecation note.
