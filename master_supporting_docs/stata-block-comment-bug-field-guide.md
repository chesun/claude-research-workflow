# Stata Block-Comment Bug Field Guide

**Portable reference for diagnosing and fixing greedy `/*` parsing in Stata projects.**

This guide is self-contained and project-agnostic. It documents a class of silent failure modes in Stata `.do` / `.doh` files caused by the parser's greedy treatment of the `/*` token, and the variants, detection commands, and fixes that close the bug across an entire codebase.

If you've never seen this bug: read Section 1, then run the detection command in Section 3 across your project. If `grep -c '/\*' <file>` is not equal to `grep -c '\*/' <file>` for some file, your project has at least one instance.

---

## Section 1 — Executive summary

### The bug

Stata's parser counts `/*` opens **greedily**. When the character sequence `/*` appears anywhere — including inside an existing `/* ... */` block, inside a `*`-prefixed line comment, or inside a `//`-prefixed line comment — Stata interprets it as a block-comment open token and increments its internal depth counter. The most common source of an unintended `/*` is a path-glob wildcard like `prepare/*` or `$logdir/*` written inside a header description block:

```stata
/* PURPOSE: clean every file under prepare/* and write to $cleandir/*
   ...                                        ^^^ extra /* opens
   ...                                        ^^^ extra /* opens
*/
```

The `/` in `prepare/` followed by the `*` glob creates a literal `/*` digraph. To Stata's parser, that is a nested block-comment open. The closing `*/` of the header now closes only the innermost open; the outer block remains open, and *everything below the header is silently treated as comment*.

### Symptoms

- **Silent script non-execution.** The script "runs" with no error; "end of do-file" reaches the log. But no commands inside the runaway block execute.
- **Missing per-file logs.** If `log using ... .smcl` sits inside the runaway block, no per-file log is produced.
- **Missing output files.** `save`, `export`, `esttab using`, `graph export` all sit unexecuted. Downstream scripts fail at the first `use` of a non-existent input.
- **No error messages on the bugged script.** The pipeline fails downstream, several scripts later, when an expected output is missing.
- **IDE highlighter confirms.** Open the file in a syntax-aware editor; the entire post-header body renders as commented out.

### One-command detection

```bash
# For any single .do file:
opens=$(grep -o '/\*' file.do | wc -l)
closes=$(grep -o '\*/' file.do | wc -l)
[ "$opens" = "$closes" ] || echo "UNBALANCED: $opens opens, $closes closes"
```

Balanced counts are necessary (but not sufficient — see Variant 4). Unbalanced counts guarantee the bug.

### The fix

Inside every comment context (`/* ... */` block, `*`-prefixed line, `//`-prefixed line), replace path-glob `*` with a placeholder like `<x>` (or `<file>`, `<filename>`). The character sequence `/*` is then reserved for legitimate block-comment opens.

Going forward, add a commit-time check: `grep -c '/\*' <file>` must equal `grep -c '\*/' <file>` for every modified `.do` / `.doh` file.

---

## Section 2 — The 8 bug variants

Each variant gets: name, severity, code example showing the bug as written and the parser's depth interpretation, a grep (or state-machine) detection command, and a fix.

Severity tags:

- **Silent** — Stata accepts the file with no error. Behavior changes invisibly.
- **Noisy** — Stata errors out at parse time. Easier to catch; still important to know.

### Variant 1 — Path-glob `*` inside `/* ... */` header block

**Severity:** Silent. The most common variant; in one production project this single variant affected 89 of 129 active files (69%).

**Code as written:**

```stata
/* -----------------------------------------------------------------
 * PURPOSE:  Clean and pool every per-year file under prepare/*
 * INPUTS:   $rawdir/prepare/*.dta
 * OUTPUTS:  $cleandir/pooled.dta
 * ----------------------------------------------------------------- */
use "$rawdir/prepare/2020.dta", clear
save "$cleandir/pooled.dta", replace
```

**Parser's depth interpretation:**

```
/* ...                                            depth 1
   prepare/*                                      depth 2 (greedy /*)
   $rawdir/prepare/*.dta                          depth 3
   $cleandir/pooled.dta                           depth 3
   */                                             depth 2 (close inner)
use ... save ...                                  depth 2 → STILL COMMENTED
EOF                                               depth 2 (unmatched)
```

At end-of-file, depth = 2. Every command after the header sits inside an open block comment and never executes.

**Detection:**

```bash
# Per-file balance check
for f in $(find . -name '*.do' -o -name '*.doh' | grep -v _archive); do
  o=$(grep -o '/\*' "$f" | wc -l | tr -d ' ')
  c=$(grep -o '\*/' "$f" | wc -l | tr -d ' ')
  [ "$o" != "$c" ] && echo "UNBALANCED: $o/$c — $f"
done
```

