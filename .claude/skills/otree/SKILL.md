---
name: otree
description: |
  Generate, review, and explain oTree experiment code. Modes: create (scaffold
  app from design doc), review (audit existing code), explain (teach oTree
  concepts). Dispatches otree-specialist agent. oTree 5.x/6.x.
argument-hint: "[create | review | explain] [design doc, app path, or concept]"
allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task,WebSearch,WebFetch
---

# oTree

Generate, review, or explain oTree experiment code by dispatching the **otree-specialist** agent.

**Input:** `$ARGUMENTS` — mode keyword followed by design document path, app path, or concept name.

**oTree version:** 5.x/6.x (latest: 6.0.13). Do NOT use legacy oTree 3.x patterns (no `models.py`, no `pages.py` as separate files — everything in `__init__.py`).

**Resources:**
- Documentation: https://otree.readthedocs.io/en/latest/
- Google Group: https://groups.google.com/g/otree
- Forum (oTree Hub): https://www.otreehub.com/forum/

When unsure about oTree API details, check the official documentation first.

**oTree 6.0 additions** (use when available):
- `async live_method` — for AI/web API integration
- `live_method` on WaitPage — real-time updates while waiting
- `participant.status` — filterable field in admin (useful for dropout tracking)
- `DecimalField` — versatile for currencies, percentages, durations
- Back button support
- Welcome pages for rooms (prevents false participants from link scanning)
- Preserve unsubmitted inputs
- `THOUSAND_SEPARATOR` and `to3`/`to4` template filters for number formatting
- Multiple `custom_export` functions
- **Breaking:** `live_method` cannot be a string anymore (must be a method)

---

## Modes

### `/otree create [design doc]` — Scaffold App from Design

Translate an experiment design into a working oTree 5.x app.

**Agent:** otree-specialist
**Output:** Complete oTree app in `experiments/oTree/`

**Workflow:**

1. Read design document from `quality_reports/designs/`
2. Read `.claude/references/inference-first-checklist.md` for elicitation and timing requirements
3. Scaffold the oTree app:

   **`__init__.py`** — Models + Pages in one file (oTree 5.x pattern):
   - `C` class (constants): num_rounds, players_per_group, participation_fee, treatment names
   - `Subsession` class: `creating_session()` for treatment assignment and group matching
   - `Group` class: group-level variables, `set_payoffs()` if interactive
   - `Player` class: all player fields with `label` and `doc` attributes
   - Page classes: `is_displayed()`, `vars_for_template()`, `before_next_page()`, `live_method()` if real-time

   **Templates** (HTML):
   - Consent page
   - Instructions (from `templates/subject-instructions-template.tex` adapted to HTML)
   - Comprehension quiz with feedback
   - Decision screens (one per elicitation task)
   - Feedback/results screen
   - Demographics questionnaire
   - Debrief page

   **`settings.py`** updates:
   - Session config with treatment parameters
   - Prolific/MTurk integration settings if online
   - `PARTICIPANT_FIELDS` and `SESSION_FIELDS`

4. Add RT collection via `before_next_page()` timestamps on decision pages
5. Add comprehension check loop (retry until correct or max attempts)
6. Save to `experiments/oTree/[app_name]/`

### `/otree review [app path]` — Audit Existing Code

Review oTree code for correctness, design compliance, and best practices.

**Agent:** otree-specialist

**Checks:**

1. **5.x compliance:** No legacy 3.x patterns (`models.py`/`pages.py` split, `Constants` instead of `C`, `FormPage` instead of `Page`)
2. **Design compliance:** Does the code implement the approved design? Treatment arms, elicitation methods, payment structure match?
3. **Randomization:** Treatment assigned in `creating_session()`, not ad hoc. Balanced across groups.
4. **Payment logic:** `set_payoffs()` correctly implements the IC payment scheme. Random round selection if applicable.
5. **Data integrity:** All decision variables stored as Player/Group fields (not just template vars). RT recorded.
6. **Comprehension:** Quiz present before main task, with retry logic.
7. **Platform integration:** Prolific redirect configured, completion code set, SONA credit grant if lab.
8. **Templates:** No raw Python in templates, proper use of `{{ }}` and `{% %}`, mobile-responsive.
9. **Session config:** All parameters in `settings.py`, not hardcoded in `__init__.py`.

Save report to `quality_reports/otree_review_[app].md`

### `/otree explain [concept]` — Teach oTree Concepts

Explain an oTree concept with examples. For when the user is learning or debugging.

**Agent:** otree-specialist

**Common topics:**

- `live_method` — real-time page updates (auctions, bargaining, public goods with live feedback)
- `creating_session` — treatment assignment, group matching, role assignment
- `custom_export` — adding computed fields to data export
- `is_displayed` — conditional page display (skip pages based on treatment/round)
- `WaitPage` — synchronization, `after_all_players_arrive`, group-by-arrival-time
- `ExtraModel` — storing multiple decisions per page (e.g., strategy method, choice lists)
- Prolific/MTurk integration — redirects, completion codes, bonus payments
- `PARTICIPANT_FIELDS` vs `participant.vars` — when to use which
- Group matching — strangers vs partners, `group_randomly()`, `group_like_round()`
- Custom JS in templates — sliders, dynamic elements, validation

Explain with minimal working code examples following oTree 5.x patterns.

---

## Common Experiment Patterns

The otree-specialist knows these standard implementations:

| Experiment Type | Key oTree Features |
|----------------|-------------------|
| Public goods | `Group` payoffs, `WaitPage`, contribution + return |
| Dictator/ultimatum/trust | Two-player groups, sequential pages, `is_displayed` by role |
| Auction (first/second price) | `Group` with bid collection, `set_payoffs` for auction rule |
| Risk elicitation (Holt-Laury) | `ExtraModel` for MPL rows, random row payment |
| Belief elicitation | Custom JS for probability input, validation sum=100 |
| Strategy method | `ExtraModel` for complete contingent strategies |
| Real-effort task | `live_method` for timer + task, piece-rate or tournament |
| Survey experiment | No `Group`, conditional blocks via `is_displayed` |

---

## Principles

- **oTree 5.x/6.x.** Everything in `__init__.py`. No `models.py`/`pages.py` split. Use 6.0 features (DecimalField, participant.status, async live_method) when available.
- **Design document is the source.** The app implements the approved design.
- **Always collect RT.** Timestamps on every decision page via `before_next_page()`.
- **Parameters in settings.** Treatment values, payment rates, and round counts in `settings.py` session config — not hardcoded.
- **Check the docs.** When unsure about API, consult https://otree.readthedocs.io/en/latest/ before guessing.
- **Test locally.** `otree devserver` and walk through as a subject before deploying.
