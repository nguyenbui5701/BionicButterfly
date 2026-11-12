# BionicButterfly — G0-A1 ARM, Recovery and No-Event Transition Matrix

- **ID:** BB-P26-FSM-101 | **Rev:** 0.1 | **Status:** SA PROPOSAL / NO CODE, NO OWNER SIGNATURE.
- **Related:** `84`, `95`, `100`, `104`. All times are SIM_ONLY test-fixture candidates.

## 1. State variables (typed conceptual contract)

```text
SafetySnapshot: {
  state: BOOT|SELF_TEST|DISARMED|ARM_CHECK|ARMED_IDLE|ACTUATION_ACTIVE|CONTINGENCY|FAULT_LATCHED;
  last_raw_serial_valid_at_us?: uint;
  last_accepted_pilot_intent_at_us?: uint;
  last_rf_health_status_at_us?: uint;
  last_rf_health: HEALTHY|LOST|UNKNOWN;
  observed_low_first_at_us?: uint;
  observed_low_last_at_us?: uint;
  low_qualified: bool;
  arm_high_edge_at_us?: uint;
  arm_high_qualified: bool;
  last_authorized_intent?: {arm_switch, flap, steer, map_revision};
  fault_latches: list<typed_reason>;
  allow_virtual_output: bool;
}
```

Snapshot states do **not** prove physical airborne status. In a single tick, the FSM reads only an immutable pre-snapshot, normalized batch and immutable policy; no wall-clock or UI callback can mutate it.

## 2. Candidate state transitions and edge invalidation

| Before | Stimulus / eligibility | After | Arm edge / last-intent behavior | Virtual output |
|---|---|---|---|---|
| `BOOT` at T=0 | valid BOOT | `SELF_TEST` | clear all | null |
| `SELF_TEST` | next tick, valid approved policy & no critical power/scheduler issue | `DISARMED` (RF UNKNOWN permitted) | no retained HIGH | null |
| `SELF_TEST` | catastrophe | `FAULT_LATCHED` | clear | null |
| `SELF_TEST` | critical power/scheduler issue (noncatastrophic) | `SELF_TEST` | clear, record reason | null |
| `DISARMED` | first healthy accepted LOW | `DISARMED` | set `low_first` timestamp only | null |
| `DISARMED` | second healthy accepted LOW, **different tick**, `event_at_us` separation >=20,000µs, no interruption | `DISARMED` | `low_qualified=true` (committed at end of second tick) | null |
| `DISARMED` | valid HIGH before LOW qualification | `DISARMED` | invalidate LOW window; not an arm edge | null |
| `DISARMED` | valid HIGH after qualified LOW at a **later tick**, neutral input and all guards | `ARM_CHECK` | record edge event timestamp | null |
| `ARM_CHECK` | HIGH confirmation at a **later tick**, >=100,000µs since edge, neutral & continuously healthy | `ARMED_IDLE` | confirmed HIGH; no active effort yet | null |
| `ARM_CHECK` | no valid control this tick | `ARM_CHECK` if still fresh else `CONTINGENCY` | no timer-only confirmation; don't refresh | null |
| `ARM_CHECK` | valid HIGH nonneutral early, invalid frame, RF expired, conflict | `CONTINGENCY` (SA proposal) | revoke candidate | null |
| `ARMED_IDLE` | later accepted valid HIGH `flap>0.05`, healthy & profile valid | `ACTUATION_ACTIVE` | store pilot intent for S1 | bounded only |
| `ACTUATION_ACTIVE` | coherent accepted valid HIGH demand | `ACTUATION_ACTIVE` | store new authorized intent, apply envelope | bounded |
| `ACTUATION_ACTIVE` | **no new frame**, accepted intent and RF still fresh | `ACTUATION_ACTIVE` S1 | retain last, age continues | bounded virtual effort |
| `ACTUATION_ACTIVE` | accepted control age or healthy RF age **>200,000µs** | `CONTINGENCY` | invalidate arm eligibility | null |
| `ACTUATION_ACTIVE` | invalid in-band frame or valid distinct LOW/HIGH conflict | `CONTINGENCY` | do not refresh or count LOW | null |
| `ACTUATION_ACTIVE`/`ARMED_IDLE` | coherent accepted LOW, healthy guards | `DISARMED` | revoke active intent and LOW qualification; begin fresh LOW after this tick | null |
| `CONTINGENCY` | RESET or LOW alone | `CONTINGENCY` | low can qualify only after health recovers; RESET never clears | null |
| `CONTINGENCY` | valid ACK + **previous-tick committed** LOW qualification + healthy RF/power + no pending hazard | `DISARMED` | **clear existing low-qualified/arm-high**; requires a new LOW observation sequence to rearm | null |
| any | catastrophe, including RESET same tick | `FAULT_LATCHED` | terminal for current run | null |
| `FAULT_LATCHED` | RESET, ACK, RF restored, LOW/HIGH | `FAULT_LATCHED` | no in-run clear | null |

