# G0-A1 — TASK-006 ARM Qualification Oracles and Review Plan

- Document BB-P218-171; baseline `f2c9237bd4a1e2e077c15db6eb4c22ed2a250d5d`; `PC_SIM_ONLY`.
- Fixture `Design/fixtures/P218_ARM_QUALIFICATION_ORACLE_INDEX.json`: **P218-T01..T32**. These are **design-only / NOT RUN as TASK-006 runtime tests**.

## Positive test pipeline

For every P218 recipe, construct legal *wire-v2* original JSON bytes from `P210_MINIMAL_WIRE_V2.json`, preserving exact decimal number tokens, BOOT at 0, event ordering and original timestamps. Run the actual TASK-001 preflight -> TASK-002 scheduler -> TASK-003 normalizer -> TASK-004 temporal facts -> TASK-005 priority -> TASK-006 proposal. Pre-state, prior timestamp snapshot, prior qualification window and hypothetical guard verdict are separate **synthetic test fixtures**, NEVER inserted into scenario JSON or treated as independent trusted permission.

Check the nine result fields with exact types/values, all input objects unchanged, repeat determinism and deep immutability. Confirm positive proposal NEVER contains post-state, accepted timestamp, output gate or effort. All outcomes remain **requires_full_fsm=True**.

## Acceptance oracle coverage

| IDs | Family |
|---|---|
| T01–06 | First LOW; 19,999 / 20,000 / 20,001µs spacing; same-tick equivalent LOWs only one sample; empty tick holds without qualifying |
| T07–12 | HIGH needs LOW qualified at a prior committed tick, and exact flap ≤0.02, abs steer ≤0.05, inclusive edges |
| T13–18 | Neutral HIGH confirmation at 99,999 / 100,000 / 100,001µs; early HIGH retains edge; empty tick does not confirm; non-neutral resets window |
| T19–24 | Coherent LOW disarm observation; ARMED_IDLE flap equal 0.05 vs strictly above; ACTIVE cannot authorize new output |
| T25–30 | INVALID, distinct valid conflict, RF LOST, RESET, catastrophe, stale armed prior age block promotion |
| T31–32 | UNRESOLVED health/control and CONTINGENCY+ACK cannot confer qualification or recovery |

## Mandatory negatives and safety audit

- Wrong input type; forged enum/wrappers; malformed tick grid/mismatch; invalid/nonnumeric/stale or non-prior committed window, conflicting high+low snapshot; bool-as-int; wrong pre_state/window pairing. Reject using ordinary API TypeError/ValueError, not new public E_/P_ code.
- Synthetic `health=PASS` with C1 blocker True; `control=ADMITTED` without one valid uncontested control group, or alongside INVALID/conflict; `health=FAIL/UNRESOLVED` with ADMITTED; `control=ABSENT` despite a visible control candidate: **reject contradictory test-verdict record**. A synthetic verifier must never be made into a runtime authorization source.
- Check HIGH neutrality exactly (Decimal 0.020000, 2e-2, ±0.05 vs 0.050001), demand `>0.05` strict, no float conversions, 5ms virtual ticks vs raw-event time, initial/terminal boundaries.
- Ensure low qualified timestamp is from a **prior committed** tick; HIGH confirmation must be a **later tick** with a new distinct admitted frame. No timer-only progression. An interrupted low series needs two new LOW observations. DISARMED or ACTIVE LOW disarm must not auto-start rearm at the same tick.
- Runtime O(1) over already-normalized metadata, no source-event scanning, upstream rerun, global state, wallclock, filesystem/network, trace, mixer, host provisioning, GPIO/servo/PWM/RF or actual flight dependencies.
- Re-run TASK-001–005 regressions **from their individual working directories**; log actual counts and failures. Build/package/wheel install + dev/wheel smoke + pip-check required. Historic 203/44/59/140/208 counts are references, not guaranteed.

## Deferred conformance

This proposal stage does **NOT** certify full FSM, state commit, host trust, effective RF, frame admission, CONTINGENCY ACK recovery, ACTIVE S1 output hold, trace append-before-publish, virtual output, real RC or flight. P28-T08/T09/T13/T14/T26/T27 and P210-T02 are NOT RUN as full-system state/output tests even if relevant proposal mechanics are tested. Full R1 health and safety priority must be resolved before output. SA reviews new Source diff and owner release hashes; Owner decides merge.
