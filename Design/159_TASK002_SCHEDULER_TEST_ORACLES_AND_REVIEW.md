# G0-A1 — TASK-002 Scheduler Acceptance & SA Review Plan

- **Document:** BB-P214-159 · **Evidence:** DESIGN ORACLES ONLY / NOT RUN ON FUTURE CODE
- **Baseline:** `ca457f784975c2d0959b1baf988483fa042f5c67`; inherits authority of `115`, `116`, `132`, `141`.

## Test families and checkpoints

Machine recipe/oracle list: `Design/fixtures/P214_TICK_BATCH_ORACLE_INDEX.json`, test IDs `P214-T01..P214-T14`. Scenarios are built by minimally mutating the approved `P210_MINIMAL_WIRE_V2.json` and must be validated using TASK-001 `validateWire` **before** invoking TASK-002 scheduler. Each test records actual result vs expected, no fabricated PASS.

| IDs | Concern | Required outcome |
|---|---|---|
| T01–T03 | T0, empty ticks, interior/boundary times | Inclusive T0 and right boundary, exclusive left |
| T04–T06 | multiple same-tick events, input order, original timestamps | no lost/reordered/rounded events |
| T07–T09 | in-band invalid UART, different VALID controls, RF contradictions | **preserved raw observations**, no conflict/health decisions |
| T10 | catastrophe + reset + ACK same tick | no priority resolution in scheduler |
| T11 | maximum duration/limit | 12001 batches, zero event duplication, no unbounded eager copies |
| T12 | rejected preflight or untrusted raw dict direct caller | no scheduling/side effects |
| T13 | immutable result and accepted scenario unchanged | mutation attempts fail or cannot affect subsequent enumeration |
| T14 | stable replay of pure batches | repeated same accepted input gives same sequence across locale/timezone settings where supported |

Additional required tests:

1. **Original timestamp semantics:** `4999` and `5000` appear at `T=5000`; `5001` appears only at `T=10000`. `0` only appears in tick zero. An event exactly at scenario duration belongs to final tick.
2. **No host authority bypass:** the output is a data-only plan, not an output grant; none of `mixM0`, trace writer, RF resolution, policy loader, servo/GPIO or network is imported/instantiated/called by the scheduler.
3. **Complexity:** instrument event visits; each original event processed no more than a small constant number of times in one full enumeration, including 20000-event admissible scenario; avoid O(ticks×events).
4. **Interoperability:** use the merged TASK-001 package from the same verified source baseline, including its immutable accepted-result type. Do not change its implementation. Validate tests on Windows Python 3.11+.
5. **Error boundary:** a rejected result passed to tick scheduler must raise a normal library misuse exception, not return a fabricated `P_*` sidecar or emit any tick; invalid raw bytes must still be processed only by TASK-001.
6. **No suppression:** tests must assert **exact IDs in each tick** and original timestamp values, not just batch counts; include duplicate-preservation of semantically equivalent control payloads with **distinct globally unique IDs**.

## Owner acceptance / review division

- **Developer**: implement source and tests, run build/unit+integration/smoke, fix bugs, report actual PASS/FAIL and exact Git diff in `Source/host_virtual_ticks/**`.
- **Owner**: unzip and place file package; do Git staging/push; run three prescribed PowerShell commands for UAT (no need to ask AI Developer to run known commands again unless errors); explicitly instruct Developer when to open PR.
- **SA**: review frozen design conformance, scheduler edge cases, all tests and provenance; inspect PR only in `ReviewPR/pr-<N>` worktree; owner alone decides merge.

## Not part of TASK-002

Not a full state engine, simulator runner, dynamic RF health/age tracker, control-batch conflict resolver, ARM qualification, fault latch, ACK state machine, trace transaction, JCS replay, executable host trust allowlist, hardware IO or flight authorization. A future task must bind those independently, without inheriting authority from this pure scheduler.