**Proposed refinement:** a `LOW` from ACTIVE causes an immediate virtual DISARMED state, but **that very LOW must not also count as first LOW for re-arming**. A subsequent distinct LOW series is necessary; no loop of disarm/arm edge in a single tick.

## 3. LOW qualification interruption rule: choose conservative policy

A qualifying LOW series requires at least two accepted LOW observations in different ticks, separated by minimum 20,000µs of original event timestamps, with continuous **effective health qualification at every intervening evaluation tick**. Interruption events reset both `low_first` and `low_qualified`:

- any accepted HIGH (whether neutral or not);
- explicit RESET;
- RF state LOST, UNKNOWN or expired, critical simulated power issue, catastrophic fault;
- any in-band INVALID frame or semantically conflicting control batch;
- map/profile mismatch and authority violations.

A tick without any new control frame **does not reset** LOW qualification so long as original LOW frame and healthy RF remain fresh. But it does not itself count as a second LOW or extend the interval. If a later LOW arrives after the previous LOW has become stale, treat it as new first LOW, not a qualified continuation.

### 3.1 The minimum two-LOW interval

At 5ms tick: LOW at 15,000µs, LOW at 35,000µs ⇒ 20ms satisfied at second tick. LOW at 15,001µs and LOW at 35,000µs ⇒ 19,999µs **insufficient**, despite the same tick indices. HIGH at 40,000µs can only arm if previously committed qualification and all guards hold.

### 3.2 HIGH continuation

HIGH edge at 40,000µs and qualifying HIGH at 140,000µs meets the 100ms boundary (if RF is still fresh); at 139,999µs the next tick evaluation is 140,000 but **the original 139,999 timestamp does not qualify**. A self-test/RESET/invalid-frame/health break during interval cancels attempt. The high-confirming frame can only enter `ARMED_IDLE`, not start flap in same tick.

## 4. Recovery invariant

`CONTINGENCY` can be cleared only by valid `SIM_ACK_FAULT` with previous-snapshot `low_qualified=true`, healthy current RF/power, no critical hazard and an approved recoverable cause. If ACK arrives with final qualifying LOW in *same tick*, reject ACK and remain CONTINGENCY; qualifying LOW may commit for the **next** tick. If an ACK clears contingency, it consumes qualification and leaves DISARMED with LOW qualification reset.

**Explicit unresolved subdecision:** which non-catastrophic causes are ACK-clearable must be an approved enum allowlist. For simulator G0-A1, SA recommends only `E_RF_NOT_HEALTHY`, `E_FRAME_STALE`, `E_CONTROL_BATCH_CONFLICT`, `E_FRAME_INVALID` and recoverable simulated voltage warnings **after all conditions are healthy**, with typed cause. A `scheduler stall` or internal `E_NUMERIC_INVALID` should require a new run absent a separately modeled recovery stimulus. Until owner approves this list, **do not mark recovery-related test oracles PASS**.

## 5. Invariants for review

`ARMED_IDLE` requires a real confirmed HIGH frame, not virtual elapsed time. `ACTUATION_ACTIVE` virtual output requires authorized fresh intent and healthy RF at **every tick**. `CONTINGENCY`/`FAULT_LATCHED` virtual effort always null. `DISARMED` virtual effort null, not physical 0-degree angle. An invalid or conflicting frame never counts as LOW, HIGH or last authorized demand. No behavior here defines real RF-loss/disarm handling during flight.
