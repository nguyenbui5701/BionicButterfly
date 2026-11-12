# BionicButterfly — G0-A1 SIM_ONLY Numeric Policy Proposal

- **ID:** BB-G0A-POL-067 | **Revision:** 0.1 | **Date:** 2026-11-12
- **SA status:** **PROPOSED / OWNER APPROVAL PENDING**. This is a *test fixture policy*, **NOT** flight controller tuning or a receiver, PWM or physical servo specification.
- **Cross-documents:** `57–60`, `63`, `66`, `68–74`.

## 1. Proposed candidate policy `SIM_POLICY_CANDIDATE_22A`

| Field | Proposed SIM value | Units / exact boundary | Engineering reason (NOT hardware validation) |
|---|---:|---|---|
| `scheduler_step_us` | **5,000** | µs, evaluation at `k*5000` | convenient virtual discretization; not an ESP32 timing commitment |
| `arm_low_observation_us` | **20,000** | µs; **two distinct valid low frames** spanning at least this time | distinguish a deliberate observed disarm position before arm request |
| `arm_high_qualification_us` | **100,000** | µs from accepted high edge; **a confirming high frame at/after boundary** | provide a multi-tick qualification window |
| `frame_timeout_us` | **200,000** | µs; fresh when `age <= 200000`, stale when `age > 200000` | permit age boundary tests independently of RF status |
| `rf_status_timeout_us` | **200,000** | µs; status becomes UNKNOWN when age `> 200000` | prevent stale one-time HEALTHY from persisting indefinitely |
| `neutral_flap_max` | **0.02** | normalized inclusive ≤ for arming, not motion claim | illustrative numerical guard for boundary testing |
| `neutral_steer_abs_max` | **0.05** | `abs(steer) <= 0.05` for arming | illustrative centering guard |
| `active_flap_threshold` | **0.05** | active only if flap `> 0.05` after armed idle | separate neutral from virtual actuation in tests |
| `virtual_left_min/max` | **0 / 1** | dimensionless virtual output | explicitly not a servo pulse, physical angle or thrust |
| `virtual_right_min/max` | **0 / 1** | dimensionless virtual output | same |
| `max_scenario_duration_us` | **60,000,000** | inclusive final evaluation time ≤ 60s | bounds host processing and replay |
| `max_events` | **20,000** | inclusive ≤ count | prevents unbounded event arrays |
| `max_input_bytes` | **2,097,152** | UTF-8 bytes; 2 MiB | parser resource bound |
| `max_trace_bytes` | **16,777,216** | UTF-8 bytes; 16 MiB | bounded export, fail closed before misreporting PASS |
| `max_json_nesting` | **16** | levels, reject deeper | parser hardening |
| `max_event_id_utf8_bytes` | **64** | nonempty, no control chars | stable identifiers |
| `max_generic_string_bytes` | **256** | except stricter IDs | avoid arbitrary payload abuse |
| `source_owner` | `SIMULATOR` | exact enum | no physical RC in host-only build |
| `context` | `PC_SIM` | exact enum | compile/composition-bound; scenario cannot elevate |
| `randomness_policy` | deterministic/no stochastic input | no random draw in G0-A1 core | avoids hidden seeds until independently designed |

**Warning:** All numbers are **SA proposals** designed to make software invariants unambiguous. A 200ms SIM timeout is *not* a safety rating for an ExpressLRS receiver; a 100ms SIM arm qualification is *not* qualified hardware arming. No number above may be copied to a flight profile without an independent G0-B/G0-C review and real measurement.

## 2. Required accepted-frame semantics

- An accepted `SIM_CONTROL_FRAME` is schema-valid, with `uart_frame_status=VALID`, valid `SIM_ONLY` map revision and source; accepted frames update `last_valid_frame_at_us` **even before SIMULATOR is armed**, so low-position qualification is possible.
- At least **two accepted LOW frames evaluated in two different ticks** and separated by `>= arm_low_observation_us` establish `observed_low_qualified=true`. The low sample must remain valid/fresh at the high edge. A single LOW event, or LOW and HIGH in one tick, is insufficient.
- A subsequent distinct valid HIGH frame creates an edge and enters `ARM_CHECK`, only if both input and RF health are current and all neutral/other preconditions pass.
- Before `ARM_CHECK -> ARMED_IDLE`, the switch must remain observed HIGH across the qualification; at least one further accepted HIGH frame at or after `high_edge_at_us + 100000` is required, and all guards must be valid at evaluation. A status-only timer tick cannot arm without a confirming frame.
- If the same tick has a critical fault, explicit disarm, conflicting frames, RF LOST, UNKNOWN or stale input, that tick cannot arm. Once an arm candidate is invalidated, a new qualified LOW sequence is required.
- Consecutive high frames after arming do not create new arm edges. On RESET or fault recovery, clear low/high edge eligibility; restored RF health alone never re-arms.