**Fix:** Replace path-globs with `<x>`:

```stata
/* -----------------------------------------------------------------
 * PURPOSE:  Clean and pool every per-year file under prepare/<x>
 * INPUTS:   $rawdir/prepare/<x>.dta
 * OUTPUTS:  $cleandir/pooled.dta
 * ----------------------------------------------------------------- */
```

### Variant 2 — Path-glob `*` inside `*`-prefixed line comment

**Severity:** Silent. Stata's line-comment-via-`*` syntax does NOT immunize the line against `/*` open detection.

**Code as written:**

```stata
* Process every file in prepare/* and save to $datadir
local files: dir "$rawdir/prepare" files "*.dta"
foreach f of local files {
   use "$rawdir/prepare/`f'", clear
   save "$datadir/`f'", replace
}
```

**Parser's depth interpretation:** The `/` in `prepare/` followed by `*` is read as `/*` → depth becomes 1 mid-line, then never closes (line comments don't open block comments in well-formed code, but the parser counts the digraph anyway). All subsequent lines until the next `*/` are eaten.

**Detection:**

```bash
grep -rE '^\s*\*.*/\*' . --include='*.do' --include='*.doh'
```

This finds `*`-prefixed lines that contain a `/*` substring anywhere on the line.

**Fix:** Same as Variant 1 — replace the path-glob with `<x>`:

```stata
* Process every file in prepare/<x> and save to $datadir
```

### Variant 3 — Path-glob `*` inside `//`-prefixed line comment

**Severity:** Silent. Same mechanism as Variant 2 but with the `//` line-comment prefix instead of `*`.

**Code as written:**

```stata
// Each script writes its log to $logdir/*.smcl
log using "$logdir/myscript.smcl", replace
```

**Parser's depth interpretation:** `$logdir/*.smcl` contains the `/*` digraph. Depth → 1 mid-line, never closes.

**Detection:**

```bash
grep -rE '^\s*//.*/\*' . --include='*.do' --include='*.doh'
```

**Fix:**

```stata
// Each script writes its log to $logdir/<x>.smcl
```

### Variant 4 — Fake nested comment block (the dormant-code trap)

**Severity:** Silent **and** semantically load-bearing. This variant is the one most likely to introduce a regression when fixed naively.

A common legacy pattern: developers use Stata's depth-counting `/*` parser to comment out a block of code that itself contains inner `/* ... */` mini-comments. The outer block is closed by exactly one `*/`; the depth counter takes care of nesting.

**Code as written:**

```stata
/* This is old code — kept for reference
   /* generate mean of vars, excluding don't know */
   gen lowbound = 1
   gen highbound = 4
   foreach v of varlist q1-q10 {
       rangestat (mean) `v', interval(`v' lowbound highbound) by(id)
       rename `v'_mean `v'mean
   }
   //drop the temp vars
*/
```

**Parser's depth interpretation (predecessor — works):**

```
/* This is old code ...               depth 1
   /* generate mean ... */            depth 2 → 1 (inner pair balanced)
   gen lowbound = 1                   depth 1 (dormant)
   ...
   //drop the temp vars               depth 1 (dormant)
*/                                    depth 0 (close outer)
```

All the code between the two outer `/*` and `*/` is dormant — by design.

**The trap when applying a naive fix:** Suppose you run a naive sweep that replaces `/*` inside any comment context with `/<x>`. The inner `/* generate mean ... */` becomes `/<x> generate mean ... */`. Now:

```
/* This is old code ...               depth 1
   /<x> generate mean ... */          depth 0 → the inner */ now closes outer!
   gen lowbound = 1                   depth 0 → CODE NOW ACTIVE
   foreach v of varlist q1-q10 {      depth 0 → CODE NOW ACTIVE
       rangestat ...                  depth 0 → CODE NOW ACTIVE
   }
   //drop the temp vars               depth 0
*/                                    depth -1 → orphan close
```

The previously-dormant code is now active. If those lines compute values that overwrite earlier-computed variables (e.g., a `rangestat`-bounded mean overwriting a simple `egen` mean), the saved dataset's variable values change. The pipeline runs without error but produces different numbers.

**Detection:** Pure grep cannot detect this — the file's `/*` and `*/` counts remain balanced. You need a state-machine pass that walks each `/* ... */` block at depth 0 and reports any block whose inner span (between the open and the matching close) contains additional `/*` or `*/` digraphs:

```python
# Pseudocode — see Section 4 for a full reference implementation
for each /* open at depth 0:
    find matching */ via depth-counting
    inner = text[open_end : close_start]
    if "\n" in inner and ("/*" in inner or "*/" in inner):
        report file + line as Variant-4 risk
