---
name: qualtrics
description: |
  Create, validate, and improve Qualtrics surveys for experiments. Modes:
  create (generate QSF from design doc), validate (check exported QSF),
  improve (suggest fixes), export-js (generate custom JS/CSS/HTML).
  Dispatches qualtrics-specialist agent.
argument-hint: "[create | validate | improve | export-js] [design doc or QSF path]"
allowed-tools: Read,Grep,Glob,Write,Edit,Bash,Task
---

# Qualtrics

Create, validate, or improve Qualtrics surveys by dispatching the **qualtrics-specialist** agent.

**Input:** `$ARGUMENTS` — mode keyword followed by a design document path or QSF file path.

**Reference docs:**
- Quick reference: `.claude/references/qualtrics-patterns.md`
- Detailed patterns with code: `quality_reports/paper_learnings/jmp-qualtrics-patterns.md`

---

## Modes

### `/qualtrics create [design doc]` — Generate Survey from Design

Translate an experiment design document into a Qualtrics-ready survey specification.

**Agent:** qualtrics-specialist
**Output:** Survey specification + flow diagram + custom JS/CSS if needed

**Workflow:**

1. Read the design document from `quality_reports/designs/` or `experiments/designs/`
2. Read the inference-first checklist for elicitation and comprehension requirements
3. Read `quality_reports/paper_learnings/jmp-qualtrics-patterns.md` for implementation patterns
4. Generate survey specification:

   **Block structure:**
   - Consent (MC Yes/No with ForceResponse → Branch: if No → End Survey, record `consent = 0`)
   - Instructions (DB/TB blocks, treatment-specific variants via display logic)
   - Comprehension quiz (MC with CustomValidation for correct answers + JS error counting → Branch: if errors >= threshold → Quiz Failed block → End Survey)
   - Main task blocks (one per treatment arm, routed via Branch on treatment code)
   - Attention checks (MC, placed at natural breaks; record `attention_N_pass` in embedded data — do NOT terminate on failure)
   - Demographics
   - Debrief / completion

   **Embedded data setup (in survey flow, before randomizer):**
   - `show_*` flags (show_consent, show_instr, show_quiz, show_part1, show_part2, show_demo) — each set to 1 by default, wrap corresponding sections in `Branch: if show_X == 1` for modular testing
   - `test_response` flag (default 0) — mark test vs real responses
   - Payment parameters (participation_fee, bonus amounts)
   - Platform IDs (PROLIFIC_PID as Recipient type)
   - Runtime variables initialized empty (draw_count, stored state, etc.)

   **Randomization:**
   - Use BlockRandomizer in survey flow (SubSet = 1 for between-subject)
   - Each arm sets treatment code as both integer (`treat_code`) and string (`treat_str`) in embedded data
   - All treatments in ONE QSF file with one randomizer — never split across files
   - For 2x2+ designs: nested randomizers or single randomizer with all cells

   **Question types:**
   - DB/TB (Descriptive Text) for instructions, JS-powered interactive interfaces, and profile displays
   - MC/SAVR for quiz, attention checks, discrete choices
   - TE/SL for numeric inputs (wage offers, amounts, estimates)
   - CS/VRTL (Constant Sum) for distribution elicitation (must sum to N)
   - Timing/PageTimer on every decision page for RT collection
   - Matrix/Likert for demographics and scaled responses

   **Custom JS (where needed):**
   - Interactive interfaces in DB/TB questions with HTML buttons and `<div>` containers
   - State persistence via Base64 JSON in hidden TE questions (hidden with CSS `display: none`)
   - `Qualtrics.SurveyEngine.setEmbeddedData()` to write JS outputs into embedded data
   - Cooldown timers parameterized via embedded data

   **Loop & Merge (for repeated tasks):**
   - JS generates merge field values at runtime (e.g., profile attributes → `profileN_name`, `profileN_avatar`)
   - L&M block uses `${e://Field/profileN_name}` as merge fields
   - `${lm://CurrentLoopNumber}` for progress display

   **External assets:**
   - Host images on GitHub Pages or external server to avoid Qualtrics upload limits
   - Construct URLs dynamically in JS using embedded data (e.g., group, gender)

   **Survey settings:**
   - BackButton: false (no going back)
   - ProgressBarDisplay: None (prevents strategic behavior)
   - BallotBoxStuffingPrevention: true
   - RecaptchaV3: true
   - SurveyTermination: Redirect → platform completion URL
   - SaveAndContinue: true (connection drops)

5. Save specification to `experiments/qualtrics/survey_spec_[topic].md`
6. Save any JS/CSS/HTML to `experiments/qualtrics/custom/`

### `/qualtrics validate [QSF path]` — Validate Exported Survey

Check an exported QSF file for common errors and design compliance.

**Agent:** qualtrics-specialist
**Input:** Path to `.qsf` file (exported from Qualtrics)

**Checks:**

