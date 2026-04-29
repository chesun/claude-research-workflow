# Anti-AI Prose

**Scope:** All external-facing prose — anything a human audience reads. Internal artifacts are exempt.

**Why this rule exists:** AI-generated prose carries stylistic tells (em-dash overuse, "delve"/"navigate" vocabulary, signposting filler, tricolon overuse, uniform sentence rhythm) that erode reader trust even when the content is correct. A reader who notices the writing was AI-assisted starts auditing the *facts* harder, and that audit is where the project loses credibility. The rule documents the patterns to strip and the voice to preserve. It is the project's standard for any document a non-author will see.

This rule is the **stylistic** counterpart to the four epistemic rules (`no-assumptions.md`, `primary-source-first.md`, `derive-dont-guess.md`, `adversarial-default.md`). Those prevent fabrication of *facts*; this one prevents fabrication of *voice*.

---

## File scope

**In scope (rule applies):**

- `paper/**/*.tex` — paper manuscript and sections
- `talks/**/*.tex` — Beamer slide decks (slide prose, frame text, speaker notes)
- `paper/cover-letter.tex`, `paper/response-letter.tex` — correspondence to editors
- `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/**/*.md` — public documentation
- `**/*-blog.md`, `blog/**/*.md` — blog posts or essay drafts
- Any explicitly-named external deliverable (`presentation-handout.md`, `executive-summary.md`, etc.)

**Out of scope (rule does not apply):**

- `quality_reports/**` — session logs, plans, reviews, internal reports
- `decisions/**` — ADRs (decision records, internal)
- `master_supporting_docs/**` — reading notes, internal supporting material
- `.claude/**` — workflow infrastructure (rules, skills, agents, hooks)
- Source code comments in `scripts/`, `do/`, etc. — comments are for the next coder, not an external audience
- `experiments/designs/`, `theory/` working drafts — promote a copy to the paper before the rule applies
- `templates/` — templates are reference material

---

## Voice profiles

The pattern catalog applies universally; the *register* and *flexibility* vary by document type. When a humanizer pass is invoked, the profile is inferred from path (table below) or set explicitly via flag.

| Profile | Inferred from | Register | Notes |
|---|---|---|---|
| `academic` | `paper/**` | Formal, dense, precise, citation-heavy | Hedging is *more* tolerated — academic prose legitimately uses "may", "suggests", "consistent with". Don't over-strip. |
| `slide` | `talks/**` | Terse, declarative, punchy | Slides are bullet-light, sentence fragments OK. Tricolons especially overused on slides — hard cap. |
| `correspondence` | `cover-letter.tex`, `response-letter.tex` | Formal, polite, direct | Formality required; no forced casualness. Promotional inflation especially out of place ("groundbreaking" in a cover letter is a tell). |
| `blog` | `blog/**`, `**/*-blog.md` | Direct, warmer, first-person OK | More leeway on contractions and conversational openers. Still strip the AI tells. |
| `docs` | `README.md`, `docs/**` | Practical, instructional, second-person OK | Imperative voice fine. The signposting trap is real here ("In this section we will...") — strip aggressively. |

If a path doesn't match any profile, the humanizer asks before applying.

---

## Pattern catalog

Six categories, ~35 patterns. Severity tiers (Critical / Major / Minor) drive the writer-critic and storyteller-critic deduction tables (see `quality.md` § 3).

### 1. Lexical (vocabulary tells)

| # | Pattern | Severity | Example | Fix |
|---|---|---|---|---|
| L1 | AI vocabulary cluster | Critical | delve, navigate, leverage (as filler verb), tapestry, landscape, foster, garner, interplay, underscore | Use the plain-English verb. "Leverage X" → "use X"; "navigate the literature" → "read the literature". |
| L2 | Promotional adjectives | Major | groundbreaking, comprehensive, robust (as filler), pivotal, transformative, cutting-edge, paradigm-shifting | Drop or replace with concrete claim. "Robust" is fine for SE methods; flag when it's a content puff word. |
| L3 | Fancy synonyms for plain words | Major | utilize, demonstrate, facilitate, subsequent, aforementioned, methodology (when "method" works), implement (when "do" works) | Plain word. Already covered in writer-critic Cochrane checks; this rule reaffirms. |
| L4 | Copula avoidance | Minor | "X serves as Y", "X represents Y", "X stands as Y" | "X is Y". |
| L5 | Vague intensifiers | Minor | very, quite, rather, somewhat, fairly, relatively (as filler) | Delete. |

