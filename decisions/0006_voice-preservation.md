# 0006: Voice preservation: one private author profile, advisory, bounded

- **Date:** 2026-10-29
- **Status:** Decided (item 6's papers-only scope superseded by #0007)
- **Scope:** Methodology / writing
- **Data quality:** Full context

## Context

The `writer` drafts in a generic academic register, and `/humanize` strips AI tells against a fixed catalog (`anti-ai-prose.md`). Neither knows how the author actually writes. So a draft can be free of AI tells and still not read as the author's, and `/humanize` can strip a habit of the author's as if it were a tell. Voice preservation was the one committed build from the 2026-09-22 infrastructure survey. Its design (survey C) assumed two paradigm profiles built from the author's papers.

On 2026-10-29 the owner settled the inputs:
- one profile of their own voice;
- other authors' papers as style models;
- the profile kept private.

The owner also stated that their recent drafts carry AI help (the July 2025 JMP draft was written with ChatGPT help, and later versions with Claude). Only parts the owner declares their own, and older unaided writing, can teach the profile.

## Decision

1. **One author profile,** at user scope: `<home>/.claude/voice/profile.md`. That folder is a clone of the owner's private GitHub repo, `chesun/voice-profile`, cloned to the same path on each machine. The profile is then durable and portable, every project reaches it, and no project repo carries it. This replaces the survey's two paradigm profiles. A missing profile is reported, never skipped silently.
2. **Style models are separate** (`style-models.md`). Built from other authors' papers, they inform structure only (openings, transitions, paragraph structure). They never feed the vocabulary, the hedging, the quirks or the carve-outs. Where they conflict with the profile, the profile wins.
3. **Only declared own text teaches the profile.** Each source carries the owner's provenance declaration, and the parts used where only some sections qualify. AI-assisted text is excluded, not down-weighted.
4. **Bounded supersession.** A profile may spare catalog flags only on an enumerated list of rows, with corpus evidence. It can never spare the floor (em-dash density, tricolons, negative parallelism, mirror-and-echo openings, the AI vocabulary core, significance inflation; in academic prose, decorative symbols and "comprehensive" claims). It never touches an epistemic check. The lists live only in `.claude/references/voice-profile.md`.
5. **Field conventions are register-level, not profile-level:** `Importantly,` / `Notably,` as literature signals, `implement` an experiment, `serves as` the control. They are in `anti-ai-prose.md` and need no corpus.
6. **Advisory only.** `writer` writes toward the profile. `writer-critic` reports voice conformance beside its score, never in it. `/humanize` uses the profile only to spare flags, and only for papers. No hook, no gate.

   Why advisory:
   - style is rebuttable (`anti-ai-prose.md` § What this rule is NOT);
   - a provisional profile built from one paper is weak evidence for a deduction;
   - the repo keeps blocking for script-decidable checks (`adversarial-default.md` § Evidence gating).
7. **Privacy.** No corpus text, excerpt, exemplar sentence or owner paragraph goes in any committed file in any repo. Committed records hold verdicts, counts and row IDs.

## Consequences

- The template ships the mechanism (`/voice-profile`, the reference, the wiring) and no profile content. A fork without a profile behaves as before.
- With one qualifying paper, traits qualify on recurrence across the paper's sections, and the profile is marked provisional until 3 papers.
- A second machine needs one `git clone` of the private repo to `<home>/.claude/voice/`. A fork's owner makes their own private repo.
- Deferred: a Tier-1 feature script (`bin/voice_features.py`), until 3 own papers or a consumer that reads its output. Merging `econ-writing-skill` into the catalog remains a separate candidate. ADR-0003's `writer` routing is revisited after the profile is built.
- Whether the profile works is tested by blind ranking and the owner's blind pick (plan acceptance A4–A5), and recorded as ranks only.

## Sources

- `quality_reports/plans/2026-10-29_voice-preservation.md` (v2; reviews fit-for-purpose 72, efficiency 80)
- `quality_reports/reviews/2026-09-22_infra-survey_C-voice.md` :: § 2 (Q1–Q4), § 3
- `quality_reports/reviews/2026-09-22_infra-survey_synthesis.md` :: § Voice-preservation design
- `.claude/references/voice-profile.md`