1. **Consent flow:** Consent block exists with MC Yes/No → Branch on "No" → End Survey. `consent` embedded data recorded.
2. **Comprehension quiz:** Quiz questions use CustomValidation (correct answer specified). JS error counting present (`errors_quizN` embedded data). Branch: if errors >= threshold → Quiz Failed block → End Survey.
3. **Attention checks:** Present at natural breaks. Record pass/fail in embedded data (`attention_N_pass`). Do NOT route to End Survey — data-only for post-hoc exclusion.
4. **Randomization:** Uses BlockRandomizer in survey flow (not question-level). Treatment code stored in embedded data (both integer and string). All arms in one file.
5. **Treatment routing:** Each treatment arm reachable via Branch on treatment code. No dead branches. Treatment-specific embedded data (e.g., `max_draws`) set before treatment blocks.
6. **Timing:** PageTimer question in every block with decision content.
7. **Modular flags:** `show_*` embedded data flags present. Each major section wrapped in `Branch: if show_X == 1`.
8. **State persistence:** Any DB/TB question with JS that writes to a hidden TE has the TE question hidden via CSS (`#QIDXXX { display: none; }` in Look & Feel custom CSS).
9. **Platform integration:** End-of-survey redirect URL configured (Prolific: `https://app.prolific.com/submissions/complete?cc=XXXXX`). No back button. Ballot box stuffing prevention enabled. reCAPTCHA enabled.
10. **Data quality:** ForceResponse on all MC and TE questions. TE numeric inputs use `ContentType: ValidNumber` with appropriate Min/Max/NumDecimals (e.g., wage offers as integers, score estimates with 2 decimals). Constant Sum questions use `ChoicesTotal` validation to enforce sum constraint. `test_response` flag present.
11. **Design compliance:** Cross-check against design document if available.

Save report to `quality_reports/qualtrics_validation_[topic].md`

### `/qualtrics improve [QSF path or survey spec]` — Suggest Improvements

Review a survey and suggest improvements for clarity, IC, and data quality.

**Agent:** qualtrics-specialist

**Focus areas:**

1. **Question clarity:** Ambiguous wording, double-barreled questions, leading questions
2. **IC compliance:** Elicitation method matches design Step 6 IC requirements
3. **Attention management:** Survey length, cognitive load, question ordering effects
4. **Mobile compatibility:** Screen layout works on phone/tablet if online
5. **Data export quality:** Variable naming, embedded data structure, recoding needs
6. **JS robustness:** Error handling in custom JS, state restoration on page refresh, edge cases (empty arrays, max draws reached)
7. **Pilot readiness:** What to check in a pilot run

Save suggestions to `quality_reports/qualtrics_improvements_[topic].md`

### `/qualtrics export-js [spec]` — Generate Custom JavaScript/CSS

Generate specific custom code for Qualtrics questions.

**Agent:** qualtrics-specialist

**Proven patterns (from JMP survey):**

- **Interactive draw interface:** DB/TB question with button click handler, draw-without-replacement from array, cooldown timer via `setTimeout`, results appended to `<div>`, Next button hidden until complete
- **Base64 state persistence:** Encode draw state (results HTML, remaining deck, draw count) as JSON → Base64, store in hidden TE input. On page load, decode and restore. Hidden via CSS `display: none`.
- **Quiz error counting:** In `addOnload`, detect `.ValidationError` elements matching the incorrect-answer message, increment `errors_quizN` embedded data counter
- **Profile generation for Loop & Merge:** Draw N random profiles from array, set `profileN_name/age/gender/avatar/race` embedded data for each, L&M block reads via merge fields
- **Yoking / matched sequences:** Embed prior participants' response data as JS arrays, randomly select one, replay their sequence
- **External asset URLs:** Construct `<img>` tags with URLs to GitHub Pages hosting (`https://yoursite.net/asset_hosting_service/...`)
- **Custom button styling:** CSS for draw buttons (normal, hover, disabled states)
- **Cooldown timer:** Parameterized via embedded data field, disable button during cooldown with visual feedback

**Standard patterns:**

- **MPL table with autofill + single-switch enforcement:** Matrix/Bipolar question, JS detects switch point and auto-fills subsequent rows, custom Next button validates single-switch, stores switch row in embedded data. Works inside L&M for per-profile WTP.
- BDM mechanism with slider + random price draw + outcome display
- Belief elicitation with probability distribution (Constant Sum)
- Timer with auto-advance
- Custom validation (sum-to-100, range checks)
- Prolific/MTurk completion redirect with piped parameters
- Embedded data manipulation via JS

Save to `experiments/qualtrics/custom/`

---

## Principles

- **Design document is the source.** The survey implements the approved design — don't invent new elements.
- **All treatments in one file.** Use one QSF with one BlockRandomizer for proper randomization. Split files are a workaround for follow-up treatments, not a best practice.
- **Comprehension before task.** Always place understanding checks before the main decision screens. Use CustomValidation for correct answers plus JS error counting.
- **Attention checks are data, not gates.** Record pass/fail in embedded data for post-hoc exclusion. Do NOT terminate the survey on attention check failure. Termination is reserved for consent refusal and comprehension quiz failure only.
- **Always collect RT.** Add Timing/PageTimer to every block with decision content (Brocas et al. 2025).
- **Randomize via survey flow.** Treatment assignment should use BlockRandomizer + embedded data in the survey flow, not question-level randomization — cleaner audit trail and data export.
- **Use `show_*` flags.** Wrap each major section in a conditional branch for modular testing during development.
- **Hide storage questions with CSS.** Hidden TE questions used for JS state persistence should be hidden via `display: none` in Look & Feel custom CSS, not Qualtrics question visibility settings.
- **Test on mobile.** If running online, the survey must work on phone screens.
- **Platform redirect.** Always configure end-of-survey redirect for the recruiting platform. Disable back button and progress bar.

## Pattern Learning

After completing any `/qualtrics validate`, `/qualtrics improve`, or `/qualtrics export-js` task, check the patterns docs for new patterns worth documenting:

1. Read `quality_reports/paper_learnings/jmp-qualtrics-patterns.md`
2. If you encountered a novel Qualtrics technique not already listed (new JS pattern, new question type usage, new validation approach, new flow structure), **append it** as a new numbered pattern
3. If the new pattern is significant enough to be a quick-reference item, also update `.claude/references/qualtrics-patterns.md`
4. This ensures the knowledge base grows with each survey Christina builds
