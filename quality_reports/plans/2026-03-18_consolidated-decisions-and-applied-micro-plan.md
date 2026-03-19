# Consolidated Decisions & Applied Micro Plan

**Date:** 2026-03-18
**Status:** DRAFT v2 — incorporating Christina's Round 4 edits (coauthors, institution, chat memory, lit review)

---

## Part 1: All Resolved Decisions (Rounds 1-4)

### Behavioral/Experimental Workflow

| Item | Decision |
|------|----------|
| Analysis language | Stata primary (95%), Python secondary, gradual transition |
| LaTeX engine | pdflatex for Beamer and papers |
| Quarto | Removed entirely |
| Test projects | JMP (`belief_distortion_discrimination`), BDM (`bdm_bic`) |
| Scattered JMP repos | Consolidate to single repo (one-off mistake) |
| `.doh` files | Do helper files, used with `include` to preserve local macros |
| Seminal papers | Claude gathers per subfield → Christina approves → Christina augments |
| Subfield categories | Christina's edited list (12 categories, belief elicitation under experimental methods) |
| Pre-registration | Core skill, always required before data collection |
| Stata packages | reghdfe, estout, coefplot, ivreghdfe, palettes, cleanplots, egenmore, regsave, cdfplot, binscatter, binscatter2 + self-updating learning rule |
| Stata package learning | Both hook-based AND memory-based (failsafe) |

### Applied Micro Workflow

| Item | Decision |
|------|----------|
| Test project | TX peer effects (immigrant kids, TERC admin data) |
| TX stage | Draft — nearing submission for long run paper |
| TX data | Admin panel data, air-gapped TERC server |
| TX identification | Family FE with within school-grade across cohort variation |
| TX multi-paper | 3 papers (long run, political, swift raid), shared cleaning pipeline, divergent analysis |
| TX language | Stata |
| Air-gapped constraint | Claude works on local .do copies + designs replication package + reviews code. Cannot see data. Workflow must also support interactive analysis for non-air-gapped projects. |
| Applied micro skills needed | DiD, IV/2SLS, RDD, balance tables, sensitivity analysis (Oster, Rambachan-Roth), CATE, synthetic control |
| Implementation priority | **Applied micro first** (TX time crunch) |

### Overleaf Integration

| Item | Decision |
|------|----------|
| Overleaf tier | Premium (already has it) |
| Current sync | Dropbox (switching to git) |
| Recommended setup | **Two separate repos** (see Part 3 below) |

### Repo Architecture

| Item | Decision |
|------|----------|
| Template approach | One template repo, domain branches (see Part 2 below) |
| Project repos | Separate standalone repos, receive `.claude/` from template |
| Upstream sync | Keep main close to Pedro's upstream for pulling innovations |

---

## Part 2: Repo Architecture — Branch Strategy

Christina's suggestion is the right call: use branches of this repo to maintain Pedro's upstream compatibility.

### Structure

```
claude-code-my-workflow/  (this repo, originally forked from Pedro)
│
├── main                  → Shared core + Pedro's upstream innovations
│   .claude/skills/       → commit, compile-latex, lit-review, write, review,
│                           submit, revise, talk, validate-bib, deep-audit,
│                           context-status, learn
│   .claude/agents/       → librarian, librarian-critic, data-engineer,
│                           coder, coder-critic, writer, writer-critic,
│                           verifier
│   .claude/rules/        → workflow, quality, logging, stata-conventions,
│                           python-conventions, working-paper-format, tikz
│   .claude/hooks/        → all shared hooks
│   templates/            → session-log, quality-report, requirements-spec
│
├── behavioral            → main + behavioral/experimental additions
│   .claude/skills/       → + design, qualtrics, otree, preregister, theory,
│                           challenge (--design mode)
│   .claude/agents/       → + designer, designer-critic, theorist,
│                           theorist-critic, qualtrics-specialist,
│                           otree-specialist, methods-referee
│   .claude/rules/        → + experiment-design-principles,
│                           domain-profile-behavioral, journal-profiles-behavioral
│   templates/            → + experiment-design-checklist,
│                           pre-registration-template,
│                           subject-instructions-template
│
└── applied-micro         → main + applied micro additions
    .claude/skills/       → + did-diagnostics, iv-tools, synth-control,
                            balance-table, sensitivity, robustness-orchestrator
    .claude/agents/       → + identification-critic, applied-micro-referee,
                            replication-auditor
    .claude/rules/        → + identification-strategy,
                            domain-profile-applied-micro,
                            journal-profiles-applied-micro,
                            air-gapped-workflow
    templates/            → + replication-package-readme,
                            referee-response-template
```

