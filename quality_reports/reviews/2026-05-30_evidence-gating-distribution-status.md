# Evidence-Gating Distribution (Phase 5) — Status & Findings

**Date:** 2026-05-30
**Action:** merge → main, push, propagate Class A to 7 consumers + full hook suite.
**Status:** Class A distribution DONE + verified consistent. Two findings (one fixed, one needs a decision). Class B (overlays + consumer workflow.md/CLAUDE.md) pending.

---

## Done

- **Merged** `design/evidence-gating-discipline` → `main` (`b675e83`), **pushed** to origin (`4a78160..b675e83`).
- **Propagated Class A to all 7 consumers** (evidence-gating files: 105 copies; then full hook suite: 70 copies). Per-consumer commits; consumer remotes NOT pushed (left to user).
- **Verified consistent:** all 7 consumers — every `settings.json`-referenced hook (19) + all 5 shared libs resolve; **0 dangling refs**. Tests pass in-consumer (36/36 normdiff, 24/24 citation). Recorder is self-contained (loads `normdiff_lib`, not `derive_lib`), so it functions even where `derive_lib` was absent.

## Finding 1 — FIXED: dangling hook refs from the 2026-05-28 enforcement wave

Propagating main's `settings.json` (which registers the full hook suite) initially created dangling references in every consumer: the 2026-05-28 enforcement hooks (`derive-check-advisory/block`, `diagnostic-claim-audit`, `output-length-check`, `plan-persist-check`) and their libs (`derive_lib`, `stop_hooks_lib`) had **never been propagated to consumers**. A `settings.json` that registers a hook whose `.py` is absent = a broken reference. **Fixed** by propagating the complete `.claude/hooks/*.py *.sh` set (70 copies); re-verified all refs resolve and the previously-missing hooks load without ImportError. Lesson: settings.json and the hook files it registers must propagate together.

## Finding 2 — NEEDS DECISION: recorder path-scope is template-default, doesn't match real consumer layouts

`evidence-gate-recorder.py` hardcodes `RESEARCH_ROOTS = (paper/, talks/, scripts/, replication/, figures/, tables/, preambles/)`. But consumers have heterogeneous layouts:

- `tx_peer_effects_local` keeps Stata code in **`do/`** (the incident files were `do/code_fix/main_do/*.do`). `_in_scope("do/.../7G_Regressions.do") → False` — **the recorder is inert on the very files the discipline was built to protect.** (Its `figures/`, `tables/` ARE in scope, but those are outputs, not the analysis code.)

A hardcoded scope inside a **Class A (universal)** hook is the wrong place for a per-repo fact: a consumer can't edit it without the next `/tools propagate` overwriting the change.

**Options:**

1. **Make scope repo-configurable (recommended).** Read `RESEARCH_ROOTS` from a non-propagated per-repo config (e.g. a key in `.claude/settings.local.json` or a `.claude/state/` file), falling back to the hardcoded default. Propagation never clobbers it. Small Phase-1 refinement; best fit for heterogeneous consumers. Worth building with the same adversarial-review workflow.
2. **Broaden the default roots** to include common layouts (`do/`, `code/`, `src/`, `analysis/`). Quick, but still one-size; a repo with an unusual layout still misses, and over-broad roots risk recording non-artifact dirs.
3. **Per-repo edit + accept re-propagation friction.** Edit each consumer's constant; document that propagation overwrites it. Fragile — not recommended.

Recommendation: **Option 1** (configurable, default-fallback), optionally plus a modest default broadening (`do/`). Until then, the recorder is live but only fires on the template-standard roots — fine for repos using `scripts/`, inert for `do/`-layout repos like tx.

## Pending — Class B (manual, advisory)

The Phase-4 operationalization-gate edit lives in Class B files that propagation does NOT route from main:

- `.claude/rules/workflow.md` §1 (Step-0 operationalization) and the `CLAUDE.md` evidence-gating bullet must be hand-applied to the `applied-micro` + `behavioral` overlay branches (and, if wanted, to consumers' own workflow.md/CLAUDE.md).
- This is advisory (Phase 4) — not required to exercise the core recorder + gate + Tier-2. Defer-able.

## Bottom line

The core discipline (Tier-1 recorder + Tier-2 citation check + the gate + all enforcement hooks) is **distributed and consistent across all 7 working repos** and testable now — *with the caveat that the recorder only fires on the template-standard research roots*. For `do/`-layout repos (incl. tx), Finding 2 must be resolved first for the recorder to actually record. Class B (advisory operationalization gate) remains a manual follow-up.