```

**Fix:** Before applying any other transform, **flatten** the inner pair so the outer block stays a single flat comment:

```stata
/* This is old code — kept for reference
   /<x> generate mean of vars, excluding don't know <x>
   gen lowbound = 1
   ...
   //drop the temp vars
*/
```

The inner `/* ... */` pair is rewritten to `/<x> ... <x>` (note: both the open and close get rewritten; replacing only the open leaves an orphan `*/` that still closes the outer). After flattening, the outer block reads as a single flat comment with no nesting risk, and the depth-counter behavior is preserved post-sweep.

### Variant 5 — Orphan `*/` (predecessor parser-bug masked an unmatched close)

**Severity:** Noisy after the upstream sweep — but only after. In a buggy codebase, an orphan `*/` may sit harmlessly inside a runaway block opened by a Variant 1 instance upstream. Once you fix Variant 1, the orphan becomes a real syntax error.

**Code as written:** Somewhere mid-file:

```stata
sort id

*/

gen newvar = 1
```

The `*/` is orphan — no matching `/*` opens it. In a codebase that already has a Variant 1 bug upstream, this orphan happily closes whatever block was hanging open, so the script "works." After you fix the upstream Variant 1, the orphan has nothing to close and Stata errors at parse time.

**Detection:**

```bash
# Find lines that are only whitespace + */
grep -rnE '^\s*\*/\s*$' . --include='*.do' --include='*.doh'
```

This finds candidate orphan-close lines. False-positive rate: each match must then be verified to lie at code-state depth 0 (not inside a legitimate block). A state-machine depth scan confirms which candidates are real orphans.

**Fix:** Strip the orphan-close line entirely:

```stata
sort id

gen newvar = 1
```

### Variant 6 — `*/` followed by path-continuation character

**Severity:** Silent. Edge case of Variants 1-3 where the closing `*/` is followed by additional path syntax, e.g., `*/<sub>`.

**Code as written:**

```stata
/* INPUTS: $rawdir/calschls/{a,b}/*/<student>.csv
   ...
*/
```

The substring `{a,b}/*/<student>.csv` contains both a `/*` (read as open) and a `*/` (read as close), but the depth-count is rebalanced within the same line. The risk is that a naive single-character fix or a regex that catches `*/` at end-of-line misses this inline case.

**Detection:**

```bash
# Find */<alphanum or <$> > inside comments — likely path-globs
grep -rnE '\*/[A-Za-z0-9_<${]' . --include='*.do' --include='*.doh'
```

**Fix:** Rewrite the entire path-glob expression to use placeholders:

```stata
/* INPUTS: $rawdir/calschls/{a,b}/<x>/<student>.csv
   ...
*/
```

The `*/` between `{a,b}` and `<student>` becomes `<x>/`.

### Variant 7 — `//*` decorative banner overlap

**Severity:** Mostly cosmetic but trips naive grep-balance checks.

**Code as written:**

```stata
//*****************************************************
//* SECTION: load and clean
//*****************************************************
```

**Parser's interpretation:** Stata sees `//` and opens a line comment; the `*` is inside the line comment and harmless to the parser. But `grep -c '/\*'` counts substring occurrences agnostic of context. Every `//****...` contributes one `/*` match (at the `/` + `*` boundary inside the banner) with no matching `*/`. So the file's balance check fails even though Stata's parser is fine.

**Detection:**

```bash
grep -rnE '//\*' . --include='*.do' --include='*.doh'
```

**Fix:** Insert a space between `//` and the `*`:

```stata
// ****************************************************
// * SECTION: load and clean
// ****************************************************
```

Semantically equivalent to Stata (`//` opens the line comment regardless of trailing space); restores grep-balance.

### Variant 8 — Over-flatten bug in fix-tool pre-pass (round-2 trap)

**Severity:** Silent. The variant is *introduced* by an incorrect Variant-4 fix tool, not by the source code itself. After the fix-tool sweep runs, formerly-correct files become broken: legitimate `/* ... */` body blocks lose their close markers, and the file enters a runaway block comment for everything downstream of the failed close. The pipeline appears to have been "swept clean" yet still fails — often more confusingly than the original Variant 1 failure, because the file's grep-balance check still PASSES post-sweep (the bug preserves balance — it just shifts WHERE close happens).

This variant is the round-2 failure mode of a Variant-4 fix tool. It happens when the tool's depth-counted matcher (used to find "multi-line outer blocks") naively treats every `/*` and `*/` digraph as a real block marker — including path-glob fragments. In files where the outer header `/* ... */` contains path-glob substrings (e.g., `$logdir/*.smcl`, `prepare/*`, `do/**/<sub>`), the inflated depth count walks past the real header close. The tool then declares some later `*/` (typically a stray inside a `*` line-comment further down the file) the "matching close" — and blanket-rewrites every digraph in the over-extended inner span.

