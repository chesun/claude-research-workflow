* Test fixture: developer forgot the close marker on a multi-line block.
*
* Mirrors 8A_Texas_Heatmaps.do from tx_peer_effects_local: two /*
* openers without any matching */ anywhere downstream. Sweep --check
* must classify as MANUAL-ATTENTION (sweep cannot safely auto-fix);
* sweep --fix must NOT mutate this file.

use heatmap_data, clear

/* WIP: this block was meant to wrap an experimental section
 * but the closing marker was forgotten when the section was
 * trimmed during refactoring.

gen treatment = 1
gen control = 0

/* Another block, also missing its close.

twoway scatter y x, ///
    title("Texas heatmap") ///
    subtitle("draft")

graph export "heatmap.png", replace