### Merge Flow

```
Pedro's upstream → pull into main → merge main into behavioral
                                  → merge main into applied-micro

Christina improves shared infra → commit to main → merge into both branches
Christina improves behavioral   → commit to behavioral branch only
Christina improves applied-micro → commit to applied-micro branch only
```

### How Project Repos Get Infrastructure

When starting a new project:

1. Decide: behavioral or applied micro?
2. Copy `.claude/`, `CLAUDE.md`, `templates/` from the appropriate branch into your project repo
3. Customize `CLAUDE.md` for the specific project
4. The project repo is then **independent** — no ongoing branch tracking

For existing projects (TX, BDM, JMP):
- Copy the appropriate `.claude/` infrastructure into the existing project repo
- This is a one-time setup, not a fork

### Why Branches Over Two Repos

- **Pedro sync**: `main` stays mergeable with Pedro's upstream
- **Shared improvements**: Changes to `main` merge cleanly into both branches
- **Single maintenance point**: One repo to manage, not two
- **Clear lineage**: `git log` shows the full history of all infrastructure decisions

---

## Part 3: Overleaf Integration — Simplest Setup

### Recommendation: Two Separate Repos (Paper + Project)

After researching all options (Overleaf GitHub sync, git remotes, subtrees, submodules), the simplest approach that works:

**Your paper lives in its own GitHub repo, linked to Overleaf. Your project repo is separate.**

### One-Time Setup (~10 minutes per project)

1. In your **existing Overleaf project** → Menu → GitHub → "Create a GitHub Repository"
   - This creates a GitHub repo containing your paper files
   - Overleaf is now linked to that GitHub repo

2. Clone the paper repo locally:
   ```
   ~/github_repos/
     bdm_bic/                    # project repo (code, data structure, etc.)
     bdm_bic_paper/              # paper repo (synced with Overleaf)
   ```

3. Done. No subtrees, no submodules, no tokens.

### Daily Workflow

| Scenario | Steps |
|----------|-------|
| Edit on Overleaf | Edit → click "Push to GitHub" in Overleaf menu |
| Pull Overleaf edits locally | `cd bdm_bic_paper && git pull` |
| Edit locally with Claude | Claude edits files → `git commit && git push` |
| Pull local edits into Overleaf | In Overleaf → click "Pull from GitHub" |
| Merge conflict | Overleaf creates a branch → you resolve via GitHub PR |

### Connecting Paper and Project Repos

Your project repo's `CLAUDE.md` includes a pointer:

```markdown
## Paper
Paper repo: ~/github_repos/bdm_bic_paper/
Overleaf: [link to Overleaf project]
```

Claude can read/edit files in the paper repo when working on writing tasks. No formal git linkage needed — just a path reference.

For figures: your analysis code in the project repo exports figures to `Figures/`. A simple copy script (or Claude) moves them to the paper repo when needed.

### Why This Wins Over Alternatives

| Alternative | Problem |
|-------------|---------|
| Overleaf GitHub sync (built-in) | Can't link existing Overleaf to existing GitHub repo; syncs entire repo (Data/, scripts/ clutter Overleaf) |
| Git subtree | Complex commands, slow pushes, easy to mess up |
| Submodules | Everyone must `git submodule update`; adds ongoing friction |
| Whole project = Overleaf | 100 MB limit, clutter, performance issues |