**Code as written (pre-sweep — already correct):**

```stata
/*------------------------------------------------------------------------------
 * PURPOSE:  clean qoi for one year; outputs go to $logdir/* and $datadir/*
 * INPUTS:   $datadir_clean/calschls/secondary/sec1415  (CHAIN read)
 * OUTPUTS:  $logdir/data_prep/qoiclean/secondary/secqoiclean1415.smcl
 *------------------------------------------------------------------------------*/

log using "$logdir/data_prep/qoiclean/secondary/secqoiclean1415.smcl", ...
use $datadir_clean/calschls/secondary/sec1415, clear

/* Note: 1415 dataset does not have qoi 27-30 */
foreach i of numlist 14/18 {
  local j = `i' + 8
  rename a`i' qoi`j'
}

* count the total number of responses in each school */
sort cdscode
by cdscode: gen totalresp = _N
```

Stata's parser handles this correctly (the `*/` at the end of line `* count ...` line-comment is harmless — line-comment terminates at newline).

**Buggy post-sweep (over-flattened — the tool over-walked):**

```stata
/*------------------------------------------------------------------------------
 * PURPOSE:  clean qoi for one year; outputs go to $logdir/<x> and $datadir/<x>
 * INPUTS:   $datadir_clean/calschls/secondary/sec1415  (CHAIN read)
 * OUTPUTS:  $logdir/data_prep/qoiclean/secondary/secqoiclean1415.smcl
 *------------------------------------------------------------------<x>     <-- header close LOST

log using ...                          (now inside runaway block)
use ... sec1415, clear                 (now inside runaway block)

/<x> Note: 1415 dataset does not have qoi 27-30 <x>      <-- body comment broken
foreach i of numlist 14/18 {           (now inside runaway block)
  ...
}

* count the total number of responses in each school <x>
sort cdscode
by cdscode: gen totalresp = _N         <-- never executes; OR if prior script left totalresp defined, errors r(110)
```

The header close at line 40 became `<x>` (the trailing `*/` got blanket-rewritten). Lines 44, 73, 74, 80 — all legitimate single-line `/* ... */` body blocks — got mangled into `/<x> ... <x>` non-comment syntax. Stata sees the runaway block, treats lines 2-87 as one giant block comment, then exits the block at line 87 (the stray `*/` that the depth-counter had landed on) and tries to execute line 88+ in an inherited dataset state. Result: `gen totalresp` errors at r(110) "totalresp already defined" — because the prior script in the pipeline left totalresp in memory, and the supposed `clear all` + `use` of THIS script never ran.

**Detection:**

```bash
# Files where the fix tool over-flattened: balance check still PASSES, but
# header close markers have been mangled. Symptom 1: header separators ending
# in <x> instead of */.
grep -rnE '^-+<x>$' . --include='*.do' --include='*.doh'

# Symptom 2: lone <x> on otherwise-empty line (legitimate single-line body
# block whose close got blanket-rewritten).
grep -rnE '^[[:space:]]*<x>[[:space:]]*$' . --include='*.do' --include='*.doh'

# Both should return 0 hits in a correctly-swept tree.
```

The tree-wide `/*` vs `*/` balance check **still passes** after this bug fires — the tool preserves digraph counts; it just shifts where the close happens. So per-file balance is not sufficient. The two grep patterns above catch the placeholder artifacts the over-flatten leaves behind.

**Root cause:** the fix tool's pre-pass used greedy depth-counted matching to find "multi-line outer blocks", then blanket replaced every `/*` and `*/` digraph in the inner span via `inner.replace("/*", "/<x>").replace("*/", "<x>")`. The depth counter saw path-glob `/*` inside the outer header (e.g., `$logdir/*` on the OUTPUTS doc-line) and incremented past zero when the real header close arrived. The matcher then walked forward to a "deeper" close — typically a stray `*/` further down (e.g., the line-end of `* count ... */`). The blanket replace inside that over-extended span then destroyed legitimate body block markers.

**Fix pattern:** distinguish path-glob digraphs (`/*` preceded by a path-continuation char, `*/` followed by a path-continuation char) from real block markers (whitespace-/punctuation-/EOF-adjacent). Two predicates:

```python
_PATH_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_<>${}.-"

def _is_path_glob_open(text, i):
    """/* at position i is a path-glob iff the char before it is a path char."""
    if i == 0:
        return False
    return text[i - 1] in _PATH_CHARS

