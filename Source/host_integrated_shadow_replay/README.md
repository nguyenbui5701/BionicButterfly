# TASK-012 — Integrated PC shadow replay

**PC_SIM_ONLY / NO_OUTPUT / NOT A FLIGHT TEST.** This is a runnable offline
timeline using the genuine TASK-001/002/003/004/005/007/008/009 pipeline and
TASK-010/011 reference/intent gates. TASK-006 is not an authority input.
All old modules and Design fixtures remain unchanged.

From this directory, with the prepared `.venv`:

```powershell
.\.venv\Scripts\python.exe scripts\demo.py --case pilot
.\.venv\Scripts\python.exe scripts\demo.py --case hazard
.\.venv\Scripts\python.exe scripts\demo.py --case conflict
.\.venv\Scripts\python.exe scripts\demo.py --case minimal
```

The four presets print 8, 6, 4 and 2 acknowledged shadow ticks respectively.
Rows show original input timestamps, flap/steering demand, observed RF, E1 state
and append acknowledgement, ARM request and mathematical left/right preview.
`HEALTHY*` means observed, never accepted RF history. `SELF_TEST` means
`UNRESOLVED_FULL_FSM`, not successful self-test. An ARM HIGH remains
`REQUESTED_NOT_GRANTED`. All rows retain `INHIBITED` output.

Preview is the exact TASK-001 M0 arithmetic in integer micro units, under all
Design/188 eligibility conditions, after E1 acknowledgement. It is neither
servo position nor an authorized virtual/physical command. Catastrophe latches
FAULT_LATCHED; RESET cannot clear that latch. Conflicting/invalid controls and
LOST/missing/ambiguous RF suppress preview. No history is invented to complete
arming, admission or FSM transitions.

`--jsonl evidence\pilot.jsonl` optionally writes a local offline diagnostic using
stable ASCII/LF serialization and a 16 MiB limit. Each record is labeled
`BB_F0_SHADOW_DIAGNOSTIC_V1` (header), `diagnostic_record_type`, and `authority=NONE`.
It is not a canonical R1 trace and has no control-trace digest. Serialization
finishes before temporary-file write and atomic replacement; a failed write
preserves a previous destination and reports failure. Atomic replacement is not
a power-loss durability guarantee. Exit codes: 0 shadow diagnostics complete,
2 blocked/incomplete shadow evidence, 1 integration/report error.

## DEV CHECK and OWNER FULL UAT

Developer command:

```powershell
.\.venv\Scripts\python.exe scripts\verify.py --dev
```

This runs TASK-012 tests (including exactly 20 named P224 oracles), all four
console/JSONL demos, development and installed-wheel smoke, build/install/pip
checks and read-only source/release provenance. Dependency wheels are built from
the pinned Git baseline; this does not execute their regression tests.

Owner runs these **five commands**, as required by Design/189:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts\demo.py --case pilot
.\.venv\Scripts\python.exe scripts\verify.py --owner
```

Only `--owner` runs all TASK-001–011 regression suites. No old regression PASS is
claimed by `--dev`. Owner acceptance and explicit authorization are required
before creating a PR; this task never merges it.

Evidence lives in `evidence/dev/` and `evidence/owner/` separately: `summary.json`,
`commands.json`, `tests.xml`, `environment.json`, individual command logs, and
`demo-*.log` / `demo-*.jsonl`. Failed verification attempts are retained in each
mode's `history/`. `evidence/baseline.json` pins 444 baseline files, 24 explicit
Design/187 pins, nine release files (plus the manifest's own SHA-256 separately)
and the policy. `evidence/performance.json` records actual elapsed time and peak
Python allocations for 60 seconds / 12001 ticks / 20000 events; process peak
memory is explicitly not measured. Current execution-affecting file hashes and
installed-source comparisons bind verification to the tested code/dependencies.

## Fresh Windows environment

The supplied working directory already has `.venv`. On a fresh checkout, create
it with Python >=3.11, install the exact tooling pins from `pyproject.toml`
`project.optional-dependencies.test`, then run `verify.py --dev` (or `--owner`
when performing Owner UAT). Verification builds and installs all project
dependencies from the pinned baseline without modifying earlier task folders.
The repository and its approved Design fixtures must be available for the CLI;
the installed runtime package itself is pure and takes seven explicit inputs.

The E2 claim and E3 engine/scheduler bytes are distinct frozen **TEST_ONLY**
fixtures, not fingerprints of a trusted executable. Matching them grants no
runtime permission, ARM, accepted history, FSM completion or output authority.
Full FSM, normative R1 trace, actual virtual actuation, hardware and flight
remain outside this deliverable.
