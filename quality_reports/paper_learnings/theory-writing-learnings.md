# Theory Writing Learnings from Papers

**Date:** 2026-03-28
**Sources:** Thomson (1999), Board & Meyer-ter-Vehn (2018), Varian (1997), Halmos (1970), Rubinstein (2006), McCloskey (2019)
**Purpose:** Inform design of theorist agent, theorist-critic agent, writer agent, writer-critic agent, `/theory develop` skill, `/theory review` skill

---

## 1. Paper Structure

- **Introduction:** Place work in context briefly. Describe main findings in plain language. Do NOT start with a 2-3 page survey. Skip technical details.
- **Literature review:** Give priority to development of ideas, not who-did-what enumeration.
- **Model section:** Definitions in logical sequences, each building only on previously defined terms. Present basic concepts in full generality without imposing assumptions needed only for existence.
- **Proofs:** Do NOT relegate to appendices by default. Give informal explanation BEFORE the formal proof.
- **Conclusion:** Do NOT rehash introduction. Instead: compact summary, main lesson, specific open questions, promising future directions.

### Discovery Process
- **Reproduce the discovery process:** Start with simplest version (2 agents, 2 goods, no uncertainty) before generalizing. Simple versions convey central ideas better than general proofs.
- **Learn from your errors:** Where you misunderstood = where readers will struggle.
- **Oscillate between general and particular** throughout exposition.

---

## 2. Notation Conventions

### Do
- **Mnemonic notation:** t for time, l for land, a for alternatives. Every symbol should be guessable.
- **Standard symbols:** ε for small quantities, i for generic individual, R_i for preference, u_i for utility, ω_i for endowment, Y for production set, p for prices, q for quantities.
- **Calligraphic letters for families of sets:** a ∈ A chosen from family 𝒜.
- **Simplify summation bounds:** Write Σx_i instead of Σ_{i=1}^{n} x_i when clear.
- **Define inequality symbols** the first time: x ≥ y means x_i ≥ y_i for all i; x > y means x ≥ y and x ≠ y; x >> y means x_i > y_i for all i.
- **Tell reader what kind of object a symbol is** when introduced (point, set, function, correspondence).

### Don't
- **Don't introduce notation used only once or twice.** A concept needs at least 3-4 uses to deserve its own symbol.
- **Don't use utility notation when only preferences are involved.**
- **Don't use multiple subscripts/superscripts** when avoidable. Use x and y for two agents' bundles instead of x_1, x_2.
- **Don't define important notation in footnotes.** They get skipped.
- **Don't use abbreviations in section headings.**
- **Don't confuse functions with values:** f is the function; f(x) is the value. f can be differentiable, not f(x). Designate functions by f, not f(·).

### Assumption Naming
- **Mnemonic abbreviations:** Not "A1-A3" but "Diff, Mon, Cont" for differentiability, monotonicity, continuity.
- **Watch ambiguity:** "Con" = continuity or convexity? Use "Cont" or "Conv".
- **Order by decreasing plausibility:** Start with least controversial. Group by category (consumers vs. firms).
- **Logical implication in naming:** Strict monotonicity should imply monotonicity should imply weak monotonicity.

---

## 3. Writing Definitions

### Format
- Use **boldface or boldface italics** for new terms: "A function is **monotone** if..."
- Display crucial definitions separately with "Definition" in boldface. But not ALL definitions — focus on critical ones.

### Boundary Examples (Critical)
For every novel definition, provide examples in four categories:
1. Objects that satisfy the definition
2. Objects that do NOT satisfy it
3. Objects that satisfy but barely (boundary cases)
4. Objects that do NOT satisfy but almost do (boundary cases)

Categories 3 and 4 do most of the work in proofs.

### Sequencing
- Each new definition uses only previously defined terms. Never ask readers to wait.
- State dimensionality before introducing consumers or technologies.
- Separate formal definitions from interpretations. Formal models can have multiple interpretations.

### Naming
- **One name per concept.** Pick one, stick with it. Note alternatives in parentheses or footnote.
- **Neutral expressions** that cover various applications over setup-specific terms.
- **One species of agent.** Don't populate paper with individuals, agents, persons, consumers, AND players.
- **"Preference relation" ≠ "utility function."** Don't use interchangeably.

---

## 4. Writing Proofs