def _is_path_glob_close(text, i):
    """*/ at position i is a path-glob iff the char after it is a path char."""
    if i + 2 >= len(text):
        return False
    return text[i + 2] in _PATH_CHARS
```

Apply in two places:

1. **Depth-counted matcher:** skip path-glob digraphs when counting depth. Only real block-comment opens / closes change depth. This fixes the matcher overshooting into a stray `*/` further down the file.
2. **Inner rewriter:** replace blanket `inner.replace("/*", "/<x>").replace("*/", "<x>")` with a context-aware walker that distinguishes path-glob from real block markers and leaves path-glob fragments intact (the main pass downstream handles them via its own state machine).

```python
def _rewrite_inner_block_markers(inner):
    """Walk inner char-by-char; rewrite ONLY genuine block /* and */ markers."""
    n = len(inner)
    out, i = [], 0
    while i < n:
        if i + 1 < n and inner[i] == "/" and inner[i+1] == "*":
            out.append("/*" if _is_path_glob_open(inner, i) else "/<x>")
            i += 2
            continue
        if i + 1 < n and inner[i] == "*" and inner[i+1] == "/":
            out.append("*/" if _is_path_glob_close(inner, i) else "<x>")
            i += 2
            continue
        out.append(inner[i])
        i += 1
    return "".join(out)
```

**Reference implementation:** `py/sweep_comments_and_logdirs.py` evolution captures the three rounds:

- **Round 1 (2026-05-17):** narrow pre-pass regex `r'/\*[ \t]*\n'` matched only lone `/*\n` openers. Missed 5 files with `/* <text>\n` outer openers. Variant 4 dormant code activated.
- **Round 2 (2026-05-17):** state-machine pre-pass replaced the narrow regex, but used greedy depth-counting + blanket `inner.replace(...)`. Closed Round 1's miss, but introduced Variant 8 on 2 files (sec1415, sec1617) where path-globs in the outer header inflated the depth.
- **Round 3 (2026-05-18):** path-glob-aware depth-counting in `_find_matching_close` + context-aware inner rewriter in `_rewrite_inner_block_markers`. Closes Variant 8.

The lesson: a Variant-4 fix tool must distinguish path-glob `/*` and `*/` from real block markers EVERYWHERE — both in the depth-counted matcher AND in the inner-rewrite. Blanket replacement is the trap.

---

## Section 3 — Detection at scale (cross-project sweep)

The following commands run against any Stata project root and surface every variant.

```bash
# Variant 1 — per-file /* / */ count imbalance
for f in $(find . -name '*.do' -o -name '*.doh' | grep -v _archive); do
  o=$(grep -o '/\*' "$f" | wc -l | tr -d ' ')
  c=$(grep -o '\*/' "$f" | wc -l | tr -d ' ')
  [ "$o" != "$c" ] && echo "UNBALANCED: $o/$c — $f"
done

# Variant 2 — *-prefixed line comments containing /*
grep -rE '^\s*\*.*/\*' . --include='*.do' --include='*.doh'

# Variant 3 — //-prefixed line comments containing /*
grep -rE '^\s*//.*/\*' . --include='*.do' --include='*.doh'

# Variant 4 — fake nested comment blocks (requires state-machine; see Section 4)
# No pure-grep detection. Run the reference implementation or equivalent.

# Variant 5 — orphan */ on otherwise-empty line
grep -rnE '^\s*\*/\s*$' . --include='*.do' --include='*.doh'

# Variant 6 — */ followed by a path-continuation char
grep -rnE '\*/[A-Za-z0-9_<${]' . --include='*.do' --include='*.doh'

# Variant 7 — //* decorative banner overlap
grep -rE '//\*' . --include='*.do' --include='*.doh'

