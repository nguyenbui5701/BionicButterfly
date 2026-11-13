# TASK-005 — READY FOR OWNER UAT

Date: 2026-11-13 (Asia/Saigon). Branch:
`feature/TASK-005-host-safety-priority-kernel`.
Pinned parent: `efe7fa3aff1beeb01af98b98a06593bd8e7af192` (merged PR #4).
Scope: Design/167 Safety Priority Kernel Stage C1, PC_SIM_ONLY.
Owner confirmed UAT PASS and authorized PR into main on 2026-11-13.
Accepted implementation commit: `e2db969ada53b3fb747e577eb9e072abd5fd0eb5`.
SA review and owner merge decision remain pending; developer does not merge.
[PR handoff](PR_HANDOFF.md) contains the complete file list and 22-oracle mapping.

## Actual results

Full verification rerun for PR preparation; runtime, tests and scripts unchanged
from the owner-accepted implementation.

| Check | Result | Evidence |
|---|---|---|
| TASK-005 unit/integration, all 22 P217 oracles | **208 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [tests.log](tests.log), [tests.xml](tests.xml) |
| Read-only TASK-001 regression | **203 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task001-regression.log](task001-regression.log) |
| Read-only TASK-002 regression | **44 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task002-regression.log](task002-regression.log) |
| Read-only TASK-003 regression | **59 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task003-regression.log](task003-regression.log) |
| Read-only TASK-004 regression | **140 PASS, 0 FAIL, 0 ERROR, 0 SKIP** | [task004-regression.log](task004-regression.log) |
| Development smoke | **12 PASS, 0 FAIL** | [smoke.log](smoke.log) |
| Installed-wheel smoke | **12 PASS, 0 FAIL** | [wheel-smoke.log](wheel-smoke.log) |
| Compile, build wheel/sdist, install, both pip checks | **PASS**, all command exits 0 | [commands.json](commands.json) |
| Provenance | **31 pinned paths + 5 release artifacts + policy digest MATCH** | [baseline.json](baseline.json) |

Total: **654 tests PASS**, plus both smoke runs. Windows AMD64, CPython 3.11.15.
No test/build failures or skips occurred in the completed verification.
Exact tool versions, JUnit counts, artifact hashes and the isolated wheel
environment location are recorded in [environment.json](environment.json).

All four prerequisite wheels were built from exact pinned Git blobs in ignored
task-local cache directories, avoiding writes to old dist artifacts. Installed
prerequisite runtime bytes in both environments match the pinned Git source.
Installed TASK-005 runtime matches current source byte-for-byte. The owner
`.venv` uses local prerequisite wheels plus editable TASK-005. Each regression
used its own existing interpreter and package working directory, `-B` and no
pytest cache; all JUnit evidence was written only inside this task subtree.

Prerequisite wheel builds emitted **18 manifest warnings** because the isolated
build copies contain runtime/build inputs but omit prerequisite tests/scripts
and TASK-001's DEPENDENCIES.md. These are packaging warnings, not test failures;
all four wheels built successfully and their installed runtime bytes match Git.
Full warnings remain in `build-task001.log` through `build-task004.log`.
The TASK-005 wheel/sdist build and all pytest suites emitted no warnings.

## Acceptance criteria