### Math-to-English Ratio
- **Optimal: 52-63.5%.** Too much math = incomprehensible. Too much English = imprecise and long.
- **Theorems should be stated in simplest English possible.**

### Structure
- **One-clause sentences** to prevent ambiguities.
- **Logical sequences:** Build each definition on previously defined terms.
- **Informal explanation BEFORE the formal proof,** outside the proof itself. Same for figures.
- **Divide into labeled units:** Step 1, Step 2, Case 1, Subcase 1a, Claim 1. Give titles indicating content if complex.
- **Make similar proof parts obvious.** Write Case 1 perfectly, copy for Case 2 with minimal adjustments. Similarity of phrasing signals reader can skip.
- **If-and-only-if:** Don't say "the if part" and "the only if part." Say "sufficiency" and "necessity." Restate the result in each direction.

### Hypothesis Placement
- **Gather ALL conditions BEFORE the conclusion.**
  - Bad: "If A and B, then D since C."
  - Good: "If A, B, and C, then D."
- **Be specific about which assumptions each step uses.** Not "the above assumptions imply..." but "Assumptions 3 and Part (i) of 4 together imply..."
- **Verify independence of each hypothesis.** Can the result be proved without it?
- **Explore variants:** If A and B imply C, check A', A̅, B', B*.

### Common Mistakes
- **"Clearly" and "obviously":** Errors hide here. After completing paper, search for these words and verify each claim.
- **Don't leave too many steps to reader.** Give complete arguments. Standard manipulations can go in appendix but don't remove entirely.
- **Verify examples exist** satisfying all assumptions. If the class is empty, any statement is vacuously true but useless (try Cobb-Douglas).

---

## 5. Figures and Diagrams

- **Use pictures** even simple ones. They lighten papers, provide relief from algebra, illustrate proof steps.
- **A figure is NOT a substitute for a proof** but can cut reading time by half or more.
- **Label completely:** allocations, prices, endowments. Shade upper contour sets. Draw indifference curves.
- **Venn diagrams** for logical relations between assumptions. Bubble size conveys relative strength.

---

## 6. Style

- **Consistent person/tense.** Don't switch between first singular, first plural, and passive. Use present tense throughout.
- **Choose agent gender once.** For two-person games, make one male and one female — helps keep things straight.
- **Don't start sentences with mathematical notation.** "x designates..." → "Let x designate..."
- **Don't collapse similar statements with parenthetical variants.** State each form separately.
- **Consistent running indices.** Either "for all i ∈ N" or "for all i = 1,...,n" — pick one.
- **Indicate end of proofs clearly.** QED or Halmos square. Delete redundant "This completes the proof."

---

## 7. Theorist Agent Rules

1. Start with simplest version of model before generalizing.
2. Separate formal model from interpretation.
3. Present basic concepts in full generality without extra assumptions.
4. Use mnemonic notation throughout.
5. Write definitions in logical sequences.
6. Generate boundary examples for each definition.
7. State assumptions in decreasing plausibility, grouped by category.
8. Use parallel format for related results.
9. Verify examples satisfying all assumptions exist.

---

## 8. Theorist-Critic Checklist

- [ ] Informal descriptions match formal statements exactly
- [ ] Each hypothesis independently needed (check independence)
- [ ] "Clearly" and "obviously" claims verified
- [ ] Notation introduced before use; nothing defined in footnotes then used in main text
- [ ] Math-to-English ratio in [52%, 63.5%] for proofs
- [ ] Quantifiers unambiguous (negation is trivial operation)
- [ ] All conditions gathered before conclusion
- [ ] Logical sequencing of definitions (no forward references)
- [ ] No notation introduced for single use
- [ ] Assumptions specified precisely in each proof step
- [ ] Consistent terminology (one name per concept)
- [ ] Functions vs. values not confused (f vs. f(x))
- [ ] Variants explored (if A,B→C, check A',B')
- [ ] Boundary examples provided for key definitions
- [ ] Examples satisfying all assumptions exist (non-vacuous)
- [ ] Parallel format for related results
- [ ] Proof divided into labeled, meaningful units

---

## 9. Board & Meyer-ter-Vehn — Paper Architecture for Theory