### For TX Specifically

TX is even simpler: code lives on TERC (air-gapped), so there's no local project repo with code. The paper repo IS the main local artifact. Once you set up the applied micro workflow:

```
~/github_repos/
  tx_peer_effects_paper/        # paper repo, synced with Overleaf
  tx_peer_effects_local/        # local copies of .do files for Claude review
                                # (manually exported from TERC)
```

---

## Part 4: Applied Micro Workflow — Plan v1

### Priority: TX Project (Time Crunch)

Since TX is near submission, the applied micro workflow should focus on what helps RIGHT NOW:
1. Paper writing and revision support
2. Code review for exported .do files
3. Replication package structure
4. Robustness check planning

The full identification strategy toolkit (DiD diagnostics, IV tools, etc.) is important for the workflow template but less urgent for TX specifically.

### Proposed Skills (Applied Micro)

#### Identification & Estimation (4)

| Command | What It Does |
|---------|-------------|
| `/identify [strategy]` | Design/review identification strategy. Modes: `did`, `iv`, `rdd`, `synth-control`, `fe-variation`, `shift-share`. Produces: assumptions, threats, diagnostic tests, robustness checks |
| `/robustness [spec]` | Orchestrate systematic robustness checks: alternative specs, sample restrictions, different SEs, placebo tests, sensitivity bounds. Outputs a robustness matrix. |
| `/balance [treatment]` | Generate balance tables: treatment vs. control summary stats, normalized differences, joint F-test |
| `/event-study [spec]` | Generate event study plots: pre-trends, dynamic effects, confidence intervals |

#### Analysis & Output (2)

| Command | What It Does |
|---------|-------------|
| `/analyze [dataset]` | End-to-end analysis. For air-gapped projects: takes variable names, summary stats, and .do file → produces code improvements, table formatting, figure suggestions. For interactive projects: runs analysis directly. |
| `/tables [spec]` | Generate publication-quality LaTeX tables from Stata output. Formatting: booktabs, threeparttable, estout conventions. |

#### Replication & Submission (2)

| Command | What It Does |
|---------|-------------|
| `/replicate [mode]` | Modes: `structure` (design replication package layout), `audit` (check completeness against AEA Data Editor standards), `readme` (generate README_for_replication.md) |
| `/submit [mode]` | Same as behavioral: target journal, package, audit, final check |

#### Review (2)

| Command | What It Does |
|---------|-------------|
| `/review [target]` | Modes: `--peer [journal]`, `--identification`, `--code`, `--proofread`, `--all`. Identification review checks: exclusion restriction, parallel trends, instrument relevance, sample selection. |
| `/revise [report]` | Address referee comments: parse referee report → map comments to paper sections → draft responses → track changes |

#### Shared (inherited from main branch) (6)

`/lit-review`, `/write`, `/talk`, `/commit`, `/compile-latex`, `/validate-bib`

### Proposed Agents (Applied Micro)

| Agent | Role |
|-------|------|
| **identification-critic** | Adversarial review of identification strategy. Asks: "What threatens your exclusion restriction?", "Show me the parallel trends", "What's your first stage F-stat?", "Oster bounds?" |
| **applied-micro-referee** | Simulated referee calibrated to top applied micro journals (AER, QJE, JPE, AEJ:Applied, AEJ:Policy, JHR, JLE, JDE) |
| **replication-auditor** | Checks replication package against AEA Data Editor standards: README completeness, code runability, data documentation, license declarations |
| **robustness-designer** | Given a main specification, proposes comprehensive robustness checks: alternative samples, controls, functional forms, SEs, placebo tests, bounds |

Plus shared agents (from `main`): librarian, librarian-critic, data-engineer, coder, coder-critic, writer, writer-critic, verifier

