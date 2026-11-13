# TASK-002: host virtual ticks 0.1.0

Pure, lazy PC-only enumeration of immutable tick batches at 5000 microseconds.
The dependency is TASK-001 `bb-host-preflight-m0==0.1.0` from merged baseline
`ca457f784975c2d0959b1baf988483fa042f5c67`; no parser or mixer is reimplemented.

## Owner UAT on Windows

In VS Code open the PowerShell terminal at `BionicButterfly/Source/host_virtual_ticks`.
The prepared `.venv` uses Python 3.11.15. Run exactly these three commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts\smoke.py
.\.venv\Scripts\python.exe -m pip check
```

Expect all tests passed, smoke checks PASS and `No broken requirements found`.
If anything fails, send the terminal output. Logs and AC mapping are in `evidence/`.
The owner confirmed these UAT results and authorized a TASK-002 PR on 2026-11-13;
SA review and the owner's merge decision remain separate.

## API

```python
from bb_host_preflight_m0 import validate_wire, AcceptedPreflight
from bb_host_virtual_ticks import iter_virtual_ticks

accepted = validate_wire(raw_bytes, frozen_schema)
if isinstance(accepted, AcceptedPreflight):
    for batch in iter_virtual_ticks(accepted):
        # batch.tick_index, batch.eval_at_us, batch.events
        pass
```

The callable rejects raw mappings/bytes and RejectedPreflight at call time with
TypeError. Obviously malformed manually constructed AcceptedPreflight wrappers
raise ValueError. The supported input is the actual immutable result returned by
TASK-001; its public dataclass is not a cryptographic token or a policy allowlist.
The scheduler does not reparse/revalidate an accepted scenario.

Each invocation returns a fresh one-shot iterator. Tick zero contains events at
zero; later windows are `(previous_tick, current_tick]`. The final duration tick
and all empty ticks are included. Each yielded frozen, slotted VirtualTickBatch
contains only `tick_index`, `eval_at_us` and an immutable `events` tuple pointing
to the original immutable event mappings. Input order, payloads, IDs and original
timestamps are preserved without copying/normalizing events.

A cursor visits every event once, caching one lookahead timestamp across empty
ticks. Work is O(ticks + events), additional memory O(largest active batch), plus
the existing accepted scenario. Retaining yielded batches is the caller's choice.
Stopping consumption does not evaluate or construct future batches.

No parsing, mixing, state transitions, conflict/RF resolution, trace/hash writing,
IO, wall clock or randomness occurs during enumeration. Batches confer no ARM,
actuation, simulation trust or flight permission. Those capabilities are outside
TASK-002.

## Developer reproduction

Python 3.11+ is required. From this package directory, create `.venv` with an
existing interpreter (`py -3.11 -m venv .venv` if registered). Install the local
TASK-001 wheel and this project's test extra:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --no-deps ..\host_preflight_m0\dist\bb_host_preflight_m0-0.1.0-py3-none-any.whl
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe scripts\verify.py
```

The TASK-001 dependency is installed as a read-only local wheel; its installed
runtime files are checked against the pinned Git source by `scripts/verify.py`.
This leaves TASK-001's source and package metadata untouched. On a clean checkout
without that wheel, build from a copy of the pinned TASK-001 tree inside this
package's ignored `.cache/` directory, then install that wheel instead. No download
of a same-named package is a substitute for the pinned local dependency.

Runtime dependencies: TASK-001 and the Python standard library only. Test/build
pins (including transitive tooling) are in pyproject.toml. pytest, iniconfig,
pluggy, setuptools, wheel, build and pyproject-hooks are MIT licensed; colorama
is BSD-3-Clause and packaging is Apache-2.0 OR BSD-2-Clause. These are the same
reviewed tooling versions used in TASK-001, without vendoring tool code.

The P214 release docs/oracle are owner-supplied files in Design and Task; they
must be present for oracle tests and release-hash verification. The owner has
authorized tracking these exact files with TASK-002; their contents are unchanged.
Locale tests use two available Windows locales;
effective OS timezone switching is tested only where Python supports `tzset`.
