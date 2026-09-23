# Infra Survey A — Base repo deep-read
**Date:** 2026-09-22
**Reviewer:** survey agent A (general-purpose)
**Target:** pedrohcgs/claude-code-my-workflow (feature inventory)
**Score:** n/a (survey)
**Status:** Active

## Scope and method

Read-only web survey of `pedrohcgs/claude-code-my-workflow` (Pedro Sant'Anna), the upstream base of this maintained repo. Version **v2.5.1** (per repo README/CHANGELOG, WebFetch-reported — *inferred*, not independently confirmed against the tag). Directory listings for `.claude/{skills,agents,rules,hooks}` were pulled **verbatim from the GitHub contents API** (verified). High-priority files (`model-routing.md`, `writing-with-ai.md`, `voice-profile/SKILL.md`, `humanize/SKILL.md`, `backtest.sh`, `model-versions.md`, the two guard hooks, `LEDGER.md`, `vaccinate`, `verify-claims`) were read from `raw.githubusercontent.com` (**verified from page**). Skills characterized from name/convention only are flagged **(inferred)**.

Note on model lineup divergence: the base's `model-versions.md` lists **Opus 5 / Fable 5 / Sonnet 5 / Haiku 4.5** as current (verified 2026-08-21). This harness reports Opus 4.8. Treat the base's IDs as its own SSOT, possibly ahead of the downstream harness — do not copy IDs blindly.

Downstream philosophy applied to every pre-call: **gates-not-nags, Claude-5-native-first, personal-scale (single repo, not a multi-consumer lab), cross-platform.**

---

## Verified inventory counts

- **Skills:** 60 (verified list from contents API)
- **Agents:** 18 (verified)
- **Rules:** 37 (verified)
- **Hooks:** 8 (verified)

---

## Feature table — notable items

Legend for "Native?": **N5** = leans on genuine Claude-5 capabilities (subagent forking, effort axis, structured output); **HR** = hand-rolled convention/script that a capable model doesn't strictly need; **mix** = both.

### Skills

| Feature | What it does | Native? | Dependencies | Pre-call + reason |
|---|---|---|---|---|
| `/voice-profile` | Builds an author voice signature from 3–12 prior papers; **one subagent per paper (`context: fork`)**, each emits ~300-word note; main session synthesizes `voice-profile.md` at repo root. Voice = **feature list, 6 fixed categories** (Lexicon, Rhythm, Openings, Transitions, Hedging, Quirks). `disable-model-invocation: true`. `--audit draft.tex` compares a draft to the profile. (verified) | mix | subagent forking; papers corpus | **ADAPT** — best-fit feature for a personal template; single-author voice is exactly the personal-scale case. Keep the 6-category feature-list representation; the fork-per-paper is optional polish. |
| `/humanize` | **Read-only** AI-prose audit of `.tex/.qmd/.md`; **10 detection categories** (boilerplate transitions, AI-cliché lexicon, em-dash overuse, symmetric paragraph shapes, tricolon abuse, hedge stacking, "not only…but also", formulaic openers, hyphenation excess, sycophancy); HIGH/MED/LOW severity; density thresholds (>8 HIGH/1000w ⇒ rewrite). No `--rewrite` by design. Reads `voice-profile.md` to suppress documented habits. (verified) | HR | `humanize-auditor` agent; optional `voice-profile.md` | **INTEGRATE** — downstream already has `/humanize` + `anti-ai-prose.md`; adopt the **voice-profile-suppression hook** (fewer false positives) and the read-only stance. |
| `/verify-claims` | Chain-of-Verification (Dhuliawala et al. 2023): extract claims → one question each → spawn **`claim-verifier` in fresh forked context that never sees the draft** → reconcile to severity tiers. HIGH-WARN (fabricated cite/contradiction) **gates `/commit`**; EXPLAINED tier (v2.0) for justified numeric mismatch. (verified) | N5 | `claim-verifier` agent; source pointers | **ADAPT (top pick)** — a real fabrication gate, Claude-5-native (forked blind verifier), matches downstream's fabrication-gate philosophy. Strong fit. |
| `/vaccinate` | Qualifies a checker before trusting it: seeds known defects into a **copy** + a clean control, runs the checker blind, records **recall + FPR** into a qualification ledger. Principle: **"an unqualified check is not weak evidence — it is none."** (verified) | HR | ledger; artifact copies | **ADAPT (concept)** — adopt the principle to harden the downstream's existing hook tests (planted-defect test each gate); skip the full ledger bureaucracy. |
| `/audit-reproducibility` | Cross-checks numeric claims in prose against script outputs via `passport.yaml` state files. (inferred from README/guide) | HR | passport.yaml convention | **ADAPT** — valuable for econ (numbers-match-tables), but reimplement lean against existing verification-ledger rather than adding a new state file. |
| `/challenge`, `/devils-advocate` | Adversarial stress-test of paper/strategy (referee objections, cold read). (inferred; downstream has `/challenge`) | HR | — | **SKIP (already present)** — downstream ships `/challenge`. |
| `/compress-session`, `/checkpoint`, `/context-status` | Session/context management + snapshots. (inferred) | mix | — | **SKIP** — Claude-5 auto-compaction; downstream already pruned context nags. `/context-status` already exists downstream. |
| `/promote-memory` (+ `promote-memory-council` agent) | Multi-agent "council" votes on which learnings to promote to memory. (inferred) | HR | council agent | **SKIP** — lab-scale ceremony; Claude-5 built-in memory + single-author scale makes a voting council overkill. |
| `/deploy`, `/replication-package`, `/disclosure-check`, `/submission-disclosures`, `/data-management-plan`, `/grant-proposal`, `/power-analysis`, `/preregister` | Submission/compliance/grant tooling. (inferred) | HR | — | **ADAPT selectively** — `/replication-package`, `/power-analysis`, `/preregister`, `/disclosure-check` are genuinely useful for empirical econ; pull individually as needed. `/deploy` is repo-publishing (skip for personal). |
| Teaching stack: `/create-lecture`, `/syllabus`, `/scaffold-exercises`, `/teach-from-paper`, `/pedagogy-review`, `/qa-quarto`, `/translate-to-quarto`, `/slide-excellence` | Lecture/slide/Quarto pedagogy tooling. (inferred) | HR | Quarto/Beamer | **SKIP** — Pedro teaches; a personal research template doesn't need the pedagogy/Quarto surface. |
| `/seven-pass-review`, `/oracle-review`, `/adjudicate-review`, `/differential-audit`, `/diagnose`, `/blast-radius`, `/triage-inbox`, `/respond-to-eval` | Assorted review/triage skills. (inferred) | HR | — | **SKIP mostly** — heavyweight review choreography; downstream's single independent-review gate + `/review` covers the need at personal scale. `/blast-radius` (change-impact) is a maybe. |

### Agents

| Feature | What it does | Native? | Pre-call + reason |
|---|---|---|---|
| `claim-verifier` | Blind forked verifier for `/verify-claims`. (verified) | N5 | **ADAPT** — comes with `/verify-claims`. |
| `humanize-auditor` | Runs the 10-category prose audit. (verified via humanize skill) | HR | **INTEGRATE** — pairs with `/humanize` voice-profile suppression. |
| `domain-referee`, `methods-referee`, `editor` | Blind peer-review + editorial synthesis. (verified names) | HR | **SKIP (already present)** — downstream ships all three. |
| `proofreader`, `r-reviewer`, `sim-reviewer`, `tikz-reviewer`, `slide-auditor`, `quarto-critic`/`quarto-fixer`, `r-package-reviewer`, `pedagogy-reviewer`, `beamer-translator` | Domain-specific critics/fixers. (verified names) | HR/mix | **SKIP most** — teaching/Quarto/R-package critics are out-of-scope; downstream has coder-critic/writer-critic/storyteller-critic/tikz-reviewer equivalents. |

### Rules

| Feature | What it does | Native? | Pre-call + reason |
|---|---|---|---|
| `model-routing.md` | **Effort axis is the primary cost lever** (`low/med/high/xhigh/max`); model tier secondary. 70/20/10 Haiku/Sonnet/Opus split; agent→model set via YAML `model:` frontmatter. **Fable 5 deliberately excluded from the fleet** (premium price; observed structured-output flakiness), reserved for interactive long-horizon user sessions. (verified) | N5 | **INTEGRATE (concept)** — adopt the "effort-first, tier-second, Fable-for-interactive-only" principle as a short reference. Skip per-agent `model:` micromanagement at personal scale (let effort do the work). |
| `writing-with-ai.md` | Splits **readability (fixable by editing)** vs **provenance (needs human rewrite)**; core claim **"a model cannot make its own output stop reading as model output"**; neural detectors (Pangram) read token-level generation statistics, so surface de-AI-ing still scores 100% AI. Internal docs: AI-drafted fine; external-facing: author writes load-bearing prose. Human-readable standard = short rubric. (verified) | HR (conceptual) | **INTEGRATE** — the readability-vs-provenance framing is the single most useful writing idea here; fold into downstream `anti-ai-prose.md`. Concretely reframes why `/humanize` is detection-only. |
| `issue-ledger.md`, `verification-protocol.md`, `post-flight-verification.md`, `inference-robustness.md`, `single-source-of-truth.md`, `replication-protocol.md`, `stata-/r-code-conventions.md`, `confidential-data.md` | Verification/convention rules. (verified names) | HR | **SKIP (already present or equivalent)** — downstream has adversarial-default/verification-ledger, SSOT, replication-protocol, code conventions, confidential-data equivalents. |
| Teaching/Quarto rules: `beamer-quarto-sync`, `no-pause-beamer`, `summary-parity`, `knowledge-base-template`, `tikz-measurement/-prevention/-visual-quality`, `r-package-conventions`, `simulation-conventions` | Pedagogy/Quarto/sim conventions. (verified names) | HR | **SKIP** — out of scope for personal research template. |
| `orchestrator-protocol.md` / `orchestrator-research.md`, `plan-first-workflow`, `session-logging`, `progress-reports`, `prompt-shaping`, `repo-hygiene` | Process orchestration + logging. (verified names) | HR | **SKIP/keep-lean** — downstream already has workflow/logging rules and pruned process nags; don't re-import ceremony. |

### Hooks

| Feature | What it does | Native? | Pre-call + reason |
|---|---|---|---|
| `git-guardrails.py` | PreToolUse Bash guard: blocks `git reset --hard`, `git clean -f`, `push --force`, `git add -A`, `checkout -- .`, and history ops on a dirty tree (reads live `git status`); warns on hardcoded machine paths. (verified) | HR | **SKIP (overlap)** — downstream's `destructive-action-guard.py` already covers this class; the dirty-tree check is a nice-to-have to fold in, not a re-import. |
| `root-of-trust-guard.py` | Blocks shell one-liner writes (`>`, `rm`, `mv`, `sed -i`, `git rm`) to `.claude/settings*.json`, `.claude/hooks/`, `.githooks/`, forcing changes through Edit so they show as diffs. Self-describes as a **tripwire, not a true root of trust** (repo-local, mutable, fail-open). (verified) | HR | **SKIP (overlap)** — downstream already has a settings.json write gate (Tier-3 in destructive-actions.md). Consider extending downstream's gate to also cover `.claude/hooks/` if not already. |
| `claim-reconcile.py` | Reconciliation step for `/verify-claims`. (inferred) | mix | **ADAPT** — comes as part of the verify-claims machinery if adopted. |
| `context-monitor.py`, `pre-compact.py`, `post-compact-restore.py`, `log-reminder.py` | Context/compaction/logging **process nags**. (verified names; behavior inferred) | HR | **SKIP (definitively)** — these are exactly the nag class the downstream deliberately pruned (its own `log-reminder.py`, `pre-compact.py` were removed 2026-09-16). Claude-5-native compaction + memory replace them. |
| `notify.sh` | Desktop/terminal notification. (verified name) | HR/OS | **SKIP** — downstream already ported its own cross-platform notify. |

---

## Qualification-ledger / backtest-gate / model-currency discipline (deep dive)

This is the base repo's signature meta-quality machinery, and the most important thing to reason about carefully.

- **`/vaccinate` + `quality_reports/qualification/LEDGER.md`** implement a *checker-qualification* discipline: every automated gate must prove itself by detecting **planted defects** on a copy while staying silent (0 false positives) on a clean control, before it's trusted. Ledger row fields (verified): `Date | Target | Artifact | Defect classes | N | Recall | FPR | Baseline | Verdict`. A gate is **PASS** only if it "detects its named class at the stated threshold" **and** "0/0 on clean control." Governing principle: **"an unqualified check is not weak evidence — it is none."**
- **`scripts/backtest.sh`** runs **10 gates** in one pass (all run regardless of failures): `surface-sync`, `skill-integrity`, `model-versions`, `links`, `spec-conformance`, `staleness`, `repo-hygiene`, `derived-counts`, `ledger-coverage` (ledger↔wired-hooks agree both directions), `hook-battery` (**re-seeds each guard's target failure every run to prove it still fires**). (verified)
- **Model currency:** `model-versions.md` is the SSOT for model IDs; `Last verified: 2026-08-21`, `Expires: 2026-10-20 (60 days)` — the currency gate **fails the build after expiry until re-verified**. (verified)

**Assessment.** The *epistemic core* is excellent and philosophically identical to the downstream's own `adversarial-default` / evidence-gating ("a verdict is only as good as its evidence"). The `hook-battery` idea — a gate that re-proves every guard still fires on a synthetic defect — is the single best piece of the machinery and directly strengthens the downstream's "gates-not-nags" posture (a gate you never test is a nag pretending to be a gate).

But the **full 10-gate battery + LEDGER bureaucracy is lab/maintenance-scale**: `surface-sync`, `derived-counts`, `link-resolution`, `spec-conformance`, `ledger-coverage` exist to keep a large, multi-consumer, heavily-enumerated *template repo* internally consistent as it churns. A strictly-personal template does not have that enumeration surface and should not carry that overhead. The **model-currency expiry gate** is genuinely useful (model IDs rot) but its hard time-bomb ("fails the build on a date") is nag-shaped — make it advisory at personal scale.

**Net:** adopt the *principle* (vaccinate hooks with planted defects; keep a tiny model-versions SSOT), skip the *apparatus* (10-gate battery, surface/derived-count/ledger-coverage gates).

---

## Model routing (Fable/Opus/Sonnet/Haiku)

Verified: **effort level is the primary cost lever, tier is secondary.** 70/20/10 Haiku/Sonnet/Opus across the fleet, set per-agent via YAML `model:`. Mechanical→Haiku (`extract-tikz`, `quarto-fixer`); review→Sonnet (`r-reviewer`, `slide-auditor`, `proofreader`); high-judgment→Opus (`editor`, referees, `claim-verifier`). **Fable 5 is deliberately not in the fleet** — premium pricing above Opus, plus a launch-week (2026-06) structured-output flakiness observation flagged as now-stale/unverified; Fable is reserved for interactive long-horizon user sessions where a human catches errors. For a personal template the durable takeaway is the **principle**, not the 70/20/10 numbers or per-agent pinning.

---

## Voice-handling finding (the headline)

The base treats "voice" and "AI-tells" as **two separate, complementary mechanisms**, and this is the most transferable design in the repo:

1. **`/voice-profile` represents a voice as a FEATURE LIST, not exemplars and not a scoring rubric.** Six fixed categories — **Lexicon, Rhythm, Openings, Transitions, Hedging, Quirks** — each populated with observed patterns (e.g., Lexicon = "words used repeatedly; words conspicuously avoided"; Rhythm = "typical sentence length; variance; where long sentences appear"). Built by forking one subagent per paper (each reads only its file, emits a ~300-word note); the main session synthesizes only the notes into `voice-profile.md`. A trait qualifies only if it appears across **most** of the corpus. The skill itself invokes no model (`disable-model-invocation: true`) — it's pure orchestration + synthesis. It has an `--audit` mode to score a draft against the profile.
2. **`/humanize` is a separate, read-only 10-category AI-tell detector** that **reads `voice-profile.md` to suppress the author's documented habits as false positives.** No auto-rewrite by design.
3. **`writing-with-ai.md` supplies the theory**: readability (editable) vs provenance (a model cannot self-edit its way past a neural detector like Pangram). So `/humanize` is honestly scoped as a *readability/tell* check, never a "make it pass as human" tool.

For a personal econ template this is close to ideal: single-author, so a `voice-profile.md` is cheap and durable; the feature-list format is auditable and portable; humanize-respects-profile removes the biggest annoyance (getting flagged for your own real style). Downstream already has `/humanize` + `anti-ai-prose.md` — the gap is the **voice-profile.md artifact and the humanize→profile suppression link**.

---

## Most worth adopting (ranked)

1. **`/verify-claims` + `claim-verifier` (forked blind CoVe)** — real fabrication gate, Claude-5-native, matches downstream fabrication-gate philosophy. ADAPT.
2. **`/voice-profile` (6-category feature-list voice signature) + humanize suppression link** — the standout voice mechanism; perfect at personal single-author scale. ADAPT.
3. **`writing-with-ai` readability-vs-provenance framing** — fold into `anti-ai-prose.md`; honestly scopes what humanizing can and can't do. INTEGRATE.
4. **`/vaccinate` planted-defect principle + `hook-battery` idea** — prove each gate still fires; strengthens gates-not-nags without importing the full ledger. ADAPT (concept only).
5. **`model-routing` effort-first principle + a tiny `model-versions` SSOT** — lightweight, durable; skip 70/20/10 pinning and the hard expiry time-bomb. INTEGRATE (lean).

## Definitely skip for a personal template

- **Process-nag hooks:** `context-monitor.py`, `pre-compact.py`, `post-compact-restore.py`, `log-reminder.py`, `notify.sh` — the exact nag class the downstream already pruned; Claude-5 compaction/memory replace them.
- **Full `backtest.sh` 10-gate battery + LEDGER bureaucracy** (`surface-sync`, `derived-counts`, `link-resolution`, `spec-conformance`, `ledger-coverage`) — lab/multi-consumer-scale repo-consistency machinery; no enumeration surface to justify it here. Keep only the `hook-battery` idea.
- **Duplicate guards:** `git-guardrails.py`, `root-of-trust-guard.py` — overlap downstream's `destructive-action-guard.py` + settings write gate; don't double up (optionally fold in the dirty-tree check and the `.claude/hooks/` write coverage).
- **Teaching / Quarto stack:** `/create-lecture`, `/syllabus`, `/scaffold-exercises`, `/teach-from-paper`, `/pedagogy-review`, `/qa-quarto`, `/translate-to-quarto`, `beamer-quarto-sync`, `no-pause-beamer`, `summary-parity`, and their critics — Pedro teaches; a personal research template doesn't.
- **Lab-ceremony skills:** `/promote-memory` + `promote-memory-council`, `/deploy`, and the heavy review choreography (`/seven-pass-review`, `/oracle-review`, `/adjudicate-review`, `/differential-audit`) — multi-agent ceremony beyond single-author scale; downstream's one independent-review gate + `/review` suffices.

---

## Caveats on evidence

Directory listings and the deep-dive files above are **verified from page** (contents API + raw files). Items marked **(inferred)** are characterized from skill name + repo convention only and were not opened. Version **v2.5.1** and the fleet-extender/fork-count claims from the initial README summary are **unverified** (the summarizer model may have fabricated them; the fork-count and named-extenders in particular smelled hallucinated and are excluded from findings). The base's model IDs (Opus 5 / Fable 5 / Sonnet 5) are its own SSOT as of 2026-08-21 and may diverge from this harness (Opus 4.8) — do not copy IDs without checking.
