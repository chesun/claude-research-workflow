---
name: challenge
description: Devil's advocate for research papers and identification strategies. Modes -- paper (contribution, framing, referee objections), --identification (exclusion restriction, parallel trends, instrument validity), --fresh (cold read with no context). Use to stress-test a paper or strategy before submission.
argument-hint: "[file path] [--paper | --identification | --fresh]"
allowed-tools: Read,Grep,Glob
---

# Challenge — Devil's Advocate

Adversarial review that challenges a paper or identification strategy with specific, actionable questions. Unlike `/review`, this is deliberately confrontational — it looks for weaknesses, not strengths.

**Input:** `$ARGUMENTS` — a file path and optional mode flag.

---

## Modes

### `--paper` (default if .tex file)
Challenge contribution framing, identification threats, and referee objections.

**Generate 5-7 challenges from:**

1. **Contribution challenge:** "What does this add beyond [closest existing paper]? Be specific."
2. **Identification challenge:** "Your identifying variation comes from X — but what if X is endogenous to Y?"
3. **Mechanism challenge:** "You show an effect but can't distinguish mechanism A from mechanism B."
4. **External validity challenge:** "Your sample is [specific population] — why should we believe this generalizes?"
5. **Magnitude challenge:** "Your effect size is [X SD] — is that economically meaningful? Back-of-envelope."
6. **Alternative explanation:** "Could [confounder] explain your entire result?"
7. **Missing analysis:** "A referee will ask for [specific robustness check] and you don't have it."

Read `.claude/references/domain-profile-applied-micro.md` for field-specific referee concerns.

### `--identification`
Challenge the identification strategy specifically.

**Generate 5-7 challenges from:**

1. **Exclusion restriction:** "Your instrument Z affects Y only through X — but what about channel W?"
2. **Parallel trends:** "Show me the event study. Do those pre-trends look like noise or a trend?"
3. **Selection:** "Who selects into treatment? Is that selection correlated with outcomes?"
4. **SUTVA:** "Does one unit's treatment affect another unit's outcome? Spillovers?"
5. **Measurement:** "Your treatment variable is measured with error — attenuation bias?"
6. **Compliers:** "Your IV estimates a LATE — who are the compliers? Are they policy-relevant?"
7. **Power:** "You have [N] observations — are you powered to detect a [plausible effect size]?"
8. **Confounders over time:** "Your follow-up is [X years] — what else happened during that window?"

Read `.claude/references/identification-checklists.md` for strategy-specific requirements.

### `--fresh`
Cold read — pretend you have never seen this paper. No access to conversation history or prior context.

1. Read the paper from scratch
2. State in one sentence what the paper claims to show
3. State your top 3 concerns as a first-time reader
4. Identify the single biggest weakness
5. Give a "desk reject or send to referees?" recommendation with reasoning

---

## Output Format

```markdown
# Devil's Advocate: [paper/Strategy Title]
**Mode:** [paper | identification | fresh]
**Date:** [YYYY-MM-DD]

## Challenges

### Challenge 1: [Category] — [Short title]
**Question:** [The specific adversarial question]
**Why it matters:** [What could go wrong / why a referee would raise this]
**Suggested response:** [How you might address this — if you can]
**Severity:** [Fatal / Serious / Manageable]

[Repeat for 5-7 challenges]

## Summary Verdict
**Biggest weakness:** [The one thing that keeps you up at night]
**Strengths to emphasize:** [2-3 things the paper does well]
**Before submitting:** [0-2 must-fix items]
```

---

## Principles

- **Be specific:** Reference exact claims, equations, tables
- **Be adversarial:** Your job is to find problems, not praise
- **Be constructive:** Every challenge has a suggested response
- **Think like a hostile referee:** What would make you recommend rejection?
- **No hedging:** "This is a problem" not "This might be a concern"
