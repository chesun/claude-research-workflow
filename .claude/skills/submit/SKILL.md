---
name: submit
description: Submission pipeline — journal targeting, replication package, audit, and final gate. Replaces /submit, /target-journal, /audit-replication, /data-deposit.
argument-hint: "[mode: target | package | audit | final] [journal name (optional)]"
allowed-tools: Read,Grep,Glob,Write,Bash,Task
---

# Submit

Submission pipeline with four modes covering journal selection through final verification.

**Input:** `$ARGUMENTS` — mode keyword, optionally followed by journal name.

---

## Modes

### `/submit target` — Journal Targeting
Get ranked journal recommendations.

**Agent:** Orchestrator (journal selection function)

Considers: contribution fit, methodology fit, audience fit, recent publications, desk rejection risk. Consults `.claude/references/domain-profile-behavioral.md` for journal tiers (AEJ:Micro, JEBO, Games and Economic Behavior, JEEA, Experimental Economics, etc.).

Output: Ranked list of 3 target journals with rationale.
Save to `quality_reports/journal_recommendations_[date].md`

### `/submit package` — Build Replication Package
Assemble AEA-compliant replication package for experimental papers.

**Agents:** Coder + Verifier
**Reference:** `.claude/references/replication-standards.md`

Produces:
- Master script (`main.do`) that runs all analyses end-to-end
- README with "computational empathy" (Vilhuber) — written for a stranger to understand
- De-identified data (strip Prolific IDs, MTurk worker IDs, IP addresses, any PII before including). If raw data cannot be shared due to IRB restrictions, provide simulated data that runs with the code.
- Code that does BOTH cleaning AND analysis
- Data documentation and codebook
- **Experimental materials:** instructions PDF, QSF export (if Qualtrics), oTree code (if oTree), IRB approval
- **Pre-registration:** link, ID, date, and compliance cross-check
- Screenshots of key decision screens
- Organized file structure per AEA standards
Save to `replication/`

### `/submit audit` — Audit Replication Package
Verify replication package completeness.

**Agent:** Verifier (submission mode — 10 checks)

Checks:
1. Master script (`main.do`) exists and runs end-to-end
2. All tables reproduce within tolerance
3. All figures reproduce
4. README complete with "computational empathy"
5. Data documentation and codebook present
6. Numbered script order matches README
7. Dependencies listed (Stata packages, Python requirements)
8. Runtime documented
9. Output paths match paper references
10. No hardcoded paths
11. **Pre-registration compliance:** all pre-registered analyses present, deviations noted
12. **Experimental materials included:** instructions, QSF/oTree code, IRB approval
13. **Data de-identified:** cleaned data with PII stripped (no Prolific IDs, MTurk worker IDs, IP addresses) can typically be shared. Raw data with PII should NOT be included — cleaning code bridges the gap.

### `/submit final [journal]` — Final Submission Gate
Full verification + score enforcement + submission checklist.

Workflow:
1. Run comprehensive review if not done recently
2. Run replication audit
3. Check score gate: aggregate >= 95, all components >= 80
4. If PASS: generate cover letter draft + submission checklist
5. If FAIL: list blocking issues and stop

---

## Principles
- **Score >= 95 + all components >= 80. No exceptions.**
- **Don't skip verification.** Even if reports exist, check they're recent.
- **If it fails, stop.** Don't generate materials for a failing paper.
- **Cover letter is a draft.** User must review before sending.