# Variant 8 — over-flatten artifacts left by a buggy Variant-4 fix tool
grep -rnE '^-+<x>$' . --include='*.do' --include='*.doh'
grep -rnE '^[[:space:]]*<x>[[:space:]]*$' . --include='*.do' --include='*.doh'
```

Combine the outputs to triage. Variants 1, 2, 3, 6 are subclasses of the same root cause (path-glob `*` in comment context). Variants 4 and 5 require attention regardless of whether Variants 1-3 are present. Variant 7 is cosmetic but worth fixing for grep-balance hygiene. Variant 8 is post-sweep regression detection — run after applying a Variant-4 fix tool to confirm the tool didn't over-flatten.

---

## Section 4 — Canonical fix algorithm (state-machine helper)

A naive `sed` or single-regex pass cannot solve this. The fix must distinguish:

- Legitimate `/*` at depth 0 in `code` state (preserve)
- `/*` at depth ≥ 1 (rewrite to `/<x>`)
- `/*` inside a `*`-line comment or `//`-line comment (rewrite to `/<x>`)
- `/*` inside a string literal (preserve verbatim — Stata strings can contain anything)
- `*/` that legitimately closes a block (preserve, state → `code`)
- `*/` that's a path-glob fragment (rewrite to `<x>/` or `<x>`)
- Multi-line `/* ... */` blocks whose inner span contains nested `/*` or `*/` (flatten the inner pairs **before** the main pass, to avoid Variant-4 dormant-code activation)

### Language-agnostic algorithm

The helper has three passes:

**Pre-pass: flatten inner pairs in multi-line blocks (prevents Variant 4)**

```
walk text forward
state = code | string
at every depth-0 /* open in code state:
    use PATH-GLOB-AWARE depth-counting:
      - every real /* (not a path-glob fragment) → +1
      - every real */ (not a path-glob fragment) → -1
    to find matching */
    inner = text between open_end and close_start
    if inner spans multiple lines AND contains nested /* or */:
        walk inner char-by-char, rewriting ONLY genuine block markers:
          - real /* → /<x>
          - real */ → <x>
          - path-glob /* and */ → leave intact