### The 6 Types of Contribution
1. **Asks a new question** — sometimes the question IS the contribution
2. **Posits a new model** — a sufficiently large conceptual step
3. **Speaks to an important application** — application elevates the theory
4. **Identifies an interesting economic force** — isolates a new feature that changes thinking
5. **Develops new empirical predictions** — explains existing findings
6. **Makes a technical contribution** — new proof methods for open problems

### Canonical Introduction (5 parts)
1. **Broad motivation** (1-2 paragraphs)
2. **The contribution** (1-2 paragraphs) — include "The contribution of this paper is..."
3. **Explain the model** (1-2 paragraphs) — sketch, not formal
4. **Explain your results** (1-2 pages) — for readers who ONLY read the intro
5. **Related work** (1-2 pages) — elaborate YOUR contribution, don't survey. Never criticize explicitly.

### Key Rules
- **"One paper, one model."** Capture variations as parameter comparative statics.
- **If model takes 4 pages to state, simplify.** If 10 theorems, which 3 would survive a cut?
- **Get to main result by page 15.**
- **Theorems should be English-language takeaways that are also mathematically true.** "Define p. Define q. Theorem: Every p is q."
- For each result: (1) remind reader of what's needed, (2) state theorem, (3) prove, (4) state intuition in plain English, (5) state implications.
- **Fewer footnotes than pages.**

---

## 10. Varian (1997) — How to Build a Model

### The KISS Workflow
1. Look for ideas in the **real world** (newspapers, conversations), NOT in journals
2. Identify agents, choices, constraints, equilibrium concept
3. Work the **simplest possible example** first (2 agents, 2 goods, linear utility)
4. Work several more examples. Find the pattern.
5. Write simplest model capturing the pattern. **Then make it even simpler.**
6. Generalize: embed in canonical framework, check robustness
7. Iterate simplify-generalize loop
8. **Delay literature search** — work independently first for originality
9. Model your paper after your seminar — get to the point
10. **Stop when you've made your point.** People remember ~10 pages.

### Key Insights
- "The best notation is no notation" — start with words and examples, not formalism
- **Sculpting metaphor:** Most work is subtracting, not adding. Chip away until the form reveals itself.
- Expect false starts. "If it were easy, it would have already been done."
- **The non-economist test:** Can you explain it to a non-economist? If not, probably not a good idea.
- **Interestingness before correctness.** If it's not interesting, nobody will care whether it's correct.

---

## 11. Halmos (1970) — How to Write Mathematics

### The "Big Table" Method
- Before writing, create a table mapping every concept to its symbol across all alphabets
- Design notation system at the beginning, not ad hoc
- **"The best notation is no notation."** Use words whenever possible.
- Test: "Explain it on a long walk with no paper available; fall back on symbols only when necessary."

### Notation Rules
- **Use no superfluous letters** = use no letter only once = leave no variable free
- Never start a sentence with a symbol
- Include "then" with every "if"
- Do not label/number displays unless referenced later
- Respect frozen conventions (e, i, π, ε, n, z)

### Proof Organization
- **Write proofs forward,** not backward (no "let δ = ε/(3M²+2)")
- For chains of equations: provide prose roadmap explaining strategy before computation
- State theorem FIRST, then prove (no "hanging theorems")
- Theorem statements should be one sentence, ideally short
- **Extract lemmas** from repeated proof patterns
- Acknowledge trivial cases explicitly

### Words vs Symbols
- Never use "any" — ambiguous. Replace with "each" or "every"
- Never use logical quantifier symbols (∀, ∃) in prose
- Distinguish: function vs value, sequence vs set, contain vs include
- "There is no good mathematical reason for using ∀ and ∃ in expository prose"

### Honesty
- **Never bluff.** If proof is cumbersome, say so.
- Signal status of every claim: proved / assumed / conjectured / obvious
- "Obvious" must actually be obvious — verify after letting manuscript ripen

---

## 12. Rubinstein (2006) — Epistemology of Theory

### Models as Fables
- "The word 'model' sounds more scientific than 'fable' although I do not see much difference."
- A good model, like a good fable, strips real-life complexity to clearly discern what cannot always be seen
- Models are not predictive instruments — "we essentially play with toys"
- Influence through culture, not prescription: "A good model can have enormous influence... not by providing advice or predicting the future, but by influencing culture"

