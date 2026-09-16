<!-- primary-source-ok: santanna_2026, korinek_2025, kohler_zollikofer_einsiedler_hoyle_ash_2026 -->
# Modernize-and-simplify plan — personal research template for Claude 5

**Status:** DRAFT v2 (review-clean) — revised after two independent reviews (`quality_reports/reviews/2026-09-16_modernize-plan_independent_review.md` → FIT WITH CHANGES; `..._modernize-plan-v2_independent_review.md` → READY WITH MINOR CHANGES, all five v1 findings verified resolved). The v2 review's three fixes are folded in: `stop_hooks_lib` deletion corrected, Track-A step 4 (live-project update) given a safe mechanism, `notify.py` fail-open + `python3` launcher fallback. Awaiting approval.
**Basis:** survey brief `quality_reports/reviews/2026-09-16_ai-econ-workflow-landscape-and-direction.md`

## What the review changed (v1 → v2)

The review found the real payoff is **removal**, and that three v1 items were bloat fighting the plan's own goal. Fixed here:
- **Split into two tracks.** Track A is pure simplification (delete nags + retire lab automation) and is what we do now. Track B (re-platform, Plugin, ledger→schema) is optional, deferred, each its own decision. A simplify plan should not contain the biggest build.
- **Do NOT swap the citation gate's regex for a model-call subagent.** `primary-source-check.py` is a *blocking* PreToolUse hook (verified). A model call there adds latency and a network dependency and fails open — it would weaken the one gate the plan says never to weaken. Keep it deterministic and offline, as-is.
- **Do NOT retire the evidence-gate recorder / verification ledger in the simplify track.** The ledger is wired into three critic agents (`coder-critic`, `verifier`, `writer-critic`) plus `adversarial-default.md`, `no-assumptions.md`, and a reference doc (verified). Retiring it is a large rewrite; it belongs in Track B, only if the Workflow re-platform happens.
- **Shared libs are handled explicitly.** `derive_lib.py` is shared by the KEPT advisory hook and the PRUNED block hook (verified) — it stays. `normdiff_lib.py` / `citation_existence_lib.py` are schema machinery — they stay. Only libs/tests used *solely* by a pruned hook get deleted.
- **The dangling-reference gate is now a grep sweep, not a hand-list.** Hand-listing the rules to edit was provably incomplete.

## Scope and context

Strictly personal template (owner changed jobs, moved abroad). Two live projects, **both behavioral**: `bdm_bic` and `belief_distortion_discrimination`. The applied-micro consumer `tx_peer_effects_local` is **dormant** (TERC data access lost); four other consumers dormant. **Live surface:** `main` + the **behavioral** overlay. **Applied-micro overlay:** keep content, freeze. Cross-platform requirement: runs on a **Windows work machine and a Mac personal machine**.

## Principle: gates vs nags

Keep hard enforcement only where the failure mode does not improve with a smarter model — **fabrication** and **irreversibility**. Process-discipline policing (logging, plan persistence, output length, unverified-claim nagging) is now covered by Claude 5's instruction-following and native memory/compaction, so it is pruned.

## Principle: cross-platform (Windows + Mac)

Every kept hook must run on both machines. Python-first; no `bash`/`jq`/`osascript`-only idioms; branch on `platform.system()` at runtime for OS-specific actions (notifications), not a manual toggle. The two shell hooks (`notify.sh`, `protect-files.sh`) are the only non-portable hook surface and both become Python. **`notify.py` must fail open** — if the native notifier is missing or errors (no `BurntToast`, headless, etc.), degrade to a console line or no-op; a notification must never break a turn. Hook launcher lines use `python3`; keep a `python`/`py` fallback so a machine without a `python3` alias still runs them. (Skills and the LaTeX toolchain use POSIX/bash idioms; those run under Git Bash on Windows, and a repo grep found no `jq` in skills — so skills are a lower-priority, separate portability check, not part of this pass.)

## Hooks — the decisions (19 active)

| Hook | Call | Note |
|---|---|---|
| `destructive-action-guard.py` | **KEEP** | irreversibility gate |
| `post-rewrite-verify.py` | **KEEP** | verify after history rewrite (pairs with the above) |
| `primary-source-check.py` (PreToolUse) | **KEEP as-is** | the citation gate; deterministic + offline + blocking — do **not** put a model call in it |
| `primary-source-audit.py` (Stop) | **KEEP** | leave as-is this pass; any lightening is Track B |
| `derive-check-advisory.py` | **KEEP** | cheap path-resolvability advisory; **owns nothing to delete** — shares `derive_lib.py` |
| `stata-comment-balance-check.py` | **KEEP** | Tier-1 deterministic; real Stata footgun |
| `evidence-gate-recorder.py` | **KEEP this pass** | retiring the ledger touches 3 critics + 2 rules → Track B only |
| `protect-files.sh` → `protect-files.py` | **KEEP, port to Python** | settings-protection gate; drop `jq`/bash |
| `notify.sh` → `notify.py` | **KEEP, port to Python** | notifications wanted; runtime OS detection (`osascript` on macOS, PowerShell toast on Windows), stdin JSON via `json`, no `jq` |
| `derive-check-block.py` | **PRUNE** | opt-in blocker, currently inert (`.enabled` flag); keep `derive_lib.py` (shared) |
| `diagnostic-claim-audit.py` | **PRUNE** | nag |
| `plan-persist-check.py` | **PRUNE** | nag |
| `log-reminder.py` | **PRUNE** | nag (fired this session as a live example) |
| `output-length-check.py` | **PRUNE** | nag |
| `verify-reminder.py` | **PRUNE** | verification is habitual now; demote to rule text |
| `context-monitor.py` | **PRUNE** | native compaction replaces it |
| `pre-compact.py` | **PRUNE** | native compaction handles it |
| `post-compact-restore.py` | **PRUNE** | native compaction + memory handles restore |
| `session-reset.py` | **REVIEW then likely PRUNE** | read it first; confirm nothing load-bearing |

