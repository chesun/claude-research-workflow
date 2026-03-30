---
name: discover
description: Discovery phase combining research interviews, literature search, data discovery, and ideation. Routes to appropriate agents based on arguments. Replaces /interview-me, /lit-review, /find-data, /research-ideation.
argument-hint: "[mode: interview | lit | data | ideate] [topic or query]"
allowed-tools: Read,Grep,Glob,Write,Edit,WebSearch,WebFetch,Task
---

# Discover

Launch the Discovery phase of research. Routes to the appropriate agents based on the mode specified.

**Input:** `$ARGUMENTS` — a mode keyword followed by a topic or query.

---

## Modes

### Default (no mode specified)
If no mode keyword is given, start with an interactive interview to build the research specification.

### `/discover interview [topic]` — Research Interview
Conduct a structured conversational interview to formalize a research idea.

**This is conversational.** Ask questions directly in your text responses, one or two at a time. Wait for the user to respond before continuing. Do NOT use AskUserQuestion.

**Agents:** Direct conversation (no agent dispatch)
**Output:** Research specification + domain profile

Interview structure:
1. **Big Picture** (1-2 questions): "What phenomenon are you trying to understand?" "Why does this matter?"
2. **Theoretical Motivation** (1-2 questions): "What's your intuition for why X happens?" "Do you have a formal model, or is this exploratory?"
3. **Experimental Setting** (1-2 questions): "Lab or online? What's your subject pool?" "Have others run experiments on this question?"
4. **Design Intuition** (1-2 questions): "What's the key comparison — what would convince a skeptic?" "What's your 'dream outcome'? (Niederle)"
5. **Expected Results** (1-2 questions): "What would you expect to find?" "What alternative explanations worry you?"
6. **Contribution** (1 question): "How does this differ from what's been done? What gap are you filling?"

Interview style:
- **Be curious, not prescriptive.** Draw out the researcher's thinking, don't impose your own ideas.
- **Probe weak spots gently.** "What would a skeptic say about...?" not "This won't work because..."
- **Build on answers.** Each question should follow from the previous response.
- **Know when to stop.** If the researcher has a clear vision after 4-5 exchanges, move to the specification.

After interview (5-8 exchanges), produce:

**Output 1: Research Specification** → `quality_reports/research_spec_[topic].md`
```markdown
# Research Specification: [Title]
## Research Question — [one sentence]
## Motivation — [why this matters, theoretical context, policy relevance]
## Hypothesis — [testable prediction with expected direction]
## Empirical Strategy — [experiment type (lab/online/field), key comparison, identification]
## Theory — [formal model if applicable, testable predictions]
## Data — [experimental data structure, subject pool, platform]
## Expected Results — [what the researcher expects and why]
## Contribution — [how this advances the literature]
## Open Questions — [issues needing further thought]
```

**Output 2: Domain Profile** → `.claude/references/domain-profile-behavioral.md` (if still template)
Fill in field, target journals, common data sources, identification strategies, field conventions, seminal references, and referee concerns based on the interview.

### `/discover lit [topic]` — Literature Review
Search and synthesize academic literature.

**Agents:** Librarian (collector) → librarian-critic (reviewer)
**Output:** Annotated bibliography + BibTeX entries + frontier map

**⚠️ MANDATORY AGENT DISPATCH: You MUST use the Agent tool (subagent_type="librarian") to dispatch the librarian agent for the search phase, and then use the Agent tool (subagent_type="librarian-critic") to dispatch the librarian-critic for review. Do NOT do the literature search yourself inline — the agents have specialized prompts and calibration. Skipping agent dispatch violates the worker-critic separation principle.**

Workflow:
1. Read `.claude/references/domain-profile-behavioral.md` for field journals and seminal references
2. Check `master_supporting_docs/` for uploaded papers
3. Read `bibliography_base.bib` for papers already in the project
4. **DISPATCH: Use the Agent tool with subagent_type="librarian"** to search. Include in the agent prompt:
   - The research topic/question
   - The relevant context from steps 1-3
   - Instructions to search in this order:
     - **First: Search Christina's Mendeley library** using `mcp__mendeley__mendeley_search_library` with relevant keywords. This contains papers Christina has already collected and read — these are the most relevant starting points. Search with multiple keyword combinations to ensure coverage.
     - **Second: Search the Mendeley catalog** using `mcp__mendeley__mendeley_search_catalog` for papers not in the personal library.
     - **Third: Search the web** using `mcp__claude_ai_Consensus__search` (Semantic Scholar) and `WebSearch` for recent working papers, NBER, SSRN.
     - **Fourth: Check seminal references** — Read `.claude/references/seminal-papers-by-subfield.md` for canonical papers that must be cited.
   - Target venues:
     - Top-5 journals (AER, Econometrica, QJE, JPE, REStud)
     - Behavioral/experimental field journals (AEJ:Micro, JEBO, Games and Economic Behavior, JEEA, Experimental Economics, JRU, JDM, Management Science)
     - Psychology crossover journals (Psychological Science, Cognition, JEP:General, PNAS) — evaluate with skepticism about inference standards
     - NBER/SSRN working papers
   - **Always check:** Is there existing experimental evidence on this question? (Before proposing a novel study)
   - **Citation chains** — forward and backward citation tracking from key papers
   - Instructions to assign **proximity scores** (1-5) to each paper:
     - **1** — Directly competes (same question, similar method)
     - **2** — Closely related (same question, different method or setting)
     - **3** — Related (overlapping topic, different angle)
     - **4** — Background (provides theory, method, or context)
     - **5** — Tangentially related (useful framing only)
   - Instructions to save results to `quality_reports/lit_review_[topic].md`
