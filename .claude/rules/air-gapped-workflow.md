# Air-Gapped Server Workflow

**Paths:** `**/*.do`, `**/*.doh`

## When This Applies
Project data/code lives on a restricted server Claude cannot access (e.g., TERC, FSRDC).

## Constraints
- Claude CANNOT see raw data or run code
- Claude CAN work with: variable names, summary stats, codebooks, exported .do files, log files

## What Claude Does
- Review exported .do files for logic errors and best practices
- Generate new code with explicit assumptions documented
- Design replication package structure
- Format tables and figures from shared output

## Defensive Code Rules
1. Add assertions: `assert _N > 0`, `assert !missing(key_var)`
2. Document assumptions: `// ASSUMPTION: merge keys are string type`
3. Flag version deps: `// REQUIRES: reghdfe with absorb() syntax`
4. Include diagnostics: `// DIAGNOSTIC: share this output with Claude`

## Communication Protocol
1. Ask for: variable names, data dimensions, summary stats, codebook
2. Write code with assumptions documented
3. User runs on server, shares output/errors
4. Claude iterates based on output