Net: keep ~9 (2 of them ported to Python), prune ~10 (including `session-reset.py` pending its read). **Lib/test rule:** delete a `*_lib.py`/`test_*` only after `grep` confirms no KEPT hook imports it. Stay (used by kept hooks): `derive_lib`, `normdiff_lib`, `citation_existence_lib`, `primary_source_lib`. **Delete: `stop_hooks_lib.py` + `test_stop_hooks_lib.py`** — grep-verified that its only importers are the three pruned Stop hooks (`plan-persist-check`, `output-length-check`, `diagnostic-claim-audit`); the kept `primary-source-audit` does not use it.

## Rules, agents, skills

- **Rules — keep as guidance.** After pruning hooks, the gate is a **grep sweep**: `grep -rl <hook-name>` across `.claude/` and docs, and remove/rewire every reference (the enforcement paragraphs in whatever rules mention each pruned hook — found by grep, not guessed).
- **Agents — untouched this pass.** The orchestrator + critic re-platform is Track B.
- **Skills — retire only the `/tools` lab subcommands** (`propagate`, `sync-overlays`, `list-consumers`) in Track A step 5. Everything else untouched.

## Track A — simplify now (removal; the real payoff)

1. **Prune the nag hooks** on `main`. For each PRUNE hook: `grep -r` the whole repo for its name, remove/rewire every reference (settings.json entry, rule enforcement paragraphs, other hooks), then delete the script and any lib/test used *only* by it. **Gate = the grep sweep returns zero references to any removed hook**, and a full Claude Code tool cycle survives. (Review `session-reset.py` before deciding.)
2. **Cross-platform the two kept shell hooks:** `protect-files.sh` → `protect-files.py`, `notify.sh` → `notify.py` (runtime OS detection). **Gate:** both run on Windows and Mac; settings-protection still blocks; a notification fires on each OS.
3. **Mirror steps 1–2 onto the behavioral overlay** (hand-merge `main` → behavioral). **Gate:** behavioral hooks load; tool cycle survives.
4. **One-time update of the two live projects** (`bdm_bic`, `belief_distortion_discrimination`) — the only step touching live work, so it is spelled out:
   - In each live repo first: commit any WIP, then tag a restore point (`git tag pre-simplify-2026-09` and/or a branch) so the change is trivially reversible.
   - Apply as a **file-level replacement of the changed `.claude/` files only** (the pruned hooks removed, the ported `notify.py`/`protect-files.py` and slimmed `settings.json` copied in) — **not** a blind clobber of the whole repo; the project's own content and any local `.claude` customizations are preserved.
   - Run the **grep sweep inside each live repo** to catch references to removed hooks (the project's own rules/docs may mention them), and rewire/remove.
   - **Gate:** restore point tagged; in-repo grep sweep returns zero references to removed hooks; a Claude Code tool cycle survives; the project's own tests/analysis still run.
5. **Retire the propagation + overlay-sync automation** and the `/tools` lab subcommands; leave applied-micro and the dormant consumers frozen.

Steps 1–2 are low-risk and independent. Step 4 is the only one touching live projects — most care there.

## Track B — modernize later (optional; each its own decision, only if a real need appears)

- **B1 — method-specification completeness check** (grounded in the reproduction study). Cheapest "add"; consider first if you want anything from this track.
- **B2 — package as a Plugin.** Only if you actually distribute the template.
- **B3 — re-platform orchestrator + critics onto a JS Workflow** with schema-validated evidence, retiring the recorder + ledger. Large rewrite (3 critics + 2 rules + refs); do only if ledger/critic maintenance actually bites. Not now.

Explicitly **not** in scope: swapping the citation gate to a model call; model cost-tiering (a Track-B nicety, not a simplification).

## Cautions

- Keep the citation gate and safety hooks regardless of model; fabrication and destructive commands don't improve with intelligence.
- Hooks are currently **live** on `main` (the log-reminder fired), so pruning takes effect immediately — verify a clean tool cycle after step 1.
- Subagent forking + background-by-default break rules assuming serial dispatch — only relevant if Track B (B3) is ever done.
