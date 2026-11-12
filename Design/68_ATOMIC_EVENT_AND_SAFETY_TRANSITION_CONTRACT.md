# BionicButterfly — Atomic Event Evaluation & Safety State Transitions

> **Phase 2.4 review note (2026-11-12):** See the candidate corrective addendum at the end and `84–90` before treating older priority/approval text as normative. **Pending owner approval; not code or flight authorization.**

- **ID:** BB-G0A-FSM-068 | **Rev:** 0.2 | **Date:** 2026-11-12
- **Author:** SA | **Status:** PROPOSED / SIM_ONLY. Only logical virtual wing outputs are defined; this is **NOT** an actual in-air emergency procedure.
- **Cross references:** `57–59`, `61`, `67`, `69`, `71`.

## 1. Canonical snapshot (conceptual type)

`StateSnapshot` has: `run_id`, `eval_at_us`, `system_state`, `owner` (`NONE|SIMULATOR`), `observed_low_first_at_us?`, `observed_low_qualified`, `last_arm_edge_at_us?`, `arm_high_since_us?`, `last_valid_frame_at_us?`, `last_rf_status_at_us?`, `last_rf_status`, `last_switch_state?`, `last_accepted_intent?`, `fault_latches[]`, `policy_digest`, `virtual_motion_allowed`. All timestamps are **integer µs** and never substituted with wall clock. `physical_airborne_status=UNKNOWN` is a constant.

A `SimEvent` is an untrusted stimulus, **not** an authorized state transition. Rejected input never directly advances an arm edge or updates the control-frame freshness timestamp. Hardware faults are *injected simulation fault codes*, not real electrical measurements.

## 2. One evaluation is one transaction

At each `eval_at_us=k*5000`, construct an immutable **pre-state** and fold every event with `event_at_us` since the prior evaluation and `<= eval_at_us` into a candidate batch. Normalizer uses a stable order for diagnostics but **must not publish intermediate actuation**, not even momentarily. From one pre-state it produces one post-state, one safety decision and at most one bounded virtual actuator record. The trace contains all denied reasons in canonical sorted order.

### Batch normalization, in this order

1. Reject malformed scenario **before the run** (wrong schema, duplicate event ID, extra actuator fields, nonfinite/oversized numbers, event-time out of bounds). Nothing may produce enabled output.
2. For a valid run, classify eligible events by `BOOT/RESET`, injected catastrophic fault, explicit disarm (LOW switch), RF/power/input fault, config-edit attempt, candidate arm, and ordinary motion request.
3. Track *fault seen during this tick*; a later HEALTHY status in the same tick **cannot erase** a LOST event or critical fault for that decision. A separately evaluated later tick may acknowledge new health for recovery, but not re-arm automatically.
4. For **one source's distinct `SIM_CONTROL_FRAME` bodies in one evaluation tick**, flag `E_EVENT_ID_CONFLICT`, deny all control frames for that tick and **do not refresh** last-valid time. Semantically duplicate accepted frames with different IDs are idempotent; they are logged and counted once. A LOW and HIGH in the same tick can never form a valid arm edge.
5. Apply any `SIM_CONFIG_WRITE` input as **DENIED** for this G0-A1 run, including when DISARMED, because config is preloaded immutable. A denied write never participates in arm qualification or changes a digest.
6. Decide faults and disarm priority from the *entire* batch, then evaluate fresh input/arm state. Prevent any tick from publishing both a denied arm and enabled output due to callback order.

### Priority semantics (SIM_ONLY)

| Priority | Trigger present during tick | Result (if no higher-priority trigger) | Virtual output |
|---|---|---|---|
| 1 | `RESET` | reset arm eligibility and transition to SELF_TEST via a visible BOOT/SELF_TEST sequence; monotonic run time continues | inhibited |
| 2 | injected `SIM_CATASTROPHIC_FAULT` | `FAULT_LATCHED`, retain typed root cause | inhibited |
| 3 | explicit accepted switch LOW/disarm | If armed: `DISARMED` and clear arm-high edge; if already DISARMED: preserve/advance LOW qualification. Do not clear LOW history on each LOW frame | inhibited |
| 4 | RF LOST/UNKNOWN/expired, input stale or injected critical supply fault | if previously armed/active: `CONTINGENCY`; otherwise remain/return DISARMED; invalidate edge candidate | inhibited |
| 5 | contradictory same-tick control observations | if previously armed/active: `CONTINGENCY`; otherwise DISARMED; `E_EVENT_ID_CONFLICT` | inhibited |
| 6 | profile/config write or mapping denial | deny edit/request; if active profile becomes invalid: fault; otherwise no owner/motion change | prior approved output only if guards remain valid and request cannot affect it |
| 7 | ARM protocol with valid guard snapshot | `ARM_CHECK` then `ARMED_IDLE` only after qualified interval | inhibited until separate subsequent demand |
| 8 | valid active demand | `ACTUATION_ACTIVE` after previous ARMED_IDLE | bounded *virtual* output only |

**A higher-priority reset or catastrophic fault is still reported together with lower-priority hazards**, but only one state transition is committed. A truly malicious parse-level invalid event **rejects the run**, rather than causing a tick-level recoverable fault.

