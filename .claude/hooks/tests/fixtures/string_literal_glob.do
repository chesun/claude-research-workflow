* Test fixture: real-world string-literal pattern.
*
* Mirrors a tx_peer_effects_local file with path-glob digraphs inside
* double-quoted strings. State-machine balance must preserve the string
* verbatim; compute_balance returns (0, 0); classify_file returns CLEAN.

display as text "Copy $outdir/*.txt and $outdir/*.log to local"
display as text "Glob $rawdir/{a,b}/*/sub.dta"
display "string with /* inside and */ inside"