```

Critical Variant-8 prevention: both the depth-counted matcher AND the inner rewriter must distinguish path-glob digraphs from real block markers. Blanket `inner.replace("/*", X).replace("*/", Y)` is the wrong pattern; it over-flattens legitimate body block markers when the depth counter has overshot.

**Main pass: rewrite path-globs in comment state**

```
walk text forward character-by-character
state = code | block | line_star | line_slash | string
at each char:
    code + /*       → state=block,       emit /*       (legitimate open)
    code + //       → state=line_slash,  emit //
    code + *      } (at line start)
                    → state=line_star,   emit *
    code + "        → state=string,      emit "
    block + /*      → emit /<x>          (SPURIOUS — inside block already)
    block + */ followed by [A-Za-z0-9_<${*]
                    → emit <x>/          (path-glob, NOT close)
    block + */ followed by whitespace/punct/EOF
                    → state=code, emit */ (legitimate close)
    line_star + /*  → emit /<x>          (SPURIOUS — inside line comment)
    line_slash + /* → emit /<x>          (SPURIOUS — inside line comment)
    line_* + \n     → state=code, emit \n
    string + "      → state=code, emit "
    string + *      → emit verbatim       (strings inviolate)
```

**Post-pass: strip orphan `*/` (handles Variant 5)**

```
scan candidate lines via regex: ^\s*\*/\s*$
for each candidate, compute the file's depth map and confirm depth==0 at the */
strip the entire line (including newline)
```

### Why the pre-pass must be a state-machine, not a regex

An early implementation of the reference tool used a narrow pre-pass regex (`r'/\*[ \t]*\n'`) that matched only lone `/*\n` outer-opener lines. It missed openers of the form `/* Note: <comment text>\n` and `/* This is old code\n`. The result: the main pass half-rewrote the inner `/* ... */` pair (open → `/<x>`, close untouched), and the retained `*/` then prematurely closed the outer block — activating dormant code.

The correct approach: forward-walk in `code` state, and at every depth-0 `/*` open, use depth-counted matching to find the closer. Inspect the inner span verbatim. Don't try to anchor on the form of the opener line.

### Why the depth-counted matcher and the inner rewriter must both be path-glob aware

A round-2 implementation correctly switched to the state-machine pre-pass, but kept naive depth counting (every `/*` and `*/` digraph counted as a depth change). In files where the outer header contained path-glob substrings (e.g., `$logdir/*`, `prepare/*`), the depth counter inflated past zero when the real header close arrived. The matcher then walked forward looking for a "deeper" close and landed on a stray `*/` further down the file. The inner rewriter, which used blanket `inner.replace("/*", "/<x>").replace("*/", "<x>")`, then destroyed legitimate `*/` body block closes in the over-extended span.

The Variant 8 fix: both the matcher and the rewriter must use the same path-glob predicates. Real block markers are whitespace-/punctuation-/EOF-adjacent; path-glob fragments are surrounded by path-continuation chars. The two predicates `_is_path_glob_open` and `_is_path_glob_close` encode the heuristic; the matcher skips them when counting depth; the rewriter leaves them intact (the main pass downstream rewrites them correctly via its own state machine).

### Critical invariants

- **String-literal protection.** `/*` and `*/` inside `"..."` are literal characters and must not transition state. Track string state in both the pre-pass and the main pass.
- **Process in reverse for in-place rewrite.** When the pre-pass collects spans `(inner_start, inner_end)`, apply rewrites in reverse so earlier rewrites don't invalidate later offsets.
- **Multi-line filter on pre-pass.** Single-line `/* foo */` blocks have no nesting risk; the pre-pass should only flatten blocks where the inner span (a) spans multiple lines AND (b) contains nested `/*` or `*/`.
- **Path-glob awareness in BOTH matcher and rewriter.** See "Why the depth-counted matcher and the inner rewriter must both be path-glob aware" above. Missing this in either place produces Variant 8.

### Reference implementation

The full Python implementation is at `py/sweep_comments_and_logdirs.py` in the va_consolidated project (≈700 lines). The load-bearing functions:

- `_is_path_glob_open(text, i) -> bool` — path-glob predicate (open)
- `_is_path_glob_close(text, i) -> bool` — path-glob predicate (close)
- `_find_matching_close(text, open_end) -> int` — depth-counting matcher (path-glob aware as of round 3)
- `_rewrite_inner_block_markers(inner) -> str` — context-aware inner rewriter (replaces blanket `inner.replace(...)` as of round 3)
- `_flatten_lone_block_opens(text) -> (text, n_rewrites)` — pre-pass
- `transform_comment_globs(text) -> (text, n_replacements)` — main pass
- `strip_orphan_block_closes(text) -> (text, n_stripped)` — post-pass

The implementation is permissively licensed (MIT-equivalent) and portable. Adapt to any language by mirroring the three passes and respecting the invariants above.

---

## Section 5 — Convention rules (preemptive)

To prevent re-introduction, codify two rules in your project's conventions.

### Rule 1 — Wildcards in comments

```text
Inside any Stata comment context — /* ... */ block, *-prefixed line, or
//-prefixed line — do not use * as a path-glob wildcard. Use <x>
(or <file>, <filename>) as the placeholder.

The character sequence /* is reserved for legitimate block-comment opens.
Stata's parser counts /* opens greedily and treats them as state transitions
regardless of context — including inside an existing /* ... */ block, inside
a // line comment, and inside a *-prefixed line comment. An extra /* from a
path-glob like `prepare/*` inside a header description creates a runaway
nested block comment that silently swallows large portions of the file.
```

Before-and-after examples:

| Before (bug pattern) | After (fixed) |
|---|---|
| `$logdir/*` | `$logdir/<x>` |
| `prepare/*` | `prepare/<x>` |
| `do/**/*.do` | `do/<x>/<x>.do` |
| `$datadir/calschls/{a,b}/*` | `$datadir/calschls/{a,b}/<x>` |

### Rule 2 — Commit-time balance check

Add to your pre-commit checklist:

```text
- [ ] /* balance — for every modified .do/.doh file in the commit:
      grep -c '/\*' <file> must equal grep -c '\*/' <file>.
      Imbalance indicates a path-glob * was written inside a comment,
      which Stata's parser will greedily treat as a /* open and create a
      runaway block comment that silently hides downstream code.
```

Both rules together cover the steady state: Rule 1 tells authors what to write, Rule 2 catches violations at commit time. The runtime invariant (checking that every script produced its expected output) is a downstream defense but is too late — by the time the runtime invariant fails, the pipeline has already broken.

Recommended for any forking project: adopt both rules verbatim. They are project-independent.

---

## Section 6 — Common false fixes that DON'T work

Patterns to avoid based on real-world attempts:

| Attempted fix | Why it fails |
|---|---|
| **Naive `sed 's|/\*|/<x>|g'`** | Catches legitimate block-comment opens too. After sweep, every `/* HEADER */` becomes `/<x> HEADER */`, leaving an orphan close everywhere. |
| **Pre-pass regex `r'/\*[ \t]*\n'`** | Matches only lone `/*\n` openers; misses `/* <text>\n` openers. Variant 4 dormant code gets activated. The pre-pass must use a state-machine depth-walk. |
| **Runtime invariant `check_comments.do`** | Catches the bug AFTER the pipeline already broke. The bug must be caught at commit time, not at runtime. |
| **Restructure block headers only** (eliminate `/* */` blocks in favor of `*` line comments) | Doesn't fix Variants 2 and 3 — `*`-line and `//`-line comments are also vulnerable. You'd need to additionally rewrite the path-glob `*` anyway. Strictly more work for no marginal safety. |
| **Treat `*/` in `block` state as always-close** | Misses Variant 6 (`*/<sub>` is a path-glob fragment, not a close). The fix tool must heuristically distinguish via the character following `*/`. |
| **Replace only inner `/*` with `/<x>` in pre-pass** | Half-rewrite — leaves orphan `*/`. The pre-pass must rewrite **both** the inner open and the inner close to maintain depth-counter equivalence. |
| **One-pass solution** | All three passes (pre-pass flattening, main-pass rewriting, post-pass orphan strip) are needed. Single-pass solutions miss at least one variant. |
| **Pre-pass that finds multi-line outer block via greedy depth-counting + blanket `inner.replace("/*", X).replace("*/", Y)`** | Over-flattens (Variant 8). Catches legitimate `*/` block closes and `/* ... */` single-line body blocks. The depth counter overshoots when path-glob `/*` substrings live inside the outer header; the blanket replace then destroys legitimate body block markers in the over-extended inner span. Result: runaway block comment AFTER the supposedly-corrective sweep, with grep-balance still passing. Use a context-aware walker (path-glob-aware depth count + path-glob-aware inner rewriter) instead. |

---

## Section 7 — Empirical evidence (case study)

The va_consolidated project (an applied-econ research codebase, ~129 active `.do`/`.doh` files at the time of the 2026-05-17 sweep) hit this bug at scale. Headline numbers:

- **89 of 129 active files (69%) had unbalanced `/*` vs `*/` counts** before the sweep.
- Top offenders: one file had 40 opens / 39 closes; another 39 opens / 25 closes; another 29 opens / 15 closes.
- A 6,588-line master log showed every nested `.do` being source-echoed and reaching "end of do-file", with **zero "file saved" messages**. The pipeline reported success but produced no outputs.
- Per-file `.smcl` logs were absent across the project — every `log using` statement sat inside an accidental runaway block comment.
- The first downstream `use` of a non-existent input file fired `r(111) file not found`, several scripts after the actual bug.
- **Five files contained Variant 4** (dormant code that a naive Variant-1 fix would have silently activated). The Variant-4 fix preserved the predecessor's intended behavior: the dormant code (a `rangestat`-bounded mean) would have overwritten a simple `egen` mean computed earlier in the same file, changing saved variable values.
- After the state-machine sweep plus the new convention rules, the full pipeline ran clean: every file produced, no errors.
- Final commit touched 122 files with ~2,700 lines of changes.
- **Variant 8 hit during round-2 sweep:** a state-machine pre-pass that replaced the narrow round-1 regex, but used greedy depth-counting + blanket `inner.replace(...)`, over-flattened **2 files** (`secqoiclean1415.do`, `secqoiclean1617.do`) whose outer headers contained path-glob substrings. M4 acceptance run #3 errored at `secqoiclean1415.do:89` with `r(110) totalresp already defined` — the script's `clear all` + `use` never ran inside the runaway block. Surgical line restoration (7 edits across 2 files) plus a path-glob-aware depth-counter and inner rewriter (round-3) closed the variant.

The lesson: **balance counts alone are necessary but not sufficient.** Variant 4 leaves balance intact while still hiding a semantic regression risk. Variant 8 ALSO leaves balance intact — it preserves digraph counts and merely shifts where the close happens. A state-machine sweep that distinguishes path-glob from real block markers in BOTH the matcher and the inner rewriter is the only fix that handles all variants safely.

---

## Section 8 — Cross-references and portability

### Reference implementation

- `py/sweep_comments_and_logdirs.py` in this project — full Python implementation of the three-pass algorithm. Approximately 700 lines including extensive docstrings documenting the design rationale and round-1/round-2/round-3 fix history.

### Convention rules

- `.claude/rules/stata-code-conventions.md` — sections "Wildcards in comments" and "Per-file logging structure" — adopt verbatim in any forking project.
- `.claude/rules/phase-1-review.md` §2 Tier-1 — commit-time balance check item — adopt verbatim.

### Portability notes

This field guide is generalizable to any Stata project. No project-specific globals, paths, or workflow assumptions are load-bearing in this document.

- The detection commands in Section 3 work against any project root containing `.do` / `.doh` files.
- The state-machine algorithm in Section 4 is described in language-agnostic terms; reimplement in Python, Ruby, Perl, or any language with state-machine parsing.
- The convention rules in Section 5 are stated in project-neutral language.

If you are adapting this guide for a new project: run the Section 3 detection commands first to confirm the bug exists in your codebase. If at least one file is unbalanced, run the reference implementation (or your reimplementation) against the codebase. After the sweep, install the two convention rules from Section 5 in your project's coding standards, and add the commit-time balance check to your pre-commit gate.

### Document history

- 2026-05-17 — Initial bug discovery and sweep (89 of 129 files affected; 5 Variant-4 instances)
- 2026-05-18 — Variant 8 (over-flatten round-2 trap) discovered + fixed; field guide extended with new variant, detection commands, Section 4 path-glob-awareness invariant, Section 6 false-fix row, and Section 7 case-study addendum
- Field guide synthesized from project plan, two coder-critic reviews, reference implementation, and 2026-05-18 round-3 fix