### The Four Dilemmas
1. **Absurd conclusions:** All models produce absurd results somewhere. Know where yours breaks.
2. **Response to evidence:** Don't evaluate models primarily by empirical fit. Evaluate by whether they clarify mechanisms.
3. **Modelless regularities:** "I doubt we need preconceived theories to find regularities." Sometimes looking at data with no model is better.
4. **Relevance:** Theory provides conceptual clarification, not actionable policy advice. Formal presentation can obscure moral complexity.

### For the Theorist Agent
- A model should be simple but rich in results with attractive interpretations
- Probe boundary conditions — expect absurd conclusions at extremes
- Look for cognitive processes behind choices (response times, framing), not just choice data
- Be honest about when theory has nothing useful to say about a practical question

---

## 13. McCloskey (2019) — Economical Writing

### Top Rules for Academic Economics Prose

**1. Avoid boilerplate:** Never start with "This paper..." Kill outline paragraphs. Kill "as we shall see."

**2. One word, one meaning:** No elegant variation. Don't rotate synonyms for the same concept. Pick "growth" and stick with it.

**3. Active verbs:** Fight nominalization. "There is a data reanalysis need" → "We must reanalyze our data." Circle every "is" and replace.

**4. Be concrete:** Singulars beat plurals. "Sheep and wheat" beats "natural resource-oriented exports."

**5. Be plain:** Prefer Anglo-Saxon over Latinate. Untie noun piles.

### Anti-Pattern Checklist (Writer-Critic)
- [ ] No "This paper..." openings or outline paragraphs
- [ ] One word per concept (no elegant variation)
- [ ] Active verbs (no nominalization, no "There is/It is")
- [ ] Concrete examples, not abstractions
- [ ] Every paragraph teaches something new
- [ ] Important idea at end of sentence
- [ ] No "not only...but also" (marks incompetence)
- [ ] No vague "this/these/those" — replace with "the" or actual noun
- [ ] Delete unnecessary adverbs (-ly words)
- [ ] Tables/figures have self-explanatory titles
- [ ] No footnotes that should be in main text (or cut entirely)

### Bad Words to Flag
- concept, data (as catch-all), situation, structure, process, individuals
- critique, implement, hypothesize, finalize, state (for "say")
- former/latter, aforementioned, interesting
- fortunately, interestingly, respectively, very
- due to, in terms of

### The Deepest Insight
Bad academic writing comes from fear and status anxiety, not ignorance. The antidote: state the claim plainly, in words your colleague would use over coffee.

---

## 14. Knuth et al. (1989) — Mathematical Writing

### The 27 Rules (Most Actionable)
1. Separate adjacent formulas with words ("Consider S_q, where q < p")
2. Never start a sentence with a symbol
3. No logical symbols (∀, ∃, ⟹) in prose — use words
4. Theorem-introducing sentences must be complete, end with colon
5. Theorem statements must be self-contained
6. "We" = author and reader together; avoid "I" in most technical writing
7. Read aloud for rhythm
8. Don't omit "that" when it helps parsing ("Assume that A is a group")
9. Vary structure but use parallelism for parallel concepts
10. Don't write homework-style (formula lists without commentary)
11. State things twice in complementary ways, especially definitions
12. **Motivate the reader:** "What does the reader know? What do they expect next?"
13. Sentences should flow when formulas are replaced by "blah"
14. Don't reuse notation for different things; be consistent
15. Minimize subscripts — use set notation instead
16. Display important formulas; number all important equations
17. Sentences readable left-to-right without ambiguity

### Proof Presentation (Knuth + Lamport + Halmos)
- **Prefer direct proofs over contradiction** when both available — direct proof is usually cleaner and stronger
- Synchronize reader with goals: insert "We want to show that..." and "Since... we know that..."
- **Lamport's structured proofs:** Write in statement-reason tabular form first, convert to prose if needed. "Don't think about format. Do think about structure."
- Halmos: stream-of-consciousness proofs (contradiction first) don't make best exposition

### Refereeing Criteria
- First criterion: **originality** — genuine advance on previous work?
- Report should contain: complete proof/algorithm, statement of limitations, missing references
- "Referees should try to be teachers"
- Beware "facile generalizations" — mechanical manipulations creating no new insight