### 2. Syntactic (sentence structure)

| # | Pattern | Severity | Example | Fix |
|---|---|---|---|---|
| S1 | Em-dash overuse | Critical | More than ~2 em-dashes per 100 words. Especially mid-clause em-dashes used like a comma. | Use commas, parens, or sentence breaks. Em-dash for *real* emphasis only. |
| S2 | Tricolon / rule-of-three overuse | Major | "Not only X, but Y, and even Z." Three-item parallel lists in every other sentence. | Vary structure. Two items, four items, or a single emphatic clause. |
| S3 | Negative parallelism | Major | "Not just X — but Y." Used as a default rhythm. | Use sparingly. Once per page max. |
| S4 | Uniform sentence length | Minor | Every sentence within 5 words of the mean. AI prose is rhythmically flat ("low burstiness"). | Vary: short sentence followed by a long one. Single-clause punctuation. |
| S5 | Symmetric sentence structure | Minor | "While X happens, Y happens." Pattern repeated within a paragraph. | Break the symmetry. Subordinate one, lead with the other. |

### 3. Structural (sectioning & layout)

| # | Pattern | Severity | Example | Fix |
|---|---|---|---|---|
| T1 | Symmetric sectioning | Major | Every section has the same word count and the same internal arc (intro paragraph → 3 examples → summary). | Let each section be the length its content requires. |
| T2 | Bullet-point thinking in prose | Major | Paragraph that reads like flattened bullets — same connective ("Furthermore,", "Additionally,", "Moreover,") between every sentence. | Connect ideas with reasoning, not with rote transitions. |
| T3 | Forced narrative arc | Minor | Every section opens with a hook, has a turning point, ends with a takeaway. Mechanical structure. | Don't impose a story arc on a section that doesn't have one. Sometimes a section just lists three facts. |
| T4 | Over-defined common terms | Minor | "GDP, the total economic output of a nation, ..." — explaining a term the audience already knows. | Trust the reader. Define jargon, not common terms. |

### 4. Rhetorical (signposting & hedging)

| # | Pattern | Severity | Example | Fix |
|---|---|---|---|---|
| R1 | Signposting filler | Major | "It's worth noting that...", "It is important to note...", "Of course,", "Clearly,", "Obviously,", "Needless to say," | Delete. State the thing directly. |
| R2 | Throat-clearing introductions | Major | "In today's increasingly complex world...", "Researchers have long debated..." | Cut to the substance in sentence 1. |
| R3 | Roadmap signposting | Minor | "The remainder of this paper is organized as follows..." (already in McCloskey list); on slides: "In this section we will explore..." | Delete on slides; one short version OK in papers. |
| R4 | Hedging stack | Minor | "may potentially", "could possibly", "might conceivably". Stacking modal hedges. | One hedge max. Academic profile tolerates single hedges. |
| R5 | Vague attribution | Minor | "Experts argue", "Researchers suggest", "Many believe". | Cite a specific source or drop the claim. |

### 5. Content (substance tells)

| # | Pattern | Severity | Example | Fix |
|---|---|---|---|---|
| C1 | Significance inflation | Major | "pivotal moment", "watershed development", "sea change". Generic hyperbole that adds no information. | State the actual mechanism or magnitude. |
| C2 | Superficial -ing analyses | Major | "highlighting the importance of", "underscoring the need for", "demonstrating the relevance of" — vague nominalized claims. | State *what* is highlighted/demonstrated, with the specific evidence. |
| C3 | Both-sidesing without commitment | Minor | "On one hand X, on the other hand Y" without taking a position or weighing the sides. | Take the position the evidence supports. Or leave the ambiguity but justify it. |
| C4 | Listicle padding | Minor | Three "key takeaways" / "main points" at the end of a section that just restate what was already said. | Trust that the reader read the section. |

