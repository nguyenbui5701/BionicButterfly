# BionicButterfly — V1 Firmware Module & Timing Contracts

- **Document ID:** BB-SW-028 | **Revision:** 0.1 | **Date:** 2026-11-12
- **Owner:** SA | **Status:** PROPOSED, interface design only; no coding task authorized.
- **Goal:** deterministic control core with RC-exclusive flight authority and clean MCU/simulator separation.

## 1. Dependency direction and module ownership

```text
┌──────────────┐  ┌────────────────┐       ┌───────────────┐
│ RC/UART      │  │ Bench/Web      │       │ PC Simulator  │
│ decoder      │  │ adapter        │       │ adapter       │
└──────┬───────┘  └───────┬────────┘       └───────┬───────┘
       └──────────────────┴─────────────────────────┘
                             ↓ (observations)
                     Validator / freshness
                             ↓ (validated pilot demand)
                     Authority + Safety FSM
                             ↓ (authorized intent)
                     Motion Profile / Mixer
                             ↓ (wing/servo targets)
                      Envelope + Slew Gate
                             ↓
                      Actuator HAL (PWM)
                             ↓
                       L / R servos

   Voltage/RF/clock/health → safety supervisor (independent inputs)
   Status/events → read-only log / telemetry → optional UI/LED
```

**Dependency rule:** Pure core does not import ESP-IDF/Arduino, Wi-Fi libraries, LEDs, clock globals or PlatformIO. HAL depends on core interfaces; core depends only on abstract time/config/observations. Adapters must never write PWM, state, owner or limits directly.

| Module | Owns | Must not own |
|---|---|---|
| `RcReceiverAdapter` | exact selected UART protocol decode, CRC/frame validity, channel mapping, available receiver health, local time stamp | arming decision, wing angles |
| `BenchInputAdapter` | authenticated bench inputs *only while allowed* | airborne control authority |
| `InputValidation` | finite/range/schema checks; frame freshness; typed accepted/rejected observations | outputs/servo drive |
| `AuthorityManager` | active owner, explicit ARM edge, revocation and source transition | physics or GPIO |
| `SafetySupervisor` | state transitions, fault latching, output permission, context-specific policy | parse CRSF or directly toggle PWM outside HAL |
| `MotionPlanner` | deterministic elapsed-time waveform, common/differential demand, profiles | bypass envelope limits |
| `EnvelopeGate` | calibrated pulse/angle/slew/saturation checks, validity of board/airframe profile | UI network logic |
| `ActuatorHAL` | hardware PWM, neutral/signal enable policy according to qualified board | source selection, fail-safe policy decisions |
| `PowerMonitor` | measured ADC voltage/validity and brownout observations | silent assumptions about charge remaining |
| `TelemetryLogger` | status and event recording without blocking control | changing state or output |
| `SimulatorHAL` | virtual monotonic time, deterministic fake RX/power/servo, event injection | claims of measured aerodynamic flight dynamics |

## 2. Canonical interface definitions — conceptual schema, no implementation

```text
ReceiverObservationV1 {
  schema_version: 1
  ingress_at_monotonic_us: u64             // stamped after validated serial control frame
  source: RC_PRIMARY
  normalized_channels: {throttle:[0,1], steering:[-1,1], arm_switch:bool, profile:enum}
  frame_integrity: VALID | INVALID
  rf_link: HEALTHY | LOST | UNKNOWN       // independent of UART receive freshness
  failsafe_indicated: TRUE | FALSE | UNKNOWN
  channel_map_revision: opaque string
  optional_transport_sequence: optional u64  // only if actual protocol provides
}
ValidatedPilotDemandV1 {
  observation_at_monotonic_us: u64
  authority: RC_PRIMARY | BENCH_LOCAL | SIMULATOR
  throttle:[0,1]; steering:[-1,1]; arm_switch:bool; profile:known_enum
  validity: VALID | REJECTED + typed reason
}
SafetyDecisionV1 {
  evaluated_at_monotonic_us: u64
  system_state: enum; operation_context: enum; owner: enum
  allowed_motion: bool
  contingency_policy: NONE | GROUND_QUALIFIED | FLIGHT_QUALIFIED // last is unavailable pre-G4
  fault_code: enum; recovery_interlock: bool
}
WingTrajectoryV1 {
  evaluated_at_monotonic_us: u64; calibrated_profile_id: string
  servo_left_target_deg: finite float; servo_right_target_deg: finite float
  // This is command angle, NOT measured wing hinge/airframe attitude.
}
ActuatorOutputV1 {
  time_us: u64; pwm_left_pulse_us: bounded integer; pwm_right_pulse_us: bounded integer
  output_enable: bool; envelope_version: string; status: enum
}
```

Fields that are `UNKNOWN` must remain explicit; never silently coerce to healthy. A normalized command is only *intent* and is not an actuator instruction. `NaN`, infinities, negative/stale timestamps or unknown configuration revisions are denied.

## 3. Control timebase, control periods and jitter — design hypotheses

