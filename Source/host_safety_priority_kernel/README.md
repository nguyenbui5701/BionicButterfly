# TASK-005: Safety Priority Kernel 0.1.0

Pure PC_SIM_ONLY Stage C1, Design/167, pinned to merged baseline
`efe7fa3aff1beeb01af98b98a06593bd8e7af192`. Provisional priority constraints only.

## Windows UAT

Open PowerShell at `BionicButterfly/Source/host_safety_priority_kernel`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

The prepared `.venv` uses Python 3.11.15. Actual results, AC-01..10 evidence and
limits are in `evidence/REPORT.md`. Owner UAT and explicit PR permission pending.

## API and exact scope

```python
from bb_host_safety_priority_kernel import SafetyState, assess_safety_priority

# A synthetic test pre-state, not scenario JSON or proof of committed history.
assessment = assess_safety_priority(SafetyState.ACTUATION_ACTIVE, observations, temporal)
```

Supply genuine TASK-003 observations and matching TASK-004 facts. Pre-state comes
from a separate trusted state owner (test-only synthetic input in this task).
The eight-state enum names states; it does not implement the full eight-state FSM.

The A-to-G order is prior latch, catastrophe, provisional CONTINGENCY hold,
armed-state explicit hazards, ordinary RESET, initial BOOT, then DEFER (None
state/category). All seven result fields are frozen. `requires_full_fsm` is
always True. A false `blocks_control_qualification` is never permission.
HEALTHY+UNKNOWN alone is blocked without an effective-health decision. Prior
missing/stale ages block armed-state qualification without forcing a transition.
Current candidates never renew accepted timestamps; ACK cannot complete recovery.

Wrong exact input types raise TypeError. Malformed tick/grid/flag/BOOT shapes
raise ValueError before producing a result, without new P_/E_ diagnostics.
Validation is constant size; event/group contents remain upstream responsibilities.
Shape checks do not authenticate forged records. No event scans, pipeline rerun,
history, clock, IO, policy loader, mixer, trace or output callback occurs.

Full FSM, age/current-health arbitration, SELF_TEST readiness, LOW/HIGH windows,
ACK recovery, host trust, committed timestamps/transitions, virtual or physical
output and flight are NOT RUN / DEFERRED. Full P28-T08/T09/T13/T14/T26 conformance
is not claimed. G0-B/G4 remain NO-GO.

## Development

Use Python 3.11+ and pinned local TASK-001..004 packages, never public substitutes.
`scripts/verify.py` builds prerequisite wheels from exact baseline Git blobs into
this package's ignored cache, installs them, runs tests and read-only regressions
from each package's own directory, then builds and checks an isolated wheel.
It needs build/test tooling in `.venv` and prepared sibling regression venvs.
The owner-supplied P217 release artifacts must remain present and unchanged.
All code, test and evidence writes are confined to this package.

Tool versions reuse TASK-004: pytest/iniconfig/pluggy/build/pyproject-hooks/
setuptools/wheel (MIT), colorama (BSD-3-Clause), packaging (Apache-2.0 OR
BSD-2-Clause). Runtime uses standard library plus exact local 0.1.0 dependencies;
no third-party source is vendored.
