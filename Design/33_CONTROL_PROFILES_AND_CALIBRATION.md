# BionicButterfly — V1 Control Profiles, Calibration and Configuration Lifecycle

- **Document ID:** BB-CAL-033 | **Version:** 0.1 | **Date:** 2026-11-12
- **Status:** PROPOSED; simulator-only concepts and hardware calibration process, no active servo configuration endorsed.
- **Dependencies:** `17–25` mechanical/electrical, `27` safety FSM, `28` firmware interfaces, `32` pilot mapping, `35` verification.

## 1. Strictly separate profiles by intended operation context

| ID (conceptual) | Purpose | Valid context | When outputs are allowed | Flight-capable? |
|---|---|---|---|---|
| `SIM_WING_KINEMATICS_V1` | virtual-time logic and fault replay | `PC_SIM` only | simulated HAL | **NO** |
| `BENCH_SIGNAL_ONLY_V1` | GPIO/PWM timing without attached wings | authorized `BENCH_SERVO_ONLY` | only measured electrical and servo limits | **NO** |
| `RESTRAINED_AIRFRAME_V1` | mechanical response and force characterization | `RESTRAINED_AIRFRAME` | after G2 pass and separate rig signoff | **NO** |
| `FLIGHT_MANUAL_C0_V1` | pilot-controlled real C0 airframe | `FLIGHT_TEST_APPROVED` only | **unavailable until G0-C/G4 authorization** | CANDIDATE, NOT APPROVED |
| `FLIGHT_MANUAL_C1_LED_V1` | C0 plus flight-tested LED mass/power | `FLIGHT_TEST_APPROVED` only | unavailable until C1 independently requalified | CANDIDATE, NOT APPROVED |

A *profile name* shall not grant context privileges. Context authorization is external to a profile and checked independently by supervisor. A profile configured for `SIM` must never be accepted as measured airframe calibration.

## 2. Versioned and immutable configuration layers

```text
CalibrationRecordV1 {
  schema_version, board_revision, airframe_revision, left_servo_id, right_servo_id
  wing_geometry_revision, battery_setup_id, transmitter_mapping_revision
  servo_left: { pulse_min, pulse_center, pulse_max, direction, measured_angle_table, safe_slew }
  servo_right: { pulse_min, pulse_center, pulse_max, direction, measured_angle_table, safe_slew }
  inertia_and_force_evidence: { test_id, report_id, uncertainty? }
  waveform: { family, measured_feasible_frequency_range, amplitude_range, phase_relation }
  allowed_operation_contexts, policy_revision, measurement_report_ids
  record_revision, checksum_or_digest, approval_status
}
```

`pulse_*`, limits, frequency, stall thresholds and phase laws are intentionally **unset** until real calibrated hardware exists. A fixed "0–180°" servo range is forbidden as a flight assumption. A record must be validated both structurally (schema/limits/revision) and against hardware identity. Storage must be transactionally updated while disarmed; failed validation/power loss restores previous valid state and **never produces permissive motion**.

## 3. Calibration progression (each stage is a separate reviewed gate)

| Stage | Safe setup | Measure | Evidence / stop condition |
|---|---|---|---|
| CAL-00 | PC simulator only | mapping signs, serial/radio failures, deterministic trajectories | event trace; simulator alone cannot certify hardware |
| CAL-01 | bench, servo disconnected from flapping mechanism | commanded pulse vs observed shaft response, reversal, current, start-up pulse; power rail | scope/serial/video log; stop on hot device, glitches, unexplained movement |
| CAL-02 | servo+linkage, without flexible wings or guarded minimal load | mechanical contact, backlash, soft endpoints, left/right symmetry | recorded endpoint table; stop on binding/stall |
| CAL-03 | fully restrained airframe behind barrier | wing stroke amplitude, frequency *under load*, current/thermal rise, force/moment | instrumented rig, multiple operating points; stop on structural damage |
| CAL-04 | same restrained rig | throttle vs measured flap effort and differential vs observed moment, CG sensitivity | empirical polarity and control authority with uncertainty |
| CAL-05 | approved G4 flight plan | manual pilot response and recovery, repeated trial evidence | never run until airframe-specific contingencies and flight site approved |

No live calibration with a free-flying vehicle. `CAL-01` is not authorization to energize unvalidated power systems: use the electrical design G2 review first.

## 4. Control rate and profile changes

- `rate=LOW/NORMAL` may modify **only** a bounded, pre-validated gain curve; it must not bypass measured servo limits or safety interlocks. Both rate options must carry their own measured profile ID.
- Default V1: *all* persistent profile edits and trim/pulse edits are disarmed + authorized bench-only. Midair profile switching is **disabled** until a specific transition law is flight tested and signed off. Fixed-profile operation is the preferred V1 first-flight scope.
- A radio switch moved while disarmed may select a profile for next arm only if both profile and mapping were approved for the current airframe. Switching context or profile cannot implicitly arm.
- Frequency and amplitude knobs in the simulator are tagged SIM_ONLY; output UI must never claim they are flight-safe values.
- If pilot trims are later needed, define explicit bounded control trim source, persistence semantics and whether editing in flight is permitted; none is currently authorized.

## 5. Candidate mixer with audit hooks (not implementation)

Conceptually: `u = demand(0..1)`, `s = steering(-1..1)`; `C = profile.common_curve(u)`, `D = profile.differential_curve(u,s)`, and `L,R = envelope(C ± D)`. Preserve common lift authority under differentiation where feasible, and log both requested and saturated values. This only describes commanded motion; it does not imply the airframe generates thrust or torque in the correct direction.

Observable data required in simulator/bench logs: `profile_id`, `mapping_revision`, `u`, `s`, `requested_common`, `requested_diff`, `limited_left/right`, `limited_reason`, `actual_servo_feedback_available` (boolean), `output_context`, `arm_status`, `link_state`, `fault`. If no physical encoder/wing sensor is fitted, output is **commanded**, not **measured**.

## 6. Calibration rejection rules

Reject and remain DISARMED if: incomplete record; mismatched board/airframe or servo pair; non-finite/out-of-range configuration; swapped left/right calibration; unverified wing geometry; calibration not signed for requested context; invalid checksum; persisted record older than mandatory schema; attempt to write while armed; attempted rollback to unsafe revision. On invalid storage, do not silently fall back to generic vendor PWM values for flight.

## 7. Change governance and signoff

Every revision: `CAL-XX` evidence ID, what changed and why, previous and new record digests, G2/G3 test reports, reviewer, owner approval for new flight-capable profile, date, Git commit and exact airframe serial/revision. Configuration migration requires a bench re-validation; changing wings, linkages, servo model or battery can invalidate a previous qualified flight profile.

## 8. Open decisions

Exact servo and coupling model, servo speed/force margins, mechanical zero, pulse/min/max, permitted waveform families, arm qualification interval, allowed in-flight trims, transport status semantics, and battery cutoff policy. No flight profile passes current gates.