### Proposed Rules (Applied Micro)

| Rule | Scope | Content |
|------|-------|---------|
| `identification-strategy.md` | `**/*.do`, `**/*.tex` | Document identification assumptions explicitly. Every causal claim needs: estimand, identifying assumption, threat assessment, diagnostic test. |
| `domain-profile-applied-micro.md` | global | Applied micro conventions: peer effects literature, education economics, immigration economics, standard identification strategies |
| `journal-profiles-applied-micro.md` | global | AER, QJE, JPE, REStud, AEJ:Applied, AEJ:Policy, JHR, JLE, JDE, J of Immigration, Education Finance and Policy, Economics of Education Review |
| `air-gapped-workflow.md` | `**/*.do` | When Claude can't see data: work from variable lists, summary stats, codebooks. Generate code defensively — add assertions, describe expected output, flag assumptions about data structure. |
| `replication-standards.md` | `Replication/**` | AEA Data Editor standards, README template, directory structure, dependency documentation |
| `multi-paper-project.md` | global | Shared data pipeline with divergent analysis branches. Naming conventions, cross-paper consistency. |

### TX-Specific CLAUDE.md Configuration

```markdown
# CLAUDE.md — TX Peer Effects Project

**Project:** Immigrant Peer Effects (Long Run Outcomes, Political, Swift Raid)
**Institution:** University of California, Davis
**Coauthors:**
  - Long run & Political papers: Briana Ballis (UC Merced), Derek Rury (Oregon State)
  - Swift raid paper: + Emily Dieckmann (UC Merced)
**Data:** Texas ERC admin panel data (AIR-GAPPED — Claude cannot access)
**Papers:** 3 papers sharing a common data pipeline
**Stage:** Long run paper near submission; political paper in progress; swift raid early stage

## Air-Gapped Workflow
- Code lives on TERC server. Local copies of .do files for review.
- Claude works from: variable names, summary stats, codebooks, .do file exports
- Claude CANNOT run code or see raw data
- Generate code with explicit assertions about expected data structure
- Server uses older reghdfe/ivreghdfe versions; test compatibility

## Paper Repo
Paper repo: ~/github_repos/tx_peer_effects_paper/
Overleaf: /Users/christinasun/Library/CloudStorage/Dropbox/Apps/Overleaf/Immigrant_PoliticalAffiliation_Jan2022
Current draft: SOLE_draft (long run outcomes)

## Identification
- Long run paper: Family FE with within school-grade across cohort variation
  in immigrant peer exposure. IV: predicted exposure from transition matrix
  instrumenting for actual exposure.
  FE specs: (1) grade×year + campus×year + family FE;
  (2) grade×year + campus×year + family×year FE;
  (3) testing grade×year + family×initial_campus for IV (following Figlio et al. 2024 ReStud)
- Political paper: Same IV/FE framework as long run paper, different outcomes (L2 voter data)
- Swift raid paper: Synthetic control + DiD around Dec 12, 2006 Operation Wagon Train
  raid in Cactus, TX (~297 workers arrested, ~3,000 population town). No IV.

## Multi-Paper Pipeline
Shared: Data cleaning → cleaned dataset (enrollment linked to transition matrix
  via campus, year, grade, grade_0; all merge keys converted to string)
Branch 1 (long run): cleaned → sample selection → IV/FE regressions → tables/figures
Branch 2 (political): cleaned → political outcome variables → [TBD]
Branch 3 (swift): cleaned → pre/post raid → synthetic control + DiD

## Known Technical Issues
- Variable type mismatches caused prior merge failures (~30M records recovered)
- e(sample) must be captured immediately after estimation (older reghdfe)
- Singleton observations concern given small campus sizes
- Grade repeaters/skippers excluded (transition matrix covers normal progression only)
- Git repos must NOT live in Dropbox (sync corrupts .git)
```

### Implementation Roadmap — Applied Micro (TX-First)

