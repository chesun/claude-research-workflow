# 0008: Voice profile: an argument level, where the adopted style model wins

- **Date:** 2026-11-01
- **Status:** Decided
- **Scope:** Methodology / writing
- **Data quality:** Full context
- **Supersedes:** #0006 in part: item 2's "where they conflict with the profile, the profile wins", for argument structure only; and item 3, by one stated exception (item 4 below). The rest of ADR-0006 stands

## Context

The first paper profile (2026-11-01) recorded word- and sentence-level traits from three of the owner's own unaided documents. The owner found it sparse and asked for whole-paper style: how a paper tells its story and builds its argument. A whole-document analysis compared the owner's documents with the first style model, a published paper the owner admires. It found 4 argument habits worth keeping and 5 points where the model's structure is stronger. The owner adopted the model's structure on those 5. Under ADR-0006 item 2 the profile would win every conflict, so the owner's habit would override the structure the owner chose. The owner also dropped the profile's list of never-used words (`avoid_vocab`, a field of the reference schema, not an ADR item): a word is judged by its use. The analysis and counts are in the session log (Sources).

## Decision

1. **An `## Argument` section heads both schemas** (`.claude/references/voice-profile.md`). It is whole-document: the arc, the central idea, how the design is motivated, the order of evidence, alternatives and limits, scope and stakes, proportions. Papers only; the slide profile (ADR-0007) is unchanged.
2. **Precedence splits by level.**
   - On argument structure, a point the profile's `## Argument` marks *model wins* follows the model; the author's other argument habits stand.
   - Everything else in a style model (`## Openings`, `## Transitions`, `## Paragraph structure`) stays as ADR-0006 item 2 has it: structure only, and the profile wins any conflict.
3. **The profile's stated target is authoritative.** Each *model wins* point names its model (`id`) and states the target in full in `profile.md`, so `writer` and `writer-critic` work from one text. A style model's own rules are background.
4. **Provenance, narrowed explicitly.** ADR-0006 item 3 still holds for every trait the profile measures. A *model wins* target is the one exception: it enters `profile.md` only by the owner's explicit adoption at build time, is labelled with its model, and is never evidence for `carve_out_rows` or the whitelist.
5. **`avoid_vocab` is dropped** from the schema. The `anti-ai-prose.md` floor, including the L1 AI vocabulary core, is unchanged (ADR-0006 item 4). Voice stays advisory (ADR-0006 item 6).

## Consequences

- `/voice-profile build` writes one argument note for the own papers together; a style model's per-document note includes its `## Argument`. Notes of unchanged sources are reused.
- The own corpus is proposals, a research summary and an early draft, compared with a published paper. The owner's habits to keep are therefore `provisional` until a finished own paper enters; the adoption choices stand regardless.
- The live profile already follows this (private repo, 2026-11-01): `## Argument` added, `avoid_vocab` removed.

## Sources

- `decisions/0006_voice-preservation.md` :: Decision, items 2–4 and 6
- `.claude/references/voice-profile.md` :: § Profile schema, § Style-model schema, § Per-document note, § How each consumer uses the profile
- `quality_reports/session_logs/2026-10-22_orientation-and-record-backlog.md` :: § 9 (argument level, owner decisions, 2026-11-01)
