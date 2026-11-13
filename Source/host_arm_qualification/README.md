# TASK-006: ARM Qualification Proposals 0.1.0

PC_SIM_ONLY Stage C2, Design/170. Parent Git pin:
`f2c9237bd4a1e2e077c15db6eb4c22ed2a250d5d` (merged PR #5).

## Windows UAT

Open PowerShell at `BionicButterfly/Source/host_arm_qualification`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

The prepared environment uses Python 3.11.15. Actual test results, all 32 oracle
outcomes and AC evidence are in `evidence/REPORT.md`. Owner UAT and explicit PR
permission pending; no developer merge.

## API and interpretation

`propose_arm_qualification(observations, temporal, priority, prior_window, verdict)`
consumes exact genuine TASK-003/004/005 records. PriorQualificationWindow and
HypotheticalQualificationVerdict are frozen, separate synthetic test inputs.
HealthVerdict is PASS/FAIL/UNRESOLVED; ControlVerdict is ADMITTED/ABSENT/DENIED/
UNRESOLVED. No scenario JSON can set these inputs or thereby obtain authority.
They test hypothetical R1 mechanics; no actual trusted admission arbiter exists.

The frozen result has exactly nine fields and always requires_full_fsm=True.
LOW uses the original first anchor and a later frame/tick, inclusive 20000us.
HIGH needs previously committed LOW qualification, exact neutral flap <=0.02
and steering between -0.05 and 0.05; later neutral HIGH confirms at >=100000us.
Comparisons do not round using the caller's Decimal context. ARMED_IDLE observes
demand only for flap >0.05. LOW disarm clears windows without starting rearm.
Silence only proposes a hold under hypothetical health PASS; it never qualifies.

Invalid or contradictory callers fail before any result (TypeError/ValueError,
not new wire errors). PASS with a priority blocker, ADMITTED without PASS and a
single exact matching candidate, ABSENT with a candidate, and DENIED without a
candidate are rejected. Prior times are exact integers, commits are earlier grid
ticks, high/low windows cannot coexist or belong to incompatible states. An
admitted HIGH in ARM_CHECK requires a committed HIGH-edge anchor to confirm;
an anchorless confirmation snapshot is a caller error. No type authenticates trust.

CONTINGENCY proposals defer ACK recovery; no window or state is committed.
BOOT/SELF_TEST do not gain qualification. The priority input remains provisional.
O(1) work over fixed metadata and one semantic group; no source/member event
scan, upstream rerun, state storage, IO, policy loader, mixer, trace or callback.

Full FSM, effective RF/current health arbitration, accepted timestamps, host
allowlist, ACK recovery, output/ACTIVE S1, trace-before-publish, hardware and flight
are NOT RUN / DEFERRED. Positive proposal kinds are never ARM/output permission.
Full P28-T08/T09/T13/T14/T26/T27 and P210-T02 conformance is not claimed.

## Reproducibility

Use Python 3.11+ with pinned build/test tooling and local TASK-001..005 packages.
`scripts/verify.py` builds prerequisites from exact Git blobs in task-local cache,
installs local wheels, runs tests and regressions from each prerequisite's own
directory/interpreter, and checks a separately installed wheel. It requires the
existing sibling test venvs. Fresh review checkouts must prepare those first.
No public same-named package substitution; owner release artifacts remain required.

Runtime uses standard library and local exact 0.1.0 packages. Tool versions reuse
TASK-005: pytest/iniconfig/pluggy/build/pyproject-hooks/setuptools/wheel (MIT),
colorama (BSD-3-Clause), packaging (Apache-2.0 OR BSD-2-Clause). No external source
is vendored; all implementation/evidence writes stay within this task subtree.
