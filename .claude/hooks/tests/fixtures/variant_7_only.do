* Test fixture: pure Variant-7 banner-only file.
*
* Mirrors a real BDD pattern where the only "unbalanced" digraphs are
* decorative banner lines (V7). Stata parses this file correctly;
* compute_balance reports (0, 0); classify_file returns CLEAN.

//*****************************************************
//* SECTION: load and clean
//*****************************************************

use foo.dta, clear

//*****************************************************
//* SECTION: save
//*****************************************************

save out.dta, replace