## 3. Boot and arming finite-state rules

1. Require `BOOT` event at t=0. At 0: BOOT→SELF_TEST, sink disabled. At first subsequent tick t=5000: SELF_TEST→DISARMED if preloaded policy has an **approved status and full schema**. Otherwise fail validation before runtime; simulator does not produce ARM state.
2. A valid LOW control observation after DISARMED starts a candidate disarm interval. A second distinct valid LOW frame in a **different evaluation tick** at least 20,000µs later establishes `observed_low_qualified=true`; both and subsequent guards require recent independent `SIM_RF_STATUS(HEALTHY)`.
3. A subsequent accepted HIGH frame (different tick) with flap `<=0.02`, abs(steer) `<=0.05`, valid map and current RF+frame freshness enters ARM_CHECK. Mark `arm_edge_at_us` using the event's original timestamp. No same-tick motion.
4. ARM_CHECK requires a confirming accepted HIGH frame at/after `arm_edge_at_us+100000`, with no LOW or fault in between and all guards current. Only at that evaluation becomes `ARMED_IDLE`, output remains inhibited.
5. A subsequent accepted HIGH frame with flap `>0.05` enters `ACTUATION_ACTIVE` and produces virtual bounded L/R. A high-throttle control frame **during** ARM_CHECK is an invalid qualification, not a hidden queue for motion after arm.
6. Explicit LOW when armed means a *virtual-only* logical disarm/inhibit; pilot still needs a fresh LOW qualification and edge for a new arm. `ARMED_IDLE` does not mean physically landed.
7. At LOST/critical fault in armed state, move to CONTINGENCY, inhibit virtual outputs and **latch recovery interlock**. A new healthy frame alone does not clear it. Only a distinct explicit `SIM_ACK_FAULT` event, observed LOW qualification again and current healthy guards can move to DISARMED; another new HIGH edge is subsequently required.
8. `SIM_ACK_FAULT` is permitted only in the SIM operation context and never grants ARM. If still unhealthy or switch not qualified LOW it is denied, and CONTINGENCY/FAULT_LATCHED persists. Catastrophic fault requires an explicit RESET **after** the source of failure has been removed; this only begins BOOT/SELF_TEST again, not ARMED_IDLE.

**Policy note:** The label `GROUND_ARMED` from early documents is replaced in this SIM candidate with `ARMED_IDLE`, which conveys no actual ground detection.

## 4. Model properties for SA design review

- All state transitions must be total over known valid events, deterministic and carry typed rejection reasons. Every accepted state change has a trace entry with `state_before`, `state_after`, `policy_digest`, `event identifiers` and `time`.
- `RF HEALTHY` or a valid serial frame alone does not grant arming; they are separate independent simulated observations.
- `uart_frame_status=INVALID` is a *deliberate in-band test observation* and cannot refresh `last_valid_frame_at_us`; malformed JSON, invalid field type or nonfinite float is a **parse rejection before runtime**.
- No profile name, source ID from input or scenario event may change `context=PC_SIM` or attach hardware output. Unknown event types/fields are rejected.
- If the virtual sink/log becomes unavailable during active state, terminate as failed, inhibit further virtual outputs and disclose incomplete evidence; never label PASS.
- `RESET` within run never rolls the monotonic clock backward; a scenario seek/restart is a **new run**. This is NOT a hardware servo reboot recovery policy.

## 5. Examples and counterexamples

| Example | Interpretation |
|---|---|
| LOW t=15,000; LOW t=35,000; HIGH t=40,000; HIGH t=140,000; demand t=145,000 | Candidate valid SIM arm path **only** if HEALTHY remains current, all other guards pass and policy was explicitly approved |
| LOW and HIGH events t=15,000/t=16,000 both eligible in tick 20,000 | Control conflict: **no** arm edge |
| HIGH at boot and HIGH repeatedly | Never establishes LOW qualification → deny ARM |
| RF LOST and HEALTHY in same tick | LOST dominates decision; cannot re-arm this tick |
| High flap >0.02 during ARM_CHECK | Cancel pending ARM; no output; require fresh LOW sequence |
| Actual in-air disarm in G4 | **NOT SPECIFIED HERE**, remains separate flight-safety blocker |

## 6. Document approval consequence

These deterministic SIM-only semantics clarify the earlier `58–59` proposals. They do **not** amend the owner's files automatically, and no code or physical test has been executed. Approval of this state machine is one **bounded G0-A1 design decision**, not permission to fly.

## Phase 2.4 atomic semantics supersession candidate (rev 0.2)

**IMPORTANT: old §2 priority table (RESET first, LOW before conflict) is superseded as a candidate by `84` and MUST NOT be implemented as the final G0-A1 policy without reconciliation.** The proposed new ordering is catastrophe over RESET, then independent faults/conflict before *trusted* disarm; normalize all same-tick valid control frames before interpreting their LOW/HIGH bits. A conflict while armed produces SIM-only CONTINGENCY, not a hidden disarm. `SIM_ACK_FAULT` cannot clear a latch in the tick that completes LOW qualification. See `85` error v2 and `86` tests. None of these changes are approved or code-tested.