#### Phase 0: Setup (Day 1) ✅ COMPLETE

- [x] Create `applied-micro` branch from `main`
- [x] Set up Overleaf git sync for TX paper (`tx_peer_effects_paper` repo, linked to Overleaf)
- [x] Create local directory structure (`tx_peer_effects_local/`, renamed from `tx_immigrant_spillovers`)
- [ ] Export .do files from TERC to `tx_peer_effects_local/` — **BLOCKED on FERPA**
- [x] Copy `.claude/` infrastructure into TX repo (11 skills, 3 agents, 11 rules, 7 hooks, 4 templates)
- [x] Write TX-specific `CLAUDE.md`

#### Phase 1: Core Rules + Shared Agents (Day 2)

**Rules:**
- [ ] Create `identification-strategy.md` rule
- [ ] Create `domain-profile-applied-micro.md` (peer effects, education, immigration lit)
- [ ] Create `air-gapped-workflow.md` rule
- [ ] Create `replication-standards.md` rule
- [ ] Create `multi-paper-project.md` rule
- [ ] Create `stata-code-conventions.md` (reghdfe, ivreghdfe, estout patterns)
- [ ] Create `journal-profiles-applied-micro.md`

**Shared Agents (build on `main`, flow to both branches):**
- [ ] Create librarian agent (literature search)
- [ ] Create librarian-critic agent (coverage evaluation, missing refs)
- [ ] Create data-engineer agent (raw → cleaned data, merge pipelines)
- [ ] Create coder agent (Stata primary, Python secondary)
- [ ] Create coder-critic agent (code quality, reproducibility)
- [ ] Create writer agent (paper drafting, anti-hedging)
- [ ] Create writer-critic agent (clarity, structure, journal compliance)
- [ ] Adapt verifier agent (from slides to papers + Stata)
- [ ] Adapt proofreader agent (from slides to papers)

**Devils-Advocate → `/challenge` Upgrade:**
- [ ] Rename `/devils-advocate` to `/challenge`
- [ ] Add `--paper` mode (shared): contribution framing, identification threats, referee objections
- [ ] Add `--fresh` mode (shared): cold read, no prior context
- [ ] Add `--identification` mode (applied-micro): exclusion restriction, parallel trends, instrument validity
- [ ] Move current slide-pedagogy content to `--slides` mode (behavioral branch only)

#### Phase 2: Urgent Skills for TX (Day 3-4)

- [ ] Create `/review --identification` mode (most urgent — helps with submission prep)
- [ ] Create `/robustness` skill (plan robustness checks for submission)
- [ ] Create `/tables` skill (format Stata output for paper)
- [ ] Create `/replicate structure` mode (start replication package)
- [ ] Create `/revise` skill (for eventual referee responses)
- [ ] Adapt `/write` for applied micro conventions
- [ ] Adapt `/compile-latex` for paper compilation (pdflatex)

#### Phase 3: Applied-Micro Agents + Identification Toolkit (Day 5-6)

**Applied-micro-only agents:**
- [ ] Create identification-critic agent
- [ ] Create applied-micro-referee agent
- [ ] Create robustness-designer agent
- [ ] Create replication-auditor agent

**Identification skills:**
- [ ] Create `/identify` skill with all strategy modes (did, iv, rdd, synth-control, fe-variation, shift-share)
- [ ] Create `/balance` skill
- [ ] Create `/event-study` skill

#### Phase 4: Beamer/Slides Adaptation (Later — Not Urgent)

- [ ] Adapt Pedro's slide agents for applied micro presentations (seminar talks, job talks)
- [ ] Copy remaining Beamer skills: `/compile-latex` slide mode, `/proofread`, `/visual-audit`, `/slide-excellence`
- [ ] Copy slide-related agents: slide-auditor, pedagogy-reviewer, domain-reviewer (adapt for econ talks)
- [ ] Copy Beamer rules: no-pause-beamer, proofreading-protocol, beamer-quarto-sync (if needed)
- [ ] Retain all TikZ infrastructure (already copied: tikz-reviewer, tikz-visual-quality, extract-tikz)

