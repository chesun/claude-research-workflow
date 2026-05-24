* Test fixture: 8 variants of the greedy block-comment parser bug.
* See master_supporting_docs for the field guide.
*
* This file is intentionally buggy. Sweep must produce
* all_eight_variants.expected.do byte-identical.

* --- Variant 1: path-glob inside header block ---
/* PURPOSE: clean prepare/<x> and write to $cleandir */
use prepare/foo.dta, clear

* --- Variant 2: path-glob in star-line comment ---
* Process files in prepare/<x> via wildcard
local files: dir "prepare" files "*.dta"

* --- Variant 3: path-glob in slash-slash line comment ---
// Each script logs to $logdir/<x>.smcl by convention
log using "$logdir/myscript.smcl", replace

* --- Variant 4: fake nested comment block ---
/* outer header
   /<x> inner mini-comment <x>
   dormant code
*/

* --- Variant 5: orphan close on its own line ---
sort id


gen newvar = 1

* --- Variant 6: trailing path-glob with continuation ---
/* INPUTS: $rawdir/{a,b}/<x>/sub.dta */

* --- Variant 7: decorative banner ---
// *****************
// * end of section
// *****************

* --- Variant 8 risk: path-glob in outer header (should survive) ---
/*------------------------------------------
 * PURPOSE: emit to $logdir/<x> and $datadir/<x>
 *-----------------------------------------*/
/* legitimate single-line body block */
display "done"