| AC | Executed proof |
|---|---|
| 01 | Only TASK-005 subtree created. AST import/call audit and spies for IO/clock/RNG/socket/M0/upstream pipeline calls PASS. Original unrelated TASK-001 evidence edit preserved. |
| 02 | All P217-T01..T22 execute raw wire bytes -> actual TASK-001 preflight -> TASK-002 tick -> TASK-003 observations -> TASK-004 temporal facts -> TASK-005. Exact seven fields and types checked; synthetic pre-state/prior are not in JSON. Upstream values/reference preservation and immutability checked. |
| 03 | Latch persistence with RESET/ACK/HEALTHY/catastrophe; simultaneous catastrophe+RESET+ACK+conflicting controls+INVALID+LOST across all seven valid later pre-states. Prior latch category outranks new catastrophe. |
| 04 | All three armed states crossed with LOST, standalone UNKNOWN, INVALID, semantic conflict, HEALTHY+LOST; simultaneous RESET loses priority even with fresh prior timestamps. |
| 05 | CONTINGENCY with healthy RF, LOW, ACK and optional RESET remains explicitly provisional CONTINGENCY_HOLD, requires_full_fsm=True. No recovery qualification invented. |
| 06 | RESET from SELF_TEST/DISARMED/armed states without higher hazard; BOOT T0; rejects non-BOOT at T0, BOOT later, missing/late BOOT flag and impossible T0 catastrophe/RESET/ACK/HEALTHY/duplicate flags. |
| 07 | HEALTHY+UNKNOWN blocked/deferred; missing/stale control/RF ages independently block armed qualification without age-based transition; fresh candidates do not override this. SELF_TEST/DISARMED/HIGH+fresh cases DEFER, never imply readiness/arming/output. |
| 08 | Exact eight-state enum and frozen seven-field result, strict input types/subclasses/grid/mirror flags, malformed numeric/shape rejection before result. Poisoned event/group contents never read; identical runtime line counts for 1 vs 5000 real RF observations. Repeat determinism under two locales/TZ environment values and Decimal precision 2; no retained latch/history. |
| 09 | Actual 203/44/59/140 prerequisite regressions; compile/build/install, smoke and pip PASS; source and installed byte checks PASS. No invented success from design-only oracles. |
| 10 | Prepared `.venv` and three PowerShell UAT commands below; no PR until explicit owner permission, no self-merge. |

## Scope, limitations and deferred work

- Runtime: `src/bb_host_safety_priority_kernel/{__init__,priority}.py`.
  Tests: `tests/{conftest,test_oracles,test_priority}.py`.
  Tooling: `scripts/{__init__,scenarios,smoke,verify}.py`, packaging/README and
  evidence. Full changed-file hashes and scope audit: [files.json](files.json).
- All writes under `Source/host_safety_priority_kernel/**`. Owner Design/Task
  release documents are now tracked unchanged as explicitly requested by the owner. Existing TASK-001
  evidence change retains its recorded SHA-256. No prerequisite code, schemas,
  .github, ReviewPR, firmware or hardware changes. The unrelated TASK-001
  evidence edit is excluded from the PR. Release-document inclusion is separate
  from the Source-only implementation scope; no specification content changed.
- The output is a provisional constraint, never a committed post-state.
  `None` state/category means DEFER; `blocks_control_qualification=False` is
  not permission; `requires_full_fsm=True` always. CONTINGENCY_HOLD can only
  be superseded by later full R1-conformant ACK-recovery proof.
- Full FSM, LOW/HIGH qualification, SELF_TEST authority, current/prior age-health
  resolution, critical power/scheduler signals, accepted timestamp owner,
  complete ACK recovery, host allowlist, trace transaction, M0/output, simulator
  runner and hardware/flight are **NOT RUN / DEFERRED**. Full P28-T08/T09/T13/T14/T26
  state/output conformance is not claimed; physical G0-B/G4 remain NO-GO.
- Constant-size caller checks do not authenticate forged records or inspect
  every nested source event/group. Genuine TASK-003/004 outputs and separately
  trusted committed pre-state are required; test states/history are synthetic.
- Effective OS timezone switching is **NOT RUN** (Windows Python lacks tzset).
  Actual locales C/English_United States.1252 and TZ environment values UTC0/ICT-7
  passed. Runtime imports no clock/environment/locale APIs.
- Aggregate verification needs prepared sibling regression venvs and pinned
  build/test tooling in the TASK-005 venv. Fresh review environments must prepare
  those prerequisites first. No unresolved test failure remains.

## Owner UAT: three PowerShell commands

Run from `BionicButterfly/Source/host_safety_priority_kernel`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Expected: **208 passed**, **Smoke: 12 PASS, 0 FAIL**,
**No broken requirements found**. PR: **NOT CREATED — WAITING FOR OWNER**.

Source diff whitespace checks pass. The original owner Task specification has
a trailing space at line 33; the full-diff check reports it. It is preserved
unchanged to retain the release manifest byte/hash match, not silently edited.