5. **DISPATCH: Use the Agent tool with subagent_type="librarian-critic"** to review the librarian's output. Include in the agent prompt:
   - Path to the lit review file the librarian produced
   - Instructions to check: coverage gaps, recency, scope calibration, journal quality, missing seminal papers
6. If librarian-critic identifies gaps, re-dispatch librarian for targeted search (max 1 round)
7. Present the final lit review to the user with the critic's assessment

**Unverified citations:** If you cannot verify a citation, mark the BibTeX entry with `% UNVERIFIED`. Do NOT fabricate or guess citation details. Note when working papers have been published — cite the published version.

Output format for each paper:

```markdown
### [Author (Year)] — [Short Title]
- **Journal:** [venue]
- **Proximity:** [1-5 score]
- **Main contribution:** [1-2 sentences]
- **Method:** [lab experiment / online experiment / field experiment / observational / descriptive]
- **Key finding:** [result with effect size]
- **Relevance:** [why it matters for our research]
```

### `/discover data [requirements]` — Data Discovery
Find and assess datasets for the research question.

**Agents:** Explorer (finder) → explorer-critic (assessor)
**Output:** Ranked data sources with feasibility grades

**⚠️ MANDATORY AGENT DISPATCH: You MUST use the Agent tool (subagent_type="explorer") for the search phase, then use the Agent tool (subagent_type="explorer-critic") for the critique. Do NOT search for data yourself inline.**

Workflow:
1. Read research spec and strategy memo if they exist
2. Read `.claude/references/domain-profile-behavioral.md` for common data sources in the field
3. Understand what variables are needed: treatment, outcome, controls, time period, geography
4. **DISPATCH: Use the Agent tool with subagent_type="explorer"** to search. Include in the agent prompt:
   - The research question and variable requirements from steps 1-3
   - Instructions to search across source categories:
     - Own experimental data (oTree exports, Qualtrics exports, Prolific demographics)
     - Existing experimental datasets (replication packages from published experiments)
     - Public microdata (CPS, ACS, NHIS — for field experiment or complementary analysis)
     - Survey data (RAND HRS, PSID, Add Health, NLSY)
     - Platform-specific: Prolific (demographics, attention metrics), MTurk, university lab pools
   - Instructions to report for each dataset: name, provider, access level, key variables, coverage, feasibility grade (A/B/C/D), strengths and limitations
   - Instructions to save to `quality_reports/data_exploration_[topic].md`
5. **DISPATCH: Use the Agent tool with subagent_type="explorer-critic"** to critique. Include in the agent prompt:
   - Path to the data exploration file the explorer produced
   - Instructions to apply the **5-point assessment** to each dataset:
     1. **Measurement validity** — Does the variable actually measure what we need?
     2. **Sample selection** — Who is in the data? Who is missing?
     3. **External validity** — Can we generalize from this sample?
     4. **Identification compatibility** — Does this data support the proposed design?
     5. **Known issues** — Documented problems with this dataset in the literature
6. Present results with the critic's assessment to the user
7. Save final exploration to `quality_reports/data_exploration_[topic].md`

**Rejected datasets:** Include a rejection table:

| Dataset | Reason for Rejection | Deal-breaker? |
|---------|---------------------|---------------|
| [Name]  | [explorer-critic's finding] | [Yes/No] |

### `/discover ideate [topic]` — Research Ideation
Generate structured research questions and hypotheses from a topic or dataset.

**Agents:** Direct generation (no agent dispatch)
**Output:** Research questions with empirical strategies

Generate:
1. 3-5 research questions with clear hypotheses
2. For each: potential identification strategy, data requirements, expected contribution
3. Rank by feasibility and novelty
4. Save to `quality_reports/research_ideas_[topic].md`

---

## Principles

- **Interview style:** Be curious, not prescriptive. Draw out the researcher's thinking.
- **Literature honesty:** Never fabricate citations. Mark unverified as `% UNVERIFIED`.
- **Proximity scoring:** Always assign 1-5 proximity scores to papers found.
- **Citation chains:** Forward and backward citation tracking is an explicit search vector — do not skip it.
- **Effect sizes matter:** Report magnitudes, not just signs. Note identification strategy for every paper.
- **Data feasibility matters:** A perfect dataset you can't access is useless. Always assign A/B/C/D grades.
- **5-point data critique:** Measurement validity, sample selection, external validity, identification compatibility, known issues. Never skip this.
- **Domain-profile aware:** Always read `.claude/references/domain-profile-behavioral.md` first for field calibration.
- **Worker-critic pairing:** Librarian + librarian-critic, Explorer + explorer-critic. Never skip the critic.