## 3. Time and event boundary policy

- Clock origin is **0 µs**. The `BOOT` event is mandatory at `event_at_us=0`; the first evaluation at `t=0` moves BOOT→SELF_TEST (virtual output disabled), and next evaluation at 5,000µs runs SELF_TEST→DISARMED (if the preloaded policy is valid).
- Each other event time is an integer `0 <= event_at_us <= max_duration_us`. It is eligible for the first evaluation at `ceil(event_at_us/5000)*5000`, where `ceil(0)=0`. The original event timestamp is preserved for age/freshness; no rounding of input time is hidden.
- Distinct frames in the **same evaluation tick** cannot form the LOW→HIGH arm edge. If they carry different contents, the batch's control component is a conflict and is denied with `E_EVENT_ID_CONFLICT`. Exact duplicate semantic observations with different IDs are counted once for state and freshness, with deduplication logged.
- Frame freshness at `t`: `last_valid_frame_at_us` exists and `(t - last_valid_frame_at_us) <= 200000`. RF health freshness is evaluated **independently** from the most recent accepted `SIM_RF_STATUS(HEALTHY)` event, with age `<=200000`. Explicit `LOST` overrides healthy status until a later independently accepted `HEALTHY` event **in a subsequent tick**.
- No valid frame or no valid RF status ⇒ not fresh. After expiration, RF is `UNKNOWN` (not implicitly `HEALTHY`); a `LOST` report is reported as `LOST`, even if the status itself later becomes stale, until a verified new status arrives or a new run begins. New arm is blocked for both states.

## 4. Proposed canonical policy record — NOT AUTHORIZED FOR EXECUTION

```json
{
  "schema_version": 1,
  "policy_id": "SIM_POLICY_CANDIDATE_22A",
  "model_tag": "SIM_ONLY",
  "allowed_context": "PC_SIM",
  "owner": "SIMULATOR",
  "scheduler_step_us": 5000,
  "arm_low_observation_us": 20000,
  "arm_high_qualification_us": 100000,
  "frame_timeout_us": 200000,
  "rf_status_timeout_us": 200000,
  "neutral_flap_max": 0.02,
  "neutral_steer_abs_max": 0.05,
  "active_flap_threshold": 0.05,
  "virtual_left_range": [0, 1],
  "virtual_right_range": [0, 1],
  "max_scenario_duration_us": 60000000,
  "max_events": 20000,
  "max_input_bytes": 2097152,
  "max_trace_bytes": 16777216,
  "max_json_nesting": 16,
  "max_event_id_utf8_bytes": 64,
  "max_generic_string_bytes": 256,
  "approved_for_host_execution": false,
  "owner_approval_ref": null,
  "physical_pwm_hz": null,
  "physical_servo_pulse_us": null,
  "airborne_failsafe_policy": null
}
```

**An implementation receiving this unchanged DRAFT policy must refuse arming/execution.** `approved_for_host_execution` may become true **only after** an explicit owner-approved baseline revision and validated configuration; this illustrative JSON itself is not executable approval. The new policy has no runtime “turn this on” bypass in scenario input.

## 5. Deferred design items

- Physics-integrated 6-DOF simulation; real aero coefficients; IMU closed-loop control; hardware servo PWM/serial rates.
- In-run persistent profile writes, crash-safe disk atomicity and rollback (separate G0-A2 or later). First G0-A1 treats config as immutable from run start; `CFG-05` and `G1B-15` are **DEFERRED** unless owner expands scope.
- Multi-step scheduler equivalence across different tick sizes; freeze only a **single** 5ms tick for G0-A1 and compare runs with the same evaluator schedule.

**Decision required:** owner must explicitly accept/revise these values as *simulator-only* under D-061, not as robot flight parameters.
