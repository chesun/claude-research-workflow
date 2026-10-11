# Theory survey C — How mathematicians use AI, and best practice
**Date:** 2026-10-11
**Reviewer:** survey agent C (general-purpose, opus)
**Target:** research-math workflows with LLMs; blueprint method; verification practice
**Status:** Active

Citation convention: sources are cited by title and URL only. Confidence tags: **[high]** = read at the primary source; **[medium]** = primary-source abstract or a reputable secondary report; **[low]** = secondary or aggregator only, not confirmed.

---

## Bottom line

- **What working mathematicians agree on is that verification is the bottleneck, and AI is safest when it checks work rather than generates it.** Terence Tao's position, gathered on his "Terence Tao on AI in mathematics (and beyond)" page (https://teorth.github.io/tao-web/ai-views.html), is that output must be independently checkable. AI fits "red-team" roles (critiquing, checking calculations, searching literature) better than "blue-team" roles (generating the argument). His usability test: if you could not present the output and field questions on it without AI help, it should not be in your workflow. [high for the quotes on that page; it is a compilation, so individual dates are medium]
- **Today's frontier models produce correct research-level proofs, but also confident wrong ones, at rates no unsupervised workflow can accept.** Evidence: human graders in "Semi-Autonomous Mathematics Discovery with Gemini: A Case Study on the Erdős Problems" (https://arxiv.org/abs/2601.22401) judged 68.5% of 200 graded responses fundamentally flawed. Of 63 technically correct solutions, only 13 addressed the intended problem. On the First Proof research-problem set, the Scientific American report "AI just got its toughest math test yet. The results are mixed" (https://www.scientificamerican.com/article/first-proof-is-ais-toughest-math-test-yet-the-results-are-mixed) found AIs gave "confident proofs to every problem, but only two were correct". [medium-high]
- **The blueprint method suits your design, and it was built for formalizing proofs already known.** A blueprint is a dependency graph of small labelled statements, each with a status. For open-ended work, the Equational Theories Project paper (https://arxiv.org/abs/2512.07087) reports that the blueprint's role "changed, but it still remained important". Prove2Me, the platform behind Anthropic's Fermat formalization (https://arxiv.org/abs/2608.28433), uses immutable statement nodes in a DAG. Your workflow needs a *living conjecture graph*: statements get created, refuted and superseded, not just ticked off. [high]
- **A Markdown/YAML blueprint is the right first tool on this machine.** leanblueprint is a plasTeX plugin; its web output needs plasTeX plus graphviz with its development libraries, and its PDF output needs a TeX engine (https://github.com/PatrickMassot/leanblueprint). Its data model ports cleanly to Markdown: labels, `\uses` split into statement and proof dependencies, and statement-status separate from proof-status. Keep the leanblueprint field names so a later Lean lane can export to it or to LeanArchitect (https://arxiv.org/abs/2601.22554). [high]
- **Five mitigations have the best evidence:**
  1. Context-isolated verifiers that see only the statement and a cleaned proof.
  2. Pattern-armed adversarial prompts, rather than "is this correct?".
  3. At least two independent verifier passes, with asymmetric thresholds.
  4. "Prove *or* refute" framing, which counters sycophancy toward the stated target. BrokenMath (https://arxiv.org/abs/2510.04721) found the best model sycophantic on false theorems 29% of the time.
  5. Computational exploration before any proof attempt, with a checker the generator cannot game.

  Sources: QED (https://arxiv.org/abs/2604.24021), Anthropic's math-olympiad and math-proof plugins (local), and Theorist Toolbox (https://arxiv.org/abs/2606.22337).
- **An economic-theory precedent exists and supports your design.** "Theorist Toolbox: Tools for Agent Based LLM-assisted economic theory Research" (https://arxiv.org/abs/2606.22337) reports three findings:
  - "external verification, not model capability, is the design variable";
  - models "will claim to prove a false theorem as readily as a true one";
  - polish masks rigor: the cleanest-looking output was the least verified.

  "Can AI Refute Economic Theory? Evidence from Beyond the Knowledge Cutoff" (https://arxiv.org/abs/2606.05383) found no model located a true error in a published theory paper without substantial human guidance. [medium-high]
- **Lean is optional, and its guarantee is narrower than it looks.** The kernel certifies that the proof proves *the formal statement*, not that the statement means what you intended. "Beyond Compilation" (https://arxiv.org/abs/2606.31002) found one system compiles 87.2% of statements but is faithful on 57.7%. The Vlasov-Maxwell-Landau formalization (https://arxiv.org/abs/2603.15929) reports "hypothesis creep" and "definition-alignment bugs". If you add the Lean lane, the economist must review every formal statement and definition. EconCSLib (https://arxiv.org/abs/2606.16144) already formalizes Arrow's theorem, Gibbard–Satterthwaite, Myerson, VCG and several fixed-point theorems. [medium-high]

---

## 1. How working mathematicians actually use LLMs: documented workflows and lessons

### 1.1 Terence Tao (the most extensively documented)

- **Verification as the filter.** "In math, we can completely check and verify outputs, and this really filters out a lot of the rubbish." Also: "I would caution against using AI tools without the ability to independently verify their output." Both quotes, with their original venues, are collected at https://teorth.github.io/tao-web/ai-views.html. [high for the quotes; medium for venue attribution, since the page is a compilation]
- **Red team over blue team, and the presentation test.** From the essay "Mathematical methods and human thought in the age of AI" (blog: https://terrytao.wordpress.com/2026/03/29/mathematical-methods-and-human-thought-in-the-age-of-ai/; arXiv: https://arxiv.org/abs/2603.26524):
  - safe uses are checking calculations you know how to do, proofreading, and writing code you can read and debug;
  - risky uses are asking for proof strategies for problems you cannot solve;
  - if you "would be unable to coherently present the output of the AI in a class presentation and be able to answer questions about it without further AI assistance, it should not be part of your workflow." [high]
- **A reading and digestion protocol.** The compilation page describes a shared chatbot transcript on the Jacobian conjecture. The user drives the algebra, the AI verifies symbolically at each step, and the stated method is to "first give the AI your own understanding... and ask it to review whether your understanding was correct" (https://teorth.github.io/tao-web/ai-views.html). [medium]
- **Exploration at scale with a robust verifier (AlphaEvolve).** The source is "Mathematical exploration and discovery at scale" (paper https://arxiv.org/abs/2511.02864; blog https://terrytao.wordpress.com/2025/11/05/mathematical-exploration-and-discovery-at-scale/):
  - the system rediscovered best-known constructions on most of 67 problems and improved several;
  - the main failure mode was *exploiting the scoring function* (near-coincident points under loose float tolerances; "cheating" through a linear-programming solver failure mode);
  - "A non-trivial amount of human effort needs to go into designing a non-exploitable verifier": exact or interval arithmetic and admissibility checks. [high]
- **Lean.** On the compilation page Tao says Lean is "a formal proof assistant rather than an automatic theorem prover", "not all that useful in discovering new proofs". Humans should author or carefully review *statements*, automation can handle proofs, and "unit tests" on subtle definitions catch misformalization. The page also says autoformalizers eagerly prove false statements, so a sudden run of easy successes signals mis-stated hypotheses (https://teorth.github.io/tao-web/ai-views.html). [medium: compiled quotes, not read at each original venue]
- **The broader stance (2026).**
  - In the 2026 ICM lecture "Mathematics in the age of AI" (https://arxiv.org/abs/2608.16753) and the "Math 2.0" post (https://terrytao.wordpress.com/2026/10/10/math-2-0/), Tao argues that blindly optimizing problem-solving is now harmful.
  - What matters is the full cycle: generation, verification, exposition, publication, canonicalization.
  - He proposes disclosing the actual chat logs, and a "talk test": if the authors cannot give an expert-level talk on the result, it should not be published.

  [high for the existence of the essay and post; the talk-test quote is via the compilation page, medium]

### 1.2 Erdős problems: the largest public record of AI contributions

- **The tracking wiki.** "AI contributions to Erdős problems" (https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems) separates primary contributions (AI alone; AI plus literature found afterward; AI building on literature; AI–human collaboration) from secondary ones (literature search, formalization, rewriting, computation). Its disclaimers include "This page is not a benchmark", "Many problems on the site lack a thorough literature review", and "Absence of past progress may reflect obscurity rather than difficulty". [high]
- **Erdős #1026.** Tao's blog post "The story of Erdős problem #1026" (https://terrytao.wordpress.com/2025/12/08/the-story-of-erdos-problem-126/) records an exploration-first pipeline:
  1. A human reformulated the ambiguous original problem as a constant c(n).
  2. A human computed the first nine exact values and conjectured a formula for perfect squares.
  3. Aristotle proved that case in Lean.
  4. AlphaEvolve produced numerical bounds.
  5. Deep-research tools found the prior literature.
  6. Three distinct proofs followed, with Lean verification.

  The site's policy allows disclosed AI use if the contents "have been carefully checked and verified by the user themselves without the assistance of AI". [high]
- **Aletheia (Google DeepMind) on 700 open problems** (https://arxiv.org/abs/2601.22401):
  - 63 technically correct solutions, but only 13 meaningfully addressed the intended statement; 50 were trivial because of misinterpretation;
  - 5 novel autonomous solutions;
  - 8 problems turned out to be already solved in the literature;
  - the authors flag "subconscious plagiarism" and the high cost of verification.

  [high for the abstract; the counts come from the paper as summarized by search, medium-high]
- **Formal resolutions.** "Resolution of Erdős Problem #728: a writeup of Aristotle's Lean proof" (https://arxiv.org/abs/2601.07421) documents an AI-generated, Lean-verified resolution. [medium; title and abstract only]

### 1.3 Competition results and how verification changed them

- **The "Proof or Bluff?" baseline.** "Proof or Bluff? Evaluating LLMs on 2025 USA Math Olympiad" (https://arxiv.org/abs/2503.21934): expert graders found only Gemini-2.5-Pro reached a non-trivial 25%; all other models scored under 5%. Final-answer benchmarks badly overstated proof ability. [high]
- **One year later.** "Proof, Not Bluff" on USAMO 2026 (https://matharena.ai/usamo/):
  - GPT-5.4 scored 95.2%, Gemini-3.1-Pro 74.4%, Opus-4.6 47.0%;
  - grading used a three-model LLM jury taking the *minimum* score when the judges agree within two points, plus human checking and code execution for symbolic steps;
  - the basic failure modes of 2025 (guessing, circular reasoning) are "much less common". [high]
- **Verification-and-refinement pipelines.** "Winning Gold at IMO 2025 with a Model-Agnostic Verification-and-Refinement Pipeline" (https://arxiv.org/abs/2507.15855): a prompt-only solve, self-verify and correct loop took three different base models to 5 of 6 IMO 2025 problems, against baselines of 21–38%. [high]
- **Learned verifiers.** "DeepSeekMath-V2: Towards Self-Verifiable Mathematical Reasoning" (https://arxiv.org/abs/2511.22570) trains a proof verifier plus a meta-verifier that checks the verifier's cited defects really exist. [medium]
- **Natural-language and formal golds.**
  - Gemini Deep Think reached IMO 2025 gold end-to-end in natural language (https://deepmind.google/discover/blog/advanced-version-of-gemini-with-deep-think-officially-achieves-gold-medal-standard-at-the-international-mathematical-olympiad/).
  - Harmonic's Aristotle reached gold-equivalent with Lean-verified solutions; its problem statements were formalized by hand (https://arxiv.org/abs/2510.01346). [medium]

### 1.4 Research-level evaluations

- **First Proof** (https://arxiv.org/abs/2602.05192; https://1stproof.org): ten unpublished lemmas from the authors' own research, with answers encrypted until evaluation.
  - Scientific American reports that on the first batch only two of the AI answers were correct, despite confident proofs to every problem (https://www.scientificamerican.com/article/first-proof-is-ais-toughest-math-test-yet-the-results-are-mixed). [medium]
  - A second batch is documented (https://arxiv.org/abs/2606.18119), but I could not confirm its per-system results at the primary source. See the Unverified section.
- **FrontierMath Tier 4 (v2).** Epoch (https://epoch.ai/benchmarks/frontiermath-tier-4-v2) has 43 Tier-4 problems, with a correction "addressing errors in 42% of problems" released 2026-06-12. The lesson: benchmark answer keys themselves need adversarial checking. [high for the audit; I did not verify any model scores]
- **AI co-mathematician (Google DeepMind)** ("AI co-mathematician: Accelerating mathematicians with agentic AI", https://arxiv.org/abs/2605.06651): a stateful workspace that "manages uncertainty, refines user intent, tracks failed hypotheses". It has literature, computation and proof sub-agents plus a reviewer. It reports 48% on FrontierMath Tier 4. Secondary reports describe an Oxford topologist finding a novel idea inside a proof the system's own reviewer had *rejected*, then patching it himself (https://www.datacamp.com/blog/google-ai-co-mathematician). [abstract medium; the anecdote low-medium]

### 1.5 Formalization at scale (2026)

- **Fermat's Last Theorem.** Anthropic's "Formalizing Fermat's Last Theorem" (https://www.anthropic.com/news/formalizing-fermats-last-theorem):
  - Claude agents produced a complete Lean proof in about 11 days;
  - the final proof uses only Lean's three standard axioms, and a comparator confirmed the statement matches Mathlib's;
  - early attempts failed because agents "quickly lost track of the project's state";
  - success required the Prove2Me DAG of statements, with statements separated from proofs.

  Secondary reports say Kevin Buzzard compiled and checked it independently (https://lean-lang.org/use-cases/flt for the background project). [high for the Anthropic post; medium for the Buzzard reaction]
- **Prove2Me** (https://arxiv.org/abs/2608.28433): each theorem statement is an immutable object that may have several proofs. Human auditing is confined "to a small curated core of statements". [medium; abstract and project page]

### 1.6 Economists specifically

- **Theorist Toolbox** (https://arxiv.org/abs/2606.22337; HTML read). It compares three methods: a single disciplined pass; an adversarial prover–refuter pair, with Claude proposing and Codex attacking "in exploration mode" for "counterexamples and boundary conditions rather than a verdict on prose"; and a multi-agent project with a reviewer gate whose verdicts (approve / approve-with-flags / reject) are written to disk, with `\unproven{}` gap flags.
  - Caught errors include an ex-post neutrality claim killed by a small counterexample (only the in-expectation form survived) and a budget-balance claim that ran into a dominant-strategy impossibility.
  - Recommendations: independent runs on different framings, so that convergence is cheap corroboration; separate prover and verifier roles; explicit gap flags; numerical gates on small instances before shipping analytic claims.
  - The single-pass output was the most polished and the least verified. [high]
- **"Can AI Refute Economic Theory?"** (https://arxiv.org/abs/2606.05383): no model located a true error in four published theory papers without substantial human guidance, though a human paired with a frontier model can outperform current peer review. [medium; abstract]
- **EconCSLib** (https://arxiv.org/abs/2606.16144): an early-stage Lean 4 library for game theory, mechanism design and social choice, which also hosts machine-checked open problems. [medium]

---

## 2. The blueprint methodology

### 2.1 What leanblueprint is and how it works

- **What it is.** leanblueprint is "a plasTeX plugin allowing to write blueprints for Lean 4 projects" (https://github.com/PatrickMassot/leanblueprint). You write LaTeX with theorem environments, each carrying a `\label`, plus these macros:
  - `\lean{decl}` links the item to its Lean declaration(s);
  - `\leanok` marks it formalized;
  - `\uses{labels}` records dependencies, and the README says the meaning depends on placement: inside the statement it means the labels are "necessary to state the definition/theorem", inside the proof it means they are needed "only in the proof";
  - `\notready` marks it not yet ready to formalize;
  - `\mathlibok` marks it as already in Mathlib;
  - `\discussion{issue}` links a GitHub issue.

  [high]
- **The dependency graph.** Colours by status, with these README defaults: stated, can_state, not_ready, proved, can_prove, defined, fully_proved, mathlib. Tao's PFR tour (https://terrytao.wordpress.com/2023/11/18/formalizing-the-proof-of-pfr-in-lean4-using-blueprint-a-short-tour/) explains the reading:
  - a green border means the statement is formalized;
  - a green fill means the proof is formalized;
  - blue means ready to work on (all prerequisites done);
  - the goal is to turn every bubble up to the final theorem green.

  Contributors pick blue nodes, so work runs asynchronously. [high]
- **Toolchain.** `pip install leanblueprint`. It depends on plastexdepgraph, which "requires graphviz and its development libraries". The web build uses plasTeX, a pure-Python TeX-to-HTML converter; the PDF build needs a TeX engine (xelatex or lualatex). Commands: `leanblueprint new / pdf / web / checkdecls / all / serve`. **On this machine**, with no TeX installed, the PDF build is impossible, and the web build means compiling pygraphviz against graphviz on Windows, which is a known source of friction (my inference, not tested). [high for the stated requirements; Windows friction is inference]

### 2.2 Projects that used it

- **PFR** (https://teorth.github.io/pfr/blueprint/):
  - a 33-page paper broken into fine-grained nodes and formalized by about 20 contributors in roughly 3 weeks;
  - formalization found an omitted hypothesis (about 2-torsion);
  - Tao: verification "makes large-scale mathematical collaboration possible without necessarily having a pre-established level of trust amongst the collaborators".

  Sources: the PFR tour post and the compilation page. [high]
- **Others.** The FLT project (https://lean-lang.org/use-cases/flt), Sphere Eversion and the Liquid Tensor Experiment, among "over 40" projects listed in the README. Anthropic's FLT run used the community's 86-page blueprint as its scaffold (Anthropic post above). [high/medium]
- **The Equational Theories Project** (https://arxiv.org/abs/2512.07087) settled all 22,028,942 implications between 4694 magma laws, mainly with automated provers (Vampire, Prover9, Mace4, SAT solvers), with Lean as the trust layer (lean4checker, lean4lean). Two lessons:
  - for open problems "the role of the blueprint changed, but it still remained important", with task claiming, CI-enforced locks and dashboards taking over the tracking;
  - human verification of the case analyses was "highly error-prone", and the provers plus Lean revealed "important gaps".

  Note that the ETP paper's contributions are almost all automated provers, not LLMs (I found no LLM-contribution section in the HTML I read). [high]

### 2.3 Status tracking in practice

- **Two status axes in leanblueprint.** The statement axis covers whether it can be stated, is stated, or is not ready. The proof axis covers whether it can be proved, is proved, or is fully proved, meaning every ancestor is proved too. `\leanok` is set when the item's own proof is free of `sorry`, even if an ancestor still depends on one. The "fully proved" colour is the transitive version (https://arxiv.org/abs/2601.22554 describes this inference). [medium-high]
- **LeanArchitect** (https://arxiv.org/abs/2601.22554, ITP 2026) moves blueprint metadata into Lean annotations (`@[blueprint]`), infers dependencies, and exports LaTeX. The motivation: decoupled LaTeX and Lean artefacts create maintenance overhead and "limit integration with AI automation". [medium-high]
- **Prove2Me:** immutable statements, multiple proofs per statement, and missions as atomized proof obligations (https://arxiv.org/abs/2608.28433). [medium]

### 2.4 Does a lighter Markdown equivalent exist, and does it make sense?

- **Existing options**, none of them a mature Markdown-native informal blueprint (I found none):
  - KnowTeX (https://arxiv.org/abs/2601.15294) draws dependency graphs from LaTeX source with no prover required, outputting DOT or TikZ, but still expects LaTeX source.
  - plastexdepgraph is the prover-free core of leanblueprint, but is still LaTeX/plasTeX.
  - Verso (https://github.com/leanprover/verso) is Markdown-like authoring *inside Lean*.
  - "Toward an Engineering of Science" (https://arxiv.org/abs/2605.10425) proposes generic "blueprints" with claims, evidence, assumptions and definitions as typed graph components, and has a prototype. That is conceptually the closest to what you need.

  [medium]
- **Recommendation: yes.** A Markdown/YAML blueprint makes sense for an informal-first workflow on a no-TeX machine. Suggested shape:
  - one Markdown file (or section) per node, with YAML front matter: `id`, `kind` (definition/lemma/proposition/conjecture/example), `statement`, `uses_statement`, `uses_proof`, `status`, `evidence` (locators to exploration scripts, verifier reports, Lean declarations), `supersedes` / `superseded_by`, `interpretation_notes`;
  - math written in `$…$` / `$$…$$`, which renders in Obsidian, Typora and GitHub;
  - the graph drawn by a short Python script that writes Mermaid (renders natively in GitHub and Obsidian) or DOT;
  - leanblueprint vocabulary kept for the formal statuses (`lean:`, `leanok`, `mathlibok`, `notready`), so a later Lean lane can generate a leanblueprint or LeanArchitect project mechanically.

  This is design inference from the sources, not an existing tool.

---

## 3. Failure modes of LLM-generated proofs, and mitigations backed by evidence

### 3.1 Failure modes (with evidence)

| Failure mode | Evidence |
|---|---|
| Confident wrong proofs; fluent prose with no substance | First Proof: confident proofs to every problem, few correct (Scientific American, URL above). Aletheia: 68.5% of graded responses fundamentally flawed (https://arxiv.org/abs/2601.22401). "Proof or Bluff?": under 5% for most models on USAMO 2025 (https://arxiv.org/abs/2503.21934). |
| **Proving false statements on request (sycophancy, motivated reasoning)** | BrokenMath: 504 expert-checked false theorems; best model sycophantic 29% of the time; mitigations "reduce, but do not eliminate" it (https://arxiv.org/abs/2510.04721). Theorist Toolbox: models "will claim to prove a false theorem as readily as a true one" (https://arxiv.org/abs/2606.22337). Tao (compilation page): autoformalizers eagerly prove false statements. |
| Solving an easier reading (specification gaming) | Aletheia: 50 of 63 "technically correct" solutions were trivial because of misinterpretation (https://arxiv.org/abs/2601.22401). QED: models "subtly changed the problem being solved while still producing plausible proof" (https://arxiv.org/abs/2604.24021). The taxonomy paper's "silent problem reformulation" (https://arxiv.org/abs/2606.24902). |
| Hallucinated or misquoted literature | QED: models "fabricate theorem numbers, attribute results to wrong sources, fabricate URLs"; removing standardized citation formats led to "misstated theorems" (https://arxiv.org/abs/2604.24021). |
| **Premise smuggling** (a load-bearing claim asserted as "standard" without justification) | "Failure Modes of Large Language Models on Research-Level Mathematics": none of eight audited proofs had a confirmed fabricated citation, "yet every single one contained at least one load-bearing claim asserted as a 'fundamental result' or 'standard argument' with no justification", so checking citations alone misses it (https://arxiv.org/abs/2606.24902). [medium: small sample] |
| Hand-waving at the crux; effort on easy parts | QED "misallocation of effort" (https://arxiv.org/abs/2604.24021); math-olympiad refutation category 7 (local). |
| Unstable plans (abandoning a route at the first difficulty) | QED (https://arxiv.org/abs/2604.24021). |
| Self-verification failure (a verifier that sees the reasoning agrees with it) | QED "context contamination" (https://arxiv.org/abs/2604.24021). The math-olympiad plugin's #1 lever (local). LLM judges show self-preference bias (various; see Unverified). |
| Unconscious reproduction of known results | Aletheia "subconscious plagiarism"; 8 "open" problems already solved (https://arxiv.org/abs/2601.22401). |
| Exploiting the checker | AlphaEvolve gaming loose float tolerances and a solver failure mode (https://terrytao.wordpress.com/2025/11/05/mathematical-exploration-and-discovery-at-scale/). |
| Formal-statement drift (Lean lane) | Compile versus faithful: 87.2% versus 57.7% for one system (https://arxiv.org/abs/2606.31002). Hypothesis creep, definition-alignment bugs, agents avoiding hard tasks (https://arxiv.org/abs/2603.15929). |
| Polish masking rigor | Theorist Toolbox: the most finished-looking output was the least verified (https://arxiv.org/abs/2606.22337). Tao: AI prose "dwells at length on trivialities" (compilation page, ICM lecture). |

### 3.2 Mitigations and how strong the evidence is

1. **Context-isolated verification.** The verifier sees only the problem plus the cleaned proof, never the trace or other verifiers' verdicts. Used by QED, which names context contamination as a failure mode (https://arxiv.org/abs/2604.24021), by the math-olympiad plugin, and by the math-proof siege workers. The evidence is design-level: the papers report the failure without isolation and adopt isolation. I found no clean controlled ablation. [medium]
2. **Adversarial, pattern-specific verifier prompts** ("try to BREAK it"; a checklist of refutation categories), as opposed to "is this correct?". These come from the math-olympiad plugin, whose patterns are distilled "from real research sessions". QED found that one generalist verifier "dilutes its attention", so it splits verification into structural phases (https://arxiv.org/abs/2604.24021). [medium]
3. **Multiple independent verifiers with conservative aggregation.**
   - MathArena takes the *minimum* of three judges' scores (https://matharena.ai/usamo/).
   - Siege requires two separate verify queries before a goal counts as certified.
   - The olympiad plugin needs 4 "holds" to confirm and 2 "hole found" to refute, with early exit.
   - QED lists a "single-model bottleneck" (different models have different blind spots), and Theorist Toolbox pairs different vendors' models.

   [medium-high]
4. **Prove-or-refute framing, plus a dedicated refuter.** Siege's closing rule asks for "a complete proof of exactly the missing statement... or else an explicit counterexample", and when a missing statement is first posed, one query "tries to REFUTE it exactly as stated" (local). This directly counters BrokenMath-style sycophancy. [medium, design-level]
5. **Interpretation check before solving.** List two or three readings and flag the trivial one. This is the olympiad plugin's step 1, motivated by Aletheia's 50 of 63. [medium-high]
6. **Calibrated abstention.** "Why Language Models Hallucinate" (https://openai.com/index/why-language-models-hallucinate/) argues evaluations reward guessing over abstaining. Its SimpleQA example: a model abstaining 52% of the time made 26% errors, against 75% errors at 1% abstention, at similar accuracy. The olympiad plugin optimizes *conditional* accuracy ("when you say solved, are you right?"). [medium-high]
7. **Inline, greppable gap marks; an honest Status section.** Olympiad `[GAP: …]`; Theorist Toolbox `\unproven{}`; siege "a clearly-marked gap is worth more than a papered-over one". [medium]
8. **Separating conjecture from result in an append-only ledger.** Siege's PROVED/REFUTED/OPEN ledger is never rewritten, only appended with RETRACT lines. The AI co-mathematician "tracks failed hypotheses". [medium]
9. **Exploration and numerical gates before proof.** Covered in section 4. Theorist Toolbox's single unchecked pass was the least trustworthy, while its numerically gated methods caught false claims (https://arxiv.org/abs/2606.22337). [medium-high]
10. **Kernel checking where the statement is human-reviewed.** Covered in sections 1.5 and 6.

---

## 4. Exploration practice: experiment before you prove

- **The classic loop** of computing small cases, guessing, trying to kill the guess, and only then proving appears in nearly every successful AI-assisted case I found:
  - **Erdős #1026:** nine exact values led to a conjectured formula, then to proofs (https://terrytao.wordpress.com/2025/12/08/the-story-of-erdos-problem-126/). [high]
  - **Knuth's note "Claude's Cycles"** (https://cs.stanford.edu/~knuth/papers/claude-cycles.pdf; I could not render the PDF, so details are from https://www.engineerscodex.com/knuth-claude-cycles-open-problem). Claude Opus 4.6 ran about 31 explorations (linear formulas, brute force, simulated annealing, dead ends) before finding a rule for odd m. The rule was verified computationally for odd m from 3 to 101, then proved by hand by Knuth, then formalized in Lean. The even case remains open. This is exactly the status ladder you plan. [medium]
  - **Search-based counterexamples:** "Constructions in combinatorics via neural networks" refuted several lesser-known conjectures with a cross-entropy search (https://arxiv.org/abs/2104.14516). PatternBoost found a counterexample to a 1992 conjecture of Graham on hypercube subgraphs (https://arxiv.org/abs/2411.00566). [medium-high]
  - **AlphaEvolve:** LLM-proposed programs scored by a verifier; the generated code is sometimes interpretable, revealing *why* a construction works (https://arxiv.org/abs/2511.02864). [high]
  - **ETP:** SAT and model-finding tools (Mace4) produced most of the counterexamples (https://arxiv.org/abs/2512.07087). [high]
- **Hygiene rules the sources support:**
  - *Test past the first nontrivial case.* Olympiad pattern 17: small cases are often degenerate, so the claim must survive at least one case beyond the degeneracy (local plugin).
  - *Make the checker non-exploitable:* exact rationals or sympy, interval arithmetic, admissibility checks, and errors raised on invalid inputs (AlphaEvolve post).
  - *Numerical survival is evidence, not proof.* The olympiad worker prompt: "'I computed n=1..10 and the pattern holds' is not a proof" (local). Give "survived search" its own status.
  - *Bound the computation.* Olympiad deep mode: work modulo a number or symbolically when objects grow doubly exponentially; kill runs past 60 seconds (local).
- **Tools that fit economic theory** (my inference, aligned with the cases above):
  - sympy for comparative statics, first-order-condition algebra and identity checks;
  - grid or random search over parameter spaces for counterexamples to monotonicity, single-crossing or uniqueness claims;
  - property-based testing with Hypothesis, which SymPy has integrated into its own test suite (https://labs.quansight.org/blog/integrating-hypothesis-into-sympy). It generates and *shrinks* counterexamples automatically, which suits "for all type distributions F satisfying …" claims;
  - SMT (z3) for finite or discrete claims such as small games, matching markets and mechanisms on finite type spaces.
- **Agent pattern.** The AI co-mathematician gives computational exploration and counterexample search their own sub-agents and workstreams (https://arxiv.org/abs/2605.06651). Theorist Toolbox runs a dedicated refuter in "exploration mode" that returns counterexamples and boundary conditions, not verdicts (https://arxiv.org/abs/2606.22337). [medium]

---

## 5. Anthropic's `math-proof` and `math-olympiad` plugins (read locally)

### 5.1 `math-proof` (solo and siege)

Files: `...\plugins\math-proof\README.md`, `skills\solo\SKILL.md`, `skills\siege\SKILL.md`, `agents\math-proof-judge.md`, `agents\math-proof-worker.md`, `agents\math-proof-worker-deep.md`.

- **solo:** Claude works one problem in-session with no web and no code. It writes the plan and every settled step (lemma, reduction, dead end with reason, current exact statement) to `notes.md` *before reasoning further*, because unwritten reasoning in a truncated response is lost. It ends with a self-contained `proof.md` for "a referee who cannot open any other file".
- **siege:** an orchestrator that does no mathematics and only runs steps. Each step is a fresh sub-agent:
  - a judge plans each round, rewrites a summary of under 6000 words, appends to a **claims ledger** (`PROVED / REFUTED / OPEN: one sentence — locator`, plus `RETRACT N`, with `[GOAL]` and `[AUDIT]` tags), and writes self-contained query files;
  - fresh workers each see *only* their query plus the problem statement, with prior results spliced in verbatim by shell and never paraphrased;
  - a bookkeeping script, not the model, decides which answers are finished (end-line sentinel) and whether the run may conclude.

  Key rules:
  - **Two separate verify queries** must certify the complete written chain before a goal counts. The verify query carries the full argument verbatim and asks for a step-by-step check ending in an explicit verdict.
  - **Targeting rule:** at least half of each round's queries must *attempt* an open question, settling it by proof, refutation or strict reduction. "Established: open" verdicts are not inherited as final.
  - **Chain and missing statement:** after escalation the summary must give the derivation of the goal from PROVED entries plus exactly one missing statement, fully self-contained with all quantifiers and hypotheses. Several identical copies of the "proof or counterexample" task go out in parallel, plus one query that tries to **refute it as stated**.
  - **Progress test:** narrowing to special cases or reformulating is recorded but is *not* progress. When stalled, change your own mechanism or decomposition, not the breadth of the search.
  - **Goal discipline:** replace a goal that is false, ill-posed or already known; raise it after proving it. "Do not swap a goal for a weaker one because it is proving hard."
  - **Retrieval rule:** before relying on or contradicting a prior result, re-read its source file, not the summary's paraphrase.
  - The judge may run Python to "confirm or kill a step: … Checking beats believing."
  - The final `proof.md` has a Status section; an automated grep rejects any reference to run files.
- **Stated caveat (README):** "any result it cites from the literature is quoted from memory: read it critically". Web tools are switched off during runs.

### 5.2 `math-olympiad`

Files: `README.md`, `skills\math-olympiad\SKILL.md`, `references\{adversarial_prompts, verifier_patterns, attempt_agent, solver_heuristics, presentation_prompts, model_tier_defaults, known_constructions}.md`.

- **"The five things that change outcomes":**
  1. strip the thinking before verifying;
  2. ask "does this prove RH?" (proves too much);
  3. for a short proof, extract the general lemma and test a 2×2 counterexample;
  4. if the same gap appears twice, step back;
  5. say "no confident solution".
- **Workflow:**
  1. interpretation check;
  2. 8–12 parallel solvers with varied starting angles, each iterating solve, self-improve, self-verify and correct;
  3. clean the solution (method, proof and answer only);
  4. fresh-context adversarial verifiers with a seven-category refutation taxonomy: step doesn't follow; hypothesis not satisfied; false in a small case; tautological; proves too much; wrong interpretation; hand-wave at the crux;
  5. asymmetric vote (4 to confirm, 2 to refute, early exit) with verifiers blind to each other;
  6. a reviser that sees only the proof and the hole report, marking `[GAP: …]` inline;
  7. a deep-mode agent allowed bounded computation before abstaining;
  8. calibrated abstention;
  9. a separate presentation pass after correctness is established.
- **Verifier patterns worth porting:** #5 (re-derive the hypotheses of every invoked theorem from scratch), #10 (same keywords, different theorem: pointwise versus average, uniform versus almost everywhere), #17 (test past the first nontrivial block), #18 (tautological reduction), #19 (an obstruction that lives in a proxy, not the original object), #23 (a formula's scope never stated), #58 (quantifier direction against domain size), #60 (easiest-interpretation trap).
- **Two cautions about the plugin's own claims:**
  - Its README attributes to "Proof or Bluff" (arXiv 2503.21934) the claim that "85.7% self-verified IMO success drops to <5% under human grading". The primary sources show **two different papers conflated**. 85.7% is the IMO 2025 verification-pipeline result (https://arxiv.org/abs/2507.15855). The under-5% figure is the USAMO 2025 human-graded result in "Proof or Bluff?" (https://arxiv.org/abs/2503.21934), where Gemini-2.5-Pro scored 25%. This is itself an instance of the "misquoted literature" failure mode. [high]
  - Its validation claim ("17/18 IMO+Putnam 2025 problems solved, 0 false positives") points to a non-public repository, so I could not verify it. [unverified]

### 5.3 What transfers to *theory development* and what does not

| Principle | Transfer? | Why |
|---|---|---|
| Write-as-you-go notes and ledger on disk; fresh sub-agent per step | **Yes** | Theory projects are long; the FLT run failed until state was externalized in a DAG (Anthropic post). |
| Append-only PROVED/REFUTED/OPEN ledger with RETRACT and locators | **Yes, generalized** | Becomes the node-status history of the blueprint. |
| Self-contained queries; prior results spliced verbatim | **Yes** | This is what makes a blind verifier possible. |
| Two independent verify passes; asymmetric thresholds | **Yes** | Defines "independently checked". |
| Verifier sees only statement plus cleaned proof | **Yes, refined** | Also give it the *statements* (not proofs) of the nodes it cites, so it can check usage without inheriting reasoning. |
| Pattern-armed adversarial verifier | **Yes, plus economics patterns** | Add: interior versus corner solutions, existence versus uniqueness, ex post versus in expectation, sign conventions in comparative statics, measurability and integrability, tie-breaking, off-path beliefs. |
| Interpretation check | **Yes, renamed "specification check"** | In theory work *you* write the statements, so the risk is a silent change of solution concept, timing or information structure. |
| Prove-or-refute framing; refuter query on every new conjecture | **Yes; central to "no predetermined conclusion"** | Counters sycophancy toward the target. |
| Progress test ("narrowing is not progress") | **Partly** | In theory development, a natural special case *is* often a publishable result; record it as a standing result rather than dismissing it. |
| Single fixed `[GOAL]`; raise or replace only | **Partly** | Theory development has many co-equal nodes and emergent goals. Keep the replace and raise discipline per node; let goals be discovered. |
| Workers: no web, no code | **No** | Exploration needs code, and literature placement matters in economics. Keep "cited from memory = unverified" as a *status*, and verify citations against the source (cf. this repo's primary-source-first rule). |
| Olympiad "NO COMPUTATION" solver prompt | **No** | Competition-specific; your workflow is exploration-first. Keep its point (numerics ≠ proof) as a status rule. |
| Best-of-N numeric vote, known-constructions file | **No** | Single-answer problems. |
| Presentation pass after correctness | **Yes** | Exposition is a separate step; supports Tao's "talk test". |
| Status section in the deliverable | **Yes** | The blueprint's rendered status is the honest summary. |

---

## 6. Design principles for the economist's workflow (each tied to evidence)

1. **Statements are first-class, immutable, ID'd nodes; a reworded statement is a new node.** Old nodes are superseded or retracted, never edited, with each status change logged with a locator. *Evidence:* Prove2Me's immutable statements and multiple proofs (https://arxiv.org/abs/2608.28433); the siege ledger's append-only RETRACT rule (local); the statement-level `\label`/`\uses` of leanblueprint (https://github.com/PatrickMassot/leanblueprint).
2. **Keep separate statuses for the statement, the proof, and the evidence.** Suggested ladder:
   - `conjecture`
   - `survived-search` (numerical or symbolic exploration found no counterexample; record the script and search space)
   - `proved-informally` (the author agent's proof, with gaps marked)
   - `checked` (at least 2 independent blind verifiers passed; the asymmetric rule means 2 dissents refute)
   - `formalized` (Lean statement *human-reviewed* and proof compiles)
   - `kernel-verified` (no `sorry`, standard axioms, external checker)

   Side states: `refuted` (with counterexample), `retracted`, `stalled`, `cited-unverified` / `cited-verified` for imported literature results. Track "fully checked" transitively, as leanblueprint does with "fully proved". *Evidence:* leanblueprint's statement and proof axes and its transitive colouring (PFR tour); the Knuth and Erdős #1026 trajectories (section 4); siege's two-verify certification.
3. **Every open node is a *decision* problem: prove or refute.** Each new conjecture gets one refuter run (counterexample search plus an adversarial agent) *before* any proof attempt, and the proof prompt always allows "here is a counterexample". *Evidence:* BrokenMath's 29% sycophancy on false theorems (https://arxiv.org/abs/2510.04721); Theorist Toolbox's false theorems claimed "as readily as" true ones (https://arxiv.org/abs/2606.22337); the siege closing rule and refute query (local).
4. **Explore before proving, with a checker the generator cannot game.** Use exact or rational arithmetic, admissibility checks, and parameter grids that go past the first nontrivial case. Store the exploration script as the evidence locator. *Evidence:* AlphaEvolve verifier exploits (https://terrytao.wordpress.com/2025/11/05/mathematical-exploration-and-discovery-at-scale/); Erdős #1026 small values then conjecture; olympiad pattern 17; Theorist Toolbox numerical gates.
5. **Run a specification check before work on any node.** Write two or three readings of the statement (solution concept, timing, information, quantifiers, what is held fixed) and flag the trivial one. A verifier checks the proof addresses the *stated* node, not an easier neighbour. *Evidence:* Aletheia's 50 of 63 misinterpretation-trivial answers (https://arxiv.org/abs/2601.22401); QED "problem modification" (https://arxiv.org/abs/2604.24021).
6. **Blind verifiers.** A verifier sees the node statement, the cleaned proof, and the *statements* of cited nodes. It never sees the author's trace, the target "we hope to show", or other verifiers' verdicts, and it is told to break the proof, not grade it. *Evidence:* QED context contamination; the olympiad plugin's dual isolation; siege's self-contained queries (local).
7. **Two or more independent verifications with conservative aggregation, and ideally a second model family.** *Evidence:* MathArena's minimum-of-three jury (https://matharena.ai/usamo/); QED's "single-model bottleneck"; Theorist Toolbox's Claude-plus-Codex pair; siege's two-verify gate.
8. **No smuggled premises: every "standard result" is either a node or a `cited` entry checked against the source.** Literature recall starts as `cited-unverified`. *Evidence:* premise smuggling in every audited proof (https://arxiv.org/abs/2606.24902); QED citation hallucination; the siege README's "quoted from memory"; Erdős literature rediscoveries (wiki URL above).
9. **Gaps are marked inline and kept visible; polish is never evidence.** Defer the exposition pass until nodes are `checked`. *Evidence:* Theorist Toolbox "polish masking rigor"; olympiad `[GAP:]` and presentation-after-verification; Tao on AI prose dwelling on trivialities (compilation page).
10. **Abstaining and stalling are legitimate outcomes, and conclusions emerge from the graph.** A node can end `stalled` with what was established toward it. Do not quietly weaken a target; record a weaker variant as a *new* node. The project's "results" are whatever nodes reach `checked`, not a pre-chosen headline. *Evidence:* "Why Language Models Hallucinate" on rewarding abstention (https://openai.com/index/why-language-models-hallucinate/); siege's goal-discipline rules; the olympiad's conditional-accuracy metric.
11. **External state, fresh agents, small nodes.** All state lives in the blueprint files and an append-only log; each worker and verifier starts fresh from files; nodes are small enough for one session. *Evidence:* FLT agents "lost track of the project's state" until Prove2Me's DAG (https://www.anthropic.com/news/formalizing-fermats-last-theorem); the PFR fine-grained decomposition enabled parallel work; solo and siege write-as-you-go.
12. **The Lean lane is optional, targeted, and statement-reviewed, and a human-understanding gate stays on top.** Formalize only load-bearing nodes, reusing EconCSLib or Mathlib where possible. The economist personally reviews every formal *statement* and *definition*, with "unit test" examples. Treat a sudden run of easy formal successes as a red flag. Finally, every `checked` node must pass Tao's test: the economist can present and defend it without AI. *Evidence:* the compile-versus-faithful gap (https://arxiv.org/abs/2606.31002); hypothesis creep (https://arxiv.org/abs/2603.15929); EconCSLib (https://arxiv.org/abs/2606.16144); Tao's presentation test (https://terrytao.wordpress.com/2026/03/29/mathematical-methods-and-human-thought-in-the-age-of-ai/).

---

## Unverified / uncertain

- **The compilation page.** The Tao quotes in section 1.1 come mostly from https://teorth.github.io/tao-web/ai-views.html, a compiled page on Tao's GitHub Pages site. I did not open each original Mastodon post or comment. Quotes are likely accurate; exact dates and venues are medium confidence. The "New mathematical workflows" PDF (https://terrytao.wordpress.com/wp-content/uploads/2026/06/new-workflows.pdf) could not be rendered here and was not read.
- **The spectral-geometry claim.** A search summary said Tao used Claude over a year as a research partner on a spectral-geometry framework. I could not find a primary source. **Treat as unverified.**
- **First Proof per-system results.** Secondary reports conflict (Scientific American: two correct on the first batch; other reports: a top harness at 6/10, and "7 of 10 at publication quality" per the compilation page). I did not confirm per-batch numbers at https://1stproof.org or https://arxiv.org/abs/2606.18119.
- **FrontierMath Tier 4 scores.** Saturation claims (one model at 97.6% and similar) come only from aggregator sites; Epoch's page as fetched showed no scores. The 48% figure is the co-mathematician paper's own claim.
- **Erdős counts** ("15 moved to solved, 11 crediting AI" and specific model or problem pairings) come from secondary articles. The tracking wiki is authoritative but I did not count entries.
- **Knuth's "Claude's Cycles"** details come from a secondary write-up; I could not render the PDF.
- **Self-preference bias in LLM proof judges** is asserted in benchmark papers surfaced by search (e.g., https://arxiv.org/abs/2604.02450, https://arxiv.org/abs/2602.20629); I did not read them.
- **The causal effect of context isolation.** I found no controlled ablation isolating the effect of hiding the reasoning trace from the verifier. The support is design-level (QED, the plugins) plus the general self-verification failure.
- **The math-olympiad plugin's validation numbers** (17/18, 0 false positives) are unverifiable (private repository). Its README also misattributes figures to "Proof or Bluff" (section 5.2).
- **The Markdown blueprint recommendation** (section 2.4) is my design inference; no existing tool was found that does exactly this.
- **Windows build friction for leanblueprint** (pygraphviz) is inference, not tested; per instructions I installed and ran nothing.