#### Phase 4: Test with TX (Day 7+)

- [ ] Import Christina's swift raid Claude Chat memory/output
- [ ] Test `/review --identification` on TX long run paper
- [ ] Test `/review --code` on exported .do files
- [ ] Test `/robustness` on TX main specification
- [ ] Test `/replicate structure` for TX replication package
- [ ] Test `/tables` on TX output
- [ ] Iterate based on output quality

---

## Part 5: Running To-Do List

### Must-Do Before Implementation

- [x] Provide test project repo paths
- [x] Confirm repo structure (separate repos)
- [x] Confirm subfield categories
- [ ] **Export .do files from TERC** (Christina — needed for Phase 0)
   - CS: awaiting FERPA review, will add once exported.
- [ ] **Share swift raid Claude Chat memory/output** (Christina — for Phase 4)

### Should-Do (Improves Quality)

- [ ] Export a QSF from existing Qualtrics survey (for `/qualtrics` skill — behavioral workflow)
- [ ] Share custom Beamer templates (pdflatex + xelatex)
- [ ] Provide sample `.doh` file (if not in test repos)
- [ ] Clarify Stata license type (SE vs MP vs BE)
- [ ] Share TX variable codebook / summary statistics (helps Claude write better code reviews)

### Nice-to-Have (Can Do Later)

- [ ] Review and refine journal profiles after testing `/review --peer`
- [ ] Identify additional referee concerns from real reviews
- [ ] Customize notation conventions per paper
- [ ] Set up Overleaf git sync for BDM and JMP papers
- [ ] Consolidate JMP satellite repos into single repo
- [ ] Gather and organize seminal papers by subfield (Claude drafts → Christina approves)
- [ ] Add GitHub Action for auto-pulling Overleaf changes (only if manual clicking gets annoying)

---

## Part 6: Resolved Items

All items from Round 4 are now resolved:

1. Branch strategy (main / behavioral / applied-micro) — **APPROVED**
2. Overleaf two-repo setup — **APPROVED**
3. TERC .do file export — **BLOCKED on FERPA clearance** (Christina will add when cleared)
4. TX CLAUDE.md — **UPDATED** with UC Davis, coauthors, identification details, technical issues
5. Applied micro subfields — **CONFIRMED** (6 subfields)
6. Other projects — **NOTED** (CSAC, GTDF — lighter needs, no immediate priority)

## Part 7: What's Next

**This plan is ready for implementation pending Christina's final approval.**

Implementation order:
1. Create `applied-micro` branch from `main` (can start now)
2. Build core rules and domain profile (can start now)
3. Build urgent skills for TX (can start now — code review, tables, robustness don't need data)
4. Set up Overleaf git sync for TX paper (can start now)
5. Test with exported .do files (blocked on FERPA)
6. Import swift raid chat memory + lit review into workflow (ready)

**Blocking question:** Should I begin implementation now (Phase 0-2), or do you want to review this plan one more time first?

CS: Begin now.

**TX project memory block:** See `quality_reports/plans/2026-03-18_tx-project-memory-revision.md` for the finalized 3-paper memory block (approved by Christina).

**Swift lit review:** See `quality_reports/plans/swift_lit_review_output.md` for comprehensive literature classification (25 papers, causal econ / causal other / non-causal) with gap analysis and contribution framing.

**Applied micro domain subfields (CONFIRMED):**
- Peer Effects & Social Interactions
- Education Economics
- Immigration Economics
- Labor Economics
- Treatment Effects Methods (DiD, IV, RDD, Synthetic Control)
- Panel Data Methods

**Other potential projects:** CSAC survey reports and GTDF LGBTQ white paper (no rigorous identification — lighter workflow needs).


