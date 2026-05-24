* Test fixture: a file already corrupted by a buggy round-2 fix tool.
*
* This mirrors the secqoiclean1415.do shape from the va_consolidated
* incident. Sweep --check must classify it as MANUAL-ATTENTION (V8
* corruption present); --fix must NOT mutate it.

/*------------------------------------------------------------------------------
 * PURPOSE:  clean qoi for one year; outputs go to $logdir/<x> and $datadir/<x>
 * INPUTS:   $datadir_clean/sec1415
 * OUTPUTS:  $logdir/data_prep/qoiclean/secondary/secqoiclean1415.smcl
 *------------------------------------------------------------------<x>

log using "$logdir/data_prep/qoiclean/secondary/secqoiclean1415.smcl", replace
use $datadir_clean/sec1415, clear

/<x> Note: 1415 dataset does not have qoi 27-30 <x>
foreach i of numlist 14/18 {
  local j = `i' + 8
  rename a`i' qoi`j'
}

* count the total number of responses in each school <x>
sort cdscode
by cdscode: gen totalresp = _N
