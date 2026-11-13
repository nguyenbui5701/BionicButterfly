# G0-A1 — TASK-003 Normalization Oracles and SA Review Gate

- ID: BB-P215-162 | Baseline `12b4ee1355d146080810d028843d24481f88af77`
- Machine test fixture: `Design/fixtures/P215_BATCH_NORMALIZER_ORACLE_INDEX.json` (18 test recipes, all NOT RUN on TASK-003 implementation at authoring time).

## Test methodology

For each positive case, convert pseudo-events into **schema-valid** v2 original JSON bytes (follow approved six event types and exact payloads), run TASK-001 `validate_wire`, then TASK-002 `iter_virtual_ticks`, then TASK-003 normalizer on the specified target tick. Decimal token strings in fixtures must be serialized as *unquoted JSON number tokens*, not converted through binary floats. Assert exact source IDs, sorted causal IDs, groups, flags, latest original timestamps and RF observations. Approved Design oracles are expected values, **not test PASS evidence**.

| Tests | Coverage |
|---|---|
| T01–T02 | BOOT and empty tick; no synthetic signals |
| T03–T04 | One valid LOW/HIGH observation, no arming |
| T05 | Distinct-ID semantically equivalent controls grouped once; latest original timestamp and UTF-8 sorted IDs |
| T06 | Two different VALID bodies → conflict fact, never state transition |
| T07–T09 | In-band INVALID alone/mixed with VALID; both conflict and invalid facts can coexist |
| T10–T12 | RF HEALTHY/LOST/UNKNOWN presence and original observation order; no inferred effective RF state |
| T13–T14 | Catastrophe+RESET+ACK, two ACKs; preservation without priority transitions |
| T15–T16 | First-seen source order differs from UTF-8 ID order; Unicode precomposed/decomposed IDs not normalized |
| T17 | `0.1000000` and `1e-1` exact decimal equivalence without binary float |
| T18 | Subsequent tick contains only its own observations, no prior-tick carryover |

### Mandatory additional tests

- Wrong type/RejectedPreflight/raw dict fails before output. Forged malformed in-memory wrapper cannot grant host trust.
- Deep immutability for nested groups, members, flags and IDs. Repeat same tick normalization yields same data.
- Legal large same-tick batch near 20,000-event policy limit, raw size within 2MiB, with *instrumented* O(N) event visits (not timing alone); no per-group full re-scan of all events.
- No M0/state/clock/trace/IO calls; no accepted-frame refresh or RF effective-state field; all original observations remain visible even if contradictory.
- Execute read-only regressions: TASK-001 203 tests and TASK-002 44 tests (actual counts may vary; report what ran). Execute build/compile/pytest/smoke/pip check. No invented PASS.

### Owner UAT and PR gate

Developer provides three ready-to-run PowerShell commands from `Source/host_batch_observations/`: `pytest -q -p no:cacheprovider`, `scripts/smoke.py`, `pip check`. Owner runs them and authorizes PR **only after UAT**; Developer never merges. SA reviews under `ReviewPR/pr-<number>/` isolation.

### Deferred

The eight-state SafetySupervisor, 20ms LOW and 100ms HIGH qualifications, independent 200ms freshness, catastrophic latch priority, ACK/RESET, S1 hold, host trust allowlist, trace commit and any virtual actuator output are **not** implemented or certified by TASK-003. G0-B/G4 physical flight gates remain NO-GO.