### Wilf's Principles
- **Get everything up front** — tell readers in plain English what you're doing. "You can quintuple your readership."
- People scan papers looking for theorem statements. Use bold face.
- Drop notational abbreviations from theorem statements.
- Be chatty leading up to a proof; prove in lean-and-mean style; be chatty after.

### Lamport on Papers
- "Bad writing comes from bad thinking, and bad thinking never produces good writing."
- "It is never a mistake to have too simple an example."
- Examples keep you honest — Lamport revised major theory when draft couldn't handle intended example.

### Writing Quality Tiers
**Hard rules (reject if violated):** No sentence starts with symbol; all variables defined at first use; no logical symbols in prose; formulas separated by words; theorem statements self-contained; consistent notation; important formulas displayed.

**Strong preferences (flag):** Sentences readable L-to-R; flow with formulas as "blah"; direct proofs preferred; proof steps synchronized with reader; definitions stated twice; opening hooks reader.

---

## 15. Cochrane (2005) — Writing Tips for PhD Students

### Triangular/Newspaper Structure
Put the punchline up front. Most readers skim. No reader reads start to finish.

### Introduction Rules (max 3 pages)
- First sentence: state what YOU do — the central contribution
- Must EXPLAIN the contribution concretely ("My results show X" is too vague — give the fact)
- Do NOT start with philosophy, literature, policy motivation, or cute quotations
- Literature review comes AFTER you explain your contribution

### The Golden Rule
> "There should be nothing before the main result that a reader does not need to know in order to understand the main result."

### Body Ordering
- Theory = minimum required to understand empirical results
- Do NOT write general model then specialize — just present what you use
- Empirical section leads with the main result, not data description
- Robustness, preliminary work → appendix
- "A good paper is not a travelogue of your search process"

### Identification (Three Most Important Things)
1. What economic mechanism caused dispersion in RHS variables?
2. What else causes variation in LHS (the error term)?
3. Why is the error uncorrelated with RHS (in economic terms)?

### Style Rules to Enforce
- Flag passive voice (search for "is" and "are")
- Flag: "it should be noted that," "it is easy to show that," "a comment is in order"
- Flag naked "this" without following noun
- Flag "I leave X for future research"
- Flag double adjectives ("very novel," "quite striking")
- Flag fancy words with simpler alternatives ("utilize" → "use")
- Flag >3 decimal places in estimates
- Flag abstract >150 words, introduction >3 pages
- Every table number discussed in text; regression caption includes equation and LHS variable

### Key Quotes
- "Figure out the ONE central and novel contribution. Write this down in one paragraph."
- "Simple is better. The less math used, the better."
- "Explain the economic significance, not just statistical significance."
- "Economics papers are essays. Most good economists spend at least 50% of their time writing."

---

## 16. All Theory/Writing Papers — Status

| Paper | Status | Location |
|-------|--------|----------|
| Thomson (1999) | Read, extracted | `master_supporting_docs/theory/Thomson, William - Guide to Writing Economic Theory_0.pdf` |
| Board & Meyer-ter-Vehn (2018) | Read, extracted | `master_supporting_docs/theory/writingeconomictheory.pdf` |
| Varian (1997) | Read, extracted | `master_supporting_docs/theory/varian-1997-how-to-build-an-economic-model-in-your-spare-time.pdf` |
| Halmos (1970) | Read, extracted | `master_supporting_docs/theory/How_to_Write_Mathematics.pdf` |
| Rubinstein (2006) | Read, extracted | `master_supporting_docs/theory/Econometrica - 2006 - Rubinstein - Dilemmas of an Economic Theorist.pdf` |
| McCloskey (2019) | Read, extracted | `master_supporting_docs/theory/economical-writing-third-edition-thirty-five-rules-for-clear-and-persuasive-prose-chicago-guides-to-writing-editing-and-publishing-9780226448077-9780226448107.pdf` |
| Knuth et al. (1989) | Read, extracted | `master_supporting_docs/theory/knuth_mathematical_writing.pdf` |
| Cochrane (2005) | Read, extracted | `master_supporting_docs/theory/phd_paper_writing.pdf` |

**Highest priority:** Board & Meyer-ter-Vehn (2018) — the most targeted "how to" by active theorists. Complements Thomson: Thomson covers micro-level (notation, definitions, proofs), Board/MtV covers macro-level (paper architecture, theorem as English-language takeaway).
