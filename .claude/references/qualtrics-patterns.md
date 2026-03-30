# Qualtrics Implementation Patterns for Experimental Economics

Portable reference for the qualtrics-specialist agent. Full code examples and detailed analysis in `quality_reports/paper_learnings/jmp-qualtrics-patterns.md`.

---

## Survey Flow Architecture

```
Embedded Data: show_* flags, payment params, platform IDs, runtime vars
  ↓
BlockRandomizer (between-subject factor 1, e.g., worker group)
  ↓
Embedded Data: error counters = 0
  ↓
BlockRandomizer (treatment arm → treat_code + treat_str)
  ↓
BRANCH: show_consent == 1
  → Consent (MC Yes/No) → if No → set consent=0 → END SURVEY
  ↓
BRANCH: show_instr == 1 → Instructions
  ↓
BRANCH: show_quiz == 1
  → Quiz (CustomValidation + JS error counting) → if errors >= 3 → Quiz Failed → END SURVEY
  ↓
BRANCH: show_partN == 1
  → Treatment routing (nested branches on treat_code)
  → Attention checks (record pass/fail in embedded data — NO termination)
  ↓
BRANCH: show_demo == 1 → Demographics
  ↓
set completed=1 → Redirect to platform
```

## Question Types & When to Use

| Type | Code | Use For |
|------|------|---------|
| Descriptive Text | DB/TB | Instructions, JS-powered interfaces, profile displays |
| Multiple Choice | MC/SAVR | Quiz, attention checks, discrete choices |
| Text Entry | TE/SL | Numeric inputs (wage offers, estimates) |
| Constant Sum | CS/VRTL | Distribution elicitation (bins sum to N) |
| Matrix/Bipolar | Matrix/Bipolar | MPL tables (two-sided choice lists) |
| Page Timer | Timing/PageTimer | Response time on every decision page |
| Matrix/Likert | Matrix/Likert | Demographics, scaled responses |

## Validation Types

| Validation | On | Purpose |
|-----------|-----|---------|
| `ForceResponse` | All decision questions | Prevent blank submissions |
| `ContentType: ValidNumber` | TE | Enforce Min/Max/NumDecimals (e.g., wage 0-12 integer) |
| `ChoicesTotal` | CS | Sum constraint (e.g., bins sum to 100) |
| `CustomValidation` | MC quiz | Specify correct answer, show error on wrong |

## JavaScript Patterns

### MPL with Autofill + Single-Switch Enforcement
- Question type: **Matrix/Bipolar** (rows = escalating outside option)
- JS detects switch point, auto-fills subsequent rows
- Custom Next button validates single switch only
- Stores switch row: `setEmbeddedData("switchrow_" + loop, switchRow)`
- Works inside Loop & Merge for per-profile WTP

### Interactive Draw Interface
- Question type: **DB/TB** with custom HTML (`<button>` + `<div id="results">`)
- Draw-without-replacement from hardcoded worker arrays
- Cooldown timer via `setTimeout` (parameterized from embedded data)
- `this.hideNextButton()` until complete, then `this.showNextButton()`

### State Persistence (Base64 JSON)
- Hidden TE question stores state as Base64-encoded JSON
- Hidden via CSS: `#QIDXXX { display: none; }` in Look & Feel
- On load: `JSON.parse(atob(storedBase64))` to restore
- On interaction: `btoa(JSON.stringify(state))` to save

### Quiz Error Counting
- Quiz MC uses CustomValidation (correct answer specified)
- JS `addOnload` detects `.ValidationError` elements
- Increments `errors_quizN` embedded data counter
- Survey flow branches on threshold (e.g., >= 3 → End Survey)

### Profile Generation for Loop & Merge
- JS draws N random profiles from array at section start
- Sets `profileN_name/age/gender/avatar/race` embedded data
- L&M block reads via `${e://Field/profileN_name}` as merge fields
- `${lm://CurrentLoopNumber}` shows progress

### Bonus Calculation
- JS reads switch points / responses from embedded data across rounds
- Randomly selects paying round via `getRandomIntInclusive(1, numRounds)`
- Computes and stores bonus in embedded data for display

## External Asset Hosting

Host images on GitHub Pages to avoid Qualtrics upload limits:
```
https://yoursite.net/asset_hosting_service/avatars/{group}_{gender}_head.jpg
```
Construct URLs dynamically in JS, store `<img>` tags in embedded data, pipe into question text.

## Embedded Data Architecture

| Category | Fields | Set By |
|----------|--------|--------|
| Modular flags | `show_consent`, `show_instr`, `show_quiz`, `show_partN`, `show_demo` | Survey flow (default 1) |
| Testing | `test_response` | Survey flow (default 0) |
| Payment params | `participation_fee`, `hire_bonus`, `quiz_bonus` | Survey flow |
| Platform | `PROLIFIC_PID` | URL parameter (Recipient) |
| Randomization | `treat_code`, `treat_str`, `worker_group` | BlockRandomizer |
| Quiz tracking | `errors_quiz1/2/3`, `quiz_failed` | JS + survey flow |
| Attention | `attention_1_pass`, `attention_2_pass` | Survey flow branches |
| Draw outputs | `draw_count`, `drawn_bins`, `drawn_races`, `draw_duration_sec` | JS |
| State storage | `stored_draws`, `max_draws` | JS |
| Profiles (×N) | `profileN_name/age/gender/avatar/race` | JS |
| Completion | `consent`, `completed` | Survey flow |

## Survey Settings for Experiments

| Setting | Value | Why |
|---------|-------|-----|
| BackButton | false | No strategic revision |
| ProgressBarDisplay | None | No strategic behavior from completion % |
| BallotBoxStuffingPrevention | true | No retakes |
| RecaptchaV3 | true | Bot protection |
| RelevantID | true | Fraud detection |
| SaveAndContinue | true | Handle connection drops |
| SurveyTermination | Redirect | Return to platform |
| EOSRedirectURL | Platform completion URL | Prolific: `https://app.prolific.com/submissions/complete?cc=XXXXX` |

## Custom CSS (Look & Feel)

```css
button { border: none; background-color: #cc9900; color: #ffffff; padding: 5px 10px; }
button:hover { background-color: #FFBF00; }
button:disabled { border: 1px solid #999999; background-color: #cccccc; color: #666666; }
#QID492 { display: none; }  /* hide state-storage questions */
```

## Key Principles

1. **All treatments in one file** with one BlockRandomizer
2. **Attention checks are data, not gates** — record in embedded data, exclude post-hoc
3. **Quiz failures terminate** — consent refusal and quiz failure are the only End Survey triggers
4. **`show_*` flags** wrap each section for modular testing
5. **Hide storage questions with CSS** not Qualtrics visibility
6. **Timing on every page** for response time analysis
7. **No back button, no progress bar** for experiments
8. **Custom JS writes to embedded data** — the bridge between JS and Qualtrics native features
