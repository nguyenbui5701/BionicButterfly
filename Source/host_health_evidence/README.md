# TASK-007 RF/control health evidence (Stage D1)

Python 3.11+, PC_SIM_ONLY. `assess_health_evidence` classifies current RF,
separately supplied TEST_ONLY prior RF status and observed control candidates.
It preserves LOST dominance, HEALTHY+UNKNOWN ambiguity and original timestamps.
All eight frozen result fields are diagnostic; `requires_full_fsm` is always true.
No control acceptance, health PASS/ADMITTED, TASK-006 adapter, ARM, FSM, output,
trace transaction, authentic history, host allowlist or hardware is implemented.

Baseline: `a47dc157453547125f5172b4ef165c3b522ff0c8`.
Normative derived contract: Design/173; 36 recipes: Design/P219 release.
Only this package is writable. Design/Task and TASK-001..006 stay unchanged.
Source checks cannot authenticate a forged record. Constant-size group checks
reuse upstream grouping; the only variable-size scan visits current RF records.

From `BionicButterfly/Source/host_health_evidence`, after developer setup:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Full verification (builds pinned prerequisite wheels, checks source hashes,
runs TASK-001..006 regressions read-only, tests installed wheel and writes logs):

```powershell
.\.venv\Scripts\python.exe scripts\verify.py
```

The full verifier needs Git, the pinned local Design release, this package's
venv with `.[test]` tooling. All regressions run using this venv with prerequisite
wheels built from pinned Git bytes; no sibling venv is changed. It writes only
here. Evidence is in `evidence/summary.json`, `tests.xml`, command logs and
`baseline.json`. Revision identity includes SHA-256 of code/tests/scripts/config;
Git HEAD alone does not identify uncommitted implementation bytes.

UAT and explicit owner approval are required before PR creation. No PR yet.
Do not repeat full verification merely for PR packaging of unchanged accepted
code/tests/dependencies/evidence. Any execution-affecting edit needs relevant
checks and renewed owner acceptance. Full R1 FSM/output and flight remain NOT RUN.
