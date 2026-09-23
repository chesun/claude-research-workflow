# Infra Survey C — Voice preservation (mechanism-only)
**Date:** 2026-09-22
**Reviewer:** survey agent C (general-purpose)
**Target:** voice-preservation design; /humanize + anti-ai-prose + writer/writer-critic harmonization
**Score:** n/a (survey)
**Status:** Active

---

## 0. Scope and constraints

Mechanism-only: design the machinery for preserving a distinctive academic voice; do **not** build profiles (no exemplar corpus yet). The settled design is taken as given: (1) rename the existing path-inferred *register* knob to **register profile** and reserve **voice profile** for a new positive per-paradigm author-voice spec; (2) `anti-ai-prose`/`humanize` stay **subtractive**, a voice profile is **additive** (`writer` generates *toward* it); (3) two profiles (applied-micro, behavioral) from a named corpus, corpus **deferred**.

Two non-negotiables threaded through every recommendation below:

- **Gates-not-nags.** The repo pruned all reminder/Stop nag hooks on 2026-09-16 ("Claude 5 keeps the log without the nag" — `.claude/rules/logging.md:16`, `output-length.md:17`, `workflow.md`). Style is explicitly *rebuttable* (`anti-ai-prose.md:141`, `:165` — "No hooks. Style is rebuttable; hooks would overfire"). So no new voice mechanism may block a commit or introduce a nag. Blocking is reserved for deterministic Tier-1 checks and even those ship advisory-by-default (`adversarial-default.md` § Evidence gating; the `derive-check-advisory.py` precedent).
- **Cross-platform (Win+Mac).** Current work is actively porting hooks to cross-platform Python (git log `12be99e` "Port notify + protect-files hooks to cross-platform Python"). Any executable piece of this design must be Python, not bash-only. The user is on a Windows enterprise laptop (MEMORY.md: work machine, R/Python/Office, no Stata/LaTeX).

---

## 1. How the upstream `/voice-profile` works

Source: `github.com/pedrohcgs/claude-code-my-workflow`, `.claude/skills/voice-profile/SKILL.md` (v2.0), `.claude/skills/humanize/` (v1.9.0), `.claude/agents/humanize-auditor.md`, `.claude/rules/writing-with-ai.md` (v2.5). Fetched 2026-09-22 from raw.githubusercontent.com/…/main/…

**How a voice is represented.** *Not* a numeric fingerprint and *not* a raw exemplar dump — a **qualitative feature list in six fixed categories** with **frequency annotations** where available:

- `Lexicon` (signature vocabulary + avoid-lists)
- `Rhythm` (sentence length, median, variance, placement of long sentences)
- `Openings` (how sections/paragraphs begin)
- `Transitions` (connectives and their frequency)
- `Hedging` (how uncertainty is expressed — the author's "actual calibration language")
- `Quirks` (distinctive habits explicitly labelled deliberate, so they aren't stripped as tells)

The load-bearing selection rule: *"A trait belongs in the profile if it appears across **most** of the corpus, not because one paper did it once,"* recorded with frequencies (its own example: *"'note that' appears in 7 of 9 papers"*). This is a frequency-thresholded qualitative rubric, not a classifier.

**How it's built.** Input = 3–12 authored documents (published papers preferred), assembled before running. One subagent per document via `context: fork`; each fork reads its single file and writes a ~300-word note against the fixed six-category schema to `notes/voice/<name>.md`, returning only the filename (keeps the corpus out of the main context window). The main session then synthesizes the notes into one profile, keeping only traits that clear the "most of corpus" threshold. Genre/register shifts are noted rather than averaged away.

**How it's stored.** A single narrative-markdown file `voice-profile.md` at repo root (allowlisted in the repo-hygiene gate). No JSON/YAML schema; the body has Signature vocabulary + avoid lists, Sentence rhythm with median metrics, Structural habits, Hedging register with calibration language, Deliberate quirks (labelled), and Register shifts by genre.

**How it's applied.** Two modes. `--audit <draft>` compares a draft against the stored profile and reports **per-section distance with evidence, where every finding cites the specific profile line it violates** ("so it is a deduction rather than taste"). Read-only — it never rewrites; the author edits. Integration: `/humanize` reads `voice-profile.md` when present and respects documented quirks so they aren't flagged as AI tells.

**Frontmatter (verbatim):** `argument-hint: "[corpus directory | --audit draft.tex]"`, `allowed-tools: ["Read","Grep","Glob","Write","Bash","Agent"]`, `disallowed-tools: ["Edit","MultiEdit"]`, `disable-model-invocation: true`.

**Critical observation — upstream is subtractive/audit-only, not additive.** The companion rule `writing-with-ai.md` (v2.5) is explicit: the approach is "subtractive rather than additive"; `/humanize` only *removes* tells; the voice profile only *audits* distance. Its thesis: *"A model cannot make its own output stop reading as model output… The author edits. That manual step is the price of a voice."* Its six non-supersedable floors are prose-quality standards (contribution clarity in the opening; informative sentences; load-bearing hedges only; claims matching evidence; transparent unfavorable results; oral readability), not anti-tell floors. So upstream never has `writer` generate *toward* the profile — that additive path is a genuine extension this repo's settled design (#2) is adding beyond upstream.

**SOTA grounding.** Recent work supports the upstream design choices and this repo's few-shot direction: LLMs hit *surface* style well but miss implicit/authentic voice, and pure imitation is still hard ([Jemama 2025, arXiv:2509.24930](https://arxiv.org/pdf/2509.24930); ["Catch Me If You Can? Not Yet", arXiv:2509.14543](https://arxiv.org/html/2509.14543v1)). The practical, infra-free lever is **few-shot exemplars of the author's prior writing** rather than fine-tuning ([TinyStyler few-shot style transfer](https://www.cis.upenn.edu/~ccb/publications/tinystyler.pdf); [GPT-4o stylometric imitation, DSH 2025](https://academic.oup.com/dsh/article/40/2/587/8118784)). Standard evaluation is authorship-attribution / same-author verification / stylistic-distribution similarity — i.e. distance-to-corpus, which is exactly the audit-cites-profile-line mechanism. Takeaway: adopt qualitative-features-plus-frequency **and** add few-shot exemplar sentences for the additive path; do **not** attempt numeric fingerprints or fine-tuning (brittle, no cross-platform infra, cost).

---

## 2. Answers to Q1–Q4

### Q1 — Separate `/humanize` (subtractive) and a `/voice-profile` capability (additive). Keep separate.

**Recommend: two separate skills, one shared artifact.** Reasons:

1. **Idempotency.** `/humanize`'s contract is "running on already-humanized prose is a no-op… if the pass keeps finding things, the agent is over-rewriting — flag and stop" (`humanize/SKILL.md:90`). An additive generate-toward-voice pass is inherently *not* idempotent: it will keep finding "gaps from the profile" and keep editing on every re-run. Fusing the two breaks the one contract that makes `/humanize` safe to re-run.
2. **Opposite directions, opposite inputs.** Subtractive removes tells against a fixed catalog (`anti-ai-prose.md`); additive generates against an evolving per-author corpus. Different source-of-truth, different failure modes, different lifecycles (catalog is stable; the profile grows with the corpus).
3. **Matches the proven upstream split** (`/voice-profile` + `/humanize`), and matches this repo's own settled framing (#2).

**But wire them, exactly as upstream does:** `/humanize` reads the voice profile when present and suppresses flags on documented quirks / whitelisted signature phrases so it doesn't strip the author's real voice as an "AI tell." And `writer` reads the profile at *generation* time (the new additive path). Net shape: `/voice-profile` (build + `--audit`) and `/humanize` (strip) are two skills over one shared `voice-profiles/<paradigm>.md` artifact.

### Q2 — Bound the supersession: enumerated carve-out set + non-supersedable Critical floor.

A profile may downgrade a flag **only** if (a) the catalog row is on the enumerated-eligible list below, **and** (b) it cites corpus frequency evidence (the trait clears the "appears in most of the corpus" threshold). It may **never** touch a Critical-floor row, regardless of evidence.

**Enumerated carve-out set — a profile MAY legitimize (downgrade to non-flag):**

| Catalog row | What the profile may legitimize | Evidence gate |
|---|---|---|
| L3 (fancy synonyms) | Field-standard verbs only: `implement` (an experiment/treatment/protocol), `methodology` in the methods-section sense | present in corpus |
| L4 (copula avoidance) | Role-assignment `serves as` ("Condition X serves as the control") | present in corpus |
| R1 (signposting) | Academic literature signals `Importantly,` / `Notably,` / `Critically,` at sentence start — **but see Q3: these move to register level, not the profile** | n/a (register) |
| R4 (hedging stack) | A *single* author-calibrated modal ("may", "suggests", "consistent with") already tolerated in the academic register | corpus calibration language |
| S4, S5, T3 (Minor rhythm/structure) | Author's demonstrated rhythm/structure habits | frequency-backed |
| Author-signature whitelist | Specific phrases/words the corpus shows the author using habitually (e.g. "note that" in 7/9 papers) — recorded as an explicit whitelist keyed by frequency | ≥ majority-of-corpus |

**Non-supersedable Critical floor — a profile can NEVER switch off (immutable regardless of any corpus evidence):**

- **S1 em-dash density** (>2 per 100 words) — a rhythm tell, never legitimate at that density.
- **S2 tricolon / rule-of-three overuse** — hard cap, especially on slides.
- **S3 negative-parallelism as default rhythm** ("not just X — but Y" every other sentence).
- **M1 mirror-and-echo openings** ("Great question!", echoing the prompt) — never an author voice.
- **L1 pure-AI vocabulary cluster core** — `delve`, `tapestry`, `navigate`/`leverage` as filler verbs, `foster`, `garner`, `interplay`, `underscore`. (Distinct from the L3 *field terms* above, which are carve-out-eligible.)
- **C1 significance inflation / promotional hyperbole** — "groundbreaking", "watershed", "sea change", "pivotal moment".
- **M3 decorative emoji/arrows** in academic/correspondence; **M4 "comprehensive/complete" puffery.**

**Two hard boundaries on the mechanism:**
1. The carve-out is a **whitelist keyed to catalog row IDs**, and the eligible row-ID set is enumerated in the rule; anything not listed (and the entire Critical floor) is immutable. A profile cannot invent new carve-outs.
2. A voice profile touches **only the `anti-ai-prose` catalog**. It can never downgrade an *epistemic* gate — claims-vs-tables, identification fidelity, derive-don't-guess numbers, bibliography-resolves. Those are out of scope for voice entirely.

### Q3 — Level of the academic carve-outs: register/catalog level, not the per-paradigm voice profile.

The TODO carve-outs (`Importantly,`/`Notably,`; `implement` an experiment; `serves as` the control — `TODO.md:48–53`) belong at the **register/catalog level**, as exception notes on the R1/L3/L4 rows gated by register profile (`academic`/`slide`). **Not** in a per-paradigm voice profile. Reasons:

1. **They are field conventions, not author idiosyncrasies.** *Every* applied-micro paper and *every* behavioral paper writes "serves as the control." That is register, not personal voice. The voice profile should carry only what is distinctive to *this* author.
2. **They must reach `storyteller-critic` too.** The open TODO explicitly names `storyteller-critic` (`TODO.md:53`). A paper-only voice profile never touches slides; a register-level catalog carve-out covers writer-critic *and* storyteller-critic.
3. **They must work with no corpus.** The corpus is deferred (#3). If these carve-outs are bound to a voice profile, the false positives persist until a corpus exists and a profile is built. At register level they can ship *now*, corpus-independent, closing the standing TODO immediately.

Clean division of labor: **catalog/register level = "what the field does"** (corpus-independent, all critics); **voice profile = "what THIS author does"** (corpus-dependent, paper-only, per paradigm). This also keeps the R1 nuance the TODO asks for — distinguish academic signals (`Importantly,`) from genuine filler (`Of course,`, `Clearly,`) — at the one place it can be stated once and inherited everywhere.

### Q4 — Conformance measurement + storage (the key deliverable).

**Representation.** Adopt upstream's six-category qualitative-feature-plus-frequency model (§1), extended with **3–6 verbatim few-shot exemplar sentences per category per paradigm** — the additive anchor `writer` generates toward (SOTA: few-shot exemplars are the infra-free lever that actually moves implicit style). No numeric fingerprint, no fine-tuning.

**Storage & format.** Two profiles, one per paradigm. Format = **markdown with a small YAML front-matter header** (machine-checkable fields a Python check or a critic can read *without* NLP) over a narrative body. Location: `.claude/references/voice-profiles/{applied-micro,behavioral}.md` (`references/` is the repo's lazy-load doc home; nothing loads it until pointed to). Front-matter, illustrative:

```yaml
paradigm: applied-micro
built: 2026-XX-XX
corpus: [angrist_pischke_2009, chetty_2014, ...]   # ties each source to its reading-notes file
corpus_size: 9
signature_vocab:  ["note that (7/9)", ...]          # freq-annotated whitelist
avoid_vocab:      ["utilize", "delve", ...]
carve_out_rows:   [L3, L4, R4]                       # ONLY from Q2's enumerated-eligible set
rhythm: {median_sentence_words: 22, long_sentence_placement: "paragraph-final"}
```

Body: the six narrative categories + the few-shot exemplar sentences. Deliberate quirks labelled (so `/humanize` won't strip them). File-classes: the **skill, the note-schema, and the empty skeleton are Class A** (universal, propagate to overlays); the **filled paradigm content is Class B / overlay-specific** (applied-micro profile with the applied-micro overlay, behavioral with behavioral) — record this in `.claude/file-classes.toml`.

**Measurement — three tiers matching the repo's own evidence-gating tiers (`adversarial-default.md`):**

- **Tier 1 — feature checks (script-decidable, cross-platform Python).** A small `voice_feature_lib.py` (+ test), mirroring the ported hooks, computes: signature-vocab presence, avoid-vocab absence, em-dash density (the S1 floor), sentence-length variance / burstiness vs the profile's `rhythm` median. Deterministic, fast, reused by both the skill's `--audit` and the critic. **Advisory-by-default** (derive-check precedent) — it reports, it does not block.
- **Tier 2 — rubric scoring by agent (locatable judgment).** `writer-critic` reads the profile and scores draft-vs-profile per category; **every finding cites the specific profile line it violates** (upstream's "deduction, not taste"). This is the *positive* counterpart to today's subtractive anti-ai-prose table (`writer-critic.md:198–222`), which only ever deducts. Report as an advisory "Voice conformance" subsection — non-blocking.
- **Tier 3 — exemplar diff (irreducible judgment).** Compare rhythm/openings against the few-shot exemplars; pure agent judgment, never an auto-fail.

**Why measurement stays advisory (gates-not-nags).** Voice conformance is *reported*, never gates a commit: (a) the corpus is deferred so there may be no profile yet; (b) style is rebuttable (`anti-ai-prose.md:141`); (c) the repo pruned nags. Treat it like talk scores — surfaced, non-blocking. The only deterministic piece (Tier-1 feature lib) stays advisory-by-default with opt-in blocking, per the `derive-check-advisory` model — no new Stop/PreToolUse nag hook is added.

**Keeping it current as the corpus grows.** The front-matter records `corpus`, `corpus_size`, `built`. Rebuild (`/voice-profile <dir>`) when N new papers land (suggest +3). Each source paper needs reading notes anyway — **primary-source-first already gates this** and the TODO flags it (`TODO.md:26`). A `/voice-profile --check-stale` reports drift (compare front-matter `corpus` list against papers on disk / reading_notes), reusing the verification-ledger's hash-staleness idea. The "appears in most of corpus" threshold auto-reweights on every rebuild; git history versions the profile.

---

## 3. Concrete build design (files, wiring, measurement)

**New files**
1. `.claude/skills/voice-profile/SKILL.md` — new skill. `build` mode (corpus dir → one fork subagent per document writing a ~300-word note → synthesize past the "most of corpus" threshold → write `voice-profiles/<paradigm>.md`) and `--audit <draft>` mode (read-only, cites profile lines). Cross-platform: `allowed-tools` may include `Bash` only for POSIX-portable steps; prefer the Python feature lib. `disable-model-invocation: true` (explicit-invocation only), mirroring upstream.
2. `.claude/references/voice-profiles/applied-micro.md`, `behavioral.md` — the two profiles (empty skeleton shipped now; content deferred to corpus).
3. `.claude/references/voice-profiles/note-schema.md` — the fixed six-category ~300-word per-document note schema.
4. `.claude/hooks/voice_feature_lib.py` + `test_voice_feature_lib.py` — Tier-1 cross-platform feature checks, shared by the skill and the critic.

**Edited files**
5. `.claude/rules/anti-ai-prose.md` — rename the "Voice profiles" section (`:46–58`) to **"Register profiles"**; the `academic`/`slide`/`correspondence`/`blog`/`docs` table becomes register profiles. Add the **Q3 register-level carve-out exception notes** on rows R1 (academic signals vs filler), L3 (`implement` for experiments), L4 (`serves as` role assignment). Add a "Voice profile (additive)" cross-reference pointing to the new skill and stating the Q2 boundary (enumerated carve-outs + immutable Critical floor + epistemic-gates-out-of-scope).
6. `.claude/agents/writer.md` — keep the subtractive humanizer pass (`:101–105`) unchanged; **add** a "Voice generation" instruction: before drafting, read the paradigm voice profile + its few-shot exemplars and generate toward them (the additive path).
7. `.claude/agents/writer-critic.md` — **add** an advisory "Voice conformance" subsection (positive, non-blocking, cites profile lines), explicitly separate from the subtractive anti-ai-prose table (`:198–222`); note it does not double-count.
8. `.claude/skills/humanize/SKILL.md` — read the voice profile if present; suppress flags on documented quirks + the signature-phrase whitelist (upstream integration); idempotency contract (`:90`) preserved because the profile only *suppresses*, never adds edits.
9. `.claude/agents/storyteller.md` / `storyteller-critic.md` — inherit the register-level carve-outs so slides get them too (Q3).
10. `.claude/file-classes.toml` — skill + note-schema + skeleton = Class A; filled paradigm profiles = Class B / overlay.

**Wiring (single artifact, three consumers)**

```
corpus (papers + reading notes, primary-source-first-gated)
        │  /voice-profile build  (fork subagent per doc → synthesize)
        ▼
.claude/references/voice-profiles/<paradigm>.md   (front-matter + 6 categories + few-shot exemplars)
        ├── writer            → generates TOWARD it            (additive; new)
        ├── writer-critic     → advisory Voice-conformance score, cites profile lines (Tier 2)
        └── /humanize         → suppress-list for quirks/whitelist (keeps subtractive + idempotent)

anti-ai-prose.md  →  stays SUBTRACTIVE; now "register profiles" + register-level academic carve-outs (Q3)
voice_feature_lib.py → Tier-1 deterministic checks, advisory-by-default (used by skill --audit + critic)
```

---

## 4. Integrate / adapt / skip call on the upstream approach

**ADAPT.**

**Integrate (adopt as-is):** the six-category qualitative-feature-plus-frequency representation; the "trait must appear across most of the corpus" threshold; per-document `context: fork` subagents each returning only a filename (keeps corpus out of context); narrative-markdown storage; audit mode where every finding cites the profile line ("deduction, not taste"); `/humanize` reads the profile to spare documented quirks.

**Adapt (take the idea, rebuild minimal for this repo):**
- **Two paradigm profiles** under `.claude/references/voice-profiles/`, not one root `voice-profile.md` (this repo is paradigm-split via overlays).
- **Add YAML front-matter** with machine-checkable fields + a **cross-platform Python `voice_feature_lib.py`** for deterministic Tier-1 checks (upstream leans on `Bash`; Win+Mac needs Python — matches the repo's active hook-porting).
- **Add few-shot exemplar sentences** and an **additive `writer` generate-toward path** — the substantive extension beyond upstream, whose `writing-with-ai.md` is deliberately subtractive-only ("the author edits… the price of a voice"). This repo's settled design #2 wants additive, and SOTA says few-shot exemplars are the right infra-free lever.
- **Advisory scoring only** (gates-not-nags); voice conformance never blocks a commit.
- **Register-level carve-outs (Q3)** — upstream folds field conventions into the profile; this repo puts them at register/catalog level so they reach all critics with no corpus.

**Skip:** upstream's neural-detector framing ("a model cannot make its own output stop reading as model output") — true but not actionable as a gate; keep it as a documented caveat, not a mechanism. Skip numeric fingerprinting and any fine-tuning (no cross-platform infra, cost, and SOTA shows brittleness).

**Explicit compliance notes:** the design adds **no blocking hook and no nag** (voice conformance is advisory, like talk scores); the one executable piece (`voice_feature_lib.py`) is **cross-platform Python, advisory-by-default**; storage is plain markdown that works identically on Windows and Mac.