- Use **monotonic time** for freshness, waveform phase and safety; do not advance phase by loop count. Virtual clock deterministically drives host tests. Handle microsecond counter wrap/restart explicitly.
- **Exploratory scheduler:** core safety/intent evaluation every `T_CORE = 5 ms`; hardware PWM nominally `T_PWM = 20 ms` (50 Hz) **only if selected servo supports these values**. These are *test assumptions*, **not approved timing/servo specifications**. Wing flap mechanical frequency is NOT servo PWM carrier frequency. Separate them in all logs.
- On ESP32-C3 candidate, LEDC hardware PWM can create independent output channels; final frequency, timer sharing, PWM resolution and GPIO boot states must be validated against board/driver version. See official https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/api-reference/peripherals/ledc.html .
- Avoid blocking delays, web requests, heap allocations and flash writes on control/safety path. ISR/RX callbacks may append bounded observations; scheduling/invariant checks occur in a controlled task/context, not fragmented callbacks.
- Proposed instrumentation: `dt_core_us`, `core_eval_worst_us`, `output_age_us`, `uart_frame_age_us`, `rf_link_state`, `brownout_count`, PWM missed-update count and queue overrun count. Define **numeric acceptable maxima after chosen exact components and G2 measurements**.
- When overloaded, record a timing fault and enter appropriate context-specific policy; **do not assume an overloaded CPU can execute a perfect emergency stop**.

## 4. Waveform and mixer semantics

For conceptual testing, normalized common input `u in [0,1]` and steering `s in [-1,1]` map to bounded stroke requests `L = common(u) + differential(s)` and `R = common(u) - differential(s)`; actual sign, linkage orientation, frequency range and control authority TBD by measured rig. Asymmetric command creates a candidate moment, **not a guaranteed yaw**.

A sinusoidal **test-only** waveform can use phase `phi(t+dt) = wrap(phi(t) + 2π f(t) dt)` with time in seconds; output `midpoint + bounded_amp × waveform(phi)`. Profiles and limit/slew law must act **before** electrical output. No unmeasured clamp to generic servo 0–180° allowed. Retain per-side calibration matrices linking servo pulse ↔ actual wing angular displacement, direction and backlash.

On motion invalidity (non-finite, impossible slew or stale config), produce an explicit supervisor fault; never reuse the most recent non-neutral servo target indefinitely without policy.

## 5. Configuration contract

- Versioned, schema-validated *board profile* (actual GPIO/UART/regulator) and *airframe profile* (each servo endpoints, safe pulse, travel, stroke-vs-command calibration, mass/CG revision).
- Software must reject missing/revision-mismatched/CRC-invalid config before arming; safe defaults are **disarmed defaults**, never active flight defaults.
- Calibrating, OTA, web commands, writing safety limits and swapping RC owners require DISARMED, grounded bench access and explicit authorization. Changes are audited as atomic config transactions; power loss must not result in an accidentally permissive profile.
- Simulator profile values must be tagged `SIM_ONLY` and **not flashed as flight envelope**.

## 6. Simulation contract and verification boundaries

- Deterministic simulated RC, UART validity/failsafe flags, timer, 2-servo actuator model with configured travel/slew constraints and voltage monitor; replay event streams, CSV trace and intentional fault injection.
- No claim that a kinematic virtual butterfly accurately predicts lift, stability, motor current, servo thermal limits, field RF reliability or touchdown. Any physics extension requires empirical coefficients and recorded validation set.
- Mandatory automated core property tests: no auto-arm across reboot; one authority; bad frames do not refresh age; bounded output; no armed config; no flight-policy assumption; repeatable virtual-time output; fault recovery needs deliberate acknowledgment.

## 7. External documents and future review evidence

- `16_RC_INTERFACE_CONTRACT.md`: RF boundary and pilot channel authority.
- `23_PINOUT_AND_SIGNAL_CONTRACT.md`: candidate D4/D5 PWM, D6/D7 UART, D1 ADC, NOT frozen.
- `27_SAFETY_AND_FLIGHT_STATE_MACHINE.md`: guards and contextual contingency, **not approved G4 policy**.
- `29_REQUIREMENTS_INTEGRATION_TRACEABILITY.md`: FR/NFR and integration tests.
- `30_G0_DESIGN_FREEZE_READINESS.md`: explicit owner approval required before tasks and energized tests.

**No code changes, firmware releases or Task assignments are authorized by this document.**

## 8. Pilot mapping / profile interfaces (v0.2 — PROPOSED)

Separate `RcChannelMapV1` (TX/RX version, channel indices, endpoint/reversal/deadband evidence) from `CalibrationRecordV1` (actual left/right servo/wing pulse and motion limits) and from `OperationContext` (test authorization). The RX adapter only normalizes verified pilot-intent observations. A transmitter arm switch edge is recognized **inside** `AuthorityManager` with reset-safe edge history; the radio-layer arm mechanism never directly enables PWM. `Rate/Profile` requests from the radio are accepted only as disarmed selections unless a later flight-validated transition is approved. No runtime edit of calibration/profile/OTA in armed contexts.

`RcReceiverAdapter` must record actual RF health/receiver failsafe provenance independently of serial-frame integrity; if the selected RX cannot expose reliable link health under transmitter-off, G2 must resolve that limitation, rather than falsely reporting HEALTHY. `MotionPlanner` should expose requested common/differential, saturated effort and reason to `TelemetryLogger`, without asserting measured lift, heading or actual servo angle. Exact calibration and tests: `32`, `33`, `35`.
