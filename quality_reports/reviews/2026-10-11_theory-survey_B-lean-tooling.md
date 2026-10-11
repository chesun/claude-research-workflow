# Theory survey B — Lean tooling, Windows, and Claude integration
**Date:** 2026-10-11
**Reviewer:** survey agent B (general-purpose, opus)
**Target:** Lean 4 toolchain + agent integration on Windows
**Status:** Active

Scope: installing Lean 4 + Mathlib on this Windows 11 work laptop, the OneDrive problem, Claude-to-Lean integration tools, auxiliary AI provers, evidence on Claude's Lean ability, and a deterministic PASS/FAIL check recipe. Nothing was installed or run except a read-only environment probe (listed in section 7). Every claim carries a URL; confidence is marked where the evidence is thin. Dates are given ISO-style.

---

## 1. Bottom line

- **Install is routine on Windows.** The official route is the `elan-init.ps1` installer plus the VS Code `lean4` extension; a Mathlib project is created with `lake +leanprover-community/mathlib4:lean-toolchain new <name> math`, then `lake exe cache get` downloads prebuilt `.olean` files. Mathlib master currently pins `leanprover/lean4:v4.35.0-rc4`. ([manual install](https://lean-lang.org/install/manual/), [Mathlib-as-dependency wiki](https://github.com/leanprover-community/mathlib4/wiki/Using-mathlib4-as-a-dependency), [lean-toolchain](https://raw.githubusercontent.com/leanprover-community/mathlib4/master/lean-toolchain))
- **Budget about 6-8 GB of disk per project plus about 1 GB per toolchain.** Mathlib has about 8,000 Lean files, and every project keeps its own copy under `.lake/`. This laptop has 336 GB free, so space is not the constraint. ([lean4 #4630](https://github.com/leanprover/lean4/issues/4630), [lean4 #13504](https://github.com/leanprover/lean4/issues/13504), [example project README](https://github.com/Dytchem/robust-z-lower-bound-lean) via search snippet)
- **Do not put the Lean project inside OneDrive.** The `.lake/` tree runs to tens of thousands of files, and Microsoft advises keeping a whole sync account under 300,000 items. Windows file locking (OS error 32) already conflicts with Lean's own concurrent reads. Lean maintainers list cloud-sync folders and corporate antivirus as standard suspects when Windows performance is bad. Junctions do not exclude a folder from sync. **Recommendation:** keep the Lean project at a short local path outside OneDrive (for example `C:\Users\christina.sun\lean\<project>`), version it with git, and have the research repo point to it. (Evidence in section 3.)
- **Integration:** `lean-lsp-mcp` is the de facto MCP server: MIT licence, v0.31.0 released 2026-09-30, actively fixed for native Windows. It exposes goals, diagnostics, `lean_verify` (reports axioms), local search and several hosted search engines. Pair it with the `lean4-skills` Claude Code plugin (MIT, commits as recent as 2026-09-29), which is CI-tested on Linux and macOS only. ([lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp), [tools.md](https://github.com/oOo0oOo/lean-lsp-mcp/blob/main/docs/tools.md), [lean4-skills](https://github.com/cameronfreer/lean4-skills))
- **Current Claude models are strong at Lean.** On Vals ProofBench (advanced undergraduate and graduate Lean 4, 40 tool turns), Opus 5.5, Sonnet 5.5 and Fable 5.1 all score 100%, as of 2026-10-07. Anthropic reports agents on a model "roughly comparable to Claude Fable 5.1" formalized Fermat's Last Theorem end to end, using only the three standard axioms. Known failure modes remain: hallucinated or renamed Mathlib lemmas, leftover `sorry`, and proofs that slip `sorryAx` past naive scans. ([ProofBench](https://www.vals.ai/benchmarks/proof_bench), [Anthropic FLT post](https://www.anthropic.com/research/formalizing-fermats-last-theorem), [ring-theorem blog](https://www.johndcook.com/blog/2026/06/17/rings-with-lean-claude/), [reward-hacking audit paper](https://arxiv.org/abs/2608.28639))
- **The economist's audit is the binding risk.** A compiled proof says nothing about whether the Lean statement means what the economist intends. The Lean reference manual and the Tao-blog guest post both put human statement auditing first. ([Validating Proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/), [Tao blog](https://terrytao.wordpress.com/2026/10/09/what-mathematicians-should-know-about-the-lean-theorem-proverquestions-of-reliability-and-ai))
- **Deterministic check:** a Python script can produce PASS/FAIL with five steps:
  1. hash-lock the audited statement file;
  2. scan proof files for forbidden tokens;
  3. run `lake build --wfail`;
  4. run `#print axioms` on a check file that re-proves each audited statement, and require the result to be a subset of `{propext, Classical.choice, Quot.sound}`;
  5. optionally run `lake env leanchecker`, which ships in every toolchain since v4.28.0.

  The recipe is in section 6.
- **External AI provers are optional.** Harmonic's Aristotle is free and has a Python SDK, but its terms let it train on submitted Lean files unless you opt out in advance. Open-weight provers (Goedel-Prover-V2, DeepSeek-Prover-V2, Kimina) need GPUs and are weaker than Claude-in-the-loop on research-style lemmas. Neither is needed to start.

---

## 2. Install and setup findings (Windows)

| Item | Finding | Source |
|---|---|---|
| Official Windows install | Install VS Code (tick "Add to PATH"), check `git --version` and `curl --version`, then `curl -O --location https://elan.lean-lang.org/elan-init.ps1` and `powershell -ExecutionPolicy Bypass -f elan-init.ps1` (option 1), then the VS Code extension `lean4` by leanprover. | https://lean-lang.org/install/manual/ |
| New Mathlib project | `lake +leanprover-community/mathlib4:lean-toolchain new <name> math` initializes a git repo with Mathlib as a dependency. Then run `lake exe cache get`, which should report decompressing about 5,000+ files. Needs elan 2.0.0 or later. | https://github.com/leanprover-community/mathlib4/wiki/Using-mathlib4-as-a-dependency |
| Updating | Copy Mathlib's `lean-toolchain` with `curl ... -o lean-toolchain`, run `lake update`, then rebuild. Use tagged releases if far behind. | same wiki; https://leanprover-community.github.io/install/project.html |
| Current versions | Mathlib master toolchain is `v4.35.0-rc4`. elan major version is 4.x (LeanInteract requires elan 4.0.0 or later). The GitHub releases page rendered stale data, so the exact latest elan version is unverified. | https://raw.githubusercontent.com/leanprover-community/mathlib4/master/lean-toolchain, https://pypi.org/project/lean-interact/, https://github.com/leanprover/elan/releases |
| Where files live | Per project: `.lake/` holds packages and build output. Toolchains go in `~/.elan/toolchains`. The Mathlib download cache is `MATHLIB_CACHE_DIR`, else `$XDG_CACHE_HOME/mathlib`, else on Windows `HOMEDRIVE+HOMEPATH\.cache\mathlib`. On this machine that resolves to `C:\Users\christina.sun\.cache\mathlib`, which is local, not OneDrive. | https://leanprover-community.github.io/install/project.html, https://raw.githubusercontent.com/leanprover-community/mathlib4/master/Cache/IO.lean |
| Disk size | Toolchain about 1 GB and Mathlib build about 4 GB+ (lean4 #4630). A Lean 4.34 install grew a Docker image from 3.6 to 7.7 GB (comment dated 2026-09-19 in the same issue). One project README cites about 6.4 GB on disk for Mathlib sources and oleans. **Confidence: medium**; the size grows with each Mathlib release. | https://github.com/leanprover/lean4/issues/4630, https://github.com/Dytchem/robust-z-lower-bound-lean (figure from search snippet) |
| File count | Mathlib has about 8,000 Lean files. Lake does a full (not shallow) clone per project. Each module yields several build artefacts (`.olean`, `.ilean`, trace and hash files), so `.lake/` holds tens of thousands of files. **The per-module artefact count is inferred, not measured.** | https://github.com/leanprover/lean4/issues/13504 |
| Build time | With `cache get`, setup takes minutes: one report measured decompression at about 106 s on a slow external disk. Without the cache, Mathlib compiles from source, which takes hours. **The no-cache time is unverified for this hardware.** | https://leanprover-community.github.io/archive/stream/270676-lean4/topic/lake.20exe.20cache.20get.20slow.html |
| Antivirus | Unpacking took 41 s, or 9 s with the destination excluded from AV scanning. Antivirus can also break `cache get` with `curl: (35) schannel: next InitializeSecurityContext failed`; the fix is to retry `lake exe cache get!`. On an enterprise machine an AV exclusion needs IT. | same Zulip thread; https://leanprover-community.github.io/install/project.html |
| Line endings | With git set to check out Windows-style CRLF, the Mathlib cache stopped matching. The fix reported was `git config --global core.autocrlf input` plus a fresh clone. A maintainer said the cache should normalise line endings, and the reports are mixed. **This machine has `core.autocrlf=true`**, so set `core.autocrlf input` (or a `.gitattributes` with `* text eol=lf`) for the Lean repo. | https://leanprover-community.github.io/archive/stream/270676-lean4/topic/Lake.20on.20Windows.html |
| File locking | A maintainer on Zulip: "windows really doesn't like concurrent modification of files that are being read". This gives OS error 32 when the language server and `cache get` run at once. Close VS Code or stop the Lean server before running `cache get`. | same thread |
| Long paths | The old Lake failure on Windows (command line over 32,767 chars) was fixed 2025-03-20 with response files. It affected linking executables, not proof projects. On this machine `LongPathsEnabled=1` is already set and git `core.longpaths` is unset; set `git config --global core.longpaths true` as a precaution. | https://github.com/leanprover/lean4/issues/4159, https://pypi.org/project/lean-interact/ |
| Corrupted toolchain | If you see `uncaught exception: no such file or directory (error code: 2)`, delete the toolchain under `%USERPROFILE%\.elan\toolchains` and its `update-hashes` entry. | https://leanprover-community.github.io/install/project.html |
| Open the folder | Always open the folder that contains the lakefile in VS Code, not single files. If something goes wrong, run `lake clean` or delete `.lake`, then `cache get` again. | https://leanprover-community.github.io/archive/stream/270676-lean4/topic/help.20with.20lake.20new.html |

---

## 3. OneDrive finding

**Verdict: keep the Lean project outside OneDrive. Confidence: high on the direction, medium on the exact failure modes.** No Lean-specific OneDrive post-mortem was found.

Evidence:
1. **Item count.** Microsoft: "For optimum performance, we recommend syncing no more than a total of 300,000 items across your cloud storage." One Mathlib project's `.lake/` adds roughly 8,000 source files plus several build artefacts per module, and every extra project or Mathlib bump adds more. ([MS limits](https://support.microsoft.com/en-us/office/restrictions-and-limitations-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa), [lean4 #13504](https://github.com/leanprover/lean4/issues/13504))
2. **Churn and locking.** `lake exe cache get`, `lake update` and every build rewrite thousands of binary files. OneDrive opens each changed file to hash and upload it, while Windows already produces OS error 32 when Lean files are read and written concurrently. Expect slow builds, "file in use" errors, sync backlogs, and on a multi-device account possibly conflict copies of `.olean` files. **The specific OneDrive-plus-Lean failure is inferred, not observed.** ([Lake on Windows thread](https://leanprover-community.github.io/archive/stream/270676-lean4/topic/Lake.20on.20Windows.html))
3. **Lean maintainers' triage list.** When Windows users report performance or memory problems, maintainers ask "are you using storage in the cloud such as Dropbox, OneDrive etc." and "what anti-virus / corporate spyware if any do you have" (Zulip, 2026-01-27). ([Issues on windows for new users](https://leanprover-community.github.io/archive/stream/113488-general/topic/Issues.20on.20windows.20for.20new.20users.html))
4. **Files On-Demand.** Synced files become reparse-point placeholders. A corrupted placeholder can make a folder unreadable and block sync. A build tree is the worst case for this. ([MS reparse-point article](https://learn.microsoft.com/en-us/troubleshoot/sharepoint/sync/delete-onedrive-synced-file-error))
5. **Junctions are not a fix.** Microsoft lists symbolic links and junctions as unsupported for sync. Q&A answers disagree on whether a junction inside OneDrive that points outside gets followed. Do not rely on a junction to exclude `.lake`. ([MS limits](https://support.microsoft.com/en-us/office/restrictions-and-limitations-in-onedrive-and-sharepoint-64883a5d-228e-48f5-b3d2-eb39e07630fa), [MS Q&A](https://learn.microsoft.com/en-us/answers/questions/1327239/onedrive-shortcuts-symlinks-and-junctions))
6. **No user-level folder exclusion.** OneDrive for Business has no per-user "ignore this folder" setting. File-type exclusion is an admin policy. **The policy specifics are unverified.**

Workaround options, in order of preference:
- **A (recommended):** put the Lean project at `C:\Users\christina.sun\lean\<project>`. That is local, short, and outside both the OneDrive root and the redirected Documents folder. Version it with git and push to the enterprise remote. The research repo in OneDrive references it by relative note or a path in config; it should not be a submodule checked out inside OneDrive. Toolchains and the Mathlib cache are already outside OneDrive (section 2).
- **B:** keep only the `.lean` sources, which are small, in the OneDrive repo, and point the build somewhere else. Lake supports `packagesDir` (default `.lake/packages`) and `buildDir` (default `.lake/build`) config fields. **Whether these accept an absolute path outside the project, and whether the VS Code extension and the cache tolerate it, is unverified.** Treat B as an experiment, not a default. ([Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/))
- **C (avoid):** a junction for `.lake`, for the reasons in item 5.

---

## 4. Integration tools

| Tool | What | Maturity | Windows? | Licence | URL |
|---|---|---|---|---|---|
| **lean-lsp-mcp** | MCP server over the Lean LSP (via `leanclient`). About 22 tools: `lean_goal`, `lean_diagnostic_messages`, `lean_multi_attempt`, `lean_run_code`, `lean_verify` ("returns axioms used + optional source pattern scan"), `lean_local_search` (needs ripgrep), `lean_build` (runs `lake build`, optionally fetches the cache), and hosted search (`lean_leansearch`, `lean_loogle`, `lean_leanfinder`, `lean_hammer_premise`), which shares a limit of 3 requests per 30 s. Install with `claude mcp add lean-lsp -s project uvx lean-lsp-mcp`. Run `lake build` before starting it to avoid timeouts. | High. 527 stars, 690+ commits; v0.31.0 released 2026-09-30; used by agentic-prover papers. | Native Windows fixes merged throughout 2026 (encoding, path separators, `lean_verify` UTF-8 loading, `lean_profile_proof` crash, 2026-08-19). README documents WSL2 config. Native use is plausible; **not tested here**. Claude Code docs say stdio servers on Windows may need a `cmd /c` wrapper. | MIT | https://github.com/oOo0oOo/lean-lsp-mcp, https://github.com/oOo0oOo/lean-lsp-mcp/blob/main/docs/tools.md, https://pypi.org/pypi/lean-lsp-mcp/json, https://github.com/oOo0oOo/lean-lsp-mcp/issues?q=windows, https://code.claude.com/docs/en/mcp |
| **lean4-skills** (Claude Code plugin) | Workflow pack: `/lean4:prove`, `autoprove`, `formalize`, `review`, `checkpoint` (includes axiom checking), `golf`, plus guardrail hooks. Install with `/plugin marketplace add cameronfreer/lean4-skills` then `/plugin install lean4`. | High. 462 stars; v4.11.x; commits on 2026-09-28/29. | **CI is Linux and macOS Bash only.** Its Bash guardrail hooks may not run under PowerShell, and Git Bash is untested. | MIT | https://github.com/cameronfreer/lean4-skills |
| mathlib-quality (plugin) | Clean-up, golfing and Mathlib-style workflows (`/cleanup`, `/buzz`). | Medium. 35 stars. | Not stated | MIT | https://github.com/CBirkbeck/mathlib-quality |
| LeanExplore | Semantic search over Lean declarations. Hosted MCP (no key, 30 requests per 60 s per IP) and a Claude Code plugin; a local backend is available via `pip install lean-explore[local]`. | Medium. 81 stars. | Not stated (Python) | Apache-2.0 | https://github.com/justincasher/lean-explore |
| Loogle | Type- and name-pattern search over Mathlib, with a `/json?q=` endpoint (format "not guaranteed"). Can be built locally against your toolchain. | High; the hosted index refreshes about every 6 h. Reachable from this network on 2026-10-11. | Hosted: yes. Local build on Windows unverified. | Apache-2.0 | https://github.com/nomeata/loogle, https://loogle.lean-lang.org |
| LeanSearch | Natural-language Mathlib search (PKU BICMR). The site says it **collects search data**. | High (widely used); reachable 2026-10-11. | Hosted | not checked | https://leansearch.net |
| Lean Finder | Semantic search API, no key, 100 requests per 60 s. Index versions offered go up to **v4.28.0**, which lags Mathlib master (v4.35). | Medium; scales to zero when idle (503 on cold start). | Hosted | not checked | https://delta-lab-ai-lean-finder.hf.space/api-docs |
| Moogle | Older natural-language search, still referenced by LeanSearchClient. **Current status unverified.** | Low / unknown | Hosted | n/a | https://florisvandoorn.com/carleson/docs/LeanSearchClient/Syntax.html |
| LeanInteract | Python wrapper for the Lean REPL, for scripted checking. v0.11.5 released 2026-07-16; needs Python 3.10+ and elan 4+. | Medium | Documents the Windows long-path setup | MIT | https://pypi.org/project/lean-interact/ |
| `leanchecker` (formerly lean4checker) | Replays `.olean` declarations through the kernel. Built into every toolchain since v4.28.0: run `lake env leanchecker [Module]`, or `--fresh` to replay into a fresh environment (slow, single-threaded). | High (official) | Ships with the Windows toolchain; **Windows run untested** | Apache-2.0 | https://github.com/leanprover/lean4checker |
| comparator | "Gold standard" judge. Checks a Solution module against a Challenge module, enforces `permitted_axioms`, replays in the kernel, and supports external kernels (nanoda). | High (official) | **No.** Needs `landrun`, which is Linux-only; would need WSL. | Apache-2.0 | https://github.com/leanprover/comparator |

**Which check to use when.**
- *LSP diagnostics* (via MCP or VS Code) are the fast inner loop.
- *`lake lean <file>`* builds a file's imports and runs `lean` on it in Lake's environment. Use it for one-off check files.
- *`lake build --wfail`* is the authoritative gate. Plain `lake build` succeeds with only a warning when a proof uses `sorry`. `--wfail` "causes builds to fail if any warnings are logged". `--no-build` exits non-zero if anything is stale.

([Lake reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Lake/), [lean4 #4159](https://github.com/leanprover/lean4/issues/4159))

**Cheating constructs.** The reference manual's ladder:
1. Blue check marks in the editor.
2. `#print axioms`: only `propext`, `Classical.choice` and `Quot.sound` are acceptable. `sorryAx`, any custom axiom, and any axiom ending in `_native` are failures. Since v4.29.0, native computation (for example `native_decide`) adds a dedicated `_native` axiom.
3. `leanchecker`.
4. comparator.

The manual also flags `debug.skipKernelTC`, `implemented_by`/`extern`, custom notation and elaborator tricks as ways to circumvent checking. ([Validating Proofs](https://lean-lang.org/doc/reference/latest/ValidatingProofs/), [4.35.0-rc2 version](https://lean-lang.org/doc/reference/4.35.0-rc2/ValidatingProofs/))

A 2026 audit found DeepSeek-Prover-V2-7B proofs that "pass compilation and the standard sorry-token scan while depending on sorryAx", so token scans alone are insufficient. ([arXiv 2608.28639](https://arxiv.org/abs/2608.28639))

**Privacy note.** The hosted search tools (LeanSearch, Loogle, Lean Finder, LeanExplore, the Lean Hammer premise server) receive the query text. For confidential lemma statements, deny those tools in Claude Code permissions (for example `mcp__lean-lsp__lean_leansearch`) and rely on `lean_local_search` and local Loogle. **Whether lean-lsp-mcp has a built-in switch for remote tools is unverified.** Also, the corporate web proxy blocked `mistral.ai` during this survey under the category "Generative AI and ML Applications". Other AI-adjacent hosts may be blocked unpredictably, and an SSL-inspecting proxy is a plausible source of the `curl ... schannel` errors above (**inferred**).

---

## 5. AI provers (helpers only)

| System | What | Availability | Use alongside Claude Code | Cost / privacy | URL |
|---|---|---|---|---|---|
| Harmonic Aristotle | Hosted formal-reasoning agent. Accepts Lean projects with `sorry`, LaTeX or English, and returns Lean proofs. | Python SDK `aristotlelib` (v2.1.0, 2026-06-18) with an API key from the dashboard. Free for students, researchers and the public. | Yes: Claude can call the CLI or SDK on a file with `sorry`. | Terms §5.2: Harmonic may train on Customer Data (including Lean files). Opt-out is a toggle that applies only going forward. No personal information allowed in inputs. **Do not send client-sensitive statements without opting out first.** | https://aristotle.harmonic.fun, https://aristotle.harmonic.fun/terms, https://pypi.org/project/aristotlelib/ |
| Goedel-Prover-V2-32B | Open-weight whole-proof model (Princeton). | Hugging Face weights; needs a GPU server. | Possible as an MCP or tool backend, but no Windows-laptop path. | Apache-2.0 | https://huggingface.co/Goedel-LM/Goedel-Prover-V2-32B |
| DeepSeek-Prover-V2 (7B / 671B) | Open-weight, recursive subgoal decomposition. | Hugging Face; 671B needs a cluster. | As above | Code MIT; weights under a model licence. Note the `sorryAx` reward-hacking finding above. | https://huggingface.co/deepseek-ai/DeepSeek-Prover-V2-671B |
| Kimina-Prover-72B | Open-weight (Moonshot / Numina), competition style. | Hugging Face | As above | MIT | https://huggingface.co/AI-MO/Kimina-Prover-72B |
| Seed-Prover / 1.5 (ByteDance) | High PutnamBench scores. | Paper; **availability unverified** | Unknown | — | https://arxiv.org/pdf/2512.17260 |
| Numina-Lean-Agent | **Claude Code + Opus 4.5 + Numina-Lean-MCP**, solving 12/12 problems from the 2025 Putnam competition. Code and solutions released. | GitHub (per abstract) | It is itself a Claude Code configuration; useful as a reference design. | Paper CC BY 4.0; code licence unchecked | https://arxiv.org/abs/2601.14027 |

Recommendation: none of these is needed for economic-theory lemmas. Aristotle is the only low-friction add-on, and it is gated by the training-on-input terms.

---

## 6. Claude-at-Lean evidence

| Evidence | Finding | Confidence | URL |
|---|---|---|---|
| Vals ProofBench (Lean 4, advanced undergraduate and graduate; tools for Mathlib search and running code; 40 turns) | Sonnet 5.5, Opus 5.5 and Fable 5.1 at 100%; Opus 5 at 99%; Fable 5 at 95%; Haiku 5.5 at 86% (updated 2026-10-07, v1.1). Cost per item from $0.16 (Haiku 5.5) to $5.45 (Fable 5). The benchmark is close to saturated. | High (official leaderboard) | https://www.vals.ai/benchmarks/proof_bench |
| Anthropic FLT formalization | Agents on an internal model "roughly comparable to Claude Fable 5.1" formalized FLT in 11 days: about 13M lines and about 29,500 intermediate theorems. The result uses only the three standard axioms, and a comparator matched the statement to Mathlib's. The main failure mode was agents losing track of project state, mitigated by a DAG of statements (Prove2Me). | High | https://www.anthropic.com/research/formalizing-fermats-last-theorem |
| Numina-Lean-Agent | Claude Code + Opus 4.5 + MCP solved 12/12 problems from the 2025 Putnam competition. | High (arXiv) | https://arxiv.org/abs/2601.14027 |
| Rocq (not Lean) | Opus 4.6 + Rocq-MCP: 10/12 problems from the 2025 Putnam competition; 198/244 on miniF2F-Rocq (per search snippet). | Medium | https://arxiv.org/html/2603.20405 |
| Practitioner report (blog, Claude version unstated) | Took 11 iterations to compile; "things moving around in Mathlib due to refactorings" and "occasional hallucinations". Ended with 5 `sorry`s, and the attempt to remove them did not compile. | Medium (single anecdote; older model) | https://www.johndcook.com/blog/2026/06/17/rings-with-lean-claude/ |
| Deprecations | A Mathlib bump to v4.34.1 hit lemmas such as `mul_le_one₀` deprecated without replacement. | Medium | https://github.com/Project-Navi/cd-formalization/pull/14 |

**Failure modes and mitigations:**
- *Hallucinated or renamed lemma names, deprecated names, Lean 3 syntax.* Mitigate by grounding every name: `lean_local_search` or Loogle before use, `lean_hover_info` and diagnostics after. Pin the Mathlib version and tell the agent which one it is. Treat deprecation warnings as errors via `--wfail`.
- *Leftover or hidden `sorry`.* Use `#print axioms` (kernel level), not just a grep.
- *Wrong statement.* The economist audits only `Statements.lean`, which is hash-locked.
- *Context loss on long efforts.* Use a lemma DAG or blueprint (the Anthropic FLT lesson).

---

## 7. Recommended minimal setup and deterministic check recipe

**Read-only probe of this laptop (2026-10-11):**
- `git` at `C:\Program Files\Git\cmd\git.exe`; VS Code CLI present; `py` launcher present; `wsl.exe` present.
- `elan`, `lean`, `lake`, `uv`, `uvx` and `rg` are absent.
- `LongPathsEnabled=1`; git `core.autocrlf=true`; `core.longpaths` unset.
- `HOMEDRIVE+HOMEPATH` = `C:\Users\christina.sun` (local); C: has 336 GB free.

**Setup steps (for the user or IT to perform; not done here):**
1. Install elan per the official PowerShell instructions, and the VS Code `lean4` extension.
2. Run `git config --global core.longpaths true`. For the Lean repo only, run `git config core.autocrlf input`, or commit a `.gitattributes` with `* text=auto eol=lf`.
3. Create the project outside OneDrive with `lake +leanprover-community/mathlib4:lean-toolchain new EconLemmas math` under `C:\Users\christina.sun\lean\`. Close VS Code, run `lake exe cache get`, then `lake build`.
4. Ask IT for a Defender exclusion on `C:\Users\christina.sun\lean` and `C:\Users\christina.sun\.cache\mathlib`. Optional, but a 4.5x unpack speed-up was reported.
5. Install `uv` (for example `py -m pip install --user uv`) and ripgrep. Then, in the project root, run `claude mcp add lean-lsp -s project -- uvx lean-lsp-mcp`; on Windows add `cmd /c` before `uvx` if the server fails to start. Deny the remote-search MCP tools if statements are confidential.
6. Optionally install `lean4-skills`, expecting its Bash hooks to need Git Bash or to misfire on Windows.

**Project convention (statement lock):**
- `EconLemmas/Statements.lean`: economist-audited definitions and `def foo_stmt : Prop := ...`. No proofs; imports only `Mathlib`.
- `EconLemmas/Proofs/*.lean`: `theorem foo : foo_stmt := by ...`. This is the agent's only write area.
- `checks/statements.sha256`: the hash recorded at audit time.
- `EconLemmas/Check.lean` (generated by the script): `import EconLemmas`, then for each audited name `theorem foo_check : EconLemmas.foo_stmt := EconLemmas.foo` and `#print axioms foo_check`. This binds the proof to the audited `Prop` regardless of how the agent stated `foo`.

**Python check (`check_lean.py`, cross-platform, `subprocess` with list arguments, `pathlib`, exit codes 0 = PASS, 1 = FAIL, 2 = UNVERIFIED):**
1. **Toolchain present:** `shutil.which("lake")`. If it is missing, report UNVERIFIED (never PASS).
2. **Statement lock:** compare the sha256 of `Statements.lean` with `checks/statements.sha256`. Any mismatch is FAIL ("statement changed since audit").
3. **Source scan** of everything except `Statements.lean`, after stripping `--` and `/- -/` comments. FAIL on any match of:

   ```
   \bsorry\b|\badmit\b|^\s*axiom\b|native_decide|\+native|implemented_by|@\[extern|\bunsafe\b|debug\.skipKernelTC|^\s*(macro|syntax|elab|notation|infix|prefix|postfix)\b|run_cmd|#eval|^\s*import\s+Lean\b
   ```

   Also restrict imports in proof files to `Mathlib.*` and `EconLemmas.*`. This step is a cheap pre-filter; steps 4-5 are authoritative.
4. **Build:** `lake build --wfail` must exit 0. This fails on the "declaration uses 'sorry'" warning, deprecation warnings and errors. Use a timeout (for example 30 minutes on a cold build) and treat a timeout as UNVERIFIED.
5. **Axioms:** `lake env lean EconLemmas/Check.lean` must exit 0. For every `*_check` name, parse either `'X' depends on axioms: [ ... ]` or `'X' does not depend on any axioms`. Require each list to be a subset of `{propext, Classical.choice, Quot.sound}`. FAIL on `sorryAx`, any name ending in `_native`, or any other axiom. Also FAIL if an expected `*_check` line is missing. **The exact output wording should be confirmed on first run** (confidence: medium-high).
6. **Optional kernel replay:** `lake env leanchecker EconLemmas` must exit 0. **Untested on Windows**, so record its outcome but do not gate on it until it has been seen to work.
7. **Out of scope on Windows:** comparator, which is Linux-only and would need WSL. Record "statement fidelity = human audit" as the residual in the report.

---

## 8. Unverified / uncertain

- No Lean-specific OneDrive incident report was found. The OneDrive verdict rests on Microsoft's sync limits, Windows locking behaviour reported on Lean Zulip, and maintainers' triage questions.
- Exact current `.lake` size and file count for Mathlib master (v4.35) were not measured; 6-8 GB is extrapolated from older figures.
- Whether Lake's `packagesDir`/`buildDir` accept absolute out-of-tree paths cleanly on Windows (option B).
- Whether native-Windows `lean-lsp-mcp` works end to end under Claude Code (the fixes are merged, but there is no first-hand test), and whether `lean4-skills` hooks run on Windows.
- Whether `leanchecker` runs correctly on Windows.
- The exact `#print axioms` output strings, and the exact `_native` axiom naming introduced in v4.29.
- The latest elan version number (the releases page rendered stale data).
- Moogle's current status; Seed-Prover availability.
- Whether the MMC proxy will block elan, `cache get` downloads (GitHub, Azure blob), PyPI/uv, or Lean search hosts. Harmonic, LeanSearch, Loogle, LeanExplore and Lean Finder were reachable during this survey; `mistral.ai` was blocked.
- Benchmark saturation (ProofBench at 100%) does not transfer automatically to novel economic-theory lemmas whose Mathlib support (for example order theory, convex analysis, measure-theoretic probability) may be thin. No economics-specific Lean benchmark was found.
