# G0-A1 TASK-005 — Pure Priority Kernel Oracle and SA Review Plan

- ID: BB-P217-168 · Source baseline `efe7fa3aff1beeb01af98b98a06593bd8e7af192` · **Design reference only: NOT RUN against TASK-005 code**.
- Machine fixture: `Design/fixtures/P217_SAFETY_PRIORITY_ORACLE_INDEX.json`, cases `P217-T01..P217-T22`.

## Positive execution pipeline

Build legal wire-v2 original JSON bytes by modifying the approved `P210_MINIMAL_WIRE_V2.json`, with one BOOT at T0, approved closed payloads, original event timestamps, and unique IDs. Run **TASK-001 preflight → TASK-002 scheduler → TASK-003 normalizer → TASK-004 temporal facts** using separate **synthetic TEST-ONLY** prior snapshots; finally call TASK-005 with a separately synthetic `pre_state` for each positive oracle. The pre-state is **not** supplied by scenario JSON, and this test does **not** prove a committed state owner exists.

For all 22 oracle recipes, assert exact `provisional_next_state`, internal `priority_category`, `blocks_control_qualification`, `requires_full_fsm=True`, and no other output fields. Preserve original accepted scenario and upstream records unchanged. All listed expected results are **SA-specified**, not Developer-executed PASS results.

### Mandatory families

| IDs | Test category |
|---|---|
| T01 | BOOT T0 ⇒ provisional SELF_TEST with no output |
| T02–T04 | prior FAULT_LATCHED persists; catastrophe overrides RESET and ACK, including pre-CONTINGENCY |
| T05–T08 | active/idle/arm-check explicit RF LOST, UART INVALID, VALID conflict, RF UNKNOWN-only ⇒ interim CONTINGENCY |
| T09–T10 | mixed HEALTHY+UNKNOWN unresolved (blocked but no forced health status); HEALTHY+LOST ⇒ hazard |
| T11–T12 | CONTINGENCY+RESET/ACK or HEALTHY+ACK remains provisional CONTINGENCY; recovery deferred |
| T13–T15 | ordinary RESET with no higher hazard ⇒ SELF_TEST from DISARMED/ACTIVE/SELF_TEST |
| T16–T17 | DISARMED LOW, SELF_TEST empty tick ⇒ defer, do not arm or complete readiness |
| T18–T19 | ACTIVE stale prior age with/without current candidate ⇒ **defer** state transition, **block** control qualification; no output permitted or stale-state conformance claim |
| T20–T22 | catastrophe+ACK; DISARMED INVALID+RESET; healthy ACTIVE with no immediate hazard ⇒ correct priority/defer |

### Mandatory negative and architecture tests

1. Reject wrong pre-state enum/caller objects, `bool`-as-int tick index, stale/mismatched tick metadata, incorrect mirror hazard flags between TASK-003 and TASK-004, malformed BOOT positioning; ordinary library error, no fake `E_*` or `P_*` sidecar.
2. Test no event scans, upstream reruns, state writes, output fields, M0, trace/IO/device imports; O(1) decision once upstream records exist. Verify frozen nested records and stable repeat determinism under locale/TZ/Decimal context.
3. Test **dominant precedence**, not just individual flags: simultaneous catastrophe+RESET+control conflict+RF LOST ⇒ latch; ACTIVE+RF LOST+RESET ⇒ CONTINGENCY; CONTINGENCY+RESET+ACK ⇒ hold; prior latched+RESET/ACK/healthy ⇒ latched.
4. Stage C1 does **not** implement host trust, critical power/scheduler priority, LOW/HIGH qualification, ACK clearance, accepted timestamp refresh, age-based forced FSM transitions, M0 output, trace commit, G1 full conformance or physical flight. These must all be reported `NOT RUN / DEFERRED` rather than falsely PASS.
5. Run TASK-001/002/003/004 regression suites from their own directories (avoid collision of `scripts.scenarios`), package build/install, test/smoke/pip check. Report actual results including skips, warnings, failing initial attempts. No stale or invented evidence.

## Roles and UAT

Developer changes **only** `Source/host_safety_priority_kernel/**`. Owner runs three copy-paste commands (pytest, smoke, pip check) from the new package folder; Developer creates PR only after Owner explicitly approves. SA reviews in separate `ReviewPR/pr-<number>` worktree; Owner merges. No code in Design/Task, and no hardware/flight permission.