### 6. Communication (filler & framing)

| # | Pattern | Severity | Example | Fix |
|---|---|---|---|---|
| M1 | Mirror-and-echo openings | Critical | "Great question! Let me explain..." or any echo of the prompt back at the reader. Almost always AI. | Delete. Start with the answer. |
| M2 | "It's all about" framing | Minor | "It's all about understanding the trade-offs." — folksy framing as a thesis. | State the actual thesis. |
| M3 | Emoji or decorative punctuation | Major (academic) / Minor (blog) | ✨, →, • used decoratively in prose. | Strip in academic / correspondence. Sparingly OK in blog/docs if the project conventions allow. |
| M4 | "Comprehensive" / "complete" claims | Major | "A comprehensive overview of...", "A complete guide to..." | Be specific about what's covered (and what isn't). |

---

## Severity → deduction mapping

The severity tiers above plug into the writer-critic and storyteller-critic deduction tables (see `quality.md` § 3 — Per-Target Deduction Tables). Headline:

| Severity | Per-instance deduction | Cap per document |
|---|---|---|
| Critical | −5 | −20 |
| Major | −3 | −15 |
| Minor | −1 | −10 |

Total anti-AI-prose deduction is capped at −30 per document so it doesn't dominate the writer-critic score (which is also assessing structure, claims-evidence alignment, identification fidelity, and grammar).

---

## What this rule is NOT

- **Not a wordlist ban.** Many of the L1/L2 words have legitimate technical uses ("robust standard errors", "leverage points"). Flag only when the word is filler. The catalog is a *rebuttable presumption*, not a hard ban.
- **Not a substitute for writer-critic's other checks.** McCloskey 11-item, Cochrane style flags, Knuth math-writing rules, claims-evidence alignment — those are separate and remain in writer-critic. This rule adds the *AI-specific* layer; it doesn't replace the broader prose-quality framework.
- **Not active on internal artifacts.** Session logs, ADRs, plans, reviews are written for the next coauthor (often the same person). Strip the rule there and you spend cycles polishing prose nobody sees.
- **Not a humanizer service.** Humanizing isn't obfuscation. The goal is "reads like the author wrote it," not "evades AI detectors." The patterns are real prose smells, not arbitrary fingerprints.

---

## Escape hatch

If a flagged pattern is intentional (e.g., a paper about AI writing that quotes AI prose; a deliberate stylistic choice the author owns), include an override comment:

```
<!-- anti-ai-ok: <reason> -->
```

The comment scopes to the paragraph it appears in. Auditable: `grep -R "anti-ai-ok" paper/ talks/ docs/` surfaces every use. The skill and critic respect the comment.

---

## How this rule is enforced

- **`/humanize` skill** — universal entry point. Reads the rule, dispatches the writer (for `paper/`) or storyteller (for `talks/`) in humanizer mode, or runs a generic humanizer pass for `docs/`/`blog/`.
- **writer-critic** — adds an "Anti-AI Prose" deduction subsection that scores against this catalog.
- **storyteller-critic** — same, scoped to slides.
- **No hooks.** Style is rebuttable; hooks would overfire on legitimate uses. The rule + critic + skill are the enforcement triad. If patterns persistently slip through despite the critic, revisit.

---

## Cross-references

- `quality.md` § 3 — deduction tables (writer-critic, storyteller-critic)
- `agents/writer.md` — writer's humanizer pass (now references this rule instead of duplicating the catalog)
- `agents/storyteller.md` — slide humanizer reference
- `skills/humanize/SKILL.md` — universal entry point
- `working-paper-format.md` — earlier hedging deductions are subsumed under this rule's R1/R4 (consolidated)
