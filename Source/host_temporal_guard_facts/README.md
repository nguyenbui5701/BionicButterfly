# TASK-004: host temporal guard facts 0.1.0

Pure PC_SIM_ONLY facts for SafetySupervisor Stage B, pinned to merged TASK-003
baseline `ed106d22c52647090768ef60fb1e4c33384e9227` and Design/164.

## Windows UAT

Open PowerShell in `BionicButterfly/Source/host_temporal_guard_facts` and run:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

The prepared environment uses Python 3.11.15. Actual results and AC mapping are
in `evidence/REPORT.md`. Owner UAT and explicit PR authorization remain pending.

## API and boundaries

```python
from bb_host_temporal_guard_facts import (
    PriorCommittedTimestampFacts, evaluate_temporal_guard_facts,
)

# Synthetic example only, not host trust or permission to execute a state machine.
prior = PriorCommittedTimestampFacts(0, None, None)
facts = evaluate_temporal_guard_facts(observations, prior)
```

`observations` must be the exact TASK-003 `NormalizedTickObservations` type,
produced by real TASK-001 preflight -> TASK-002 scheduler -> TASK-003 normalizer.
`prior` is a separate immutable timestamp snapshot from a future trusted state
owner; test snapshots are explicitly synthetic and never scenario JSON history.
The evaluator validates prior timestamps at call time: T0 requires all None;
later ticks require an earlier 5000us-grid commit and optional original times
between zero and that commit. Exact int excludes bool. None age is never fresh.
Both ages independently use inclusive 200000us bounds, without rounding.

Current candidates remain uncommitted; they never refresh prior timestamps.
One uncontested VALID group with no INVALID yields its latest original time.
Only exclusively HEALTHY RF yields a candidate. Hazards remain independent of
prior age. RESET/catastrophe/RF hazards do not suppress raw control candidates
or grant acceptance. The result exposes exactly Design/164's twelve fields.

All records/results are frozen and slotted. Wrong top-level types (including
subclasses) raise TypeError; malformed consumed shapes/times raise ValueError.
These are library caller errors, not new P_/E_ wire diagnostics. Shape checks
do not authenticate a manually forged record or rerun TASK-003: original source
events and grouping are trusted upstream responsibilities. Work is O(RF events)
with O(1) extra memory; no source/group rescan, cache, mutation or IO.

No FSM, ARM, acceptance/commit, effective RF, output, trace, host allowlist or
hardware/flight authority is implemented. P28-T13/T14/T26 full state/output
conformance remains NOT RUN at this stage; only the P216 age facts are tested.

## Development and reproducibility

Use Python 3.11+ with the three prerequisite packages from the pinned tree.
The supplied workspace already has local prerequisite wheels. Create `.venv`,
install these local wheels with `pip install --no-index --no-deps`, then install
this package's `.[test]` extra. Never substitute public same-named packages.
`scripts/verify.py` performs provenance, tests/regressions, packaging and separate
wheel smoke checks; it requires the existing sibling dev environments and wheels.
Fresh checkouts must first prepare those prerequisites in isolated copies.
The five P216 release files and manifest must be supplied by the owner unchanged.

Runtime uses Python's standard library and the pinned local TASK-003 package
(with TASK-001/002 transitively). Test/build tooling uses the same exact versions
as TASK-003: pytest/iniconfig/pluggy/build/pyproject-hooks/setuptools/wheel (MIT),
colorama (BSD-3-Clause), packaging (Apache-2.0 OR BSD-2-Clause); no vendored code.
