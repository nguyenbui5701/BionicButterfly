# TASK-003: host batch observations 0.1.0

Pure, immutable tick observations for future SafetySupervisor Stage A. The
library consumes a genuine TASK-002 VirtualTickBatch and retains all original
events. It classifies facts without deciding state, priority, freshness or output.

## Owner UAT on Windows

Open PowerShell at `BionicButterfly/Source/host_batch_observations`. The prepared
`.venv` uses Python 3.11.15. Run these three commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Expect all tests passed, all smoke checks PASS, and `No broken requirements found`.
Actual counts, logs and the AC map are in `evidence/REPORT.md`. Owner UAT and
explicit PR authorization are pending; no automatic commit, push or PR.

## API and guarantees

```python
from bb_host_batch_observations import normalize_tick_observations

observations = normalize_tick_observations(batch)  # genuine TASK-002 batch
```

NormalizedTickObservations exposes exactly the fields in Design/161. Source
events retain the input tuple and mapping references. ValidControlGroup contains
the first member's full immutable VALID payload, original member references in
source order, unsigned UTF-8 sorted IDs and latest original timestamp. Group
order follows first appearance. Exact int/Decimal equality groups equivalent
spellings, with no binary float conversion or Unicode normalization.

INVALID, distinct-valid conflict, duplicate-semantic, all three RF presence
flags and lifecycle flags are independent. No previous tick data is carried
over. Empty batches contain no invented observations. There is no state_after,
reason_codes, rf_effective, accepted_frame_at_us, control_authorized, can_arm,
output_allowed or effort output.

Wrong input types raise TypeError at call time. Malformed in-memory shapes raise
ValueError before returning a result. Shape guards ensure immutable scalar
payloads and consistent tick windows, but are not a parser, policy allowlist or
authentication scheme: never construct a wrapper to bypass preflight. Always
use TASK-001 preflight followed by TASK-002 scheduling.

The classification/grouping pass visits each event once, with expected O(N)
dictionary grouping and O(N) memory. Required sorted ID metadata separately costs
O(N log N) comparisons in the worst case; no group re-scans all source events.
Tests instrument event visits and executed lines, including legal near-20k
batches and many distinct groups. No filesystem/network/device access, clock,
RNG, sleep, parser/scheduler rerun, M0, FSM or trace occurs inside the library.

## Development setup and provenance

Dependencies are local TASK-001 and TASK-002 version 0.1.0 from merged baseline
`12b4ee1355d146080810d028843d24481f88af77`. Their installed runtime files are
checked against exact Git source. Their source trees are read-only to this task.
For the supplied workspace, create a Python 3.11+ venv and install the existing
local wheels, then the test extra:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-index --no-deps ..\host_preflight_m0\dist\bb_host_preflight_m0-0.1.0-py3-none-any.whl ..\host_virtual_ticks\dist\bb_host_virtual_ticks-0.1.0-py3-none-any.whl
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe scripts\verify.py
```

If `py` has no registered interpreter, use an existing Python 3.11+ executable.
The workstation has Python 3.11.15 under the user's uv-managed Python directory.
For a fresh checkout without prerequisite wheels, build the pinned prerequisite
trees in copies under this package's ignored `.cache/`, rather than changing
their original source trees. Never download same-named packages as a substitute.
The aggregate verification script additionally uses the existing prerequisite
development environments for read-only regression runs.

The P215 owner-supplied Design/Task/oracle files must be present for tests and
provenance checking. This implementation does not edit or publish them.
Tests construct raw unquoted decimal tokens directly from their recipes.

Runtime uses the standard library and these two local project dependencies.
Exact test/build tool versions, including transitives, are in pyproject.toml:
pytest, iniconfig, pluggy, build, pyproject-hooks, setuptools and wheel use MIT;
colorama uses BSD-3-Clause; packaging uses Apache-2.0 OR BSD-2-Clause. These
are the previously reviewed TASK-001/002 tool versions; no tool code is vendored.
